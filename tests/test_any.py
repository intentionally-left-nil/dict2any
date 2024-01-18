from typing import Any
from unittest.mock import Mock

import pytest

from dict2any.jq_path import JqPath
from dict2any.parsers import AnyParser, Stage


@pytest.mark.parametrize(
    ['stage', 'field_type', 'expected'],
    [(Stage.Exact, Any, True), (Stage.Exact, int, False), (Stage.Fallback, Any, False)],
)
def test_can_parse(stage: Stage, field_type: Any, expected: bool, path: JqPath):
    assert AnyParser().can_parse(stage=stage, path=path, field_type=field_type) == expected


def test_parse(path: JqPath, subparser: Mock):
    assert AnyParser().parse(path=path, field_type=int, data=5, subparse=subparser) == 5
    assert subparser.call_count == 0
