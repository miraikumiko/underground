import pytest
from httpx import AsyncClient, ASGITransport
from src.config import HOST, PORT
from src.main import app


@pytest.fixture(scope="session")
async def http_client():
    async with AsyncClient(transport=ASGITransport(app), base_url=f"http://{HOST}:{PORT}") as client:
        yield client
