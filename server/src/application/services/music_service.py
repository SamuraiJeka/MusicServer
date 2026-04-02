from domain.ports.uow_interface import UoWInterface
from application.schemas.music_schemas import (
    PostTrackSchema,
    PostAlbumSchema,
    AlbumSchema,
    PostPlaylistSchema,
    PlaylistSchema,
)
from application.schemas.user_schema import UserSchema
from application.services.audio_metadata import get_mp3_duration
from application.mappers.track_list_mapper import TrackListMapper
from application.mappers.track_mapper import TrackMapper
from domain.entities.track_list import TrackList, TrackListType
from domain.entities.track import Track


class MusicService:
    def __init__(self, uow: UoWInterface) -> None:
        self._uow = uow

    async def create_album(self, user: UserSchema, dto: PostAlbumSchema) -> AlbumSchema:
        album = await TrackListMapper.album_dto_to_entity(
            owner_id=user.id,
            title=dto.title,
        )
        album = await self._uow.track_list_repo.create(album)
        return await TrackListMapper.album_entity_to_dto(album)

    async def add_track_to_album(
        self,
        user: UserSchema,
        album_id: int,
        track_dto: PostTrackSchema,
    ) -> AlbumSchema:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            raise ValueError("Album does not exist.")
        if album.owner_id != user.id:
            raise PermissionError("User is not the owner of the album.")

        track_entity = await self._create_track_for_album(user=user, album=album, track_dto=track_dto)
        album = await self._uow.track_list_repo.add_tracks(album, [track_entity])
        return await TrackListMapper.album_entity_to_dto(album)

    async def _create_track_for_album(
        self,
        user: UserSchema,
        album: TrackList,
        track_dto: PostTrackSchema,
    ) -> Track:
        duration = get_mp3_duration(track_dto.content)
        track_entity: Track = await TrackMapper.dto_to_entity(
            owner_id=user.id,
            title=track_dto.title,
            duration=duration,
            content=track_dto.content,
        )

        track_entity = await self._uow.track_repo.create(track_entity)
        album.add_track(track_entity)

        await self._uow.storage.save(
            user.id,
            track_entity.title,
            track_entity.content,
        )

        return track_entity

    async def create_playlist(
        self,
        user: UserSchema,
        dto: PostPlaylistSchema,
    ) -> PlaylistSchema:
        playlist: TrackList = await TrackListMapper.playlist_dto_to_entity(
            owner_id=user.id,
            title=dto.title,
        )
        playlist = await self._uow.track_list_repo.create(playlist)

        existing_tracks = []
        if dto.track_ids:
            for track_id in dto.track_ids:
                track = await self._uow.track_repo.get_by_id(track_id)
                if track is not None:
                    playlist.add_track(track)
                    existing_tracks.append(track)

            playlist = await self._uow.track_list_repo.add_tracks(playlist, existing_tracks)

        return await TrackListMapper.playlist_entity_to_dto(playlist)

    async def add_track_to_playlist(
        self,
        user: UserSchema,
        playlist_id: int,
        track_id: int,
    ) -> PlaylistSchema:
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            raise ValueError("Playlist does not exist.")
        if playlist.owner_id != user.id:
            raise PermissionError("User is not the owner of the playlist.")

        track = await self._uow.track_repo.get_by_id(track_id)
        if track is None:
            raise ValueError("Track does not exist.")

        playlist.add_track(track)
        playlist = await self._uow.track_list_repo.add_tracks(playlist, [track])
        return await TrackListMapper.playlist_entity_to_dto(playlist)

    async def remove_track_from_playlist(
        self,
        user: UserSchema,
        playlist_id: int,
        track_id: int,
    ) -> bool:
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            return False
        if playlist.owner_id != user.id:
            raise PermissionError("User is not the owner of the playlist.")

        track = await self._uow.track_repo.get_by_id(track_id)
        if track is None:
            return False

        playlist.remove_track(track)
        await self._uow.track_list_repo.remove_track(playlist)
        return True
