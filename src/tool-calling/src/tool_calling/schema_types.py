"""Shared contracts for seeded tool-calling data generation.

The first parameter name is its semantic identifier; subsequent names are
presentation aliases. Schema files provide cases, preparation, and resolution.
"""

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence
import random


class InvalidCombination(Exception):
    """A generated case cannot produce a valid interaction."""


@dataclass(frozen=True)
class Parameter:
    names: Sequence[str]


@dataclass(frozen=True)
class Task:
    id: str
    prompts: Sequence[str]
    answers: Sequence[str]
    cases: Callable[[random.Random, int], Iterable[dict]]
    case_count: int | None = None
    presentations_per_case: int | None = None


@dataclass(frozen=True)
class Decision:
    fields: dict
    arguments: dict


@dataclass(frozen=True)
class Schema:
    id: str
    tool_names: Sequence[str]
    descriptions: Sequence[str]
    parameters: Sequence[Parameter]
    tasks: Sequence[Task]
