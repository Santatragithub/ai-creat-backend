import io
from fastapi.testclient import TestClient


def test_upload_and_status(client: TestClient):
    files = [
        ("files", ("test1.png", io.BytesIO(b"fake image data"), "image/png")),
        ("files", ("test2.png", io.BytesIO(b"fake image data"), "image/png")),
    ]
    response = client.post(
        "/api/v1/projects/upload",
        data={"projectName": "Test Project"},
        files=files,
    )
    assert response.status_code == 202
    project_id = response.json()["projectId"]

    status_resp = client.get(f"/api/v1/projects/{project_id}/status")
    assert status_resp.status_code == 200
    assert "status" in status_resp.json()
