from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_trend_missing_messages_returns_422():
    response = client.post(
        "/analyze-chat-trend",
        json={
            "language": "he"
        }
    )

    assert response.status_code == 422
