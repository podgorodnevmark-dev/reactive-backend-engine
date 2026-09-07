from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = "postgresql+asyncpg://user:1234@localhost:5432/cyberware_db"

async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

class Base (DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
               await session.rollback()
               raise
