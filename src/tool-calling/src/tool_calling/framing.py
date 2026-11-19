"""Tool-use framing shared by preparation and generation; controls are inert."""

from collections.abc import Callable, Iterator, Sequence
from enum import StrEnum

from model_tokenizer import Tokenizer


class _Control(StrEnum):
    TOOL = "<TOOL>"
    PARAMS = "<PARAMS>"
    DELIMETER = "<DELIMETER>"  # Preserve the source protocol spelling.
    DESCRIPTION = "<DESCRIPTION>"
    TOOL_END = "<TOOL_END>"
    USER = "<USER>"
    TOOL_CALL = "<TOOL_CALL>"
    EXECUTE = "<EXECUTE>"
    TOOL_RESULT = "<TOOL_RESULT>"
    TOOL_RESULT_END = "<TOOL_RESULT_END>"
    ASSISTANT = "<ASSISTANT>"
    END_OF_DOCUMENT = "<END_OF_DOCUMENT>"


CONTROL_TOKENS = tuple(marker.value for marker in _Control)
_TextEncoder = Callable[[str], Sequence[int]]


def _parts(record: dict) -> Iterator[tuple[str, bool]]:
    """Yield text or a control, annotated with whether the model predicts it."""
    for tool in record["tools"]:
        yield _Control.TOOL, False
        yield tool["name"], False
        yield _Control.PARAMS, False
        if not isinstance(tool["parameters"], list):
            raise ValueError("Tool parameters must be a list.")
        for index, parameter in enumerate(tool["parameters"]):
            if index:
                yield _Control.DELIMETER, False
            yield parameter, False
        yield _Control.DESCRIPTION, False
        yield tool["description"], False
        yield _Control.TOOL_END, False

    for message in record["messages"]:
        role = message["role"]
        if role == "user":
            yield _Control.USER, False
            yield message["content"], False
        elif role == "tool":
            yield _Control.TOOL_RESULT, False
            yield message["content"], False
            yield _Control.TOOL_RESULT_END, False
        elif role == "assistant":
            content = message.get("content")
            call = message.get("tool_call")
            if content is None and call is None:
                raise ValueError("Assistant message needs content or a tool call.")
            if content is not None:
                yield _Control.ASSISTANT, True
                yield content, True
            if call is not None:
                yield _Control.TOOL_CALL, True
                yield call["name"], True
                if not isinstance(call["arguments"], list):
                    raise ValueError("Tool call arguments must be a list.")
                for argument in call["arguments"]:
                    yield _Control.DELIMETER, True
                    yield argument, True
                yield _Control.EXECUTE, True
        else:
            raise ValueError(f"Unsupported message role: {role!r}")


def _ordinary_text(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Expected a text field to be a string.")
    return value


def iter_text_fields(record: dict) -> Iterator[str]:
    """Yield independent BPE documents, excluding controls and metadata."""
    for value, _ in _parts(record):
        if not isinstance(value, _Control):
            yield _ordinary_text(value)


def _encode_piece(tokenizer: Tokenizer, value: str, encode_text: _TextEncoder) -> Sequence[int]:
    if isinstance(value, _Control):
        return (tokenizer.control_token_ids[value.value],)
    return encode_text(_ordinary_text(value))


def format_prefix(tokenizer: Tokenizer, record: dict) -> list[int]:
    """Frame tools and supplied turns without a response marker or document end."""
    tokens = []
    for value, _ in _parts(record):
        tokens.extend(_encode_piece(tokenizer, value, tokenizer.encode))
    return tokens


def format_prompt(tokenizer: Tokenizer, user_text: str, tools: list[dict]) -> list[int]:
    """Frame the tool definitions and user turn as a generation prefix."""
    return format_prefix(tokenizer, {"tools": tools, "messages": [{"role": "user", "content": user_text}]})


def format_record(tokenizer: Tokenizer, record: dict, *, encode_text: _TextEncoder | None = None) -> dict:
    """Return one complete sequence with True only for assistant-predicted IDs."""
    if encode_text is None:
        encode_text = tokenizer.encode
    tokens = []
    loss_mask = []
    for value, generated in _parts(record):
        ids = _encode_piece(tokenizer, value, encode_text)
        tokens.extend(ids)
        loss_mask.extend([generated] * len(ids))
    tokens.append(tokenizer.control_token_ids[_Control.END_OF_DOCUMENT.value])
    loss_mask.append(True)
    return {"tokens": tokens, "loss_mask": loss_mask}
