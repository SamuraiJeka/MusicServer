from application.schemas.music_schemas import (
    AlbumSchema,
    AlbumSummarySchema,
    PlaylistSchema,
    PlaylistSummarySchema,
)
from domain.entities.track_list import TrackList, TrackListType
from application.mappers.track_mapper import TrackMapper


class TrackListMapper:
    @staticmethod
    def _require_track_list_id(entity: TrackList) -> int:
        if entity.id is None:
            raise ValueError("TrackList must be persisted before mapping to DTO")
        return entity.id

    @staticmethod
    async def album_entity_to_dto(entity: TrackList) -> AlbumSchema:
        tracks = [
            await TrackMapper.entity_to_dto(track)
            for track in getattr(entity, "track_list", [])
        ]
        return AlbumSchema(
            id=TrackListMapper._require_track_list_id(entity),
            owner_id=entity.owner_id,
            title=entity.title,
            tracks=tracks,
        )

    @staticmethod
    async def playlist_entity_to_dto(entity: TrackList) -> PlaylistSchema:
        tracks = [
            await TrackMapper.entity_to_dto(track)
            for track in getattr(entity, "track_list", [])
        ]
        return PlaylistSchema(
            id=TrackListMapper._require_track_list_id(entity),
            owner_id=entity.owner_id,
            title=entity.title,
            tracks=tracks,
        )

    @staticmethod
    def album_entity_to_summary(entity: TrackList) -> AlbumSummarySchema:
        return AlbumSummarySchema(
            id=TrackListMapper._require_track_list_id(entity),
            owner_id=entity.owner_id,
            title=entity.title,
        )

    @staticmethod
    def playlist_entity_to_summary(entity: TrackList) -> PlaylistSummarySchema:
        return PlaylistSummarySchema(
            id=TrackListMapper._require_track_list_id(entity),
            owner_id=entity.owner_id,
            title=entity.title,
        )

    @staticmethod
    async def album_dto_to_entity(owner_id: int, title: str) -> TrackList:
        return TrackList(
            id=None,
            owner_id=owner_id,
            title=title,
            _type=TrackListType.ALBUM,
        )

    @staticmethod
    async def playlist_dto_to_entity(owner_id: int, title: str) -> TrackList:
        return TrackList(
            id=None,
            owner_id=owner_id,
            title=title,
            _type=TrackListType.PLAYLIST,
        )
