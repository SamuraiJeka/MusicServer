from domain.ports.uow_interface import UoWInterface
from application.schemas.music_schemas import (
    PostTrackSchema,
    PostAlbumSchema,
    AlbumSchema,
    AlbumSummarySchema,
    PostPlaylistSchema,
    PlaylistSchema,
    PlaylistSummarySchema,
    TrackSchema,
)
from application.schemas.user_schema import UserSchema
from application.services.audio_metadata import get_mp3_duration
from application.mappers.track_list_mapper import TrackListMapper
from application.mappers.track_mapper import TrackMapper
from domain.entities.track_list import TrackList, TrackListType
from domain.entities.track import Track


def _require_user_id(user: UserSchema) -> int:
    if user.id is None:
        raise ValueError("Authenticated user must have id")
    return user.id


class MusicService:
    def __init__(self, uow: UoWInterface) -> None:
        self._uow = uow

    async def create_album(self, user: UserSchema, dto: PostAlbumSchema) -> AlbumSchema:
        album = await TrackListMapper.album_dto_to_entity(
            owner_id=_require_user_id(user),
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
        if album.owner_id != _require_user_id(user):
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
        if duration is None:
            raise ValueError("Could not read audio duration")
        owner_id = _require_user_id(user)
        track_entity: Track = await TrackMapper.dto_to_entity(
            owner_id=owner_id,
            title=track_dto.title,
            duration=duration,
            content=track_dto.content,
        )

        track_entity = await self._uow.track_repo.create(track_entity)
        album.add_track(track_entity)

        await self._uow.storage.save(
            str(owner_id),
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
            owner_id=_require_user_id(user),
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
        if playlist.owner_id != _require_user_id(user):
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
        if playlist.owner_id != _require_user_id(user):
            raise PermissionError("User is not the owner of the playlist.")

        track = await self._uow.track_repo.get_by_id(track_id)
        if track is None:
            return False

        playlist.remove_track(track)
        await self._uow.track_list_repo.remove_track(playlist)
        return True

    async def list_album_tracks(self, album_id: int) -> list[TrackSchema]:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            raise ValueError("Album not found.")
        return [
            await TrackMapper.entity_to_dto(track)
            for track in album.track_list
        ]

    async def list_playlist_tracks(
        self, user: UserSchema, playlist_id: int
    ) -> list[TrackSchema]:
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            raise ValueError("Playlist not found.")
        if playlist.owner_id != _require_user_id(user):
            raise PermissionError("Playlist is private.")
        return [
            await TrackMapper.entity_to_dto(track)
            for track in playlist.track_list
        ]

    async def list_my_tracks_by_views(
        self, user: UserSchema, limit: int | None = None
    ) -> list[TrackSchema]:
        tracks = await self._uow.track_repo.list_by_owner_order_by_view_desc(
            _require_user_id(user), limit
        )
        return [await TrackMapper.entity_to_dto(t) for t in tracks]

    async def list_my_albums(self, user: UserSchema) -> list[AlbumSummarySchema]:
        albums = await self._uow.track_list_repo.list_by_owner_and_type(
            _require_user_id(user), TrackListType.ALBUM
        )
        return [TrackListMapper.album_entity_to_summary(a) for a in albums]

    async def list_my_playlists(self, user: UserSchema) -> list[PlaylistSummarySchema]:
        playlists = await self._uow.track_list_repo.list_by_owner_and_type(
            _require_user_id(user), TrackListType.PLAYLIST
        )
        return [TrackListMapper.playlist_entity_to_summary(p) for p in playlists]

    async def list_popular_tracks(self, limit: int) -> list[TrackSchema]:
        tracks = await self._uow.track_repo.list_order_by_view_desc(limit)
        return [await TrackMapper.entity_to_dto(t) for t in tracks]

    async def get_album(self, album_id: int) -> AlbumSummarySchema:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            raise ValueError("Album not found.")
        return TrackListMapper.album_entity_to_summary(album)

    async def list_albums(
        self,
        limit: int,
        offset: int,
        owner_id: int | None = None,
    ) -> list[AlbumSummarySchema]:
        albums = await self._uow.track_list_repo.list_albums(
            limit=limit,
            offset=offset,
            owner_id=owner_id,
        )
        return [TrackListMapper.album_entity_to_summary(a) for a in albums]

    async def patch_album(
        self,
        user: UserSchema,
        album_id: int,
        title: str,
    ) -> AlbumSummarySchema:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            raise ValueError("Album not found.")
        if album.owner_id != _require_user_id(user):
            raise PermissionError("User is not the owner of the album.")

        album.title = title
        # TrackList уже в сессии, flush на выходе UoW зафиксирует изменения
        return TrackListMapper.album_entity_to_summary(album)

    async def remove_track_from_album(
        self,
        user: UserSchema,
        album_id: int,
        track_id: int,
    ) -> bool:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            return False
        if album.owner_id != _require_user_id(user):
            raise PermissionError("User is not the owner of the album.")

        track = next((t for t in album.track_list if t.id == track_id), None)
        if track is None:
            return False

        album.remove_track(track)
        await self._uow.track_list_repo.remove_track(album)
        return True

    async def delete_album(self, user: UserSchema, album_id: int) -> bool:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            return False
        if album.owner_id != _require_user_id(user):
            raise PermissionError("User is not the owner of the album.")

        return await self._uow.track_list_repo.delete_album_by_id(album_id)
