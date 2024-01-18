from typing import Any, Optional, Union, get_args, get_origin

from dict2any.jq_path import JqPath
from dict2any.parsers.parser import Parser, Stage, Subparse


class UnionParser(Parser):
    def can_parse(self, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.Exact:
                return field_type in (Union, Optional) or get_origin(field_type) is Union
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        for arg in get_args(field_type):
            try:
                return subparse(path=path, field_type=arg, data=data)
            except ValueError:
                pass
        raise ValueError(f"Invalid type: {type(data)}")
