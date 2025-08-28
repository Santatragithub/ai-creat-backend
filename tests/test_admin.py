from fastapi.testclient import TestClient


def test_admin_platforms(client: TestClient):
    # List platforms
    resp = client.get("/api/v1/admin/platforms")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_admin_formats(client: TestClient):
    # List formats
    resp = client.get("/api/v1/admin/formats")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_admin_rules(client: TestClient):
    # Get adaptation rules
    resp = client.get("/api/v1/admin/rules/adaptation")
    assert resp.status_code == 200
    assert "focalPointLogic" in resp.json()
