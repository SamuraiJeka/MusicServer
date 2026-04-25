from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.ports.repositories.track_repository_interface import TrackRepositoryInterface
from domain.entities.track import Track


class TrackRepository(TrackRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, track: Track) -> Track:
        self._session.add(track)
        await self._session.flush()
        return track
    
    async def delete(self, track: Track) -> bool:
        await self._session.delete(track)
        await self._session.flush()
        return True

    async def get_by_id(self, track_id: int) -> Track | None:
        track = await self._session.get(Track, track_id)
        return track

    async def list_by_owner_order_by_view_desc(
        self, owner_id: int, limit: int | None = None
    ) -> list[Track]:
        stmt = (
            select(Track)
            .where(Track.owner_id == owner_id)  # type: ignore[arg-type]
            .order_by(Track.view.desc())  # type: ignore[attr-defined]
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_order_by_view_desc(self, limit: int, offset: int = 0) -> list[Track]:
        stmt = (
            select(Track)
            .order_by(Track.view.desc())  # type: ignore[attr-defined]
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_title(self, query: str, limit: int, offset: int = 0) -> list[Track]:
        stmt = (
            select(Track)
            .where(Track.title.ilike(f"%{query}%"))  # type: ignore[attr-defined]
            .order_by(Track.view.desc())  # type: ignore[attr-defined]
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
