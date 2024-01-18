from enum import StrEnum, auto
from typing import Any, Protocol

from dict2any.jq_path import JqPath


class Stage(StrEnum):
    Override = auto()
    Exact = auto()
    Fallback = auto()
    LastChance = auto()


class Subparse(Protocol):
    def __call__(self, *, path: JqPath, field_type: type, data: Any) -> Any:
        ...


class Parser(Protocol):
    def can_parse(self, *, stage: Stage, path: JqPath, field_type: type):
        ...

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        ...
