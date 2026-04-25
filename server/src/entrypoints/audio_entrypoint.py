from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.exceptions import ApplicationError
from application.schemas.music_schemas import (
    AlbumSchema,
    BulkAddTracksSchema,
    PlaylistSchema,
    PostTrackSchema,
    TrackSchema,
    TrackAudioUrlSchema,
)
from application.schemas.user_schema import UserSchema
from application.services.music_service import MusicService
from entrypoints.dependencies import get_authenticated_user, get_uow

router = APIRouter(prefix="/music", tags=["audio"])


@router.get("/tracks/{track_id}/audio-url", response_model=TrackAudioUrlSchema)
async def get_track_audio_url(
    track_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> TrackAudioUrlSchema:
    async with uow:
        try:
            return await MusicService(uow).get_track_audio_url(user=user, track_id=track_id)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/albums/{album_id}/tracks", response_model=list[TrackSchema])
async def list_album_tracks(
    album_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[TrackSchema]:
    async with uow:
        try:
            return await MusicService(uow).list_album_tracks(album_id)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/playlists/{playlist_id}/tracks", response_model=list[TrackSchema])
async def list_playlist_tracks(
    playlist_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[TrackSchema]:
    async with uow:
        try:
            return await MusicService(uow).list_playlist_tracks(user, playlist_id)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/me/tracks", response_model=list[TrackSchema])
async def list_my_tracks_by_views(
    user: UserSchema = Depends(get_authenticated_user),
    limit: int | None = Query(default=None, ge=1, le=500),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[TrackSchema]:
    async with uow:
        return await MusicService(uow).list_my_tracks_by_views(user, limit)


@router.get("/tracks/popular", response_model=list[TrackSchema])
async def list_popular_tracks(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[TrackSchema]:
    async with uow:
        return await MusicService(uow).list_popular_tracks(limit, offset)


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


@router.delete("/albums/{album_id}/tracks/{track_id}")
async def delete_track_from_album(
    album_id: int,
    track_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> bool:
    async with uow:
        try:
            return await MusicService(uow).remove_track_from_album(user=user, album_id=album_id, track_id=track_id)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.post("/playlists/{playlist_id}/tracks", response_model=PlaylistSchema)
async def add_track_to_playlist(
    playlist_id: int,
    track_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> PlaylistSchema:
    async with uow:
        return await MusicService(uow).add_track_to_playlist(user, playlist_id, track_id)


@router.post("/playlists/{playlist_id}/tracks/bulk", response_model=PlaylistSchema)
async def add_tracks_to_playlist_bulk(
    playlist_id: int,
    dto: BulkAddTracksSchema,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> PlaylistSchema:
    async with uow:
        try:
            return await MusicService(uow).add_tracks_to_playlist_bulk(
                user=user,
                playlist_id=playlist_id,
                track_ids=[int(tid) for tid in dto.track_ids],
            )
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.delete("/playlists/{playlist_id}/tracks/{track_id}")
async def delete_track_from_playlist(
    playlist_id: int,
    track_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> bool:
    async with uow:
        return await MusicService(uow).remove_track_from_playlist(user, playlist_id, track_id)
