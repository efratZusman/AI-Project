from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_trend_success_response(monkeypatch):
    monkeypatch.setattr(
        "app.ai.analyzer_chat_trend.generate_structured_json",
        lambda *args, **kwargs: {
            "risk_level": "medium",
            "warning_text": "הטון הכללי של ההודעות נשמע כבד ועלול להיתפס כלחוץ."
        }
    )

    response = client.post(
        "/analyze-chat-trend",
        json={
            "messages": [
                "רק רציתי לבדוק מה הסטטוס",
                "עבר כבר זמן ולא קיבלתי מענה"
            ],
            "language": "he"
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["ai_ok"] is True
    assert data["risk_level"] == "medium"
    assert data["warning_text"]
