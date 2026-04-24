from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.exceptions import ApplicationError
from application.services.music_service import MusicService
from application.schemas.user_schema import UserSchema
from domain.entities.track_list import TrackListType
from entrypoints.dependencies import get_authenticated_user, get_uow

router = APIRouter(prefix="/music", tags=["image"])


@router.post("/albums/{album_id}/image")
async def add_album_image(
    album_id: int,
    file: UploadFile = File(...),
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> bool:
    content = await file.read()
    async with uow:
        try:
            return await MusicService(uow).add_track_list_image(
                user=user,
                track_list_id=album_id,
                content=content,
                filename=file.filename,
                expected_type=TrackListType.ALBUM,
            )
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.patch("/albums/{album_id}/image")
async def update_album_image(
    album_id: int,
    file: UploadFile = File(...),
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> bool:
    content = await file.read()
    async with uow:
        try:
            return await MusicService(uow).update_track_list_image(
                user=user,
                track_list_id=album_id,
                content=content,
                filename=file.filename,
                expected_type=TrackListType.ALBUM,
            )
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.post("/playlists/{playlist_id}/image")
async def add_playlist_image(
    playlist_id: int,
    file: UploadFile = File(...),
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> bool:
    content = await file.read()
    async with uow:
        try:
            return await MusicService(uow).add_track_list_image(
                user=user,
                track_list_id=playlist_id,
                content=content,
                filename=file.filename,
                expected_type=TrackListType.PLAYLIST,
            )
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.patch("/playlists/{playlist_id}/image")
async def update_playlist_image(
    playlist_id: int,
    file: UploadFile = File(...),
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> bool:
    content = await file.read()
    async with uow:
        try:
            return await MusicService(uow).update_track_list_image(
                user=user,
                track_list_id=playlist_id,
                content=content,
                filename=file.filename,
                expected_type=TrackListType.PLAYLIST,
            )
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e
