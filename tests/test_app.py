from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities_returns_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_adds_participant():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Verify the participant was added
    activity_response = client.get("/activities")
    participants = activity_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_duplicate_returns_400():
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"

    first_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert first_response.status_code == 200

    duplicate_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_existing_participant():
    activity_name = "Gym Class"
    email = "removeme@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_response.status_code == 200

    delete_response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity_name}"

    activity_response = client.get("/activities")
    participants = activity_response.json()[activity_name]["participants"]
    assert email not in participants


def test_remove_missing_participant_returns_404():
    activity_name = "Art Studio"
    email = "doesnotexist@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
