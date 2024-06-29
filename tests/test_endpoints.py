import pytest


@pytest.mark.asyncio
async def test_get_course(client):
    response = await client.get("/payment/course")

    assert response.status_code == 200
