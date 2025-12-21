from app.ai.analyzer import analyze_before_send


def test_analyze_before_send_is_consistent_on_core_fields():
    args = dict(
        subject="ASAP",
        body="Please respond ASAP",
        language="en",
        is_reply=False,
        thread_context=None,
    )

    result_1 = analyze_before_send(**args)
    result_2 = analyze_before_send(**args)

    # בודקים רק שדות דטרמיניסטיים
    assert result_1["risk_level"] == result_2["risk_level"]
    assert result_1["send_decision"] == result_2["send_decision"]
    assert result_1["analysis_layer"] == result_2["analysis_layer"]
