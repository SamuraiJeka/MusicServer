from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from adapters.postgres.orm import chats, chat_members
from domain.entities.chat import Chat
from domain.entities.chat_member import ChatMember
from domain.ports.repositories.chat_repository_interface import ChatRepositoryInterface


class ChatRepository(ChatRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_private_chat(self, user_a_id: int, user_b_id: int) -> Chat | None:
        stmt = (
            select(Chat)
            .where(
                exists()
                .where(chat_members.c.chat_id == Chat.id)
                .where(chat_members.c.user_id == user_a_id)
            )
            .where(
                exists()
                .where(chat_members.c.chat_id == Chat.id)
                .where(chat_members.c.user_id == user_b_id)
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_private_chat(self, user_a_id: int, user_b_id: int) -> Chat:
        chat = Chat(id=None, created_at=datetime.utcnow())
        self._session.add(chat)
        await self._session.flush()

        if chat.id is None:
            raise RuntimeError("Chat id was not generated")

        self._session.add(ChatMember(id=None, chat_id=chat.id, user_id=user_a_id))
        self._session.add(ChatMember(id=None, chat_id=chat.id, user_id=user_b_id))
        await self._session.flush()
        return chat

    async def list_by_user(self, user_id: int) -> list[Chat]:
        stmt = (
            select(Chat)
            .join(chat_members, chat_members.c.chat_id == Chat.id)
            .where(chat_members.c.user_id == user_id)
            .order_by(Chat.id.desc())  # type: ignore[union-attr]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def is_member(self, chat_id: int, user_id: int) -> bool:
        stmt = select(chat_members.c.id).where(
            chat_members.c.chat_id == chat_id,
            chat_members.c.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.first() is not None
