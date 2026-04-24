from fastapi import APIRouter, Depends, HTTPException, Query

from entrypoints.dependencies import get_authenticated_user, get_uow
from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.schemas.user_schema import UserSchema
from application.schemas.music_schemas import (
    PostAlbumSchema,
    AlbumSchema,
    AlbumSummarySchema,
    PatchAlbumSchema,
    PostPlaylistSchema,
    PlaylistSchema,
    PlaylistSummarySchema,
    PatchPlaylistSchema,
    OrderTracksSchema,
    SearchResponseSchema,
)
from application.services.music_service import MusicService
from application.exceptions import ApplicationError

router = APIRouter(prefix="/music", tags=["music"])


@router.get("/search", response_model=SearchResponseSchema)
async def search(
    q: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> SearchResponseSchema:
    async with uow:
        try:
            return await MusicService(uow).search(query=q, limit=limit, offset=offset)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e

@router.get("/albums", response_model=list[AlbumSummarySchema])
async def list_albums(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    owner_id: int | None = Query(default=None, ge=1),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[AlbumSummarySchema]:
    async with uow:
        return await MusicService(uow).list_albums(limit=limit, offset=offset, owner_id=owner_id)


@router.get("/albums/{album_id}", response_model=AlbumSummarySchema)
async def get_album(
    album_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> AlbumSummarySchema:
    async with uow:
        try:
            return await MusicService(uow).get_album(album_id)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.patch("/albums/{album_id}", response_model=AlbumSummarySchema)
async def patch_album(
    album_id: int,
    dto: PatchAlbumSchema,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> AlbumSummarySchema:
    async with uow:
        try:
            return await MusicService(uow).patch_album(user=user, album_id=album_id, title=dto.title)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/users/{user_id}/albums", response_model=list[AlbumSummarySchema])
async def list_user_albums(
    user_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[AlbumSummarySchema]:
    async with uow:
        return await MusicService(uow).list_albums(limit=limit, offset=offset, owner_id=user_id)


@router.get("/playlists/{playlist_id}", response_model=PlaylistSchema)
async def get_playlist(
    playlist_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> PlaylistSchema:
    async with uow:
        try:
            return await MusicService(uow).get_playlist(user=user, playlist_id=playlist_id)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/me/albums", response_model=list[AlbumSummarySchema])
async def list_my_albums(
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[AlbumSummarySchema]:
    async with uow:
        return await MusicService(uow).list_my_albums(user)


@router.get("/me/playlists", response_model=list[PlaylistSummarySchema])
async def list_my_playlists(
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[PlaylistSummarySchema]:
    async with uow:
        return await MusicService(uow).list_my_playlists(user)


@router.post("/albums", response_model=AlbumSchema)
async def create_album(
    album_dto: PostAlbumSchema,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> AlbumSchema:
    async with uow:
        return await MusicService(uow).create_album(user, album_dto)


@router.patch("/albums/{album_id}/order", response_model=AlbumSchema)
async def set_album_track_order(
    album_id: int,
    dto: OrderTracksSchema,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> AlbumSchema:
    async with uow:
        try:
            return await MusicService(uow).set_album_track_order(
                user=user,
                album_id=album_id,
                ordered_track_ids=[int(tid) for tid in dto.track_ids],
            )
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.delete("/albums/{album_id}")
async def delete_album(
    album_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> bool:
    async with uow:
        try:
            return await MusicService(uow).delete_album(user=user, album_id=album_id)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.post("/playlists", response_model=PlaylistSchema)
async def create_playlist(
    playlist_dto: PostPlaylistSchema,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> PlaylistSchema:
    async with uow:
        return await MusicService(uow).create_playlist(user, playlist_dto)


@router.patch("/playlists/{playlist_id}/order", response_model=PlaylistSchema)
async def set_playlist_track_order(
    playlist_id: int,
    dto: OrderTracksSchema,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> PlaylistSchema:
    async with uow:
        try:
            return await MusicService(uow).set_playlist_track_order(
                user=user,
                playlist_id=playlist_id,
                ordered_track_ids=[int(tid) for tid in dto.track_ids],
            )
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.patch("/playlists/{playlist_id}", response_model=PlaylistSummarySchema)
async def patch_playlist(
    playlist_id: int,
    dto: PatchPlaylistSchema,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> PlaylistSummarySchema:
    async with uow:
        try:
            return await MusicService(uow).patch_playlist(
                user=user,
                playlist_id=playlist_id,
                title=dto.title,
            )
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.delete("/playlists/{playlist_id}")
async def delete_playlist(
    playlist_id: int,
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> bool:
    async with uow:
        try:
            return await MusicService(uow).delete_playlist(user=user, playlist_id=playlist_id)
        except ApplicationError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail) from e


