from collections import OrderedDict, UserDict, defaultdict
from collections.abc import Mapping, MutableMapping
from inspect import isclass
from typing import Any, Generic, NotRequired, Required, TypedDict, TypeVar

import pytest

from dict2any.jq_path import JqPath
from dict2any.parsers import Stage, Subparse
from dict2any.parsers.dict import DictParser


class MyTypedDict(TypedDict):
    a: int
    b: str
    c: NotRequired[bool]


class MyPartialTypedDict(TypedDict, total=False):
    a: Required[int]
    b: str


class MyUserDict(UserDict):
    pass


T = TypeVar('T')


class MyGenericUserDict(UserDict, Generic[T]):
    pass


class MySubclassDict(dict):
    pass


class MyCustomMapping(Mapping):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return self.data.__len__()

    def __eq__(self, other):
        return isinstance(other, MyCustomMapping) and self.data == other.data


class MyCustomMutableMapping(MutableMapping):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return self.data.__len__()

    def __delitem__(self, key: Any) -> None:
        return self.data.__delitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        return self.data.__delitem__(key, value)

    def __eq__(self, other):
        return isinstance(other, MyCustomMutableMapping) and self.data == other.data


@pytest.mark.parametrize(
    ['stage', 'field_type', 'expected'],
    [
        (Stage.Exact, dict, True),
        (Stage.Exact, OrderedDict, True),
        (Stage.Exact, dict[str, int], True),
        (Stage.Exact, dict[str, str], True),
        (Stage.Exact, list, False),
        (Stage.Exact, MyTypedDict, False),
        (Stage.Exact, MyPartialTypedDict, False),
        (Stage.Exact, MyUserDict, False),
        (Stage.Exact, MySubclassDict, False),
        (Stage.Exact, MyCustomMapping, False),
        (Stage.Exact, MyCustomMutableMapping, False),
        (Stage.Exact, defaultdict, False),
        (Stage.Exact, None, False),
        (Stage.Fallback, dict, True),
        (Stage.Fallback, OrderedDict, True),
        (Stage.Fallback, dict[str, int], True),
        (Stage.Fallback, dict[str, str], True),
        (Stage.Fallback, MyTypedDict, True),
        (Stage.Fallback, MyPartialTypedDict, True),
        (Stage.Fallback, MyUserDict, True),
        (Stage.Fallback, MySubclassDict, True),
        (Stage.Fallback, MyCustomMapping, True),
        (Stage.Fallback, MyCustomMutableMapping, True),
        (Stage.Fallback, defaultdict, True),
        (Stage.Fallback, None, False),
        (Stage.Fallback, list, False),
    ],
)
def test_can_parse(stage: Stage, field_type: Any, expected: bool, path: JqPath):
    assert DictParser().can_parse(stage=stage, path=path, field_type=field_type) == expected


def test_cannot_parse_override(path: JqPath):
    assert DictParser().can_parse(stage=Stage.Override, path=path, field_type=dict) == False


@pytest.mark.parametrize(
    ['field_type', "data", 'expected'],
    [
        (dict, None, ValueError),
        (dict, {}, {}),
        (dict, {"hello": "world"}, {"hello": "world"}),
        (dict, {1: 1, 2: 2}, {1: 1, 2: 2}),
        (dict[str, str], {"hello": "world"}, {"hello": "world"}),
        (dict[str, int], {"hello": "world"}, ValueError),
        (dict, MyTypedDict(a=1, b="hello"), {"a": 1, "b": "hello"}),
        (dict, MyTypedDict(a=1, b="hello", c=True), {"a": 1, "b": "hello", "c": True}),
        (MyTypedDict, MyTypedDict(a=1, b="hello"), MyTypedDict(a=1, b="hello")),
        (MyPartialTypedDict, MyPartialTypedDict(a=1, b="hello"), MyPartialTypedDict(a=1, b="hello")),
        (dict, MyPartialTypedDict(a=1, b="hello", extra=32), {"a": 1, "b": "hello", "extra": 32}),  # type: ignore
        (dict, MyUserDict({"hello": "world"}), {"hello": "world"}),
        (MyUserDict, MyUserDict({"hello": "world"}), MyUserDict({"hello": "world"})),
        (dict, MySubclassDict({"hello": "world"}), {"hello": "world"}),
        (MySubclassDict, {"hello": "world"}, MySubclassDict({"hello": "world"})),
        (dict, MyCustomMapping({"hello": "world"}), {"hello": "world"}),
        (MyCustomMapping, {"hello": "world"}, MyCustomMapping({"hello": "world"})),
        (dict, MyCustomMutableMapping({"hello": "world"}), {"hello": "world"}),
        (MyCustomMutableMapping, {"hello": "world"}, MyCustomMutableMapping({"hello": "world"})),
        (dict, defaultdict(list, {"hello": "world"}), {"hello": "world"}),  # type: ignore
        (defaultdict, {"hello": "world"}, TypeError),
        (dict[str, Any], None, ValueError),
    ],
)
def test_parse(field_type, data, expected, path: JqPath, subparser: Subparse):
    if isclass(expected) and issubclass(expected, BaseException):
        with pytest.raises(expected):
            DictParser().parse(path=path, field_type=field_type, data=data, subparse=subparser)
    else:
        assert DictParser().parse(path=path, field_type=field_type, data=data, subparse=subparser) == expected
