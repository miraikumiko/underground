import pytest
from src.database import r


@pytest.mark.asyncio
async def test_register(client):
    captcha_id = 0
    captcha_text = "test"

    await r.set(f"captcha:{captcha_id}", captcha_text, ex=60)

    response = await client.post("/auth/register", json={
        "username": "test",
        "password": "test",
        "captcha_id": captcha_id,
        "captcha_text": captcha_text
    })

    assert response.status_code == 201
