from typing import Any, get_origin

from dict2any.jq_path import JqPath
from dict2any.parsers.parser import Parser, Stage, Subparse


class AnyParser(Parser):
    def can_parse(self, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.Exact:
                return field_type is Any or get_origin(field_type) is Any
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        return data
