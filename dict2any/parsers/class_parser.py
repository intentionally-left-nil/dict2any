import inspect
from collections.abc import Mapping
from types import FunctionType
from typing import Any, Optional, Union, get_args, get_origin

from dict2any.jq_path import JqPath
from dict2any.parsers.parser import Parser, Stage, Subparse


class ClassParser(Parser):
    def can_parse(self, stage: Stage, path: JqPath, field_type: type):
        match stage:
            case Stage.LastChance:
                return (
                    inspect.isclass(field_type)
                    and not issubclass(field_type, FunctionType)
                    and not any(
                        [
                            param.kind is inspect.Parameter.POSITIONAL_ONLY and i != 0
                            for i, param in enumerate(inspect.signature(field_type.__init__).parameters.values())
                        ]
                    )
                )
            case _:
                return False

    def parse(self, *, path: JqPath, field_type: type, data: Any, subparse: Subparse) -> Any:
        if not isinstance(data, Mapping):
            raise ValueError(f"Invalid type: {type(data)}")
        parameters = inspect.signature(field_type.__init__).parameters.items()  # type: ignore[misc]
        kwargs = (
            {k: v for k, v in data.items()}
            if any(p.kind is inspect.Parameter.VAR_KEYWORD for _, p in parameters)
            else dict()
        )
        for i, (name, parameter) in enumerate(parameters):
            if (i == 0 and name == "self") or parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            if name in data:
                kwargs[name] = subparse(path=path.child(name=name), field_type=parameter.annotation, data=data[name])
            elif parameter.default is inspect.Parameter.empty:
                raise ValueError(f"Missing required parameter: {name}")
        return field_type(**kwargs)
