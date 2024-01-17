from collections.abc import Mapping, Sequence
from inspect import isclass
from typing import Any, NamedTuple, get_args, get_origin, get_type_hints

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


class NamedTupleParser(Parser):
    def can_parse(self, *, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case stage.Exact:
                return isclass(field_type) and issubclass(field_type, tuple) and hasattr(field_type, '_fields')
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        kwargs = {}
        if not isinstance(data, Sequence) and not isinstance(data, Mapping):
            raise ValueError(f"Invalid type: {type(data)}")

        sub_types: dict[str, Any] = {}
        field_names: tuple = getattr(field_type, '_fields', tuple())
        if NamedTuple in getattr(field_type, '__orig_bases__', tuple()):
            type_hints = get_type_hints(field_type)
            sub_types = {}
            for field_name in field_names:
                sub_types[field_name] = type_hints.get(field_name, Any)
        else:
            sub_types = {field_name: Any for field_name in field_names}

        if len(sub_types) != len(data):
            raise ValueError(f"Invalid tuple length")
        if isinstance(data, Sequence):
            for i, (field_name, sub_type) in enumerate(sub_types.items()):
                kwargs[field_name] = subparse(path=path.child(index=i), field_type=sub_type, data=data[i])
            return field_type(**kwargs)
        else:
            for i, (field_name, sub_type) in enumerate(sub_types.items()):
                if field_name not in data:
                    raise ValueError(f"Missing field {field_name}")

                kwargs[field_name] = subparse(
                    path=path.child(name=field_name), field_type=sub_type, data=data[field_name]
                )
            return field_type(**kwargs)
