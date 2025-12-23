from app.ai.analyzer import analyze_before_send


def test_very_long_text_forces_gemini(monkeypatch):
    long_body = "Please review. " * 200  # טקסט ארוך מאוד

    monkeypatch.setattr(
        "app.ai.analyzer.generate_structured_json",
        lambda *args, **kwargs: {
            "risk_level": "medium",
            "send_decision": "rewrite_recommended",
            "safer_body": "Shorter rewritten message",
        }
    )

    res = analyze_before_send(
        subject="Long message",
        body=long_body,
        language="en",
        is_reply=False,
        thread_context=None,
    )

    assert res["analysis_layer"] == "gemini"
    assert res["send_decision"] == "rewrite_recommended"
    assert res["ai_ok"] is True
