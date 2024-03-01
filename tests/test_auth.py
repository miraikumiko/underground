from conftest import client


async def test_register():
    response = client.post("http://test/api/auth/register", json={
        "email": "test@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })

    assert response.status_code == 201
