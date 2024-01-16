from unittest.mock import Mock

import pytest

from dict2any.jq_path import JqPath


@pytest.fixture
def path():
    return JqPath.parse('.')


@pytest.fixture
def subparser() -> Mock:
    return Mock(side_effect=lambda *args, **kwargs: kwargs['data'])
