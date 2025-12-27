from fastapi import APIRouter, Depends

from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.schemas.user_schema import PostUserSchema
from application.schemas.auth_schema import LoginSchema, RefreshTokenSchema
from application.services.auth_service import AuthService
from entrypoints.dependencies import get_uow

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registration", status_code=201)
async def registration(
    user_dto: PostUserSchema,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    return await AuthService(uow).registration(user_dto)


@router.post("/login", status_code=200)
async def login(
    user_dto: LoginSchema,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    return await AuthService(uow).login(user_dto)


@router.post("/refresh", status_code=200)
async def refresh(
    token_dto: RefreshTokenSchema,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)
):
    return await AuthService(uow).refresh(token_dto.refresh_token)
