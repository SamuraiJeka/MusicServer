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
    audio_key: Optional[str] = None
    duration: timedelta
    view: int


class TrackAudioUrlSchema(BaseModel):
    url: str
    expires_in: int = 3600


class PostAlbumSchema(BaseModel):
    title: str


class AlbumSchema(BaseModel):
    id: PositiveInt
    owner_id: PositiveInt
    title: str
    image_filename: Optional[str] = None
    tracks: List[TrackSchema]


class AlbumSummarySchema(BaseModel):
    id: PositiveInt
    owner_id: PositiveInt
    title: str
    image_filename: Optional[str] = None


class PatchAlbumSchema(BaseModel):
    title: str


class PostPlaylistSchema(BaseModel):
    title: str
    track_ids: Optional[list[PositiveInt]] = Field(default=None)


class PlaylistSchema(BaseModel):
    id: PositiveInt
    owner_id: PositiveInt
    title: str
    image_filename: Optional[str] = None
    tracks: List[TrackSchema]


class PlaylistSummarySchema(BaseModel):
    id: PositiveInt
    owner_id: PositiveInt
    title: str
    image_filename: Optional[str] = None


class PatchPlaylistSchema(BaseModel):
    title: str


class BulkAddTracksSchema(BaseModel):
    track_ids: list[PositiveInt]


class OrderTracksSchema(BaseModel):
    track_ids: list[PositiveInt]


class SearchResponseSchema(BaseModel):
    albums: list[AlbumSummarySchema]
    tracks: list[TrackSchema]
