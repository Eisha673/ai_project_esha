import os

import pytest_asyncio

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from api.database import Base, get_engine
from api import models  # noqa: F401, E402


@pytest_asyncio.fixture(autouse=True)
async def reset_test_db():
    engine = get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield
