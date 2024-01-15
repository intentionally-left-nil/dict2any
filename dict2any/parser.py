from typing import Protocol

class Parser(Protocol):
    def parse(self) -> None:
        ...
