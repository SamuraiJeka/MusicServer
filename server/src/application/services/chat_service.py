from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from application.exceptions import BadRequestError, ForbiddenError, NotFoundError
from application.schemas.chat_schemas import ChatSchema, MessageHistorySchema, MessageSchema
from application.schemas.user_schema import UserSchema
from application.services.chat_audio_presign import presign_chat_audio
from domain.entities.message import Message, MessageType
from domain.ports.uow_interface import UoWInterface


def _require_user_id(user: UserSchema) -> int:
    if user.id is None:
        raise BadRequestError("Authenticated user must have id")
    return user.id


class ChatService:
    def __init__(self, uow: UoWInterface) -> None:
        self._uow = uow

    async def get_or_create_private_chat(self, user: UserSchema, other_user_id: int) -> ChatSchema:
        if other_user_id <= 0:
            raise BadRequestError("Invalid user_id")
        user_id = _require_user_id(user)
        if user_id == other_user_id:
            raise BadRequestError("Cannot create chat with yourself")

        async with self._uow:
            other = await self._uow.user_repo.get_by_id(other_user_id)
            if other is None:
                raise NotFoundError("User not found")

            chat = await self._uow.chat_repo.get_private_chat(user_id, other_user_id)
            if chat is None:
                chat = await self._uow.chat_repo.create_private_chat(user_id, other_user_id)

            if chat.id is None or chat.created_at is None:
                raise RuntimeError("Chat fields missing")

            return ChatSchema(id=chat.id, created_at=chat.created_at)

    async def list_my_chats(self, user: UserSchema) -> list[ChatSchema]:
        user_id = _require_user_id(user)
        async with self._uow:
            chats = await self._uow.chat_repo.list_by_user(user_id)
            out: list[ChatSchema] = []
            for c in chats:
                if c.id is None or c.created_at is None:
                    continue
                out.append(ChatSchema(id=c.id, created_at=c.created_at))
            return out

    async def list_messages(self, user: UserSchema, chat_id: int, limit: int, offset: int) -> MessageHistorySchema:
        user_id = _require_user_id(user)
        async with self._uow:
            if not await self._uow.chat_repo.is_member(chat_id, user_id):
                raise ForbiddenError("Not a member of this chat")

            msgs = await self._uow.message_repo.list_by_chat(chat_id=chat_id, limit=limit, offset=offset)
            items: list[MessageSchema] = []
            for m in msgs:
                if m.id is None or m.created_at is None:
                    continue
                audio_url = None
                if m.type == MessageType.AUDIO and m.audio_key:
                    audio_url = await presign_chat_audio(m.audio_key)
                items.append(
                    MessageSchema(
                        id=m.id,
                        chat_id=m.chat_id,
                        user_id=m.user_id,
                        type=m.type.value,
                        text=m.text,
                        audio_key=m.audio_key,
                        audio_url=audio_url,
                        created_at=m.created_at,
                    )
                )
            return MessageHistorySchema(items=items, limit=limit, offset=offset)

    async def upload_audio(self, user: UserSchema, content: bytes, original_filename: str | None) -> str:
        user_id = _require_user_id(user)
        if not content:
            raise BadRequestError("Empty file")

        filename = (original_filename or "audio.mp3").lower()
        if not filename.endswith(".mp3"):
            raise BadRequestError("Only .mp3 is supported")

        key = f"chat_uploads/{user_id}/{uuid4().hex}.mp3"
        prefix, fname = key.rsplit("/", 1)
        async with self._uow:
            await self._uow.audio_storage.save(prefix, fname, content)
        return key

    async def create_text_message(self, user: UserSchema, chat_id: int, text: str) -> MessageSchema:
        user_id = _require_user_id(user)
        if not text or not text.strip():
            raise BadRequestError("Text is empty")

        async with self._uow:
            if not await self._uow.chat_repo.is_member(chat_id, user_id):
                raise ForbiddenError("Not a member of this chat")

            msg = Message(
                id=None,
                chat_id=chat_id,
                user_id=user_id,
                type=MessageType.TEXT,
                text=text.strip(),
                audio_key=None,
                created_at=datetime.utcnow(),
            )
            msg = await self._uow.message_repo.create(msg)

            if msg.id is None:
                raise RuntimeError("Message id was not generated")

            return MessageSchema(
                id=msg.id,
                chat_id=msg.chat_id,
                user_id=msg.user_id,
                type=msg.type.value,
                text=msg.text,
                audio_key=None,
                audio_url=None,
                created_at=msg.created_at or datetime.utcnow(),
            )

    async def create_audio_message(self, user: UserSchema, chat_id: int, audio_key: str) -> MessageSchema:
        user_id = _require_user_id(user)
        if not audio_key or "/" not in audio_key:
            raise BadRequestError("Invalid audio_key")

        async with self._uow:
            if not await self._uow.chat_repo.is_member(chat_id, user_id):
                raise ForbiddenError("Not a member of this chat")

            msg = Message(
                id=None,
                chat_id=chat_id,
                user_id=user_id,
                type=MessageType.AUDIO,
                text=None,
                audio_key=audio_key,
                created_at=datetime.utcnow(),
            )
            msg = await self._uow.message_repo.create(msg)

            if msg.id is None:
                raise RuntimeError("Message id was not generated")

            audio_url = await presign_chat_audio(audio_key)
            return MessageSchema(
                id=msg.id,
                chat_id=msg.chat_id,
                user_id=msg.user_id,
                type=msg.type.value,
                text=None,
                audio_key=audio_key,
                audio_url=audio_url,
                created_at=msg.created_at or datetime.utcnow(),
            )
