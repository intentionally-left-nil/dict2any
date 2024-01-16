from collections.abc import MutableSequence
from dataclasses import dataclass, fields
from typing import Any, Generic, TypeVar
from unittest.mock import Mock

import pytest

from dict2any.jq_path import JqPath
from dict2any.parsers import Stage
from dict2any.parsers.list import ListParser


class SubList(list):
    pass


class MyCustomSequence(MutableSequence):
    def __init__(self, items):
        self.items = items

    def __eq__(self, other):
        return isinstance(other, MyCustomSequence) and self.items == other.items

    def __getitem__(self, index):
        return self.items.__getitem__(index)

    def __setitem__(self, index, val):
        return self.items.__setitem__(index)

    def __delitem__(self, index):
        return self.items.__delitem__(index)

    def __len__(self):
        return self.items.__len__()

    def insert(self, index, val):
        return self.items.insert(index, val)


T = TypeVar('T')


class MyGenericCustomSequence(Generic[T], MyCustomSequence):
    pass


@dataclass
class MyData:
    my_list: list
    my_int_list: list[int]
    my_str_list: list[str]
    my_list_list: list[list[str]]
    my_tuple: tuple
    my_int_tuple: tuple[int]
    my_list_tuple: tuple[list]
    my_custom_sequence: MyCustomSequence
    my_generic_sequence: MyGenericCustomSequence[int]


my_data_types = {field.name: field.type for field in fields(MyData)}


@pytest.mark.parametrize(
    ['field_type', 'expected'],
    [
        (list, True),
        (tuple, False),
        (SubList, False),
        (MyCustomSequence, False),
        (my_data_types['my_int_list'], True),
        (my_data_types['my_str_list'], True),
        (my_data_types['my_list_list'], True),
        (my_data_types['my_tuple'], False),
        (my_data_types['my_int_tuple'], False),
        (my_data_types['my_list_tuple'], False),
    ],
)
def test_can_parse_exact(field_type: type, expected: bool, path: JqPath):
    assert ListParser().can_parse(stage=Stage.Exact, path=path, field_type=field_type) == expected


@pytest.mark.parametrize(
    ['field_type', 'expected'],
    [
        (MyCustomSequence, True),
        (SubList, True),
        (list, True),
        (tuple, False),
        (my_data_types['my_int_list'], True),
        (my_data_types['my_str_list'], True),
        (my_data_types['my_list_list'], True),
        (my_data_types['my_custom_sequence'], True),
        (my_data_types['my_generic_sequence'], True),
        (my_data_types['my_tuple'], False),
        (my_data_types['my_int_tuple'], False),
        (my_data_types['my_list_tuple'], False),
    ],
)
def test_can_parse_fallback(field_type: type, expected: bool, path: JqPath):
    assert ListParser().can_parse(stage=Stage.Fallback, path=path, field_type=field_type) == expected


def test_can_parse_override(path: JqPath):
    assert ListParser().can_parse(stage=Stage.Override, path=path, field_type=list) == False


@pytest.mark.parametrize(
    ['field_type', 'data', 'expected'],
    [
        (list, [], []),
        (list, [1], [1]),
        (list, [1, 2], [1, 2]),
        (list, MyCustomSequence([1, 2]), [1, 2]),
        (my_data_types['my_int_list'], [1, 2], [1, 2]),
        (my_data_types['my_str_list'], ["a"], ["a"]),
        (list, (1, 2), [1, 2]),
        (list, [[1], [2, 3]], [[1], [2, 3]]),
        (SubList, [], SubList([])),
        (SubList, [1], SubList([1])),
        (SubList, (1, 2), SubList([1, 2])),
        (MyCustomSequence, [1, 2], MyCustomSequence([1, 2])),
        (my_data_types['my_custom_sequence'], [1, 2], MyCustomSequence([1, 2])),
        (my_data_types['my_generic_sequence'], [1, 2], MyGenericCustomSequence[int]([1, 2])),
    ],
)
def test_parse(field_type: type, data: Any, expected: Any, path: JqPath, subparser: Mock):
    assert ListParser().parse(path=path, field_type=field_type, data=data, subparse=subparser) == expected
    assert subparser.call_count == len(data)
    for i, _ in enumerate(data):
        assert subparser.call_args_list[i].kwargs["path"].path() == f"{path.path()}[{i}]"
        expected_field_type = Any if field_type in (list, SubList, MyCustomSequence) else type(data[0])
        assert subparser.call_args_list[i].kwargs["field_type"] == expected_field_type
        assert subparser.call_args_list[i].kwargs["data"] == data[i]


def test_parse_fails_for_non_lists(path: JqPath, subparser: Mock):
    with pytest.raises(ValueError):
        ListParser().parse(path=path, field_type=list, data={"hello": "world"}, subparse=subparser)

    with pytest.raises(ValueError):
        ListParser().parse(path=path, field_type=list, data={"hello": "world"}, subparse=subparser)
