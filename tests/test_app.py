"""
Tests for the Mergington High School API backend.

Uses FastAPI TestClient and pytest with Arrange-Act-Assert structure.
"""

import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset in-memory activity state before each test."""
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


@pytest.fixture
def client():
    """Provide a FastAPI TestClient for each test."""
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_200_and_activity_data(self, client):
        # Arrange
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 12


class TestSignupForActivity:
    def test_signup_new_participant_adds_participant(self, client):
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]

    def test_signup_existing_email_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    def test_remove_participant_successfully_deletes(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        assert email in activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants/{quote(email)}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]

    def test_remove_missing_participant_returns_404(self, client):
        # Arrange
        activity_name = "Basketball Team"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants/{quote(email)}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants/{quote(email)}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
