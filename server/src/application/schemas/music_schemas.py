from datetime import timedelta
from typing import Optional, List

from pydantic import BaseModel, PositiveInt, Field


class PostTrackSchema(BaseModel):
    title: str
    content: bytes


class TrackSchema(BaseModel):
    id: PositiveInt
    owner_id: PositiveInt
    title: str
    duration: timedelta
    view: int


class PostAlbumSchema(BaseModel):
    title: str


class AlbumSchema(BaseModel):
    id: PositiveInt
    owner_id: PositiveInt
    title: str
    tracks: List[TrackSchema]


class PostPlaylistSchema(BaseModel):
    title: str
    track_ids: Optional[list[PositiveInt]] = Field(default=None)


class PlaylistSchema(BaseModel):
    id: PositiveInt
    owner_id: PositiveInt
    title: str
    tracks: List[TrackSchema]
