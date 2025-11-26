from abc import ABC, abstractmethod

from domain.entities.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def add(self, user: User) -> User:
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
