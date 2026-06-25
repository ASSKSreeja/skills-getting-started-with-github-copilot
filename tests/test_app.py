import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all_activities():
    # Arrange
    expected_keys = {"Chess Club", "Programming Class", "Gym Class", "Soccer Team", "Basketball Club", "Drama Club", "Art Club", "Debate Team", "Science Olympiad"}

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert expected_keys.issubset(set(data.keys()))


def test_signup_adds_participant_and_returns_message():
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data == {"message": f"Signed up {email} for {activity_name}"}
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    data = response.json()

    # Assert
    assert response.status_code == 400
    assert data["detail"] == "Student already signed up for this activity"


def test_delete_removes_participant():
    # Arrange
    activity_name = "Gym Class"
    email = "remove@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    assert email in client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data == {"message": f"Removed {email} from {activity_name}"}
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_delete_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Drama Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    data = response.json()

    # Assert
    assert response.status_code == 404
    assert data["detail"] == "Student not signed up for this activity"
