from unittest.mock import Mock

from dict2any.jq_path import JqPath
from dict2any.parsers import (
    BaseDictParser,
    BaseListParser,
    BoolParser,
    FloatParser,
    IntParser,
    Stage,
    StringParser,
)


def test_can_parse(path: JqPath):
    class Example:
        pass

    for stage in [Stage.Exact, Stage.Fallback, Stage.Override]:
        assert BoolParser().can_parse(stage, path, bool) == (stage != Stage.Override)
        assert IntParser().can_parse(stage, path, int) == (stage != Stage.Override)
        assert FloatParser().can_parse(stage, path, float) == (stage != Stage.Override)
        assert StringParser().can_parse(stage, path, str) == (stage != Stage.Override)
        assert BaseListParser().can_parse(stage, path, list) == (stage != Stage.Override)
        assert BaseDictParser().can_parse(stage, path, dict) == (stage != Stage.Override)

        assert BoolParser().can_parse(stage, path, Example) is False
        assert IntParser().can_parse(stage, path, Example) is False
        assert FloatParser().can_parse(stage, path, Example) is False
        assert StringParser().can_parse(stage, path, Example) is False
        assert BaseListParser().can_parse(stage, path, Example) is False
        assert BaseDictParser().can_parse(stage, path, Example) is False


def test_parse(path: JqPath):
    assert BoolParser().parse(Stage.Exact, path, bool, True, Mock()) is True
    assert IntParser().parse(Stage.Exact, path, int, 42, Mock()) == 42
    assert FloatParser().parse(Stage.Exact, path, float, 42.0, Mock()) == 42.0
    assert StringParser().parse(Stage.Exact, path, str, "42", Mock()) == "42"
    assert BaseListParser().parse(Stage.Exact, path, list, ['hello', 'world'], Mock()) == ['hello', 'world']
    assert BaseDictParser().parse(Stage.Exact, path, dict, {"hello": "world"}, Mock()) == {"hello": "world"}


def test_dict_subclass(path: JqPath):
    class MyDict(dict):
        pass

    assert BaseDictParser().can_parse(Stage.Exact, path, MyDict) is False
    assert BaseDictParser().can_parse(Stage.Fallback, path, MyDict) is True
    actual = BaseDictParser().parse(Stage.Fallback, path, MyDict, {"hello": "world"}, Mock())
    assert isinstance(actual, MyDict)
    assert actual == {"hello": "world"}
    actual = BaseDictParser().parse(Stage.Fallback, path, dict, {"hello": "world"}, Mock())
    assert isinstance(actual, MyDict) is False


BoolParser().can_parse(Stage.Exact, JqPath.parse('.'), bool)
