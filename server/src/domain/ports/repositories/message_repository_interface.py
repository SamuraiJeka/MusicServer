from abc import ABC, abstractmethod

from domain.entities.message import Message


class MessageRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, message: Message) -> Message:
        raise NotImplementedError

    @abstractmethod
    async def list_by_chat(
        self,
        chat_id: int,
        limit: int,
        offset: int,
    ) -> list[Message]:
        raise NotImplementedError
