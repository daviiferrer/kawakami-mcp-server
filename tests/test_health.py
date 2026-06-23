from starlette.testclient import TestClient

from src.server import create_mcp


def test_health_endpoint_reports_process_readiness():
    app = create_mcp().streamable_http_app()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
