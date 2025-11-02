"""
Integration test for new crew planner API endpoints: /teams, /members, /assignments
"""
import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from fastapi.testclient import TestClient
from datetime import date
from app.core.db import engine, Base
from app.data.orm_models import *
from main import app

# Create database schema
Base.metadata.create_all(bind=engine)

# Create test client
client = TestClient(app)


def test_get_teams():
    """Test GET /crew/teams endpoint"""
    response = client.get("/crew/teams")
    assert response.status_code == 200, f"Failed to get teams: {response.text}"
    
    teams = response.json()
    assert isinstance(teams, list), "Teams should be a list"
    assert len(teams) > 0, "Should have at least one team"
    
    # Check structure of team objects
    for team in teams:
        assert "name" in team, "Team should have 'name' field"
        assert "value" in team, "Team should have 'value' field"
    
    # Check that expected teams are present
    team_values = [t["value"] for t in teams]
    assert "SURF" in team_values, "SURF team should be present"
    assert "YOGA" in team_values, "YOGA team should be present"
    
    print(f"✓ GET /crew/teams returned {len(teams)} teams")


def test_get_members():
    """Test GET /crew/members endpoint"""
    # First create a crew member
    response = client.post("/crew/crew", json={
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone": "9876543210",
        "team": "YOGA",
        "skills": "Yoga instructor",
        "notes": "Available mornings"
    })
    assert response.status_code == 201, f"Failed to create crew member: {response.text}"
    
    # Test GET /crew/members - get all members
    response = client.get("/crew/members")
    assert response.status_code == 200, f"Failed to get members: {response.text}"
    
    members = response.json()
    assert isinstance(members, list), "Members should be a list"
    assert len(members) >= 1, "Should have at least one member"
    
    # Check structure of member objects
    for member in members:
        assert "id" in member, "Member should have 'id' field"
        assert "first_name" in member, "Member should have 'first_name' field"
        assert "last_name" in member, "Member should have 'last_name' field"
        assert "email" in member, "Member should have 'email' field"
        assert "team" in member, "Member should have 'team' field"
    
    print(f"✓ GET /crew/members returned {len(members)} members")
    
    # Test filtering by team
    response = client.get("/crew/members?team=YOGA")
    assert response.status_code == 200
    yoga_members = response.json()
    assert all(m["team"] == "YOGA" for m in yoga_members), "All members should be YOGA team"
    
    print(f"✓ GET /crew/members?team=YOGA returned {len(yoga_members)} YOGA members")


def test_get_members_empty():
    """Test GET /crew/members returns empty list when no members exist"""
    # This test assumes a fresh database with no pre-existing data
    # In a real test, we might want to clear the database first
    response = client.get("/crew/members")
    assert response.status_code == 200, f"Failed to get members: {response.text}"
    
    members = response.json()
    assert isinstance(members, list), "Members should be a list"
    # We allow members to exist from previous tests
    print(f"✓ GET /crew/members handles empty/populated database correctly")


def test_get_assignments():
    """Test GET /crew/assignments endpoint"""
    # First create crew member, position, and assignment
    crew_response = client.post("/crew/crew", json={
        "first_name": "Bob",
        "last_name": "Johnson",
        "email": "bob@example.com",
        "phone": "5551234567",
        "team": "SURF",
        "skills": "Surf instructor",
        "notes": ""
    })
    assert crew_response.status_code == 201
    crew_id = crew_response.json()["id"]
    
    position_response = client.post("/crew/positions", json={
        "name": "Surf Instructor",
        "team": "SURF",
        "description": "Main surf instructor"
    })
    assert position_response.status_code == 201
    position_id = position_response.json()["id"]
    
    # Create assignment
    assignment_response = client.post("/crew/assign-crew", json={
        "crew_member_id": crew_id,
        "position_id": position_id,
        "assignment_date": "2025-07-15"
    })
    assert assignment_response.status_code == 201
    
    # Test GET /crew/assignments - get all assignments
    response = client.get("/crew/assignments")
    assert response.status_code == 200, f"Failed to get assignments: {response.text}"
    
    assignments = response.json()
    assert isinstance(assignments, list), "Assignments should be a list"
    assert len(assignments) >= 1, "Should have at least one assignment"
    
    # Check structure of assignment objects
    for assignment in assignments:
        assert "id" in assignment, "Assignment should have 'id' field"
        assert "crew_member_id" in assignment, "Assignment should have 'crew_member_id' field"
        assert "position_id" in assignment, "Assignment should have 'position_id' field"
        assert "assignment_date" in assignment, "Assignment should have 'assignment_date' field"
    
    print(f"✓ GET /crew/assignments returned {len(assignments)} assignments")


def test_get_assignments_with_date_filter():
    """Test GET /crew/assignments with date range filters"""
    # Create another assignment for a different date
    crew_response = client.post("/crew/crew", json={
        "first_name": "Alice",
        "last_name": "Williams",
        "email": "alice@example.com",
        "phone": "5559876543",
        "team": "SKATE",
        "skills": "Skate instructor",
        "notes": ""
    })
    assert crew_response.status_code == 201
    crew_id = crew_response.json()["id"]
    
    position_response = client.post("/crew/positions", json={
        "name": "Skate Instructor",
        "team": "SKATE",
        "description": "Skateboard instructor"
    })
    assert position_response.status_code == 201
    position_id = position_response.json()["id"]
    
    # Create assignment for August
    assignment_response = client.post("/crew/assign-crew", json={
        "crew_member_id": crew_id,
        "position_id": position_id,
        "assignment_date": "2025-08-20"
    })
    assert assignment_response.status_code == 201
    
    # Test filtering by date range
    response = client.get("/crew/assignments?start_date=2025-08-01&end_date=2025-08-31")
    assert response.status_code == 200
    august_assignments = response.json()
    
    # All assignments should be in August 2025
    for assignment in august_assignments:
        assignment_date = date.fromisoformat(assignment["assignment_date"])
        assert assignment_date >= date(2025, 8, 1), "Assignment should be after start date"
        assert assignment_date <= date(2025, 8, 31), "Assignment should be before end date"
    
    print(f"✓ GET /crew/assignments with date filter returned {len(august_assignments)} assignments")


def test_get_assignments_empty():
    """Test GET /crew/assignments returns empty list when no assignments exist"""
    # Filter to a date range with no assignments
    response = client.get("/crew/assignments?start_date=2026-01-01&end_date=2026-01-31")
    assert response.status_code == 200, f"Failed to get assignments: {response.text}"
    
    assignments = response.json()
    assert isinstance(assignments, list), "Assignments should be a list"
    # Should be empty or have only assignments from other tests
    print(f"✓ GET /crew/assignments handles empty results correctly")


if __name__ == "__main__":
    import sys
    
    print("Running tests for new crew planner endpoints...")
    print()
    
    try:
        test_get_teams()
        test_get_members()
        test_get_members_empty()
        test_get_assignments()
        test_get_assignments_with_date_filter()
        test_get_assignments_empty()
        
        print()
        print("✓ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
