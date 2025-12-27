from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.postgres.engine import get_session
from adapters.postgres.sql_uow import SqlAlchemyUnitOfWork


async def get_uow(
    session: AsyncSession = Depends(get_session),
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)
