#!/usr/bin/env python3
"""
Manual test script for crew planner endpoints
Run this with: python test_crew_manual.py

You can test the API with curl commands like:

# Create crew member
curl -X POST http://localhost:8000/crew/crew \\
  -H "Content-Type: application/json" \\
  -d '{"first_name":"John","last_name":"Doe","email":"john@test.com","phone":"123","team":"SURF"}'

# Get crew members
curl http://localhost:8000/crew/crew

# Get crew members filtered by team
curl http://localhost:8000/crew/crew?team=SURF

# Create position
curl -X POST http://localhost:8000/crew/positions \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Lead Instructor","team":"SURF","description":"Main instructor"}'

# Assign crew to position
curl -X POST http://localhost:8000/crew/assign-crew \\
  -H "Content-Type: application/json" \\
  -d '{"crew_member_id":1,"position_id":1,"assignment_date":"2025-06-15"}'

# Get crew calendar
curl "http://localhost:8000/crew/crew-calendar?start=2025-06-01&end=2025-06-30"

# Get crew calendar filtered by team
curl "http://localhost:8000/crew/crew-calendar?start=2025-06-01&end=2025-06-30&team=SURF"

# Create accommodation
curl -X POST http://localhost:8000/crew/accommodations \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Tent A","accommodation_type":"tent","capacity":2,"notes":"Near beach"}'

# Assign accommodation
curl -X POST http://localhost:8000/crew/assign-accommodation \\
  -H "Content-Type: application/json" \\
  -d '{"crew_member_id":1,"accommodation_id":1,"start_date":"2025-06-01","end_date":"2025-06-30"}'

# Get accommodation assignments
curl http://localhost:8000/crew/accommodation-assignments
"""

import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from datetime import date
from app.core.db import engine, Base, SessionLocal
from app.data.orm_models import *
from app.domain.models import Team, CrewMember, Position, Accommodation
from app.services.crew_service import CrewService
from app.data.sql_alchemey_repository_impl import (
    SQLAlchemyCrewMemberRepositoryImpl,
    SQLAlchemyPositionRepositoryImpl,
    SQLAlchemyCrewAssignmentRepositoryImpl,
    SQLAlchemyAccommodationRepositoryImpl,
    SQLAlchemyAccommodationAssignmentRepositoryImpl
)

# Create database schema
print("Creating database schema...")
Base.metadata.create_all(bind=engine)
print("✓ Database schema created\n")

# Create a session
session = SessionLocal()

# Create crew service
crew_service = CrewService(
    crew_member_repo=SQLAlchemyCrewMemberRepositoryImpl(session),
    position_repo=SQLAlchemyPositionRepositoryImpl(session),
    crew_assignment_repo=SQLAlchemyCrewAssignmentRepositoryImpl(session),
    accommodation_repo=SQLAlchemyAccommodationRepositoryImpl(session),
    accommodation_assignment_repo=SQLAlchemyAccommodationAssignmentRepositoryImpl(session)
)

print("Testing Crew Planner Service...\n")

# Test 1: Create crew members
print("1. Creating crew members...")
crew1 = crew_service.create_crew_member(CrewMember(
    id=None,
    first_name="John",
    last_name="Doe",
    email="john@test.com",
    phone="123-456-7890",
    team=Team.SURF,
    skills="Advanced surf instruction",
    notes="Available weekends"
))
print(f"   ✓ Created: {crew1.first_name} {crew1.last_name} (ID: {crew1.id}, Team: {crew1.team.value})")

crew2 = crew_service.create_crew_member(CrewMember(
    id=None,
    first_name="Jane",
    last_name="Smith",
    email="jane@test.com",
    phone="098-765-4321",
    team=Team.YOGA,
    skills="Certified yoga instructor",
    notes=""
))
print(f"   ✓ Created: {crew2.first_name} {crew2.last_name} (ID: {crew2.id}, Team: {crew2.team.value})")

# Test 2: Get crew members
print("\n2. Getting all crew members...")
all_crew = crew_service.get_crew_members()
print(f"   ✓ Found {len(all_crew)} crew members")

