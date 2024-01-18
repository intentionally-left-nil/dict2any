from dataclasses import KW_ONLY, dataclass, field
from inspect import isclass
from typing import Any

import pytest

from dict2any.jq_path import JqPath
from dict2any.parsers import Stage, Subparse
from dict2any.parsers.dataclass import DataclassParser


@dataclass
class EmptyDataclass:
    pass


class Custom:
    pass


custom = Custom()


@dataclass
class MyDataclass:
    a: int
    b: str | None
    not_in_init: str = field(init=False)
    _: KW_ONLY
    optional_str: str | None = None
    optional_list: list[int] | None = field(default_factory=list)
    optional_custom: Custom | None = None

    def __post_init__(self):
        self.not_in_init = "not_in_init"


@pytest.mark.parametrize(
    ['stage', 'field_type', 'expected'],
    [
        (Stage.Exact, EmptyDataclass, True),
        (Stage.Exact, MyDataclass, True),
        (Stage.Exact, dict, False),
        (Stage.Fallback, MyDataclass, False),
    ],
)
def test_can_parse(stage: Stage, field_type: Any, expected: bool, path: JqPath):
    assert DataclassParser().can_parse(stage=stage, path=path, field_type=field_type) == expected


@pytest.mark.parametrize(
    ['field_type', "data", 'expected'],
    [
        (EmptyDataclass, {}, EmptyDataclass()),
        (EmptyDataclass, {"hello": "world"}, ValueError),
        (MyDataclass, {}, ValueError),
        (MyDataclass, [], ValueError),
        (MyDataclass, {"a": 1, "b": "hello"}, MyDataclass(a=1, b="hello")),
        (MyDataclass, {"a": 1, "b": "hello", "not_in_init": "oops"}, ValueError),
        (MyDataclass, {"a": 1, "b": "hello", "optional_str": "opt"}, MyDataclass(a=1, b="hello", optional_str="opt")),
        (MyDataclass, {"a": 1, "b": "hello", "optional_list": [5]}, MyDataclass(a=1, b="hello", optional_list=[5])),
        (
            MyDataclass,
            {"a": 1, "b": "hello", "optional_custom": custom},
            MyDataclass(a=1, b="hello", optional_custom=custom),
        ),
        (MyDataclass, {"a": "not_an_int", "b": "hello"}, ValueError),
    ],
)
def test_parse(field_type, data, expected, path: JqPath, subparser: Subparse):
    if isclass(expected) and issubclass(expected, BaseException):
        with pytest.raises(expected):
            DataclassParser().parse(path=path, field_type=field_type, data=data, subparse=subparser)
    else:
        assert DataclassParser().parse(path=path, field_type=field_type, data=data, subparse=subparser) == expected
