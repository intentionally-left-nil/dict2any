from collections.abc import MutableSequence, Sequence
from inspect import isclass
from typing import Any, get_args, get_origin

from dict2any.jq_path import JqPath
from dict2any.parsers.parser import Parser, Stage, Subparse


class ListParser(Parser):
    def can_parse(self, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.Exact:
                return field_type is list or get_origin(field_type) is list
            case Stage.Fallback:
                if isclass(field_type) and issubclass(field_type, MutableSequence):
                    return True
                origin = get_origin(field_type)
                # Make sure to only try parsing mutable sequences, not tuples
                return isclass(origin) and issubclass(origin, list)
            case _:
                return False

    def parse(self, stage: Stage, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        match stage:
            case Stage.Exact:
                if not type(data) in (list, tuple):
                    raise ValueError(f"Invalid type: {type(data)}")
            case Stage.Fallback:
                if not isinstance(data, Sequence):
                    raise ValueError(f"Invalid type: {type(data)}")

        args = get_args(field_type)
        sub_type = Any if len(args) == 0 else args[0]
        sub_items = [
            subparse(path=path.child(index=index), field_type=sub_type, data=item) for index, item in enumerate(data)
        ]
        return field_type(sub_items)
