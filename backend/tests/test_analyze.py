from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_endpoint():
    payload = {
        "subject": "Test",
        "body": "Please respond ASAP"
    }

    response = client.post("/analyze-before-send", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "risk_level" in data
    assert "intent" in data


