from abc import ABC, abstractmethod


class RepositoryInterface(ABC):
    @abstractmethod
    async def get(*args, **kwargs):
        raise NotImplementedError
    
    async def get_list(*args, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    async def post(*args, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    async def patch(*args, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    async def delete(*args, **kwargs):
        raise NotImplementedError
