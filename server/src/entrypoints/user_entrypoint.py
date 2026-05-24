from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.exceptions import ApplicationError
from application.schemas.user_schema import UserSchema, UserMeSchema, UserPublicSchema
from application.services.user_service import UserService
from entrypoints.dependencies import get_authenticated_user, get_uow

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserMeSchema)
async def get_me(
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    try:
        return await UserService(uow).get_me(user)
    except ApplicationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.post("/me/avatar", response_model=UserMeSchema)
async def upload_avatar(
    file: UploadFile = File(...),
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    content = await file.read()
    try:
        return await UserService(uow).update_avatar(user, content, file.filename)
    except ApplicationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/test", status_code=200)
async def user_test(
    user: UserSchema = Depends(get_authenticated_user),
):
    return f"pass!. USER_ID = {user.id}"


@router.get("/{user_id}", response_model=UserPublicSchema)
async def get_user_public(
    user_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    try:
        return await UserService(uow).get_public_profile(user_id)
    except ApplicationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e
