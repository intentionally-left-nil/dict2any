from inspect import isclass
from typing import Any, Optional, Union

import pytest

from dict2any.jq_path import JqPath
from dict2any.parsers import Stage, Subparse
from dict2any.parsers.union import UnionParser


@pytest.mark.parametrize(
    ['stage', 'field_type', 'expected'],
    [
        (Stage.Exact, Union, True),
        (Stage.Exact, Optional, True),
        (Stage.Exact, Union[Any, None], True),
        (Stage.Exact, Union[str, list], True),
        (Stage.Exact, dict[str, Union[int, list]], False),
        (Stage.Exact, list[str], False),
        (Stage.Exact, Optional[str], True),
        (Stage.Fallback, Union, False),
    ],
)
def test_can_parse(stage: Stage, field_type: Any, expected: bool, path: JqPath):
    assert UnionParser().can_parse(stage=stage, path=path, field_type=field_type) == expected


@pytest.mark.parametrize(
    ['field_type', "data", 'expected'],
    [
        (int | str, 1, 1),
        (int | str, "hello", "hello"),
        (Optional[int], None, None),
        (Optional[int], 5, 5),
        (int | str, None, ValueError),
    ],
)
def test_parse(field_type, data, expected, path: JqPath, subparser: Subparse):
    if isclass(expected) and issubclass(expected, BaseException):
        with pytest.raises(expected):
            UnionParser().parse(path=path, field_type=field_type, data=data, subparse=subparser)
    else:
        assert UnionParser().parse(path=path, field_type=field_type, data=data, subparse=subparser) == expected
