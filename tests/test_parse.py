from dataclasses import dataclass
from inspect import isclass
from typing import Any

import pytest

from dict2any import parse
from dict2any.parsers import Parser


class Custom:
    def __eq__(self, other):
        return isinstance(other, Custom)


custom = Custom()


def my_function():
    pass


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
        (Custom, {}, Custom()),
        (type(my_function), {}, ValueError),
    ],
)
def test_parse(field_type, data, expected):
    if isclass(expected) and issubclass(expected, BaseException):
        with pytest.raises(expected):
            parse(field_type, data)
    else:
        assert parse(field_type, data) == expected


def test_parse_with_custom_parser():
    class CustomParser(Parser):
        def can_parse(self, stage, path, field_type):
            return True

        def parse(self, path, field_type, data, subparse):
            return "custom"

    assert parse(str, {}, parsers=[CustomParser()]) == "custom"
