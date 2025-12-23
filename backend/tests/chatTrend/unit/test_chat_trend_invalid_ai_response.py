from app.ai.analyzer_chat_trend import analyze_chat_trend


def test_chat_trend_invalid_ai_response(monkeypatch):
    monkeypatch.setattr(
        "app.ai.analyzer_chat_trend.generate_structured_json",
        lambda *args, **kwargs: "שלום אני לא JSON"
    )

    res = analyze_chat_trend(
        messages=["בדיקה פשוטה"],
        language="he"
    )

    assert res["ai_ok"] is False
    assert res["risk_level"] == "low"
    assert res["warning_text"] == ""
