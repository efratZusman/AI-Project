from app.ai.analyzer import analyze_before_send

def test_clean_message_skips_gemini():
    res = analyze_before_send(
        subject="Hello",
        body="Thank you for the update, sounds good.",
        language="en",
        is_reply=False,
        thread_context=None,
    )

    assert res["risk_level"] == "low"
    assert res["send_decision"] == "send_as_is"
    assert res["analysis_layer"] == "local_scoring"
    assert res["ai_ok"] is True
    assert res["safer_body"] == "Thank you for the update, sounds good."
