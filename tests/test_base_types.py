from dataclasses import dataclass, fields
from unittest.mock import Mock

import pytest

from dict2any.jq_path import JqPath
from dict2any.parsers import (
    BoolParser,
    FloatParser,
    IntParser,
    Parser,
    Stage,
    StringParser,
)


@dataclass
class MyData:
    my_int_list: list[int]


int_list_type = fields(MyData)[0].type


class MyStr(str):
    pass


@pytest.mark.parametrize(
    ['parser', 'stage', 'field_type', 'expected'],
    [
        (BoolParser(), Stage.Exact, bool, True),
        (IntParser(), Stage.Exact, int, True),
        (FloatParser(), Stage.Exact, float, True),
        (StringParser(), Stage.Exact, str, True),
        (StringParser(), Stage.Exact, int_list_type, False),
        (BoolParser(), Stage.Exact, int, False),
        (IntParser(), Stage.Exact, float, False),
        (FloatParser(), Stage.Exact, str, False),
        (StringParser(), Stage.Exact, list, False),
        (StringParser(), Stage.Fallback, MyStr, True),
        (StringParser(), Stage.Fallback, int_list_type, False),
        (StringParser(), Stage.Fallback, None, False),
    ],
)
def test_can_parse(parser: Parser, stage: Stage, field_type: type, expected: bool, path: JqPath):
    assert parser.can_parse(stage, path, field_type) == expected
    assert parser.can_parse(Stage.Override, path, field_type) == False


def test_can_parse_subdict(path: JqPath):
    class MyStr(str):
        pass

    assert StringParser().can_parse(Stage.Exact, path, MyStr) is False
    assert StringParser().can_parse(Stage.Fallback, path, MyStr) is True


def test_parse(path: JqPath, subparser: Mock):
    assert BoolParser().parse(Stage.Exact, path, bool, True, subparser) is True
    assert IntParser().parse(Stage.Exact, path, int, 42, subparser) == 42
    assert FloatParser().parse(Stage.Exact, path, float, 42.0, subparser) == 42.0
    assert StringParser().parse(Stage.Exact, path, str, "42", subparser) == "42"
    assert StringParser().parse(Stage.Fallback, path, MyStr, MyStr("42"), subparser) == MyStr("42")


def test_parse_failure(path: JqPath, subparser: Mock):
    with pytest.raises(ValueError):
        StringParser().parse(Stage.Exact, path, str, 42, subparser)

    with pytest.raises(ValueError):
        StringParser().parse(Stage.Fallback, path, str, 42, subparser)

    with pytest.raises(ValueError):
        StringParser().parse(Stage.Exact, path, MyStr, 42, subparser)

    with pytest.raises(ValueError):
        StringParser().parse(Stage.Exact, path, str, None, subparser)
