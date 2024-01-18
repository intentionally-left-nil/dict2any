from inspect import isclass
from typing import Any

from dict2any.jq_path import JqPath
from dict2any.parsers.parser import Parser, Stage, Subparse


class BaseParser(Parser):
    field_type: type

    def __init__(self, field_type: type):
        self.field_type = field_type

    def can_parse(self, *, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.Exact:
                return field_type is self.field_type
            case Stage.Fallback:
                return isclass(field_type) and issubclass(field_type, self.field_type)
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        if not isinstance(data, self.field_type):
            raise ValueError(f"Invalid type: {type(data)}")
        return data


def create_base_parser(field_type: type) -> type[Parser]:
    class P(BaseParser):
        def __init__(self):
            super().__init__(field_type)

        def __repr__(self):
            return f"{field_type.__name__.capitalize()}Parser"

    return P


BoolParser = create_base_parser(bool)
IntParser = create_base_parser(int)
FloatParser = create_base_parser(float)
StringParser = create_base_parser(str)
NoneParser = create_base_parser(type(None))
