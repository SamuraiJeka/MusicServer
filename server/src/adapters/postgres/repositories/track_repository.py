from sqlalchemy.ext.asyncio import AsyncSession

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
        result = await self._session.delete(track)
        await self._session.commit()
        return bool(result)

    async def get_by_id(self, track_id: int) -> Track | None:
        track = await self._session.get(Track, track_id)
        return track
