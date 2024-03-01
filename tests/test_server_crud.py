from conftest import client


async def test_crud_create_server():
    response = client.post("http://test/api/server/create", json={
        "cores": 1,
        "ram": 1024,
        "disk_type": "ssd",
        "disk_size": 25,
        "traffic": 1,
        "location": "Spain",
        "avaible": True,
        "price": 5
    })

    assert response.status_code == 201
