from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_endpoint_basic(monkeypatch):
    # מדמים תשובה של Gemini (קובע סופית)
    def fake_generate(prompt, schema):
        return {
            "intent": "Professional reminder",
            "risk_level": "medium",
            "risk_factors": ["Pressure"],
            "recipient_interpretation": "Might feel pressured",
            "send_decision": "rewrite_recommended",
            "follow_up_needed": False,
            "follow_up_reason": "",
            "safer_subject": None,
            "safer_body": "Could you please update me when you have a moment?",
            "notes_for_sender": [],
        }

    monkeypatch.setattr(
        "app.ai.analyzer.generate_structured_json",
        fake_generate
    )

    payload = {
        "subject": "ASAP",
        "body": "Please respond ASAP, you didn't respond to my last message",
        "language": "en",
        "is_reply": False,
        "thread_context": None,
    }

    response = client.post("/analyze-before-send", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["risk_level"] == "medium"
    assert data["send_decision"] == "rewrite_recommended"
    assert data["analysis_layer"] == "gemini"
    assert data["ai_ok"] is True
    assert "safer_body" in data
