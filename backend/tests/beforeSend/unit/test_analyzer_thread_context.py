from app.ai.analyzer import analyze_before_send
from app.models import ThreadMessage


def test_thread_context_forces_gemini(monkeypatch):
    # Gemini מחזיר החלטה
    monkeypatch.setattr(
        "app.ai.analyzer.generate_structured_json",
        lambda *args, **kwargs: {
            "risk_level": "medium",
            "send_decision": "rewrite_recommended",
            "safer_body": "Rewritten message",
        }
    )

    thread = [
        ThreadMessage(author="me", text="Ping"),
        ThreadMessage(author="me", text="Following up"),
        ThreadMessage(author="me", text="Any update?"),
    ]

    res = analyze_before_send(
        subject="Update?",
        body="Please respond ASAP",
        language="en",
        is_reply=True,
        thread_context=thread,
    )

    assert res["analysis_layer"] == "gemini"
    assert res["send_decision"] == "rewrite_recommended"
    assert res["ai_ok"] is True
