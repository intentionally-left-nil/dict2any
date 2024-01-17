from collections import OrderedDict
from collections.abc import Mapping
from inspect import isclass
from typing import Any, get_args, get_origin

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
