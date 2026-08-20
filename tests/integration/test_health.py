def test_health_endpoint(client, app_url):
    resp = client.get(f"{app_url}/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "services": {"database": "up"}}

def test_health_endpoint(client, app_url):
    resp = client.get(f"{app_url}/api/billing/check")

    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
