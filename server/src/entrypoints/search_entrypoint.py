from fastapi import APIRouter, Depends, HTTPException, Query

from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork
from application.exceptions import ApplicationError
from application.schemas.search_schemas import GlobalSearchResponseSchema, MessengerUserSchema
from application.schemas.user_schema import UserSchema
from application.services.search_service import SearchService
from entrypoints.dependencies import get_authenticated_user, get_uow

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/global", response_model=GlobalSearchResponseSchema)
async def global_search(
    q: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GlobalSearchResponseSchema:
    try:
        return await SearchService(uow).global_search(query=q, limit=limit, offset=offset)
    except ApplicationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e


@router.get("/messenger/users", response_model=list[MessengerUserSchema])
async def search_messenger_users(
    q: str = Query(default="", max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: UserSchema = Depends(get_authenticated_user),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> list[MessengerUserSchema]:
    try:
        return await SearchService(uow).messenger_user_search(user=user, query=q, limit=limit, offset=offset)
    except ApplicationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) from e
