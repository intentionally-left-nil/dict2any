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
    assert parser.can_parse(stage=stage, path=path, field_type=field_type) == expected
    assert parser.can_parse(stage=Stage.Override, path=path, field_type=field_type) == False


def test_can_parse_subdict(path: JqPath):
    class MyStr(str):
        pass

    assert StringParser().can_parse(stage=Stage.Exact, path=path, field_type=MyStr) is False
    assert StringParser().can_parse(stage=Stage.Fallback, path=path, field_type=MyStr) is True


def test_parse(path: JqPath, subparser: Mock):
    assert BoolParser().parse(stage=Stage.Exact, path=path, field_type=bool, data=True, subparse=subparser) is True
    assert IntParser().parse(stage=Stage.Exact, path=path, field_type=int, data=42, subparse=subparser) == 42
    assert FloatParser().parse(stage=Stage.Exact, path=path, field_type=float, data=42.0, subparse=subparser) == 42.0
    assert StringParser().parse(stage=Stage.Exact, path=path, field_type=str, data="42", subparse=subparser) == "42"
    assert StringParser().parse(
        stage=Stage.Exact, path=path, field_type=MyStr, data=MyStr("42"), subparse=subparser
    ) == MyStr("42")
    assert StringParser().parse(
        stage=Stage.Fallback, path=path, field_type=MyStr, data=MyStr("42"), subparse=subparser
    ) == MyStr("42")


def test_parse_failure(path: JqPath, subparser: Mock):
    with pytest.raises(ValueError):
        StringParser().parse(stage=Stage.Exact, path=path, field_type=str, data=42, subparse=subparser)

    with pytest.raises(ValueError):
        StringParser().parse(stage=Stage.Fallback, path=path, field_type=str, data=42, subparse=subparser)

    with pytest.raises(ValueError):
        StringParser().parse(stage=Stage.Exact, path=path, field_type=MyStr, data=42, subparse=subparser)

    with pytest.raises(ValueError):
        StringParser().parse(stage=Stage.Exact, path=path, field_type=str, data=None, subparse=subparser)
