import pytest
from fastapi.testclient import TestClient


def test_get_activities(client):
    """Test GET /activities returns all activities with correct structure"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    # Verify activities are returned
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Verify Chess Club exists (known activity)
    assert "Chess Club" in activities
    
    # Verify activity structure
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity(client):
    """Test POST /activities/{activity_name}/signup successfully registers a student"""
    email = "test_student@mergington.edu"
    activity = "Chess Club"
    
    # Get initial participant count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity]["participants"])
    
    # Sign up for activity
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity in result["message"]
    
    # Verify participant was added
    updated_response = client.get("/activities")
    updated_count = len(updated_response.json()[activity]["participants"])
    assert updated_count == initial_count + 1
    assert email in updated_response.json()[activity]["participants"]


def test_remove_participant(client):
    """Test DELETE /activities/{activity_name}/signup/{email} removes participant"""
    # First, sign up a student
    email = "remove_test@mergington.edu"
    activity = "Programming Class"
    
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Verify they were added
    verify_response = client.get("/activities")
    assert email in verify_response.json()[activity]["participants"]
    initial_count = len(verify_response.json()[activity]["participants"])
    
    # Remove the participant
    delete_response = client.delete(
        f"/activities/{activity}/signup/{email}"
    )
    
    assert delete_response.status_code == 200
    result = delete_response.json()
    assert "message" in result
    
    # Verify participant was removed
    final_response = client.get("/activities")
    final_count = len(final_response.json()[activity]["participants"])
    assert final_count == initial_count - 1
    assert email not in final_response.json()[activity]["participants"]


def test_root_redirect(client):
    """Test GET / redirects to static index page"""
    response = client.get("/", follow_redirects=False)
    
    # Should be a redirect (307)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_activity_structure_consistency(client):
    """Test all activities have consistent structure"""
    response = client.get("/activities")
    activities = response.json()
    
    required_fields = ["description", "schedule", "max_participants", "participants"]
    
    for activity_name, activity_data in activities.items():
        # Verify all required fields exist
        for field in required_fields:
            assert field in activity_data, f"{activity_name} missing {field}"
        
        # Verify field types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
        
        # Verify participants are emails (strings)
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
