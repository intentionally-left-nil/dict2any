from collections.abc import Sequence
from typing import Any, get_args, get_origin

from dict2any.jq_path import JqPath
from dict2any.parsers.parser import Parser, Stage, Subparse


class TupleParser(Parser):
    def can_parse(self, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.Exact:
                return field_type is tuple or get_origin(field_type) is tuple
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        if not isinstance(data, Sequence):
            raise ValueError(f"Invalid type: {type(data)}")
        args = get_args(field_type)
        if len(args) == 2 and args[1] is Ellipsis:
            args = (args[0],) * len(data)
        elif len(args) == 0:
            args = (Any,) * len(data)

        if len(args) != len(data):
            raise ValueError(f"Invalid tuple length")
        sub_items: list[Any] = []
        for i in range(len(data)):
            sub_items.append(subparse(path=path.child(index=i), field_type=args[i], data=data[i]))
        return field_type(sub_items)
