from sqlalchemy.ext.asyncio import AsyncSession

from adapters.postgres.repositories.user_repository import UserRepository
from adapters.postgres.repositories.track_list_repository import TrackListRepository
from domain.ports.uow_interface import UoWInterface


class SqlAlchemyUnitOfWork(UoWInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self):
        self.user_repo = UserRepository(self._session)
        self.track_list_repo = TrackListRepository(self._session)
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()
        await self._session.close()
