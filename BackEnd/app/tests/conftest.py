import pytest
import shutil
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.main import app
from app.databaseSetup import get_db


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog_test.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)

TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


TEST_DB_PATH = "./blog_test.db"
TEST_DB_BACKUP = "./blog_test_backup.db"

@pytest.fixture(scope="session", autouse=True)
def backup_restore_db():
    # Backup DB before tests
    if os.path.exists(TEST_DB_PATH):
        shutil.copy(TEST_DB_PATH, TEST_DB_BACKUP)
    yield
    # Restore DB after tests
    if os.path.exists(TEST_DB_BACKUP):
        shutil.copy(TEST_DB_BACKUP, TEST_DB_PATH)
        os.remove(TEST_DB_BACKUP)


@pytest.fixture(scope="session", autouse=True)
def disable_rate_limit():
    if hasattr(app.state, "limiter"):
        app.state.limiter.enabled = False


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback() 
