from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_analyze_endpoint_missing_body_returns_422():
    response = client.post(
        "/analyze-before-send",
        json={
            "subject": "Hello",
            "language": "en",
            "is_reply": False,
        },
    )

    assert response.status_code == 422
