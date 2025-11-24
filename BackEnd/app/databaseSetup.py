from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from .config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings
from typing import AsyncGenerator

engine=create_async_engine(settings.database_url,echo= settings.echo_sql)

Base =declarative_base()
try:
     AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

except SQLAlchemyError as e:
    raise RuntimeError(f"Database connection failed ",{str(e)})



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:  
            yield session
        finally:
            await session.close()
