from typing import Protocol


class Infrastructure(Protocol):
    def update(self) -> bool:
        ...


class Encryption(Protocol):
    def encrypt(self, string: str) -> bytes:
        ...

    def decrypt(self, token: bytes) -> str:
        ...
