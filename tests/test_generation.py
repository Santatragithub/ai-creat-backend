import io
from fastapi.testclient import TestClient


def test_generate_flow(client: TestClient):
    # Step 1: Upload a project with one file
    files = [("files", ("test.png", io.BytesIO(b"fake image data"), "image/png"))]
    resp = client.post("/api/v1/projects/upload", data={"projectName": "Gen Project"}, files=files)
    assert resp.status_code == 202
    project_id = resp.json()["projectId"]

    # Step 2: Trigger generation
    gen_resp = client.post(
        "/api/v1/generate",
        json={"projectId": project_id, "formatIds": [], "customResizes": []},
    )
    assert gen_resp.status_code == 202
    job_id = gen_resp.json()["jobId"]

    # Step 3: Poll status
    status_resp = client.get(f"/api/v1/generate/{job_id}/status")
    assert status_resp.status_code == 200
    assert "status" in status_resp.json()
