import pytest

USERNAME="test"
SHORT_PASSWORD="ab12"
LONG_PASSWORD="abcd1234"


@pytest.mark.asyncio(loop_scope="session")
async def test_register(http_client) -> None:
    response = await http_client.post("/auth/register", data={
        "username": USERNAME,
        "password": SHORT_PASSWORD
    })

    assert response.status_code == 400

    response = await http_client.post("/auth/register", data={
        "username": USERNAME,
        "password": LONG_PASSWORD
    })

    http_client.cookies.clear()

    assert response.status_code in (301, 409)


@pytest.mark.asyncio(loop_scope="session")
async def test_login(http_client) -> None:
    response = await http_client.post("/auth/login", data={
        "username": USERNAME,
        "password": LONG_PASSWORD
    })

    http_client.cookies.clear()

    assert response.status_code == 301


@pytest.mark.asyncio(loop_scope="session")
async def test_logout(http_client) -> None:
    response = await http_client.post("/auth/login", data={
        "username": USERNAME,
        "password": LONG_PASSWORD
    })

    assert response.status_code == 301

    response = await http_client.post("/auth/logout")

    assert response.status_code == 301
