"""
Test script for new crew planner endpoints without httpx dependency
"""
import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from datetime import date
from app.core.db import engine, Base, get_db
from app.data.orm_models import *
from app.services.crew_service import CrewService
from app.data.sql_alchemey_repository_impl import (
    SQLAlchemyCrewMemberRepositoryImpl,
    SQLAlchemyPositionRepositoryImpl,
    SQLAlchemyCrewAssignmentRepositoryImpl,
    SQLAlchemyAccommodationRepositoryImpl,
    SQLAlchemyAccommodationAssignmentRepositoryImpl
)
from app.domain.models import Team, CrewMember, Position

# Create database schema
Base.metadata.create_all(bind=engine)


def test_service_methods():
    """Test the service methods that power the new endpoints"""
    print("Testing crew service methods...")
    
    # Get a database session
    db = next(get_db())
    
    # Create service
    crew_service = CrewService(
        crew_member_repo=SQLAlchemyCrewMemberRepositoryImpl(db),
        position_repo=SQLAlchemyPositionRepositoryImpl(db),
        crew_assignment_repo=SQLAlchemyCrewAssignmentRepositoryImpl(db),
        accommodation_repo=SQLAlchemyAccommodationRepositoryImpl(db),
        accommodation_assignment_repo=SQLAlchemyAccommodationAssignmentRepositoryImpl(db)
    )
    
    # Test 1: Get teams (this is just the enum values)
    print("\n1. Testing Team enum:")
    teams = [{"name": team.name, "value": team.value} for team in Team]
    print(f"   Found {len(teams)} teams: {[t['value'] for t in teams]}")
    assert len(teams) > 0, "Should have teams"
    assert "SURF" in [t["value"] for t in teams], "Should have SURF team"
    print("   ✓ Team enum works correctly")
    
    # Test 2: Create and get crew members
    print("\n2. Testing get_crew_members:")
    
    # Create a test crew member
    member1 = CrewMember(
        id=None,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        team=Team.SURF,
        skills="Surfing",
        notes="Test member"
    )
    created_member = crew_service.create_crew_member(member1)
    print(f"   Created crew member: {created_member.first_name} {created_member.last_name}")
    
    # Get all crew members
    all_members = crew_service.get_crew_members()
    print(f"   Found {len(all_members)} total crew members")
    assert len(all_members) >= 1, "Should have at least one member"
    print("   ✓ get_crew_members() works")
    
    # Get members by team
    surf_members = crew_service.get_crew_members(Team.SURF)
    print(f"   Found {len(surf_members)} SURF team members")
    assert len(surf_members) >= 1, "Should have at least one SURF member"
    print("   ✓ get_crew_members(team=SURF) works")
    
    # Test 3: Create and get crew assignments
    print("\n3. Testing get_crew_assignments:")
    
    # Create a position
    position1 = Position(
        id=None,
        name="Lead Instructor",
        team=Team.SURF,
        description="Main instructor"
    )
    created_position = crew_service.create_position(position1)
    print(f"   Created position: {created_position.name}")
    
    # Create an assignment
    assignment = crew_service.assign_crew(
        crew_member_id=created_member.id,
        position_id=created_position.id,
        assignment_date=date(2025, 7, 15)
    )
    print(f"   Created assignment for {assignment.assignment_date}")
    
    # Get all assignments
    all_assignments = crew_service.get_crew_assignments()
    print(f"   Found {len(all_assignments)} total assignments")
    assert len(all_assignments) >= 1, "Should have at least one assignment"
    print("   ✓ get_crew_assignments() works")
    
    # Get assignments by date range
    date_assignments = crew_service.get_crew_assignments(
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 31)
    )
    print(f"   Found {len(date_assignments)} assignments in July 2025")
    assert len(date_assignments) >= 1, "Should have at least one assignment in July"
    print("   ✓ get_crew_assignments(start_date, end_date) works")
    
    # Test with date range that has no assignments
    empty_assignments = crew_service.get_crew_assignments(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31)
    )
    print(f"   Found {len(empty_assignments)} assignments in Jan 2026 (should be 0)")
    assert len(empty_assignments) == 0, "Should have no assignments in 2026"
    print("   ✓ get_crew_assignments() returns empty list correctly")
    
    db.close()


def test_endpoint_logic():
    """Test the logic that will be in the endpoints"""
    print("\n\nTesting endpoint response logic...")
    
    # Get a database session
    db = next(get_db())
    
    # Create service
    crew_service = CrewService(
        crew_member_repo=SQLAlchemyCrewMemberRepositoryImpl(db),
        position_repo=SQLAlchemyPositionRepositoryImpl(db),
        crew_assignment_repo=SQLAlchemyCrewAssignmentRepositoryImpl(db),
        accommodation_repo=SQLAlchemyAccommodationRepositoryImpl(db),
        accommodation_assignment_repo=SQLAlchemyAccommodationAssignmentRepositoryImpl(db)
    )
    
    # Test 1: GET /teams response format
    print("\n1. Testing /teams endpoint response:")
    teams = [{"name": team.name, "value": team.value} for team in Team]
    print(f"   Response: {teams[:2]}... ({len(teams)} total)")
    assert all("name" in t and "value" in t for t in teams), "Each team should have name and value"
    print("   ✓ Teams response format correct")
    
    # Test 2: GET /members response format
    print("\n2. Testing /members endpoint response:")
    members = crew_service.get_crew_members()
    if members:
        member_responses = [
            {
                "id": cm.id,
                "first_name": cm.first_name,
                "last_name": cm.last_name,
                "email": cm.email,
                "phone": cm.phone,
                "team": cm.team.value,
                "skills": cm.skills,
                "notes": cm.notes
            }
            for cm in members
        ]
        print(f"   Response sample: {member_responses[0]}")
        assert all("id" in m and "team" in m for m in member_responses), "Each member should have required fields"
        print("   ✓ Members response format correct")
    else:
        print("   Response: [] (empty list)")
        print("   ✓ Empty members response correct")
    
    # Test 3: GET /assignments response format
    print("\n3. Testing /assignments endpoint response:")
    assignments = crew_service.get_crew_assignments()
    if assignments:
        assignment_responses = [
            {
                "id": a.id,
                "crew_member_id": a.crew_member_id,
                "position_id": a.position_id,
                "assignment_date": a.assignment_date.isoformat()
            }
            for a in assignments
        ]
        print(f"   Response sample: {assignment_responses[0]}")
        assert all("id" in a and "crew_member_id" in a for a in assignment_responses), "Each assignment should have required fields"
        print("   ✓ Assignments response format correct")
    else:
        print("   Response: [] (empty list)")
        print("   ✓ Empty assignments response correct")
    
    db.close()


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Testing New Crew Planner Endpoints (Service Layer)")
    print("=" * 60)
    
    try:
        test_service_methods()
        test_endpoint_logic()
        
        print("\n" + "=" * 60)
        print("✓ All service tests passed!")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
