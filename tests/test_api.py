from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Expect some known activities from the in-memory fixture
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure the test email is not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    assert email not in participants

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Signing up again should fail (already registered)
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # Confirm participant appears in activities
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Unregistering again should return a 400 (not registered)
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 400

    # Confirm participant removed
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email not in participants
