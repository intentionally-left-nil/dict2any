import pytest

from dict2any.jq_path import JqPath


@pytest.fixture
def path():
    return JqPath.parse('.')
