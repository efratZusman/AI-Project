from app.ai.analyzer_chat_trend import analyze_chat_trend


def test_chat_trend_without_gemini(monkeypatch):
    # מכריחים כשל Gemini
    monkeypatch.setattr(
        "app.ai.analyzer_chat_trend.generate_structured_json",
        lambda *args, **kwargs: {"error": "NO_API_KEY"}
    )

    res = analyze_chat_trend(
        messages=[
            "זה כבר מתחיל להיות מתסכל",
            "ההתנהלות הזו לא נראית תקינה בכלל"
        ],
        language="he"
    )

    assert res["ai_ok"] is False
    assert res["risk_level"] == "low"
    assert res["warning_text"] == ""
