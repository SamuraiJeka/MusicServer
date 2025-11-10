from abc import ABC, abstractmethod

from repositories.repository_interface import RepositoryInterface


class UoWInterface(ABC):
    repository: RepositoryInterface

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError
    
    @abstractmethod
    def __exit__(self):
        raise NotImplementedError

    @abstractmethod
    def commit(self):
        raise NotImplementedError
