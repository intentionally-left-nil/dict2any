from collections import namedtuple
from inspect import isclass
from typing import NamedTuple

import pytest

from dict2any.jq_path import JqPath
from dict2any.parsers import Stage, Subparse
from dict2any.parsers.tuple import NamedTupleParser, TupleParser

UntypedTuple = namedtuple("UntypedTuple", ["a", "b"])


class TypedTuple(NamedTuple):
    a: int
    b: str


@pytest.mark.parametrize(
    ["field_type", "expected"],
    [
        (tuple, True),
        (tuple, True),
        (tuple[int], True),
        (tuple[int, str], True),
        (tuple[int, str, str], True),
        (tuple[int, ...], True),
        (UntypedTuple, False),
        (TypedTuple, False),
        (list, False),
    ],
)
def test_can_parse(field_type, expected, path: JqPath):
    assert TupleParser().can_parse(stage=Stage.Exact, path=path, field_type=field_type) == expected


def test_cannot_parse_fallback(path: JqPath):
    assert TupleParser().can_parse(stage=Stage.Fallback, path=path, field_type=tuple) == False


@pytest.mark.parametrize(
    ["field_type", "data", "expected"],
    [
        (tuple, tuple(), tuple()),
        (tuple, (1,), (1,)),
        (tuple, (1, 2), (1, 2)),
        (tuple, (1, 2, "hello"), (1, 2, "hello")),
        (tuple, [], tuple()),
        (tuple, [1], (1,)),
        (tuple, [1, 2], (1, 2)),
        (tuple, TypedTuple(1, "hello"), (1, "hello")),
        (tuple, UntypedTuple(1, "hello"), (1, "hello")),
        (tuple[int], (1,), (1,)),
        (tuple[int, int], (1, 2), (1, 2)),
        (tuple[int, int], (1,), ValueError),
        (tuple[int, int, str], (1, 2, "hello"), (1, 2, "hello")),
        (tuple[int, int, str], (1, 2, 3), ValueError),
        (tuple[int], ("hello"), ValueError),
        (tuple[int, ...], tuple(), tuple()),
        (tuple[int, ...], (1,), (1,)),
        (tuple[int, ...], (1, 2), (1, 2)),
        (tuple[int, ...], (1, 2, "hello"), ValueError),
        (tuple, None, ValueError),
    ],
)
def test_parse(field_type, data, expected, path: JqPath, subparser: Subparse):
    if isclass(expected) and issubclass(expected, BaseException):
        with pytest.raises(expected):
            TupleParser().parse(path=path, field_type=field_type, data=data, subparse=subparser)
    else:
        assert TupleParser().parse(path=path, field_type=field_type, data=data, subparse=subparser) == expected


@pytest.mark.parametrize(
    ["field_type", "expected"],
    [
        (TypedTuple, True),
        (UntypedTuple, True),
        (tuple, False),
        (tuple, False),
        (tuple[int], False),
        (list, False),
    ],
)
def test_can_parse_named_tuple(field_type, expected, path: JqPath):
    assert NamedTupleParser().can_parse(stage=Stage.Exact, path=path, field_type=field_type) == expected


def test_cannot_parse_named_tuple_fallback(path: JqPath):
    assert NamedTupleParser().can_parse(stage=Stage.Fallback, path=path, field_type=TypedTuple) == False


@pytest.mark.parametrize(
    ["field_type", "data", "expected"],
    [
        (TypedTuple, [5, "hello"], TypedTuple(5, "hello")),
        (TypedTuple, (5, "hello"), TypedTuple(5, "hello")),
        (TypedTuple, tuple(), ValueError),
        (TypedTuple, (5,), ValueError),
        (TypedTuple, (5, 5), ValueError),
        (TypedTuple, (5, 5, 5), ValueError),
        (TypedTuple, {"a": 5, "b": "hello"}, TypedTuple(5, "hello")),
        (TypedTuple, {}, ValueError),
        (TypedTuple, {"a": 5}, ValueError),
        (TypedTuple, {"a": 5, "b": None}, ValueError),
        (TypedTuple, {"a": 5, "c": None}, ValueError),
        (TypedTuple, {"a": 5, "b": "hello", "c": 5}, ValueError),
        (TypedTuple, None, ValueError),
        (
            TypedTuple,
            tuple[int](
                [5],
            ),
            ValueError,
        ),
        (UntypedTuple, [5, "hello"], UntypedTuple(5, "hello")),
        (UntypedTuple, (5, "hello"), UntypedTuple(5, "hello")),
        (UntypedTuple, (5, 5), UntypedTuple(5, 5)),  # Unlike a TypedTuple, there are no type checks
        (UntypedTuple, tuple(), ValueError),
        (UntypedTuple, (5,), ValueError),
        (UntypedTuple, (5, 5, 5), ValueError),
        (UntypedTuple, {"a": 5, "b": "hello"}, UntypedTuple(5, "hello")),
        (UntypedTuple, {}, ValueError),
        (UntypedTuple, {"a": 5}, ValueError),
        (UntypedTuple, {"a": 5, "b": None}, UntypedTuple(5, None)),
        (UntypedTuple, {"a": 5, "c": None}, ValueError),
        (UntypedTuple, {"a": 5, "b": "hello", "c": 5}, ValueError),
        (UntypedTuple, None, ValueError),
        (
            UntypedTuple,
            tuple[int](
                [5],
            ),
            ValueError,
        ),
    ],
)
def test_parse_named_tuple(field_type, data, expected, path: JqPath, subparser: Subparse):
    if isclass(expected) and issubclass(expected, BaseException):
        with pytest.raises(expected):
            NamedTupleParser().parse(path=path, field_type=field_type, data=data, subparse=subparser)
    else:
        assert NamedTupleParser().parse(path=path, field_type=field_type, data=data, subparse=subparser) == expected
