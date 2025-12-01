from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config.settings import settings


engine = create_async_engine(
    settings.postgres_url,
    isolation_level="REPEATABLE READ",
    echo=settings.POSTGRES_ECHO,
)

session_factory = async_sessionmaker(bind=engine)
