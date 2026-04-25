from __future__ import annotations

from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"


class Message:
    def __init__(
        self,
        id: int | None,
        chat_id: int,
        user_id: int,
        type: MessageType,
        text: str | None = None,
        audio_key: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.chat_id = chat_id
        self.user_id = user_id
        self.type = type
        self.text = text
        self.audio_key = audio_key
        self.created_at = created_at
