from app.ai.analyzer import analyze_before_send

def test_pressure_word_without_gemini(monkeypatch):
    # מדמים ש-Gemini לא קיים
    monkeypatch.setenv("GEMINI_API_KEY", "")

    res = analyze_before_send(
        subject="ASAP",
        body="Please respond ASAP",
        language="en",
        is_reply=False,
        thread_context=None,
    )

    assert res["risk_level"] in ("medium", "high")
    assert res["send_decision"] != "send_as_is"
    assert res["ai_ok"] is False
    assert res["analysis_layer"] in ("lexicon", "lexicon_only", "gemini_failed")
    assert res["safer_body"] == "Please respond ASAP"
    assert res["notes_for_sender"]
