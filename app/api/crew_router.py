from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.domain.models import Team
from app.services.crew_service import CrewService
from app.data.sql_alchemey_repository_impl import (
    SQLAlchemyCrewMemberRepositoryImpl,
    SQLAlchemyPositionRepositoryImpl,
    SQLAlchemyCrewAssignmentRepositoryImpl,
    SQLAlchemyAccommodationRepositoryImpl,
    SQLAlchemyAccommodationAssignmentRepositoryImpl
)

router = APIRouter(prefix="/crew", tags=["crew"])


# Pydantic models for request/response validation

class CrewMemberCreate(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    team: Team
    skills: str = ""
    notes: str = ""


class CrewMemberResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    team: str
    skills: str
    notes: str

    class Config:
        from_attributes = True


class PositionCreate(BaseModel):
    name: str = Field(..., min_length=1)
    team: Team
    description: str = ""


class PositionResponse(BaseModel):
    id: int
    name: str
    team: str
    description: str

    class Config:
        from_attributes = True


class CrewAssignmentCreate(BaseModel):
    crew_member_id: int
    position_id: int
    assignment_date: date


class AccommodationCreate(BaseModel):
    name: str = Field(..., min_length=1)
    accommodation_type: str = Field(..., min_length=1)
    capacity: int = Field(..., ge=1)
    notes: str = ""


class AccommodationResponse(BaseModel):
    id: int
    name: str
    accommodation_type: str
    capacity: int
    notes: str

    class Config:
        from_attributes = True


class AccommodationAssignmentCreate(BaseModel):
    crew_member_id: int
    accommodation_id: int
    start_date: date
    end_date: date


# Helper function to create crew service
def get_crew_service(session: Session = Depends(get_db)) -> CrewService:
    return CrewService(
        crew_member_repo=SQLAlchemyCrewMemberRepositoryImpl(session),
        position_repo=SQLAlchemyPositionRepositoryImpl(session),
        crew_assignment_repo=SQLAlchemyCrewAssignmentRepositoryImpl(session),
        accommodation_repo=SQLAlchemyAccommodationRepositoryImpl(session),
        accommodation_assignment_repo=SQLAlchemyAccommodationAssignmentRepositoryImpl(session)
    )


# Crew Member Endpoints

@router.get("/crew", response_model=List[CrewMemberResponse])
def get_crew_members(
    team: Optional[Team] = Query(None, description="Filter by team"),
    crew_service: CrewService = Depends(get_crew_service)
):
    """Get all crew members, optionally filtered by team"""
    try:
        crew_members = crew_service.get_crew_members(team)
        return [
            CrewMemberResponse(
                id=cm.id,
                first_name=cm.first_name,
                last_name=cm.last_name,
                email=cm.email,
                phone=cm.phone,
                team=cm.team.value,
                skills=cm.skills,
                notes=cm.notes
            )
            for cm in crew_members
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crew", response_model=CrewMemberResponse, status_code=201)
def create_crew_member(
    crew_member: CrewMemberCreate,
    crew_service: CrewService = Depends(get_crew_service)
):
    """Create a new crew member"""
    try:
        from app.domain.models import CrewMember
        new_crew = CrewMember(
            id=None,
            first_name=crew_member.first_name,
            last_name=crew_member.last_name,
            email=crew_member.email,
            phone=crew_member.phone,
            team=crew_member.team,
            skills=crew_member.skills,
            notes=crew_member.notes
        )
        created = crew_service.create_crew_member(new_crew)
        return CrewMemberResponse(
            id=created.id,
            first_name=created.first_name,
            last_name=created.last_name,
            email=created.email,
            phone=created.phone,
            team=created.team.value,
            skills=created.skills,
            notes=created.notes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Position Endpoints

@router.get("/positions", response_model=List[PositionResponse])
def get_positions(
    team: Optional[Team] = Query(None, description="Filter by team"),
    crew_service: CrewService = Depends(get_crew_service)
):
    """Get all positions, optionally filtered by team"""
    try:
        positions = crew_service.get_positions(team)
        return [
            PositionResponse(
                id=pos.id,
                name=pos.name,
                team=pos.team.value,
                description=pos.description
            )
            for pos in positions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/positions", response_model=PositionResponse, status_code=201)
def create_position(
    position: PositionCreate,
    crew_service: CrewService = Depends(get_crew_service)
):
    """Create a new position"""
    try:
        from app.domain.models import Position
        new_position = Position(
            id=None,
            name=position.name,
            team=position.team,
            description=position.description
        )
        created = crew_service.create_position(new_position)
        return PositionResponse(
            id=created.id,
            name=created.name,
            team=created.team.value,
            description=created.description
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Crew Assignment Endpoints

@router.post("/assign-crew", status_code=201)
def assign_crew(
    assignment: CrewAssignmentCreate,
    crew_service: CrewService = Depends(get_crew_service)
):
    """Assign a crew member to a position on a specific date"""
    try:
        created = crew_service.assign_crew(
            crew_member_id=assignment.crew_member_id,
            position_id=assignment.position_id,
            assignment_date=assignment.assignment_date
        )
        return {
            "id": created.id,
            "crew_member_id": created.crew_member_id,
            "position_id": created.position_id,
            "assignment_date": created.assignment_date.isoformat(),
            "message": "Crew assignment created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crew-calendar")
def get_crew_calendar(
    start: date = Query(..., description="Start date (yyyy-mm-dd)"),
    end: date = Query(..., description="End date (yyyy-mm-dd)"),
    team: Optional[Team] = Query(None, description="Filter by team"),
    crew_service: CrewService = Depends(get_crew_service)
):
    """Get daily crew planning overview for a date range, filterable by team"""
    try:
        if start > end:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        calendar = crew_service.get_crew_calendar(start, end, team)
        return calendar
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Accommodation Endpoints

@router.get("/accommodations", response_model=List[AccommodationResponse])
def get_accommodations(
    crew_service: CrewService = Depends(get_crew_service)
):
    """Get all accommodations"""
    try:
        accommodations = crew_service.get_accommodations()
        return [
            AccommodationResponse(
                id=acc.id,
                name=acc.name,
                accommodation_type=acc.accommodation_type,
                capacity=acc.capacity,
                notes=acc.notes
            )
            for acc in accommodations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/accommodations", response_model=AccommodationResponse, status_code=201)
def create_accommodation(
    accommodation: AccommodationCreate,
    crew_service: CrewService = Depends(get_crew_service)
):
    """Create a new accommodation"""
    try:
        from app.domain.models import Accommodation
        new_accommodation = Accommodation(
            id=None,
            name=accommodation.name,
            accommodation_type=accommodation.accommodation_type,
            capacity=accommodation.capacity,
            notes=accommodation.notes
        )
        created = crew_service.create_accommodation(new_accommodation)
        return AccommodationResponse(
            id=created.id,
            name=created.name,
            accommodation_type=created.accommodation_type,
            capacity=created.capacity,
            notes=created.notes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign-accommodation", status_code=201)
def assign_accommodation(
    assignment: AccommodationAssignmentCreate,
    crew_service: CrewService = Depends(get_crew_service)
):
    """
    Assign accommodation to a crew member
    
    Validates:
    - No double booking (accommodation capacity)
    - No tent changes during a crew member's stay
    """
    try:
        created = crew_service.assign_accommodation(
            crew_member_id=assignment.crew_member_id,
            accommodation_id=assignment.accommodation_id,
            start_date=assignment.start_date,
            end_date=assignment.end_date
        )
        return {
            "id": created.id,
            "crew_member_id": created.crew_member_id,
            "accommodation_id": created.accommodation_id,
            "start_date": created.start_date.isoformat(),
            "end_date": created.end_date.isoformat(),
            "message": "Accommodation assignment created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accommodation-assignments")
def get_accommodation_assignments(
    start: Optional[date] = Query(None, description="Start date filter"),
    end: Optional[date] = Query(None, description="End date filter"),
    crew_service: CrewService = Depends(get_crew_service)
):
    """Get accommodation assignments, optionally filtered by date range"""
    try:
        assignments = crew_service.get_accommodation_assignments(start, end)
        return [
            {
                "id": a.id,
                "crew_member_id": a.crew_member_id,
                "accommodation_id": a.accommodation_id,
                "start_date": a.start_date.isoformat(),
                "end_date": a.end_date.isoformat(),
                "crew_member": {
                    "id": a.crew_member.id,
                    "first_name": a.crew_member.first_name,
                    "last_name": a.crew_member.last_name
                } if a.crew_member else None,
                "accommodation": {
                    "id": a.accommodation.id,
                    "name": a.accommodation.name,
                    "type": a.accommodation.accommodation_type
                } if a.accommodation else None
            }
            for a in assignments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
