from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_trend_ai_failure(monkeypatch):
    monkeypatch.setattr(
        "app.ai.analyzer_chat_trend.generate_structured_json",
        lambda *args, **kwargs: {"error": "TIMEOUT"}
    )

    response = client.post(
        "/analyze-chat-trend",
        json={
            "messages": [
                "בדיקה",
                "עוד בדיקה"
            ],
            "language": "he"
        }
    )

    data = response.json()

    assert data["ai_ok"] is False
    assert data["risk_level"] == "low"
