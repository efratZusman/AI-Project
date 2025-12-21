from app.ai.analyzer import analyze_before_send


def test_empty_body_does_not_crash():
    res = analyze_before_send(
        subject="Ping",
        body="",
        language="en",
        is_reply=False,
        thread_context=None,
    )

    assert "risk_level" in res
    assert "send_decision" in res
    assert res["ai_ok"] is True
