from typing import Optional

from pydantic import BaseModel, PositiveInt

from application.schemas.music_schemas import AlbumSummarySchema


class ArtistSchema(BaseModel):
    id: PositiveInt
    username: str
    avatar_url: Optional[str] = None


class SearchTrackSchema(BaseModel):
    id: PositiveInt
    title: str
    artist_name: str
    owner_id: PositiveInt
    cover_url: Optional[str] = None


class MessengerUserSchema(BaseModel):
    id: PositiveInt
    username: str
    has_chat: bool = False
    chat_id: Optional[PositiveInt] = None
    last_message: Optional[str] = None


class GlobalSearchResponseSchema(BaseModel):
    artists: list[ArtistSchema]
    albums: list[AlbumSummarySchema]
    tracks: list[SearchTrackSchema]
