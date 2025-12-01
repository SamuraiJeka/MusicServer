from abc import ABC, abstractmethod

from domain.ports.repositories.user_repository_interface import UserRepositoryInterface
from domain.ports.repositories.track_list_repository_interface import TrackListRepositoryInterface


class UoWInterface(ABC):
    user_repo: UserRepositoryInterface
    track_list_repo: TrackListRepositoryInterface

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError
    
    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
