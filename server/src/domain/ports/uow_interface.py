from abc import ABC, abstractmethod

from domain.ports.repositories.user_repository_interface import UserRepositoryInterface
from domain.ports.repositories.track_list_repository_interface import TrackListRepositoryInterface
from domain.ports.repositories.track_repository_interface import TrackRepositoryInterface
from domain.ports.repositories.chat_repository_interface import ChatRepositoryInterface
from domain.ports.repositories.message_repository_interface import MessageRepositoryInterface
from domain.ports.storage_interface import StorageInterface


class UoWInterface(ABC):
    user_repo: UserRepositoryInterface
    track_list_repo: TrackListRepositoryInterface
    track_repo: TrackRepositoryInterface
    chat_repo: ChatRepositoryInterface
    message_repo: MessageRepositoryInterface
    audio_storage: StorageInterface
    image_storage: StorageInterface

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError
