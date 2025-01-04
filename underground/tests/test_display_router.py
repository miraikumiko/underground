import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_index_display(http_client) -> None:
    response = await http_client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_login_display(http_client) -> None:
    response = await http_client.get("/login")
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_register_display(http_client) -> None:
    response = await http_client.get("/register")
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_dashboard_display(http_client) -> None:
    response = await http_client.get("/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_promo_display(http_client) -> None:
    response = await http_client.get("/promo")
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_install_display(http_client) -> None:
    response = await http_client.get("/install/abc")
    assert response.status_code == 404

    response = await http_client.get("/install/123")
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_vnc_display(http_client) -> None:
    response = await http_client.get("/vnc/abc")
    assert response.status_code == 404

    response = await http_client.get("/vnc/123")
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_upgrademenu_display(http_client) -> None:
    response = await http_client.get("/upgrademenu/abc")
    assert response.status_code == 404

    response = await http_client.get("/upgrademenu/123")
    assert response.status_code == 401
