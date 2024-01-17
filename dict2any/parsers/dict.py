from collections import OrderedDict
from collections.abc import Mapping
from inspect import isclass
from typing import Any, TypedDict, get_args, get_origin, get_type_hints

from dict2any.jq_path import JqPath
from dict2any.parsers import Parser, Stage, Subparse
from dict2any.parsers.parser import Stage


class DictParser(Parser):
    def can_parse(self, *, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.Exact:
                return field_type in (dict, OrderedDict) or (get_origin(field_type) in (dict, OrderedDict))
            case Stage.Fallback:
                if isclass(field_type) and issubclass(field_type, Mapping):
                    return True
                origin = get_origin(field_type)
                return isclass(origin) and issubclass(origin, Mapping)
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        if not isinstance(data, Mapping):
            raise ValueError(f"Invalid type: {type(data)}")

        args = get_args(field_type)
        if len(args) != 2:
            args = (Any, Any)

        key_type, val_type = args

        return field_type(
            {
                subparse(path=path.child(name=str(key)), field_type=key_type, data=key): subparse(
                    path=path.child(name=str(key)), field_type=val_type, data=val
                )
                for key, val in data.items()
            }
        )


class TypedDictParser(Parser):
    def can_parse(self, *, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.Exact:
                return isclass(field_type) and TypedDict in getattr(field_type, '__orig_bases__', tuple())
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        if not isinstance(data, Mapping):
            raise ValueError(f"Invalid type: {type(data)}")
        required_keys: frozenset = getattr(field_type, '__required_keys__', frozenset())
        if any(key not in data for key in required_keys):
            raise ValueError(f"Missing required keys: {required_keys - frozenset(data.keys())}")

        kwargs = {}
        allow_unknown_keys: bool = not getattr(field_type, '__total__', True)
        optional_keys: frozenset = getattr(field_type, '__optional_keys__', frozenset())
        type_hints = get_type_hints(field_type)
        for key, value in data.items():
            if not allow_unknown_keys and (key not in required_keys) and (key not in optional_keys):
                raise ValueError(f"Unknown key: {key}")
            parsed_value = subparse(path=path.child(name=str(key)), field_type=type_hints.get(key, Any), data=value)
            kwargs[key] = parsed_value
        return field_type(**kwargs)
