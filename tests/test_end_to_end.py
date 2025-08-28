import io
from fastapi.testclient import TestClient


def test_full_flow(client: TestClient):
    # 1. Login
    login_resp = client.post("/api/v1/auth/login", json={"username": "naomi", "password": "password123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload project with two files
    files = [
        ("files", ("test1.png", io.BytesIO(b"fake image data"), "image/png")),
        ("files", ("test2.png", io.BytesIO(b"fake image data"), "image/png")),
    ]
    upload_resp = client.post(
        "/api/v1/projects/upload",
        data={"projectName": "E2E Project"},
        files=files,
        headers=headers,
    )
    assert upload_resp.status_code == 202
    project_id = upload_resp.json()["projectId"]

    # 3. Poll project status
    status_resp = client.get(f"/api/v1/projects/{project_id}/status", headers=headers)
    assert status_resp.status_code == 200

    # 4. Get formats
    formats_resp = client.get("/api/v1/formats", headers=headers)
    assert formats_resp.status_code == 200

    # 5. Start generation
    gen_resp = client.post(
        "/api/v1/generate",
        json={"projectId": project_id, "formatIds": [], "customResizes": []},
        headers=headers,
    )
    assert gen_resp.status_code == 202
    job_id = gen_resp.json()["jobId"]

    # 6. Poll job status
    job_status_resp = client.get(f"/api/v1/generate/{job_id}/status", headers=headers)
    assert job_status_resp.status_code == 200

    # 7. Get job results
    job_results_resp = client.get(f"/api/v1/generate/{job_id}/results", headers=headers)
    assert job_results_resp.status_code == 200

    # 8. Apply manual edits (PUT /generated-assets/{id})
    # Fake asset id for flow demonstration
    fake_asset_id = "00000000-0000-0000-0000-000000000000"
    edit_resp = client.put(
        f"/api/v1/generated-assets/{fake_asset_id}",
        json={"edits": {"saturation": 1.2}},
        headers=headers,
    )
    assert edit_resp.status_code in [200, 404]

    # 9. Download assets
    download_resp = client.post(
        "/api/v1/download",
        json={"assetIds": [fake_asset_id], "format": "png", "quality": "high", "grouping": "individual"},
        headers=headers,
    )
    assert download_resp.status_code == 200
