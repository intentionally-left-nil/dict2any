import re
from dataclasses import dataclass
from typing import Any

ARRAY_REGEX = re.compile(r'\.?\[(\d)+\]')
FIND_WITHIN_QUOTES = r'(?:[^".\n\[\]]*(?:\\")*?)*?'
DICT_REGEX = re.compile(r'\.("{}"|{})(?=\.|$|\[)'.format(FIND_WITHIN_QUOTES, FIND_WITHIN_QUOTES))


@dataclass(frozen=True)
class JqPathPart:
    name: str | None = None
    index: int | None = None

    def __str__(self):
        return self.name if self.index is None else f'[{self.index}]'

    def __post_init__(self):
        if (self.name is None) == (self.index is None):
            raise ValueError("Either name or index must be set")


@dataclass(frozen=True)
class JqPath:
    parts: tuple[JqPathPart, ...]

    def __post_init__(self):
        if len(self.parts) == 0:
            raise ValueError("Path must have at least one part")

    @classmethod
    def parse(cls, path: str) -> 'JqPath':
        if path == "" or path == ".":
            return cls(parts=(JqPathPart(name=""),))

        jq_parts = [JqPathPart(name="")]
        while len(path) > 0:
            match = ARRAY_REGEX.match(path)
            if match is not None:
                jq_parts.append(JqPathPart(index=int(match.group(1))))
                path = path[match.end() :]
                continue

            match = DICT_REGEX.match(path)
            if match is not None:
                name = match.group(1)
                if len(name) == 0:
                    raise ValueError(f"Invalid path: {path}")
                jq_parts.append(JqPathPart(name=match.group(1)))
                path = path[match.end() :]
                continue

            raise ValueError(f"Invalid path: {path}")
        return cls(parts=tuple(jq_parts))

    def path(self):
        if len(self.parts) == 1:
            return '.'
        return ''.join([f'.{part}' for part in self.parts[1:]])

    def parent(self) -> 'JqPath | None':
        return JqPath(parts=self.parts[:-1]) if len(self.parts) > 1 else None

    def child(self, *, name: str | None = None, index: int | None = None) -> 'JqPath':
        return JqPath(parts=self.parts + (JqPathPart(name=name, index=index),))
