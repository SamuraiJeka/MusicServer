from pydantic import BaseModel, PositiveInt

from application.schemas.music_schemas import AlbumSummarySchema, TrackSchema


class ArtistSchema(BaseModel):
    id: PositiveInt
    username: str


class GlobalSearchResponseSchema(BaseModel):
    artists: list[ArtistSchema]
    albums: list[AlbumSummarySchema]
    tracks: list[TrackSchema]
