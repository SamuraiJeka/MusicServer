from abc import ABC, abstractmethod


class UoWInterface(ABC):
    @abstractmethod
    async def __enter__(self):
        raise NotImplementedError
    
    @abstractmethod
    async def __exit__(self):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError
    
    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
