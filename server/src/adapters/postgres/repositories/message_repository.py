from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.entities.message import Message
from domain.ports.repositories.message_repository_interface import MessageRepositoryInterface


class MessageRepository(MessageRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, message: Message) -> Message:
        self._session.add(message)
        await self._session.flush()
        return message

    async def list_by_chat(self, chat_id: int, limit: int, offset: int) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)  # type: ignore[arg-type]
            .order_by(Message.created_at.desc())  # type: ignore[union-attr]
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_last_by_chats(self, chat_ids: list[int]) -> dict[int, Message]:
        if not chat_ids:
            return {}
        stmt = (
            select(Message)
            .where(Message.chat_id.in_(chat_ids))  # type: ignore[attr-defined]
            .order_by(Message.chat_id, Message.created_at.desc())  # type: ignore[union-attr]
            .distinct(Message.chat_id)  # type: ignore[arg-type]
        )
        result = await self._session.execute(stmt)
        return {m.chat_id: m for m in result.scalars().all()}
