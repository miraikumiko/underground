import pytest
from httpx import AsyncClient, ASGITransport
from src.config import HOST, PORT
from src.main import app


@pytest.fixture(scope="session")
async def http_client():
    async with AsyncClient(transport=ASGITransport(app), base_url=f"http://{HOST}:{PORT}") as client:
        yield client


@pytest.mark.asyncio(loop_scope="session")
async def test_index_display(http_client) -> None:
    r = await http_client.get("/")
    assert r.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_login_display(http_client) -> None:
    r = await http_client.get("/login")
    assert r.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_register_display(http_client) -> None:
    r = await http_client.get("/register")
    assert r.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_dashboard_display(http_client) -> None:
    r = await http_client.get("/dashboard")
    assert r.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_promo_display(http_client) -> None:
    r = await http_client.get("/promo")
    assert r.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_install_display(http_client) -> None:
    r = await http_client.get("/install/1")
    assert r.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_vnc_display(http_client) -> None:
    r = await http_client.get("/vnc/1")
    assert r.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_buy_display(http_client) -> None:
    r = await http_client.get("/buy/1")
    assert r.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_pay_display(http_client) -> None:
    r = await http_client.get("/pay/1")
    assert r.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_upgrademenu_display(http_client) -> None:
    r = await http_client.get("/upgrademenu/1")
    assert r.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_upgrade_display(http_client) -> None:
    r = await http_client.get("/upgrade/1")
    assert r.status_code == 401
