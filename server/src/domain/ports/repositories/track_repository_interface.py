from abc import ABC, abstractmethod

from domain.entities.track_list import TrackList
from domain.entities.track import Track


class TrackRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, track: Track) -> Track:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, track: Track) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, track_id: int) -> Track:
        raise NotImplementedError
