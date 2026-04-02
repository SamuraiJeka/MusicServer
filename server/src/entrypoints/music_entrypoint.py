from fastapi import APIRouter, Depends, UploadFile, File, Form

from entrypoints.dependencies import get_authenticated_user, get_uow
from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.schemas.user_schema import UserSchema
from application.schemas.music_schemas import (
    PostAlbumSchema,
    AlbumSchema,
    PostPlaylistSchema,
    PlaylistSchema,
    PostTrackSchema,
)
from application.services.music_service import MusicService

router = APIRouter(prefix="/music", tags=["music"])


@router.post("/albums", response_model=AlbumSchema)
async def create_album(
    album_dto: PostAlbumSchema,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> AlbumSchema:
    async with uow:
        return await MusicService(uow).create_album(user, album_dto)


@router.post("/albums/{album_id}/tracks", response_model=AlbumSchema)
async def add_track_to_album(
    album_id: int,
    title: str = Form(...),
    file: UploadFile = File(...),
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> AlbumSchema:
    content = await file.read()
    track_dto = PostTrackSchema(title=title, content=content)
    async with uow:
        return await MusicService(uow).add_track_to_album(user, album_id, track_dto)


@router.post("/playlists", response_model=PlaylistSchema)
async def create_playlist(
    playlist_dto: PostPlaylistSchema,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> PlaylistSchema:
    async with uow:
        return await MusicService(uow).create_playlist(user, playlist_dto)


@router.post("/playlists/{playlist_id}/tracks", response_model=PlaylistSchema)
async def add_track_to_playlist(
    playlist_id: int,
    track_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> PlaylistSchema:
    async with uow:
        return await MusicService(uow).add_track_to_playlist(user, playlist_id, track_id)


@router.delete("/playlists/{playlist_id}/tracks/{track_id}")
async def delete_track_from_playlist(
    playlist_id: int,
    track_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> bool:
    async with uow:
        return await MusicService(uow).remove_track_from_playlist(user, playlist_id, track_id)
