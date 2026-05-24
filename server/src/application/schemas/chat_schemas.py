from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, PositiveInt


class ChatSchema(BaseModel):
    id: PositiveInt
    created_at: datetime


class ChatPeerSchema(BaseModel):
    id: PositiveInt
    username: str


class ChatSummarySchema(BaseModel):
    id: PositiveInt
    created_at: datetime
    peer: ChatPeerSchema
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None


class MessageSchema(BaseModel):
    id: PositiveInt
    chat_id: PositiveInt
    user_id: PositiveInt
    type: Literal["text", "audio"]
    text: Optional[str] = None
    audio_key: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: datetime


class MessageHistorySchema(BaseModel):
    items: list[MessageSchema]
    limit: int = Field(ge=1, le=200)
    offset: int = Field(ge=0)


class UploadAudioResponseSchema(BaseModel):
    audio_key: str


class SendTextMessageSchema(BaseModel):
    text: str


class SendAudioMessageSchema(BaseModel):
    audio_key: str
