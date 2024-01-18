from pathlib import Path
from typing import Any

from dict2any.jq_path import JqPath
from dict2any.parsers.parser import Parser, Stage, Subparse


class PathParser(Parser):
    def can_parse(self, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.Exact:
                return field_type is Path
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        if not isinstance(data, str) and not isinstance(data, Path):
            raise ValueError(f"Invalid type: {type(data)}")
        return Path(data)
