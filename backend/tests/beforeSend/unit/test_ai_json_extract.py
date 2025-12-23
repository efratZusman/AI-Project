# tests/unit/test_ai_json_extract.py

from app.ai.ai import _extract_json


def test_extract_json_valid():
    raw = '{"risk_level": "low", "intent": "professional"}'
    result = _extract_json(raw)

    assert result["risk_level"] == "low"
    assert result["intent"] == "professional"


def test_extract_json_embedded_in_text():
    raw = """
    Sure! Here is the analysis you requested:
    {
        "risk_level": "medium",
        "intent": "pressure detected"
    }
    Let me know if you need anything else.
    """

    result = _extract_json(raw)

    assert result["risk_level"] == "medium"
    assert result["intent"] == "pressure detected"


def test_extract_json_no_json():
    raw = "This is not JSON at all"

    result = _extract_json(raw)

    assert "error" in result
    assert result["error"] in ("NO_JSON", "JSON_PARSE_FAILED")


def test_extract_json_empty_string():
    raw = ""

    result = _extract_json(raw)

    assert result["error"] == "EMPTY_RESPONSE"
