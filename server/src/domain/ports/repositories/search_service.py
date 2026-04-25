from abc import ABC, abstractmethod
from typing import Sequence

from domain.entities.track import Track
from domain.entities.user import User


class SearchServiceInterface(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int, offset: int = 0) -> list[Track]:
        raise NotImplementedError
    
    @abstractmethod
    async def search_users(self, query: str, limit: int, offset: int = 0) -> list[User]:
        raise NotImplementedError
