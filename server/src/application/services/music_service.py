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
    TrackAudioUrlSchema,
    ImageUrlSchema,
    SearchResponseSchema,
)
from application.schemas.user_schema import UserSchema
from application.services.audio_metadata import get_mp3_duration
from application.mappers.track_list_mapper import TrackListMapper
from application.mappers.track_mapper import TrackMapper
from domain.entities.track_list import TrackList, TrackListType
from domain.entities.track import Track
from application.exceptions import BadRequestError, ForbiddenError, NotFoundError
from application.services.track_audio_presign import presign_track_audio
from application.services.track_list_image_presign import presign_track_list_image
from uuid import uuid4


class MusicService:
    def __init__(self, uow: UoWInterface) -> None:
        self._uow = uow

    async def create_album(self, user: UserSchema, dto: PostAlbumSchema) -> AlbumSchema:
        album = await TrackListMapper.album_dto_to_entity(
            owner_id=self._require_user_id(user),
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
            raise NotFoundError("Album does not exist.")
        if album.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the album.")

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
            raise BadRequestError("Could not read audio duration")
        owner_id = self._require_user_id(user)
        audio_key = f"tracks/{owner_id}/{uuid4().hex}.mp3"
        prefix, filename = audio_key.rsplit("/", 1)
        track_entity: Track = await TrackMapper.dto_to_entity(
            owner_id=owner_id,
            title=track_dto.title,
            duration=duration,
            content=track_dto.content,
            audio_key=audio_key,
            created_album_id=album.id,
        )

        track_entity = await self._uow.track_repo.create(track_entity)
        album.add_track(track_entity)

        await self._uow.audio_storage.save(
            prefix,
            filename,
            track_entity.content,
        )

        return track_entity

    def _image_prefix_for_list(self, owner_id: int, track_list: TrackList) -> str:
        list_id = track_list.id
        if list_id is None:
            raise BadRequestError("TrackList must be persisted before saving image")
        return f"{owner_id}/{track_list._type.value}/{list_id}"

    async def get_album_image_url(self, user: UserSchema, album_id: int) -> ImageUrlSchema:
        self._require_user_id(user)
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            raise NotFoundError("Album not found.")
        if not getattr(album, "image_filename", None):
            raise NotFoundError("Album image not found.")
        prefix = self._image_prefix_for_list(album.owner_id, album)
        key = f"{prefix}/{album.image_filename}"
        expires_in = 3600
        url = await presign_track_list_image(key, expires_in=expires_in)
        return ImageUrlSchema(url=url, expires_in=expires_in)

    async def get_playlist_image_url(self, user: UserSchema, playlist_id: int) -> ImageUrlSchema:
        self._require_user_id(user)
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            raise NotFoundError("Playlist not found.")
        if not getattr(playlist, "image_filename", None):
            raise NotFoundError("Playlist image not found.")
        prefix = self._image_prefix_for_list(playlist.owner_id, playlist)
        key = f"{prefix}/{playlist.image_filename}"
        expires_in = 3600
        url = await presign_track_list_image(key, expires_in=expires_in)
        return ImageUrlSchema(url=url, expires_in=expires_in)

    async def add_track_list_image(
        self,
        user: UserSchema,
        track_list_id: int,
        content: bytes,
        filename: str | None,
        expected_type: TrackListType,
    ) -> bool:
        track_list = await self._uow.track_list_repo.get_by_id(track_list_id)
        if track_list is None or track_list._type != expected_type:
            raise NotFoundError("Track list does not exist.")
        if track_list.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner.")
        if getattr(track_list, "image_filename", None):
            raise BadRequestError("Image already exists. Use update endpoint.")

        track_list.image_filename = filename or "image"
        await self._uow.image_storage.save(
            self._image_prefix_for_list(track_list.owner_id, track_list),
            track_list.image_filename,
            content,
        )
        return True

    async def update_track_list_image(
        self,
        user: UserSchema,
        track_list_id: int,
        content: bytes,
        filename: str | None,
        expected_type: TrackListType,
    ) -> bool:
        track_list = await self._uow.track_list_repo.get_by_id(track_list_id)
        if track_list is None or track_list._type != expected_type:
            raise NotFoundError("Track list does not exist.")
        if track_list.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner.")

        prefix = self._image_prefix_for_list(track_list.owner_id, track_list)
        old_filename = getattr(track_list, "image_filename", None)
        if old_filename:
            await self._uow.image_storage.delete(prefix, old_filename)

        track_list.image_filename = filename or "image"
        await self._uow.image_storage.save(prefix, track_list.image_filename, content)
        return True

    async def create_playlist(
        self,
        user: UserSchema,
        dto: PostPlaylistSchema,
    ) -> PlaylistSchema:
        playlist: TrackList = await TrackListMapper.playlist_dto_to_entity(
            owner_id=self._require_user_id(user),
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
            raise NotFoundError("Playlist does not exist.")
        if playlist.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the playlist.")

        track = await self._uow.track_repo.get_by_id(track_id)
        if track is None:
            raise NotFoundError("Track does not exist.")

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
        if playlist.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the playlist.")

        track = await self._uow.track_repo.get_by_id(track_id)
        if track is None:
            return False

        playlist.remove_track(track)
        await self._uow.track_list_repo.remove_track(playlist)
        return True

    async def list_album_tracks(self, album_id: int) -> list[TrackSchema]:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            raise NotFoundError("Album not found.")
        return [
            await TrackMapper.entity_to_dto(track)
            for track in album.track_list
        ]

    async def list_playlist_tracks(
        self, user: UserSchema, playlist_id: int
    ) -> list[TrackSchema]:
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            raise NotFoundError("Playlist not found.")
        if playlist.owner_id != self._require_user_id(user):
            raise ForbiddenError("Playlist is private.")
        return [
            await TrackMapper.entity_to_dto(track)
            for track in playlist.track_list
        ]

    async def list_my_tracks_by_views(
        self, user: UserSchema, limit: int | None = None
    ) -> list[TrackSchema]:
        return await self.list_user_tracks_by_views(self._require_user_id(user), limit)

    async def list_user_tracks_by_views(
        self, owner_id: int, limit: int | None = None
    ) -> list[TrackSchema]:
        if owner_id <= 0:
            raise BadRequestError("Invalid user_id")
        tracks = await self._uow.track_repo.list_by_owner_order_by_view_desc(owner_id, limit)
        return [await TrackMapper.entity_to_dto(t) for t in tracks]

    async def list_my_albums(self, user: UserSchema) -> list[AlbumSummarySchema]:
        albums = await self._uow.track_list_repo.list_by_owner_and_type(
            self._require_user_id(user), TrackListType.ALBUM
        )
        return [TrackListMapper.album_entity_to_summary(a) for a in albums]

    async def list_my_playlists(self, user: UserSchema) -> list[PlaylistSummarySchema]:
        playlists = await self._uow.track_list_repo.list_by_owner_and_type(
            self._require_user_id(user), TrackListType.PLAYLIST
        )
        return [TrackListMapper.playlist_entity_to_summary(p) for p in playlists]

    async def list_popular_tracks(self, limit: int, offset: int = 0) -> list[TrackSchema]:
        tracks = await self._uow.track_repo.list_order_by_view_desc(limit, offset)
        return [await TrackMapper.entity_to_dto(t) for t in tracks]

    async def get_track_audio_url(self, user: UserSchema, track_id: int) -> TrackAudioUrlSchema:
        self._require_user_id(user)
        track = await self._uow.track_repo.get_by_id(track_id)
        if track is None:
            raise NotFoundError("Track not found.")
        if not track.audio_key:
            raise BadRequestError("Track audio is not available.")
        expires_in = 3600
        url = await presign_track_audio(track.audio_key, expires_in=expires_in)
        return TrackAudioUrlSchema(url=url, expires_in=expires_in)

    async def get_album(self, album_id: int) -> AlbumSummarySchema:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            raise NotFoundError("Album not found.")
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

    async def list_popular_albums(self, limit: int, offset: int = 0) -> list[AlbumSummarySchema]:
        albums = await self._uow.track_list_repo.list_popular_albums(limit=limit, offset=offset)
        return [TrackListMapper.album_entity_to_summary(a) for a in albums]

    async def search(self, query: str, limit: int, offset: int = 0) -> SearchResponseSchema:
        albums = await self._uow.track_list_repo.search_albums(query=query, limit=limit, offset=offset)
        tracks = await self._uow.track_repo.search_by_title(query=query, limit=limit, offset=offset)
        return SearchResponseSchema(
            albums=[TrackListMapper.album_entity_to_summary(a) for a in albums],
            tracks=[await TrackMapper.entity_to_dto(t) for t in tracks],
        )

    async def patch_album(
        self,
        user: UserSchema,
        album_id: int,
        title: str,
    ) -> AlbumSummarySchema:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            raise NotFoundError("Album not found.")
        if album.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the album.")

        album.title = title
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
        if album.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the album.")

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
        if album.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the album.")

        return await self._uow.track_list_repo.delete_album_by_id(album_id)

    async def get_playlist(self, user: UserSchema, playlist_id: int) -> PlaylistSchema:
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            raise NotFoundError("Playlist not found.")
        if playlist.owner_id != self._require_user_id(user):
            raise ForbiddenError("Playlist is private.")
        return await TrackListMapper.playlist_entity_to_dto(playlist)

    async def patch_playlist(
        self,
        user: UserSchema,
        playlist_id: int,
        title: str,
    ) -> PlaylistSummarySchema:
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            raise NotFoundError("Playlist not found.")
        if playlist.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the playlist.")
        playlist.title = title
        return TrackListMapper.playlist_entity_to_summary(playlist)

    async def delete_playlist(self, user: UserSchema, playlist_id: int) -> bool:
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            return False
        if playlist.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the playlist.")
        return await self._uow.track_list_repo.delete_playlist_by_id(playlist_id)

    async def add_tracks_to_playlist_bulk(
        self,
        user: UserSchema,
        playlist_id: int,
        track_ids: list[int],
    ) -> PlaylistSchema:
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            raise NotFoundError("Playlist not found.")
        if playlist.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the playlist.")

        tracks_to_add: list[Track] = []
        for track_id in track_ids:
            track = await self._uow.track_repo.get_by_id(track_id)
            if track is None:
                raise NotFoundError(f"Track not found: {track_id}")
            playlist.add_track(track)
            tracks_to_add.append(track)

        playlist = await self._uow.track_list_repo.add_tracks(playlist, tracks_to_add)
        return await TrackListMapper.playlist_entity_to_dto(playlist)

    async def set_playlist_track_order(
        self,
        user: UserSchema,
        playlist_id: int,
        ordered_track_ids: list[int],
    ) -> PlaylistSchema:
        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None or playlist._type != TrackListType.PLAYLIST:
            raise NotFoundError("Playlist not found.")
        if playlist.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the playlist.")

        existing_ids = {t.id for t in playlist.track_list if t.id is not None}
        if not ordered_track_ids:
            raise BadRequestError("track_ids must not be empty")

        if any(tid not in existing_ids for tid in ordered_track_ids):
            raise BadRequestError("track_ids contains track not in playlist")

        await self._uow.track_list_repo.set_track_order(playlist_id, ordered_track_ids)

        playlist = await self._uow.track_list_repo.get_by_id(playlist_id)
        if playlist is None:
            raise NotFoundError("Playlist not found.")
        return await TrackListMapper.playlist_entity_to_dto(playlist)

    async def set_album_track_order(
        self,
        user: UserSchema,
        album_id: int,
        ordered_track_ids: list[int],
    ) -> AlbumSchema:
        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None or album._type != TrackListType.ALBUM:
            raise NotFoundError("Album not found.")
        if album.owner_id != self._require_user_id(user):
            raise ForbiddenError("User is not the owner of the album.")

        existing_ids = {t.id for t in album.track_list if t.id is not None}
        if not ordered_track_ids:
            raise BadRequestError("track_ids must not be empty")
        if any(tid not in existing_ids for tid in ordered_track_ids):
            raise BadRequestError("track_ids contains track not in album")

        await self._uow.track_list_repo.set_track_order(album_id, ordered_track_ids)

        album = await self._uow.track_list_repo.get_by_id(album_id)
        if album is None:
            raise NotFoundError("Album not found.")
        return await TrackListMapper.album_entity_to_dto(album)
    
    @staticmethod
    def _require_user_id(user: UserSchema) -> int:
        if user.id is None:
            raise BadRequestError("Authenticated user must have id")
        return user.id
