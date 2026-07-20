from pathlib import Path


def test_env_example_contains_no_real_secrets():
    content = (Path(__file__).parents[1] / ".env.example").read_text(encoding="utf-8")
    assert "re_" not in content
    assert "change-me" in content


def test_security_headers(client):
    response = client.get("/conoceme")
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_healthcheck_uses_database_repository(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
