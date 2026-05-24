from abc import ABC, abstractmethod

from domain.entities.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError
    
    @abstractmethod
    async def delete_by_id(self, user_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def search(self, query: str, limit: int, offset: int = 0) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    async def search_by_username(self, query: str, limit: int, offset: int = 0, exclude_ids: list[int] | None = None,
    ) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_ids(self, user_ids: list[int]) -> list[User]:
        raise NotImplementedError
