import dataclasses
from collections.abc import Mapping
from typing import Any, Mapping

from dict2any.jq_path import JqPath
from dict2any.parsers import Parser, Stage, Subparse
from dict2any.parsers.parser import Stage


class DataclassParser(Parser):
    def can_parse(self, *, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.Exact:
                return dataclasses.is_dataclass(field_type)
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        if not isinstance(data, Mapping):
            raise ValueError(f"Invalid type: {type(data)}")

        fields = [field for field in dataclasses.fields(field_type) if field.init]
        field_names = frozenset(field.name for field in fields)
        if any(key not in field_names for key in data.keys()):
            raise ValueError(f"Unknown keys: {frozenset(data.keys()) - field_names}")

        kwargs = {}
        for field in fields:
            if field.name in data:
                kwargs[field.name] = subparse(
                    path=path.child(name=field.name), field_type=field.type, data=data[field.name]
                )
            elif field.default is dataclasses.MISSING and field.default_factory is dataclasses.MISSING:
                raise ValueError(f"Missing required field: {field.name}")
        return field_type(**kwargs)
