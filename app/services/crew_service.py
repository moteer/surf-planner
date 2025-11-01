from datetime import date
from typing import List, Optional, Dict, Any
from app.domain.models import CrewMember, Position, CrewAssignment, Accommodation, AccommodationAssignment, Team
from app.data.sql_alchemey_repository_impl import (
    SQLAlchemyCrewMemberRepositoryImpl,
    SQLAlchemyPositionRepositoryImpl,
    SQLAlchemyCrewAssignmentRepositoryImpl,
    SQLAlchemyAccommodationRepositoryImpl,
    SQLAlchemyAccommodationAssignmentRepositoryImpl
)


class CrewService:
    """Service for crew management business logic"""
    
    def __init__(
        self,
        crew_member_repo: SQLAlchemyCrewMemberRepositoryImpl,
        position_repo: SQLAlchemyPositionRepositoryImpl,
        crew_assignment_repo: SQLAlchemyCrewAssignmentRepositoryImpl,
        accommodation_repo: SQLAlchemyAccommodationRepositoryImpl,
        accommodation_assignment_repo: SQLAlchemyAccommodationAssignmentRepositoryImpl
    ):
        self.crew_member_repo = crew_member_repo
        self.position_repo = position_repo
        self.crew_assignment_repo = crew_assignment_repo
        self.accommodation_repo = accommodation_repo
        self.accommodation_assignment_repo = accommodation_assignment_repo

    def get_crew_members(self, team: Optional[Team] = None) -> List[CrewMember]:
        """Get all crew members, optionally filtered by team"""
        if team:
            return self.crew_member_repo.get_by_team(team)
        return self.crew_member_repo.get_all()

    def create_crew_member(self, crew_member: CrewMember) -> CrewMember:
        """Create a new crew member"""
        return self.crew_member_repo.save(crew_member)

    def get_positions(self, team: Optional[Team] = None) -> List[Position]:
        """Get all positions, optionally filtered by team"""
        if team:
            return self.position_repo.get_by_team(team)
        return self.position_repo.get_all()

    def create_position(self, position: Position) -> Position:
        """Create a new position"""
        return self.position_repo.save(position)

    def assign_crew(self, crew_member_id: int, position_id: int, assignment_date: date) -> CrewAssignment:
        """Assign a crew member to a position on a specific date"""
        # Verify crew member exists
        crew_member = self.crew_member_repo.get_by_id(crew_member_id)
        if not crew_member:
            raise ValueError(f"Crew member with id {crew_member_id} not found")
        
        # Verify position exists
        position = self.position_repo.get_by_id(position_id)
        if not position:
            raise ValueError(f"Position with id {position_id} not found")
        
        assignment = CrewAssignment(
            id=None,
            crew_member_id=crew_member_id,
            position_id=position_id,
            assignment_date=assignment_date,
            crew_member=crew_member,
            position=position
        )
        return self.crew_assignment_repo.save(assignment)

    def get_crew_calendar(
        self, 
        start_date: date, 
        end_date: date, 
        team: Optional[Team] = None
    ) -> Dict[str, Any]:
        """
        Get daily crew planning overview for a date range
        Returns a calendar view with assignments grouped by date
        """
        # Get all assignments in the date range
        assignments = self.crew_assignment_repo.get_by_date_range(start_date, end_date)
        
        # Filter by team if specified
        if team:
            positions = self.position_repo.get_by_team(team)
            position_ids = {pos.id for pos in positions}
            assignments = [a for a in assignments if a.position_id in position_ids]
        
        # Group assignments by date
        calendar = {}
        current_date = start_date
        while current_date <= end_date:
            daily_assignments = [
                a for a in assignments 
                if a.assignment_date == current_date
            ]
            calendar[current_date.isoformat()] = [
                {
                    "id": a.id,
                    "crew_member": {
                        "id": a.crew_member.id,
                        "first_name": a.crew_member.first_name,
                        "last_name": a.crew_member.last_name,
                        "team": a.crew_member.team.value
                    } if a.crew_member else None,
                    "position": {
                        "id": a.position.id,
                        "name": a.position.name,
                        "team": a.position.team.value
                    } if a.position else None,
                    "assignment_date": a.assignment_date.isoformat()
                }
                for a in daily_assignments
            ]
            current_date = date.fromordinal(current_date.toordinal() + 1)
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "team": team.value if team else None,
            "calendar": calendar
        }

    def get_accommodations(self) -> List[Accommodation]:
        """Get all accommodations"""
        return self.accommodation_repo.get_all()

    def create_accommodation(self, accommodation: Accommodation) -> Accommodation:
        """Create a new accommodation"""
        return self.accommodation_repo.save(accommodation)

    def assign_accommodation(
        self, 
        crew_member_id: int, 
        accommodation_id: int, 
        start_date: date, 
        end_date: date
    ) -> AccommodationAssignment:
        """
        Assign accommodation to a crew member with conflict checking
        
        Ensures:
        1. No double booking - the accommodation has capacity
        2. No tent changes - crew member doesn't change accommodation during their stay
        """
        # Verify crew member exists
        crew_member = self.crew_member_repo.get_by_id(crew_member_id)
        if not crew_member:
            raise ValueError(f"Crew member with id {crew_member_id} not found")
        
        # Verify accommodation exists
        accommodation = self.accommodation_repo.get_by_id(accommodation_id)
        if not accommodation:
            raise ValueError(f"Accommodation with id {accommodation_id} not found")
        
        # Check for double booking - get all assignments for this accommodation in the date range
        existing_assignments = self.accommodation_assignment_repo.get_by_accommodation_and_date_range(
            accommodation_id, start_date, end_date
        )
        
        # Count how many crew members will be in this accommodation during the period
        crew_count = len(set(a.crew_member_id for a in existing_assignments))
        if crew_count >= accommodation.capacity:
            raise ValueError(
                f"Accommodation '{accommodation.name}' is at capacity ({accommodation.capacity}). "
                f"Cannot assign more crew members during this period."
            )
        
        # Check for tent changes - ensure crew member doesn't have other accommodation assignments that overlap
        crew_assignments = self.accommodation_assignment_repo.get_by_crew_member(crew_member_id)
        overlapping_assignments = [
            a for a in crew_assignments
            if a.accommodation_id != accommodation_id and (
                (a.start_date <= end_date and a.end_date >= start_date)
            )
        ]
        
        if overlapping_assignments:
            conflicting = overlapping_assignments[0]
            raise ValueError(
                f"Crew member is already assigned to accommodation "
                f"'{conflicting.accommodation.name if conflicting.accommodation else 'Unknown'}' "
                f"during this period ({conflicting.start_date} to {conflicting.end_date}). "
                f"Cannot change accommodation during a stay."
            )
        
        # Create the assignment
        assignment = AccommodationAssignment(
            id=None,
            crew_member_id=crew_member_id,
            accommodation_id=accommodation_id,
            start_date=start_date,
            end_date=end_date,
            crew_member=crew_member,
            accommodation=accommodation
        )
        return self.accommodation_assignment_repo.save(assignment)

    def get_accommodation_assignments(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[AccommodationAssignment]:
        """Get accommodation assignments, optionally filtered by date range"""
        if start_date and end_date:
            return self.accommodation_assignment_repo.get_by_date_range(start_date, end_date)
        return self.accommodation_assignment_repo.get_all()
