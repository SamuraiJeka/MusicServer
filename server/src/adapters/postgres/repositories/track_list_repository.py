from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import selectinload

from domain.ports.repositories.track_list_repository_interface import TrackListRepositoryInterface
from domain.entities.track_list import TrackList, TrackListType
from domain.entities.track import Track
from adapters.postgres.orm import tracks
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

    async def search_albums(self, query: str, limit: int, offset: int = 0) -> list[TrackList]:
        stmt = (
            select(TrackList)
            .where(
                TrackList._type == TrackListType.ALBUM,  # type: ignore[arg-type]
                TrackList.title.ilike(f"%{query}%"),  # type: ignore[attr-defined]
            )
            .order_by(TrackList.id.desc())  # type: ignore[union-attr]
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_popular_albums(self, limit: int, offset: int = 0) -> list[TrackList]:
        # Popularity: sum of track.view for tracks linked to the album.
        views_sum = func.coalesce(func.sum(tracks.c.view), 0).label("views_sum")
        stmt = (
            select(TrackList)
            .select_from(TrackList)
            .join(tracks_track_lists, tracks_track_lists.c.track_list_id == TrackList.id, isouter=True)
            .join(tracks, tracks.c.id == tracks_track_lists.c.track_id, isouter=True)
            .where(TrackList._type == TrackListType.ALBUM)  # type: ignore[arg-type]
            .group_by(TrackList.id)
            .order_by(views_sum.desc(), TrackList.id.desc())  # type: ignore[union-attr]
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
        rowcount = getattr(result, "rowcount", 0)
        return bool(rowcount)

    async def delete_playlist_by_id(self, playlist_id: int) -> bool:
        stmt_links = delete(tracks_track_lists).where(tracks_track_lists.c.track_list_id == playlist_id)
        await self._session.execute(stmt_links)

        stmt_playlist = delete(TrackList).where(
            TrackList.id == playlist_id,  # type: ignore[arg-type]
            TrackList._type == TrackListType.PLAYLIST,  # type: ignore[arg-type]
        )
        result = await self._session.execute(stmt_playlist)
        await self._session.commit()
        rowcount = getattr(result, "rowcount", 0)
        return bool(rowcount)

    async def set_track_order(self, track_list_id: int, ordered_track_ids: list[int]) -> None:
        for idx, track_id in enumerate(ordered_track_ids, start=1):
            stmt = (
                update(tracks_track_lists)
                .where(
                    tracks_track_lists.c.track_list_id == track_list_id,
                    tracks_track_lists.c.track_id == track_id,
                )
                .values(position=idx)
            )
            await self._session.execute(stmt)
        await self._session.flush()
