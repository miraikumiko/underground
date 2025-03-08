import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_display_index(http_client) -> None:
    response = await http_client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_display_login(http_client) -> None:
    response = await http_client.get("/login")
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_display_register(http_client) -> None:
    response = await http_client.get("/register")
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_display_dashboard(http_client) -> None:
    response = await http_client.get("/dashboard")
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_display_promo(http_client) -> None:
    response = await http_client.get("/promo")
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_display_install(http_client) -> None:
    response = await http_client.get("/install/abc")
    assert response.status_code == 404

    response = await http_client.get("/install/123")
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_display_vnc(http_client) -> None:
    response = await http_client.get("/vnc/abc")
    assert response.status_code == 404

    response = await http_client.get("/vnc/123")
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_display_upgrade(http_client) -> None:
    response = await http_client.get("/upgrademenu/abc")
    assert response.status_code == 404

    response = await http_client.get("/upgrademenu/123")
    assert response.status_code == 403
