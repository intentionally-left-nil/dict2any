from pathlib import Path

import pytest

from dict2any.jq_path import JqPath
from dict2any.parsers import Stage, Subparse
from dict2any.parsers.path import PathParser


def test_can_parse(path: JqPath):
    assert PathParser().can_parse(stage=Stage.Exact, path=path, field_type=Path) == True
    assert PathParser().can_parse(stage=Stage.Exact, path=path, field_type=str) == False
    assert PathParser().can_parse(stage=Stage.Fallback, path=path, field_type=Path) == False


def test_parse(path: JqPath, subparser: Subparse):
    assert PathParser().parse(path=path, field_type=Path, data="hello", subparse=subparser) == Path("hello")
    assert PathParser().parse(path=path, field_type=Path, data=Path("hello"), subparse=subparser) == Path("hello")
    with pytest.raises(ValueError):
        PathParser().parse(path=path, field_type=Path, data=None, subparse=subparser)
