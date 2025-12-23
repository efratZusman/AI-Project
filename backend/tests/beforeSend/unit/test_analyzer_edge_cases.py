from app.ai.analyzer import analyze_before_send


def test_empty_body_does_not_crash():
    res = analyze_before_send(
        subject="Ping",
        body="",
        language="en",
        is_reply=False,
        thread_context=None,
    )

    assert res["risk_level"] == "low"
    assert res["send_decision"] == "send_as_is"
    assert res["analysis_layer"] == "local_scoring"
    assert res["ai_ok"] is True
