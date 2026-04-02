from application.schemas.music_schemas import AlbumSchema, PlaylistSchema
from domain.entities.track_list import TrackList, TrackListType
from application.mappers.track_mapper import TrackMapper


class TrackListMapper:
    @staticmethod
    async def album_entity_to_dto(entity: TrackList) -> AlbumSchema:
        tracks = [
            await TrackMapper.entity_to_dto(track)
            for track in getattr(entity, "track_list", [])
        ]
        return AlbumSchema(
            id=entity.id,
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
            id=entity.id,
            owner_id=entity.owner_id,
            title=entity.title,
            tracks=tracks,
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
