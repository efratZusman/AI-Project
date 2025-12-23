from app.ai.analyzer import analyze_before_send


def test_language_is_detected_as_hebrew_when_text_contains_hebrew():
    res = analyze_before_send(
        subject=None,
        body="זה טקסט בעברית",
        language="auto",
        is_reply=False,
        thread_context=None,
    )

    # אם עברית זוהתה – ההודעה הבסיסית בעברית
    assert res["intent"].startswith("העברת")
    assert res["risk_level"] == "low"
    assert res["analysis_layer"] == "local_scoring"
    assert res["ai_ok"] is True


def test_language_is_detected_as_english_when_text_is_english():
    res = analyze_before_send(
        subject=None,
        body="This is a simple English message",
        language="auto",
        is_reply=False,
        thread_context=None,
    )

    assert res["intent"].startswith("Professional")
    assert res["risk_level"] == "low"
    assert res["analysis_layer"] == "local_scoring"
    assert res["ai_ok"] is True
