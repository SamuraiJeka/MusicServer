from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    async def save(self, prefix: str, filename: str | None, content: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, prefix: str, filename: str,) -> None:
        raise NotImplementedError
