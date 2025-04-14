from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from .config import settings

DATABASE_URI = str(settings.SQLALCHEMY_DATABASE_URI)

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_size=100,
    max_overflow=50,
    pool_pre_ping=True,
)


async def get_connection() -> AsyncConnection:
    conn = await engine.connect()
    return conn
