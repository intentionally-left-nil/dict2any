from inspect import isclass
from typing import Any, Optional, Union

import pytest

from dict2any.jq_path import JqPath
from dict2any.parsers import ClassParser, Stage, Subparse


class Simple:
    def __eq__(self, other):
        return isinstance(other, Simple)


class MyClass:
    def __init__(self, x: int, y: str = "hello", *, z: Optional[int] = None):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return isinstance(other, MyClass) and self.x == other.x and self.y == other.y and self.z == other.z


class MyClassWithKwargs:
    def __init__(self, x: int, y: str = "hello", **kwargs: Any):
        self.x = x
        self.y = y
        self.kwargs = kwargs

    def __eq__(self, other):
        return (
            isinstance(other, MyClassWithKwargs)
            and self.x == other.x
            and self.y == other.y
            and self.kwargs == other.kwargs
        )

    def __repr__(self):
        return f"MyClassWithKwargs(x={self.x}, y={self.y}, kwargs={self.kwargs})"


class WithPositionalOnly:
    def __init__(self, x: int, /, y: str = "hello", *, z: Optional[int] = None):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return isinstance(other, MyClass) and self.x == other.x and self.y == other.y and self.z == other.z


class MySubclass(MyClass):
    def __init__(self, a: int, b: str = "hello", *, c: Optional[int] = None):
        super().__init__(x=a, y=b, z=c)


empty = lambda x: x


@pytest.mark.parametrize(
    ['stage', 'field_type', 'expected'],
    [
        (Stage.LastChance, Simple, True),
        (Stage.LastChance, int, True),
        (Stage.LastChance, MyClass, True),
        (Stage.LastChance, MySubclass, True),
        (Stage.LastChance, MyClassWithKwargs, True),
        (Stage.LastChance, WithPositionalOnly, False),
        (Stage.LastChance, type(empty), False),
        (Stage.Exact, Simple, False),
        (Stage.Fallback, Simple, False),
    ],
)
def test_can_parse(stage: Stage, field_type: Any, expected: bool, path: JqPath):
    assert ClassParser().can_parse(stage=stage, path=path, field_type=field_type) == expected


@pytest.mark.parametrize(
    ['field_type', "data", 'expected'],
    [
        (Simple, {}, Simple()),
        (Simple, 5, ValueError),
        (MyClass, {"x": 5, "y": "hello"}, MyClass(x=5, y="hello")),
        (MyClass, {"x": 5, "y": "hello", "z": 42}, MyClass(x=5, y="hello", z=42)),
        (MyClass, {"x": 5}, MyClass(x=5, y="hello", z=None)),
        (MyClass, {"y": "missing_x"}, ValueError),
        (
            MyClassWithKwargs,
            {"x": 5, "y": "hello", "unknown": "other"},
            MyClassWithKwargs(x=5, y="hello", unknown="other"),
        ),
        (MySubclass, {"a": 5, "b": "hello"}, MySubclass(a=5, b="hello", c=None)),
    ],
)
def test_parse(field_type, data, expected, path: JqPath, subparser: Subparse):
    if isclass(expected) and issubclass(expected, BaseException):
        with pytest.raises(expected):
            ClassParser().parse(path=path, field_type=field_type, data=data, subparse=subparser)
    else:
        assert ClassParser().parse(path=path, field_type=field_type, data=data, subparse=subparser) == expected
