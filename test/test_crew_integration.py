"""
Integration test for crew planner API endpoints
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


def test_crew_workflow():
    """Test complete crew planner workflow"""
    
    # 1. Create a crew member
    response = client.post("/crew/crew", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "team": "SURF",
        "skills": "Advanced surfing instructor",
        "notes": "Available weekends"
    })
    assert response.status_code == 201, f"Failed to create crew member: {response.text}"
    crew_member = response.json()
    crew_member_id = crew_member["id"]
    print(f"✓ Created crew member: {crew_member['first_name']} {crew_member['last_name']}")
    
    # 2. Get all crew members
    response = client.get("/crew/crew")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    print(f"✓ Retrieved {len(response.json())} crew members")
    
    # 3. Filter crew members by team
    response = client.get("/crew/crew?team=SURF")
    assert response.status_code == 200
    assert all(cm["team"] == "SURF" for cm in response.json())
    print(f"✓ Filtered crew members by team SURF")
    
    # 4. Create a position
    response = client.post("/crew/positions", json={
        "name": "Lead Surf Instructor",
        "team": "SURF",
        "description": "Main instructor for advanced groups"
    })
    assert response.status_code == 201
    position = response.json()
    position_id = position["id"]
    print(f"✓ Created position: {position['name']}")
    
    # 5. Get all positions
    response = client.get("/crew/positions")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    print(f"✓ Retrieved {len(response.json())} positions")
    
    # 6. Assign crew to position
    response = client.post("/crew/assign-crew", json={
        "crew_member_id": crew_member_id,
        "position_id": position_id,
        "assignment_date": "2025-06-15"
    })
    assert response.status_code == 201
    print(f"✓ Assigned crew member to position on 2025-06-15")
    
    # 7. Get crew calendar
    response = client.get("/crew/crew-calendar?start=2025-06-01&end=2025-06-30")
    assert response.status_code == 200
    calendar = response.json()
    assert "calendar" in calendar
    assert "2025-06-15" in calendar["calendar"]
    assert len(calendar["calendar"]["2025-06-15"]) >= 1
    print(f"✓ Retrieved crew calendar with {len(calendar['calendar'])} days")
    
    # 8. Filter crew calendar by team
    response = client.get("/crew/crew-calendar?start=2025-06-01&end=2025-06-30&team=SURF")
    assert response.status_code == 200
    calendar = response.json()
    assert calendar["team"] == "SURF"
    print(f"✓ Filtered crew calendar by team SURF")
    
    # 9. Create an accommodation
    response = client.post("/crew/accommodations", json={
        "name": "Tent A",
        "accommodation_type": "tent",
        "capacity": 2,
        "notes": "Near the beach"
    })
    assert response.status_code == 201
    accommodation = response.json()
    accommodation_id = accommodation["id"]
    print(f"✓ Created accommodation: {accommodation['name']}")
    
    # 10. Get all accommodations
    response = client.get("/crew/accommodations")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    print(f"✓ Retrieved {len(response.json())} accommodations")
    
    # 11. Assign accommodation to crew member
    response = client.post("/crew/assign-accommodation", json={
        "crew_member_id": crew_member_id,
        "accommodation_id": accommodation_id,
        "start_date": "2025-06-01",
        "end_date": "2025-06-30"
    })
    assert response.status_code == 201
    print(f"✓ Assigned accommodation to crew member")
    
    # 12. Test accommodation double booking prevention
    response = client.post("/crew/crew", json={
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "phone": "0987654321",
        "team": "SURF",
        "skills": "",
        "notes": ""
    })
    crew_member_2_id = response.json()["id"]
    
    response = client.post("/crew/crew", json={
        "first_name": "Bob",
        "last_name": "Wilson",
        "email": "bob@example.com",
        "phone": "1111111111",
        "team": "SURF",
        "skills": "",
        "notes": ""
    })
    crew_member_3_id = response.json()["id"]
    
    # Fill the tent (capacity 2)
    response = client.post("/crew/assign-accommodation", json={
        "crew_member_id": crew_member_2_id,
        "accommodation_id": accommodation_id,
        "start_date": "2025-06-01",
        "end_date": "2025-06-30"
    })
    assert response.status_code == 201
    print(f"✓ Assigned second crew member to accommodation")
    
    # Try to overbook (should fail)
    response = client.post("/crew/assign-accommodation", json={
        "crew_member_id": crew_member_3_id,
        "accommodation_id": accommodation_id,
        "start_date": "2025-06-01",
        "end_date": "2025-06-30"
    })
    assert response.status_code == 400
    assert "at capacity" in response.json()["detail"].lower()
    print(f"✓ Prevented accommodation double booking (capacity exceeded)")
    
    # 13. Test tent change prevention
    response = client.post("/crew/accommodations", json={
        "name": "Tent B",
        "accommodation_type": "tent",
        "capacity": 2,
        "notes": ""
    })
    accommodation_2_id = response.json()["id"]
    
    # Try to assign same crew member to different accommodation (should fail)
    response = client.post("/crew/assign-accommodation", json={
        "crew_member_id": crew_member_id,
        "accommodation_id": accommodation_2_id,
        "start_date": "2025-06-10",
        "end_date": "2025-06-20"
    })
    assert response.status_code == 400
    assert "already assigned" in response.json()["detail"].lower()
    print(f"✓ Prevented tent change during crew member's stay")
    
    # 14. Get accommodation assignments
    response = client.get("/crew/accommodation-assignments")
    assert response.status_code == 200
    assert len(response.json()) >= 2
    print(f"✓ Retrieved {len(response.json())} accommodation assignments")
    
    # 15. Filter accommodation assignments by date range
    response = client.get("/crew/accommodation-assignments?start=2025-06-01&end=2025-06-30")
    assert response.status_code == 200
    print(f"✓ Filtered accommodation assignments by date range")
    
    print("\n✅ All crew planner integration tests passed!")


if __name__ == "__main__":
    test_crew_workflow()
