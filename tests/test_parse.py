from dataclasses import dataclass
from inspect import isclass
from typing import Any

import pytest

from dict2any import parse


class Custom:
    pass


custom = Custom()


@dataclass
class Inner:
    inner: int


@dataclass
class Outer:
    inner: Inner
    outer: int


@pytest.mark.parametrize(
    ['field_type', 'data', 'expected'],
    [
        (int, 1, 1),
        (Any, custom, custom),
        (dict[str, int], {"a": 1, "b": 2}, {"a": 1, "b": 2}),
        (dict[str, dict[str, int]], {"a": {"b": 1}}, {"a": {"b": 1}}),
        (Outer, {"inner": {"inner": 1}, "outer": 2}, Outer(inner=Inner(inner=1), outer=2)),
    ],
)
def test_parse(field_type, data, expected):
    assert parse(field_type, data) == expected
    if isclass(expected) and issubclass(expected, BaseException):
        with pytest.raises(expected):
            parse(field_type, data)
    else:
        assert parse(field_type, data) == expected
