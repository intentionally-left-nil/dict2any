from inspect import isclass
from typing import Any
from unittest.mock import Mock

import pytest

from dict2any.jq_path import JqPath


@pytest.fixture
def path():
    return JqPath.parse('.')


@pytest.fixture
def subparser() -> Mock:
    def _subparse(path: JqPath, field_type: type, data: Any) -> Any:
        if isclass(field_type) and field_type is not Any and not isinstance(data, field_type):
            raise ValueError(f"Invalid type: {type(data)}")
        return data

    return Mock(side_effect=_subparse)
