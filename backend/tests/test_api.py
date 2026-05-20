def test_health_check(client):
    """Test that the /health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data

def test_metrics_endpoint(client):
    """Test that Prometheus metrics are correctly exposed."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "rag_request_count_total" in response.text
