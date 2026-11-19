"""Build deterministic interactions from bundled, inert tool simulations."""

import hashlib
from importlib import import_module
import inspect
import json
import math
from pathlib import Path
from pkgutil import iter_modules
import random
import string

from . import schemas
from .schema_types import Decision, InvalidCombination, Parameter, Schema, Task

DEFAULT_SEED = 42
SPLITS = ("train", "validation")
SPLIT_BUDGETS = {"train": (175, 3), "validation": (100, 2)}
SCHEMA_COUNTS = {"train": 198, "validation": 12}



def _strings(values, label):
    if not isinstance(values, (list, tuple)) or not values:
        raise ValueError(f"{label} must be a nonempty list or tuple of strings")
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError(f"{label} must contain nonempty strings")


def _template(template, fields, label):
    try:
        for _, name, spec, _ in string.Formatter().parse(template):
            if name is not None and name not in fields:
                raise ValueError(f"unknown field {name!r}")
            if spec and ("{" in spec or "}" in spec):
                raise ValueError("nested format fields are not supported")
        return template.format_map(fields)
    except (ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        raise ValueError(f"invalid {label}: {exc}") from exc


def _add_prompt_newline(template, rng):
    """Occasionally insert a newline in literal prompt text, never in a field."""
    if rng.random() >= 0.2:
        return template
    try:
        parts = list(string.Formatter().parse(template))
    except ValueError:
        return template  # Let _template report malformed templates consistently.
    separators = []
    brace_depth = 0
    quoted = False
    single_quoted = False
    for part_index, (literal, _, _, _) in enumerate(parts):
        for index, char in enumerate(literal):
            if char == '"' and not single_quoted:
                quoted = not quoted
            elif char == "'" and not quoted:
                if single_quoted and (index + 1 == len(literal) or not literal[index + 1].isalnum()):
                    single_quoted = False
                elif not single_quoted and (index == 0 or not literal[index - 1].isalnum()):
                    single_quoted = True
            elif not quoted and not single_quoted and char == "{":
                brace_depth += 1
            elif not quoted and not single_quoted and char == "}" and brace_depth:
                brace_depth -= 1
            elif (char == " " and not quoted and not single_quoted and not brace_depth
                  and 0 < index < len(literal) - 1
                  and literal[index - 1].isalpha() and literal[index + 1].isalpha()):
                separators.append((part_index, index))
    if not separators:
        return template
    part_index, index = rng.choice(separators)
    rebuilt = []
    for current, (literal, name, spec, conversion) in enumerate(parts):
        if current == part_index:
            literal = literal[:index + 1] + "\n" + literal[index + 1:]
        rebuilt.append(literal.replace("{", "{{").replace("}", "}}"))
        if name is not None:
            field = "{" + name
            if conversion is not None:
                field += "!" + conversion
            if spec:
                field += ":" + spec
            rebuilt.append(field + "}")
    return "".join(rebuilt)


def _validate_schema(schema, prepare, resolve, source):
    """Reject malformed definitions before emitting examples."""
    if not isinstance(schema, Schema):
        raise ValueError(f"{source}: SCHEMA must be a Schema")
    if not isinstance(schema.id, str) or not schema.id:
        raise ValueError(f"{source}: schema id must be a nonempty string")
    _strings(schema.tool_names, f"{source}: tool names")
    _strings(schema.descriptions, f"{source}: descriptions")
    if not isinstance(schema.parameters, (list, tuple)):
        raise ValueError(f"{source}: parameters must be a list or tuple")
    aliases = set()
    semantic_names = []
    for parameter in schema.parameters:
        if not isinstance(parameter, Parameter):
            raise ValueError(f"{source}: each parameter must be a Parameter")
        _strings(parameter.names, f"{source}: parameter names")
        if len(set(parameter.names)) != len(parameter.names) or aliases.intersection(parameter.names):
            raise ValueError(f"{source}: parameter names must be unique within a schema")
        aliases.update(parameter.names)
        semantic_names.append(parameter.names[0])
    if not callable(prepare) or not callable(resolve):
        raise ValueError(f"{source}: prepare and resolve must be callable")
    try:
        inspect.signature(prepare).bind(task_id="example", case={})
        inspect.signature(resolve).bind(**dict.fromkeys(semantic_names, "example"))
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{source}: incompatible prepare or resolve signature: {exc}") from exc
    if not isinstance(schema.tasks, (list, tuple)) or not schema.tasks:
        raise ValueError(f"{source}: tasks must be a nonempty list or tuple")
    task_ids = set()
    for task in schema.tasks:
        if not isinstance(task, Task) or not isinstance(task.id, str) or not task.id:
            raise ValueError(f"{source}: each task must have a nonempty id")
        if task.id in task_ids:
            raise ValueError(f"{source}: duplicate task id {task.id!r}")
        task_ids.add(task.id)
        _strings(task.prompts, f"{source}: task {task.id} prompts")
        _strings(task.answers, f"{source}: task {task.id} answers")
        if not callable(task.cases):
            raise ValueError(f"{source}: task {task.id} cases must be callable")
        try:
            inspect.signature(task.cases).bind(random.Random(0), 1)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{source}: task {task.id} cases must accept rng and count: {exc}") from exc
        for name in ("case_count", "presentations_per_case"):
            value = getattr(task, name)
            if value is not None and (type(value) is not int or value < 1):
                raise ValueError(f"{source}: task {task.id} {name} must be a positive integer or None")


def _load_schemas(split):
    """Import only the model's bundled modules, preserving source schema order."""
    package = import_module(f"{schemas.__name__}.{split}")
    modules = sorted(
        item.name for item in iter_modules(package.__path__)
        if not item.ispkg and not item.name.startswith("_")
    )
    if len(modules) != SCHEMA_COUNTS[split]:
        raise ValueError(
            f"Expected {SCHEMA_COUNTS[split]} bundled {split} schemas, found {len(modules)}."
        )
    loaded = []
    ids = set()
    for name in modules:
        module = import_module(f"{package.__name__}.{name}")
        filename = f"{name}.py"
        source = f"{split}/{filename}"
        schema = getattr(module, "SCHEMA", None)
        prepare = getattr(module, "prepare", None)
        resolve = getattr(module, "resolve", None)
        _validate_schema(schema, prepare, resolve, source)
        if schema.id in ids:
            raise ValueError(f"{source}: duplicate schema id {schema.id!r} in {split}")
        ids.add(schema.id)
        loaded.append((filename, schema, prepare, resolve))
    return sorted(loaded, key=lambda item: item[1].id)


def _rng(seed, split, schema_id, task_id, stream):
    key = json.dumps([seed, split, schema_id, task_id, stream], ensure_ascii=False, separators=(",", ":"))
    return random.Random(int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest(), "big"))


