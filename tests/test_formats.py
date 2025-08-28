from fastapi.testclient import TestClient


def test_get_formats(client: TestClient):
    response = client.get("/api/v1/formats")
    assert response.status_code == 200
    assert "resizing" in response.json()
    assert "repurposing" in response.json()
