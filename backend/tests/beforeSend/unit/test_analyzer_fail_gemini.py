from app.ai.analyzer import analyze_before_send

def test_pressure_word_without_gemini(monkeypatch):
    monkeypatch.setattr(
        "app.ai.analyzer.generate_structured_json",
        lambda *args, **kwargs: {"error": "NO_API_KEY"}
    )

    res = analyze_before_send(
        subject="ASAP",
        body="Please respond ASAP, you didn't respond to my last message",
        language="en",
        is_reply=False,
        thread_context=None,
    )

    assert res["risk_level"] in ("medium", "high")
    assert res["send_decision"] != "send_as_is"
    assert res["analysis_layer"] == "gemini_failed"
    assert res["ai_ok"] is False
