from app.ai.analyzer_chat_trend import analyze_chat_trend


def test_chat_trend_valid_ai_response(monkeypatch):
    monkeypatch.setattr(
        "app.ai.analyzer_chat_trend.generate_structured_json",
        lambda *args, **kwargs: {
            "risk_level": "high",
            "warning_text": "רצף ההודעות נשמע מתוח ועלול להיתפס כהסלמה."
        }
    )

    res = analyze_chat_trend(
        messages=[
            "כבר כמה פעמים שפניתי",
            "זה מתחיל להיות מאוד לא נעים"
        ],
        language="he"
    )

    assert res["ai_ok"] is True
    assert res["risk_level"] == "high"
    assert res["warning_text"]