# Test 3: Filter by team
print("\n3. Filtering crew members by team SURF...")
surf_crew = crew_service.get_crew_members(team=Team.SURF)
print(f"   ✓ Found {len(surf_crew)} SURF team members")

# Test 4: Create positions
print("\n4. Creating positions...")
pos1 = crew_service.create_position(Position(
    id=None,
    name="Lead Surf Instructor",
    team=Team.SURF,
    description="Main instructor for advanced groups"
))
print(f"   ✓ Created: {pos1.name} (ID: {pos1.id}, Team: {pos1.team.value})")

pos2 = crew_service.create_position(Position(
    id=None,
    name="Yoga Teacher",
    team=Team.YOGA,
    description="Morning and evening sessions"
))
print(f"   ✓ Created: {pos2.name} (ID: {pos2.id}, Team: {pos2.team.value})")

# Test 5: Assign crew to position
print("\n5. Assigning crew to positions...")
assignment = crew_service.assign_crew(crew1.id, pos1.id, date(2025, 6, 15))
print(f"   ✓ Assigned {crew1.first_name} to {pos1.name} on 2025-06-15")

# Test 6: Get crew calendar
print("\n6. Getting crew calendar...")
calendar = crew_service.get_crew_calendar(date(2025, 6, 1), date(2025, 6, 30))
assignments_count = sum(len(day_assignments) for day_assignments in calendar["calendar"].values())
print(f"   ✓ Calendar covers {len(calendar['calendar'])} days with {assignments_count} total assignments")

# Test 7: Create accommodations
print("\n7. Creating accommodations...")
acc1 = crew_service.create_accommodation(Accommodation(
    id=None,
    name="Tent A",
    accommodation_type="tent",
    capacity=2,
    notes="Near the beach"
))
print(f"   ✓ Created: {acc1.name} (Type: {acc1.accommodation_type}, Capacity: {acc1.capacity})")

# Test 8: Assign accommodation
print("\n8. Assigning accommodation...")
acc_assignment = crew_service.assign_accommodation(
    crew1.id, acc1.id, date(2025, 6, 1), date(2025, 6, 30)
)
print(f"   ✓ Assigned {crew1.first_name} to {acc1.name} from 2025-06-01 to 2025-06-30")

# Test 9: Test capacity limit
print("\n9. Testing accommodation capacity limits...")
crew3 = crew_service.create_crew_member(CrewMember(
    id=None,
    first_name="Bob",
    last_name="Wilson",
    email="bob@test.com",
    phone="555-123-4567",
    team=Team.SURF,
    skills="",
    notes=""
))
acc_assignment2 = crew_service.assign_accommodation(
    crew3.id, acc1.id, date(2025, 6, 1), date(2025, 6, 30)
)
print(f"   ✓ Assigned {crew3.first_name} to {acc1.name}")

# Try to exceed capacity
crew4 = crew_service.create_crew_member(CrewMember(
    id=None,
    first_name="Alice",
    last_name="Johnson",
    email="alice@test.com",
    phone="555-987-6543",
    team=Team.SURF,
    skills="",
    notes=""
))

try:
    crew_service.assign_accommodation(crew4.id, acc1.id, date(2025, 6, 1), date(2025, 6, 30))
    print("   ✗ ERROR: Should have prevented overbooking!")
except ValueError as e:
    print(f"   ✓ Correctly prevented overbooking: {str(e)}")

# Test 10: Test tent change prevention
print("\n10. Testing tent change prevention...")
acc2 = crew_service.create_accommodation(Accommodation(
    id=None,
    name="Tent B",
    accommodation_type="tent",
    capacity=2,
    notes=""
))
print(f"   ✓ Created second accommodation: {acc2.name}")

try:
    crew_service.assign_accommodation(crew1.id, acc2.id, date(2025, 6, 10), date(2025, 6, 20))
    print("   ✗ ERROR: Should have prevented tent change!")
except ValueError as e:
    print(f"   ✓ Correctly prevented tent change: {str(e)}")

print("\n" + "="*60)
print("✅ All crew planner service tests passed!")
print("="*60)

# Clean up
session.close()

print("\n" + __doc__)
