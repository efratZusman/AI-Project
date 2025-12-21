from app.ai.analyzer import analyze_before_send

def test_pressure_word_triggers_gemini_when_available(monkeypatch):
    # mock לפונקציה של Gemini
    def fake_gemini(prompt, schema):
        return {
            "intent": "Pressure detected",
            "risk_level": "medium",
            "risk_factors": ["Pressure"],
            "recipient_interpretation": "May feel pressured",
            "send_decision": "rewrite_recommended",
            "follow_up_needed": False,
            "follow_up_reason": "",
            "safer_subject": None,
            "safer_body": "Could you please respond when you have a moment?",
            "notes_for_sender": ["Tone softened"],
        }

    monkeypatch.setattr(
        "app.ai.analyzer.generate_structured_json",
        fake_gemini
    )

    res = analyze_before_send(
        subject="ASAP",
        body="Please respond ASAP",
        language="en",
        is_reply=False,
        thread_context=None,
    )

    assert res["analysis_layer"] == "gemini"
    assert res["ai_ok"] is True
    assert res["risk_level"] == "medium"
    assert res["send_decision"] == "rewrite_recommended"
    assert res["safer_body"].startswith("Could you please")
