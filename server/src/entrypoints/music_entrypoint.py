from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    Query,
    status,
)

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
    PostTrackSchema,
    TrackSchema,
)
from application.services.music_service import MusicService
from application.exceptions import ApplicationError

router = APIRouter(prefix="/music", tags=["music"])


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


@router.get("/tracks/popular", response_model=list[TrackSchema])
async def list_popular_tracks(
    limit: int = Query(default=50, ge=1, le=100),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[TrackSchema]:
    async with uow:
        return await MusicService(uow).list_popular_tracks(limit)


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
