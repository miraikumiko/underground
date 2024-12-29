import re
import asyncio
import pytest

SHORT_PASSWORD="ab12"
LONG_PASSWORD="abcd1234"


@pytest.mark.asyncio(loop_scope="session")
async def test_register(http_client) -> None:
    response = await http_client.get("/register")
    match = re.search(r'value="(\d+)"', response.text)

    assert match

    captcha_id = match.group(1)

    await asyncio.sleep(2)

    response = await http_client.post("/api/auth/register", data={
        "password1": SHORT_PASSWORD, "password2": SHORT_PASSWORD, "captcha_id": captcha_id
    })

    assert response.status_code == 400

    await asyncio.sleep(2)

    response = await http_client.post("/api/auth/register", data={
        "password1": LONG_PASSWORD, "password2": LONG_PASSWORD, "captcha_id": captcha_id
    })

    http_client.cookies.clear()

    assert response.status_code in (301, 409)


@pytest.mark.asyncio(loop_scope="session")
async def test_login(http_client) -> None:
    response = await http_client.get("/login")
    match = re.search(r'value="(\d+)"', response.text)

    assert match

    captcha_id = match.group(1)

    await asyncio.sleep(2)

    response = await http_client.post("/api/auth/login", data={
        "password": LONG_PASSWORD, "captcha_id": captcha_id
    })

    http_client.cookies.clear()

    assert response.status_code == 301


@pytest.mark.asyncio(loop_scope="session")
async def test_logout(http_client) -> None:
    response = await http_client.get("/login")
    match = re.search(r'value="(\d+)"', response.text)

    assert match

    captcha_id = match.group(1)

    await asyncio.sleep(2)

    response = await http_client.post("/api/auth/login", data={
        "password": LONG_PASSWORD, "captcha_id": captcha_id
    })

    assert response.status_code == 301

    response = await http_client.post("/api/auth/logout")

    assert response.status_code == 301
