from typing import Protocol


class Infrastructure(Protocol):
    def update(self) -> bool:
        ...
