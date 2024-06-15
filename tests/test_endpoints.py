import pytest


@pytest.mark.asyncio
async def test_get_prices(client):
    response = await client.get("/payment/prices")

    assert response.status_code == 200
