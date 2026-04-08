from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from domain.ports.repositories.track_list_repository_interface import TrackListRepositoryInterface
from domain.entities.track_list import TrackList, TrackListType
from domain.entities.track import Track
from adapters.postgres.orm import tracks_track_lists


class TrackListRepository(TrackListRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, track_list: TrackList) -> TrackList:
        self._session.add(track_list)
        await self._session.flush()
        return track_list

    async def get_by_id(self, track_list_id: int) -> TrackList | None:
        stmt = (
            select(TrackList)
            .options(selectinload(TrackList.track_list))  # type: ignore[arg-type]
            .where(TrackList.id == track_list_id)  # type: ignore[arg-type]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_owner_and_type(
        self, owner_id: int, list_type: TrackListType
    ) -> list[TrackList]:
        stmt = (
            select(TrackList)
            .where(
                TrackList.owner_id == owner_id,  # type: ignore[arg-type]
                TrackList._type == list_type,  # type: ignore[arg-type]
            )
            .order_by(TrackList.id.desc())  # type: ignore[union-attr]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_albums(
        self,
        limit: int,
        offset: int,
        owner_id: int | None = None,
    ) -> list[TrackList]:
        stmt = select(TrackList).where(TrackList._type == TrackListType.ALBUM)  # type: ignore[arg-type]
        if owner_id is not None:
            stmt = stmt.where(TrackList.owner_id == owner_id)  # type: ignore[arg-type]

        stmt = (
            stmt.order_by(TrackList.id.desc())  # type: ignore[union-attr]
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_tracks(self, track_list: TrackList, tracks: Sequence[Track]) -> TrackList:
        self._session.add(track_list)
        await self._session.flush()
        return track_list

    async def remove_track(self, track_list: TrackList) -> TrackList:
        self._session.add(track_list)
        await self._session.flush()
        return track_list

    async def delete_by_id(self, track_list_id: int) -> bool:
        stmt = delete(TrackList).where(TrackList.id == track_list_id)  # type: ignore[arg-type]
        result = await self._session.execute(stmt)
        await self._session.commit()
        return bool(result)

    async def delete_album_by_id(self, album_id: int) -> bool:
        stmt_links = delete(tracks_track_lists).where(tracks_track_lists.c.track_list_id == album_id)
        await self._session.execute(stmt_links)

        stmt_album = delete(TrackList).where(
            TrackList.id == album_id,  # type: ignore[arg-type]
            TrackList._type == TrackListType.ALBUM,  # type: ignore[arg-type]
        )
        result = await self._session.execute(stmt_album)
        await self._session.commit()
        return bool(result.rowcount)
