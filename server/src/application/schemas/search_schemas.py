from typing import Optional

from pydantic import BaseModel, PositiveInt

from application.schemas.music_schemas import AlbumSummarySchema, TrackSchema


class ArtistSchema(BaseModel):
    id: PositiveInt
    username: str


class MessengerUserSchema(BaseModel):
    id: PositiveInt
    username: str
    has_chat: bool = False
    chat_id: Optional[PositiveInt] = None
    last_message: Optional[str] = None


class GlobalSearchResponseSchema(BaseModel):
    artists: list[ArtistSchema]
    albums: list[AlbumSummarySchema]
    tracks: list[TrackSchema]
