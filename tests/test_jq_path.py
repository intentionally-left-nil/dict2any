from dict2any.jq_path import JqPath, JqPathPart
import pytest


def test_parse_empty():
    assert JqPath.parse('') == JqPath(parts=(JqPathPart(name=''),))


def test_parse_dot():
    assert JqPath.parse('.') == JqPath(parts=(JqPathPart(name=''),))


@pytest.mark.parametrize(
    'path',
    [
        "..",
        "[42.2]",
        '"no_end_quote',
        'no_start_quote"',
        '[no_end_bracket',
        'no_start_bracket]',
        '["42"]',
        '["not_a_number"]',
        'a.b.[oops.d',
    ],
)
def test_invalid_paths(path: str):
    with pytest.raises(ValueError):
        JqPath.parse(path)


@pytest.mark.parametrize(
    'path',
    ['.', '.a', '.a.b', '.a.b.c', '.[1]', '.[1].[0]', '.[1].a' '.[0].a.[1]', '.[0]'],
)
def test_path(path: str):
    jq_path = JqPath.parse(path)
    assert jq_path.path() == path


def test_normalized_array_path():
    assert JqPath.parse('[0]').path() == '.[0]'
    assert JqPath.parse('[0][1]').path() == '.[0].[1]'
    assert JqPath.parse('[0].[1][2]').path() == '.[0].[1].[2]'
    assert JqPath.parse('.a[0]').path() == '.a.[0]'


@pytest.mark.parametrize(
    ['path', 'expected'],
    [
        ('.', None),
        ('', None),
        ('.a', JqPath.parse('.')),
        ('.a.b', JqPath.parse('.a')),
        ('.a.b.c', JqPath.parse('.a.b')),
        ('.a.b.c.[1]', JqPath.parse('.a.b.c')),
        ('.a.b.c[1]', JqPath.parse('.a.b.c')),
        ('[1]', JqPath.parse('.')),
        ('.[2]', JqPath.parse('.')),
        ('.[0][1]', JqPath.parse('.[0]')),
    ],
)
def test_parent(path, expected):
    assert JqPath.parse(path).parent() == expected


def test_child_from_root():
    assert JqPath.parse('.').child(name='a') == JqPath.parse('.a')


def test_child_index_from_root():
    assert JqPath.parse('.').child(index=1) == JqPath.parse('.[1]')


def test_child():
    assert JqPath.parse('.a').child(name='b') == JqPath.parse('.a.b')


def test_child_index():
    assert JqPath.parse('.a').child(index=1) == JqPath.parse('.a[1]')


def test_part_validity():
    with pytest.raises(ValueError, match="Either name or index must be set"):
        JqPathPart()
    with pytest.raises(ValueError, match="Either name or index must be set"):
        JqPathPart(name="a", index=1)


def test_verify_direct_initialization():
    with pytest.raises(ValueError, match="Path must have at least one part"):
        JqPath(parts=())
