from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from adapters.postgres.engine import session_factory
from adapters.postgres.repositories.user_repository import UserRepository
from adapters.postgres.repositories.track_list_repository import TrackListRepository
from domain.ports.uow_interface import UoWInterface


class SqlAlchemyUnitOfWork(UoWInterface):
    def __init__(self, session_factory: async_sessionmaker = session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()

        self.user_repo = UserRepository(self.session)
        self.track_list_repo = TrackListRepository(self.session)

        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
    
    async def commit(self) -> None:
        self.session.commit()
    
    async def rollback(self):
        self.session.rollback()
