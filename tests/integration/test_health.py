def test_health_endpoint(client, app_url):
    resp = client.get(f"{app_url}/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "services": {"database": "up"}}
