from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)


def test_get_jobs():
    response = client.get("/jobs")
    print(response.json())

    assert response.status_code == 200
    assert isinstance(response.json(), list)




if __name__ == "__main__":
    test_get_jobs()