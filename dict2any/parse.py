from random import shuffle
from typing import Any, Type, TypeVar

from dict2any.jq_path import JqPath
from dict2any.parsers import (
    AnyParser,
    BoolParser,
    DataclassParser,
    DictParser,
    FloatParser,
    IntParser,
    ListParser,
    NamedTupleParser,
    NoneParser,
    Parser,
    PathParser,
    Stage,
    StringParser,
    TupleParser,
    TypedDictParser,
    UnionParser,
)

PARSERS = [
    BoolParser(),
    FloatParser(),
    IntParser(),
    NoneParser(),
    StringParser(),
    AnyParser(),
    DataclassParser(),
    DictParser(),
    TypedDictParser(),
    ListParser(),
    PathParser(),
    NamedTupleParser(),
    TupleParser(),
    UnionParser(),
]


T = TypeVar('T')


def parse(cls: Type[T], data: Any, extra_parsers: list[Parser] | None = None) -> T:
    parsers = PARSERS + (extra_parsers or [])
    shuffle(parsers)  # The ordering of the parsers should never matter, enforce that by randomizing the order 😈

    def subparse(path: JqPath, field_type: type, data: Any) -> Any:
        for stage in (Stage.Override, Stage.Exact, Stage.Fallback):
            for parser in parsers:
                if parser.can_parse(stage=stage, path=path, field_type=field_type):
                    return parser.parse(path=path, field_type=field_type, data=data, subparse=subparse)
        raise ValueError(f'No parser found for {field_type} at {path}')

    return subparse(path=JqPath.parse('.'), field_type=cls, data=data)
