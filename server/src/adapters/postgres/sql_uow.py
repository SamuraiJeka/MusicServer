from sqlalchemy.ext.asyncio import AsyncSession

from adapters.postgres.repositories.user_repository import UserRepository
from adapters.postgres.repositories.track_list_repository import TrackListRepository
from adapters.postgres.repositories.track_repository import TrackRepository
from adapters.postgres.repositories.chat_repository import ChatRepository
from adapters.postgres.repositories.message_repository import MessageRepository
from adapters.minio.audio_storage import AudioStorage
from adapters.minio.image_storage import ImageStorage
from domain.ports.uow_interface import UoWInterface


class SqlAlchemyUnitOfWork(UoWInterface):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.user_repo = UserRepository(self._session)
        self.track_list_repo = TrackListRepository(self._session)
        self.track_repo = TrackRepository(self._session)
        self.chat_repo = ChatRepository(self._session)
        self.message_repo = MessageRepository(self._session)
        self.audio_storage = AudioStorage()
        self.image_storage = ImageStorage()

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()
        # Session lifecycle is managed by FastAPI dependency `get_session`.
        # Do not close here to allow WebSocket dependencies to reuse the same session safely.
