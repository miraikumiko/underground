import asyncio
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models import Base


@pytest.fixture(scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def asyncio_loop(request):
    with asyncio.get_event_loop_policy().new_event_loop() as loop:
        yield loop


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(base_url="http://test/api", transport=ASGITransport(app)) as client:
        yield client
