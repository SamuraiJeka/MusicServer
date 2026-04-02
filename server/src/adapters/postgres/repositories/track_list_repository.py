from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from domain.ports.repositories.track_list_repository_interface import TrackListRepositoryInterface
from domain.entities.track_list import TrackList
from domain.entities.track import Track


class TrackListRepository(TrackListRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, track_list: TrackList) -> TrackList:
        self._session.add(track_list)
        await self._session.flush()
        return track_list

    async def get_by_id(self, track_list_id: int) -> TrackList | None:
        stmt = select(TrackList).options(selectinload(TrackList.track_list)).where(TrackList.id == track_list_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_tracks(self, track_list: TrackList, tracks: Sequence[Track]) -> TrackList:
        self._session.add(track_list)
        await self._session.flush()
        return track_list

    async def remove_track(self, track_list: TrackList) -> TrackList:
        self._session.add(track_list)
        await self._session.flush()
        return track_list

    async def delete_by_id(self, track_list_id: int) -> bool:
        stmt = delete(TrackList).where(TrackList.id == track_list_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return bool(result)
