from fastapi import APIRouter

from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.schemas.user_schema import PostUserSchema
from application.schemas.auth_schema import LoginSchema, RefreshTokenSchema
from application.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registration", status_code=201)
async def registration(user_dto: PostUserSchema):
    return await AuthService(SqlAlchemyUnitOfWork()).registration(user_dto)


@router.post("/login", status_code=200)
async def login(user_dto: LoginSchema):
    return await AuthService(SqlAlchemyUnitOfWork()).login(user_dto)


@router.post("/refresh", status_code=200)
async def refresh(token_dto: RefreshTokenSchema):
    return await AuthService(SqlAlchemyUnitOfWork()).refresh(token_dto.refresh_token)
