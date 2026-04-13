from abc import ABC, abstractmethod

from domain.entities.track import Track


class TrackRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, track: Track) -> Track:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, track: Track) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, track_id: int) -> Track | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_owner_order_by_view_desc(
        self, owner_id: int, limit: int | None = None
    ) -> list[Track]:
        raise NotImplementedError

    @abstractmethod
    async def list_order_by_view_desc(self, limit: int, offset: int = 0) -> list[Track]:
        raise NotImplementedError

    @abstractmethod
    async def search_by_title(self, query: str, limit: int, offset: int = 0) -> list[Track]:
        raise NotImplementedError
