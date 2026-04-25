from abc import ABC, abstractmethod

from domain.entities.chat import Chat


class ChatRepositoryInterface(ABC):
    @abstractmethod
    async def get_private_chat(self, user_a_id: int, user_b_id: int) -> Chat | None:
        raise NotImplementedError

    @abstractmethod
    async def create_private_chat(self, user_a_id: int, user_b_id: int) -> Chat:
        raise NotImplementedError

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[Chat]:
        raise NotImplementedError

    @abstractmethod
    async def is_member(self, chat_id: int, user_id: int) -> bool:
        raise NotImplementedError
