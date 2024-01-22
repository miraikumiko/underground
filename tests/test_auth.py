from conftest import client


async def test_register():
    response = client.post("/api/auth/register", json={
        "email": "string",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    
    assert response.status_code == 201
