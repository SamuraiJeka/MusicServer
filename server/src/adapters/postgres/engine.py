from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator, Any

from config.settings import settings


engine = create_async_engine(
    settings.postgres_url,
    isolation_level="REPEATABLE READ",
    echo=settings.POSTGRES_ECHO,
)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