def _permutation(size, rank):
    """Unrank a permutation without materializing the factorial-sized set."""
    remaining = list(range(size))
    result = []
    for width in range(size, 0, -1):
        rank, index = divmod(rank, math.factorial(width - 1))
        result.append(remaining.pop(rank))
        rank = index
    return result

def _generate_schema(split, filename, schema, prepare, resolve, output, seed):
    """Write bounded presentations from simulated inputs and results."""
    semantic_names = [parameter.names[0] for parameter in schema.parameters]
    source = f"{split}/{filename}"
    for task in sorted(schema.tasks, key=lambda item: item.id):
        default_cases, default_presentations = SPLIT_BUDGETS[split]
        case_count = task.case_count if task.case_count is not None else default_cases
        presentations_per_case = (task.presentations_per_case
                                  if task.presentations_per_case is not None else default_presentations)
        case_rng = _rng(seed, split, schema.id, task.id, "cases")
        presentation_rng = _rng(seed, split, schema.id, task.id, "presentations")
        whitespace_rng = _rng(seed, split, schema.id, task.id, "whitespace") if split == "train" else None
        choices = [schema.tool_names, schema.descriptions, task.prompts, task.answers]
        choices.extend(parameter.names for parameter in schema.parameters)
        decks = [[] for _ in choices]
        order_count = math.factorial(len(semantic_names))
        order_offset = presentation_rng.randrange(order_count)
        task_valid = 0
        cases = iter(task.cases(case_rng, case_count))
        for _ in range(case_count):
            try:
                case = next(cases)
            except StopIteration as exc:
                raise ValueError(f"{source}: task {task.id} yielded fewer than {case_count} cases") from exc
            if not isinstance(case, dict):
                raise ValueError(f"{source}: task {task.id} case must be a dict")
            try:
                decision = prepare(task_id=task.id, case=case)
                if not isinstance(decision, Decision) or not isinstance(decision.fields, dict) or not isinstance(decision.arguments, dict):
                    raise ValueError(f"{source}: prepare must return a Decision with dict fields and arguments")
                if set(decision.arguments) != set(semantic_names):
                    raise ValueError(f"{source}: decision arguments must match semantic parameter names")
                if "result" in decision.fields:
                    raise ValueError(f"{source}: result is reserved for answer templates")
                result = resolve(**decision.arguments)
            except InvalidCombination:
                continue
            if not isinstance(result, str):
                raise ValueError(f"{source}: resolve must return a string, got {type(result).__name__}")
            if any(not isinstance(value, str) for value in decision.arguments.values()):
                raise ValueError(f"{source}: decision arguments must be strings")
            for presentation in range(presentations_per_case):
                ordinal = task_valid * presentations_per_case + presentation
                selected = []
                for index, choice in enumerate(choices):
                    if ordinal % len(choice) == 0:
                        decks[index] = list(choice)
                        presentation_rng.shuffle(decks[index])
                    selected.append(decks[index][ordinal % len(choice)])
                tool_name, description, prompt, answer = selected[:4]
                user_text = _template(prompt, decision.fields, f"{source}: prompt")
                if whitespace_rng is not None:
                    augmented = _add_prompt_newline(prompt, whitespace_rng)
                    if augmented != prompt:
                        candidate = _template(augmented, decision.fields, f"{source}: prompt")
                        # Some schemas put an argument's value directly in a template literal.
                        if all(value not in user_text or value in candidate
                               for value in decision.arguments.values()):
                            user_text = candidate
                aliases = selected[4:]
                order = _permutation(len(semantic_names), (order_offset + ordinal) % order_count)
                semantic_order = [semantic_names[index] for index in order]
                record = {
                    "tools": [{"name": tool_name, "description": description, "parameters": [aliases[index] for index in order]}],
                    "messages": [
                        {"role": "user", "content": user_text},
                        {"role": "assistant", "tool_call": {"name": tool_name, "arguments": [decision.arguments[name] for name in semantic_order]}},
                        {"role": "tool", "content": result},
                        {"role": "assistant", "content": _template(answer, {**decision.fields, "result": result}, f"{source}: answer")},
                    ],
                    "execution": {"schema_file": source, "schema_id": schema.id, "task_id": task.id, "semantic_parameter_order": semantic_order},
                }
                output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            task_valid += 1
        try:
            next(cases)
        except StopIteration:
            pass
        else:
            raise ValueError(f"{source}: task {task.id} yielded more than {case_count} cases")

def write_structured_splits(directory: Path, *, seed: int = DEFAULT_SEED) -> None:
    """Generate each seeded split into a new directory, without any live tools."""
    directory.mkdir(exist_ok=False)
    for split in SPLITS:
        with (directory / f"{split}.jsonl").open("x", encoding="utf-8", newline="\n") as output:
            for filename, schema, prepare, resolve in _load_schemas(split):
                _generate_schema(split, filename, schema, prepare, resolve, output, seed)
