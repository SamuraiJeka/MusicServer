from sqlalchemy.ext.asyncio import AsyncSession

from domain.ports.repositories.track_list_repository_interface import TrackListRepositoryInterface


class TrackListRepository(TrackListRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, track_list):
        return await super().create(track_list)
    
    async def get_by_id(self, track_list_id):
        return await super().get_by_id(track_list_id)
    
    async def add_track(self, track_list, track):
        return await super().add_track(track_list, track)
    
    async def remove_track(self, track_list, track):
        return await super().remove_track(track_list, track)
    
    async def delete_by_id(self, track_list):
        return await super().delete_by_id(track_list)
