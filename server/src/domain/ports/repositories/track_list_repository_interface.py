from abc import ABC, abstractmethod

from domain.entities.track_list import TrackList
from domain.entities.track import Track


class TrackListRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, track_list: TrackList):
        raise NotImplementedError

    @abstractmethod
    async def insert(self, track_list: TrackList, track: Track) -> TrackList:
        raise NotImplementedError
    
    @abstractmethod
    async def remove(self, track_list: TrackList, track: Track) -> TrackList:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, track_list: TrackList) -> bool:
        raise NotImplementedError
