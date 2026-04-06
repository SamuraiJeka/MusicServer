from abc import ABC, abstractmethod
from typing import Sequence

from domain.entities.track_list import TrackList, TrackListType
from domain.entities.track import Track


class TrackListRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, track_list: TrackList) -> TrackList:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, track_list_id: int) -> TrackList | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_owner_and_type(
        self, owner_id: int, list_type: TrackListType
    ) -> list[TrackList]:
        raise NotImplementedError

    @abstractmethod
    async def add_tracks(self, track_list: TrackList, tracks: Sequence[Track]) -> TrackList:
        raise NotImplementedError

    @abstractmethod
    async def remove_track(self, track_list: TrackList) -> TrackList:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, track_list_id: int) -> bool:
        raise NotImplementedError
