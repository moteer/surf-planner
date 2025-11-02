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
    """
    Service for crew management business logic.
    
    Manages crew members, positions, crew assignments, accommodations, and accommodation assignments.
    Provides business logic and validation for all crew-related operations including:
    - CRUD operations for crew members and positions
    - Crew assignment scheduling
    - Accommodation management with capacity checking
    - Conflict detection and prevention
    """
    
    def __init__(
        self,
        crew_member_repo: SQLAlchemyCrewMemberRepositoryImpl,
        position_repo: SQLAlchemyPositionRepositoryImpl,
        crew_assignment_repo: SQLAlchemyCrewAssignmentRepositoryImpl,
        accommodation_repo: SQLAlchemyAccommodationRepositoryImpl,
        accommodation_assignment_repo: SQLAlchemyAccommodationAssignmentRepositoryImpl
    ):
        """
        Initialize the CrewService with repository dependencies.
        
        Args:
            crew_member_repo: Repository for crew member operations
            position_repo: Repository for position operations
            crew_assignment_repo: Repository for crew assignment operations
            accommodation_repo: Repository for accommodation operations
            accommodation_assignment_repo: Repository for accommodation assignment operations
        """
        self.crew_member_repo = crew_member_repo
        self.position_repo = position_repo
        self.crew_assignment_repo = crew_assignment_repo
        self.accommodation_repo = accommodation_repo
        self.accommodation_assignment_repo = accommodation_assignment_repo

    def get_crew_members(self, team: Optional[Team] = None) -> List[CrewMember]:
        """
        Get all crew members, optionally filtered by team.
        
        Args:
            team: Optional Team enum to filter by (SURF, YOGA, SKATE, etc.)
            
        Returns:
            List of CrewMember objects
        """
        if team:
            return self.crew_member_repo.get_by_team(team)
        return self.crew_member_repo.get_all()

    def create_crew_member(self, crew_member: CrewMember) -> CrewMember:
        """
        Create a new crew member.
        
        Args:
            crew_member: CrewMember domain object with crew member details
            
        Returns:
            The created CrewMember with assigned ID
        """
        return self.crew_member_repo.save(crew_member)

    def get_crew_member_by_id(self, crew_member_id: int) -> Optional[CrewMember]:
        """
        Get a crew member by ID.
        
        Args:
            crew_member_id: ID of the crew member
            
        Returns:
            CrewMember object or None if not found
        """
        return self.crew_member_repo.get_by_id(crew_member_id)

    def update_crew_member(self, crew_member_id: int, update_data: Dict[str, Any]) -> Optional[CrewMember]:
        """
        Update an existing crew member.
        
        Args:
            crew_member_id: ID of the crew member to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated CrewMember or None if not found
        """
        crew_member = self.crew_member_repo.get_by_id(crew_member_id)
        if not crew_member:
            return None
        
        # Whitelist of allowed fields to update (excluding id)
        allowed_fields = {'first_name', 'last_name', 'email', 'phone', 'team', 'skills', 'notes'}
        
        # Update only allowed fields
        for field, value in update_data.items():
            if field in allowed_fields and value is not None:
                setattr(crew_member, field, value)
        
        return self.crew_member_repo.save(crew_member)

    def delete_crew_member(self, crew_member_id: int) -> bool:
        """
        Delete a crew member.
        
        Args:
            crew_member_id: ID of the crew member to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.crew_member_repo.delete(crew_member_id)

    def get_positions(self, team: Optional[Team] = None) -> List[Position]:
        """
        Get all positions, optionally filtered by team.
        
        Args:
            team: Optional Team enum to filter by
            
        Returns:
            List of Position objects
        """
        if team:
            return self.position_repo.get_by_team(team)
        return self.position_repo.get_all()

    def create_position(self, position: Position) -> Position:
        """
        Create a new position.
        
        Args:
            position: Position domain object with position details
            
        Returns:
            The created Position with assigned ID
        """
        return self.position_repo.save(position)

    def get_position_by_id(self, position_id: int) -> Optional[Position]:
        """
        Get a position by ID.
        
        Args:
            position_id: ID of the position
            
        Returns:
            Position object or None if not found
        """
        return self.position_repo.get_by_id(position_id)

    def update_position(self, position_id: int, update_data: Dict[str, Any]) -> Optional[Position]:
        """
        Update an existing position.
        
        Args:
            position_id: ID of the position to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated Position or None if not found
        """
        position = self.position_repo.get_by_id(position_id)
        if not position:
            return None
        
        # Whitelist of allowed fields to update (excluding id)
        allowed_fields = {'name', 'team', 'description'}
        
        # Update only allowed fields
        for field, value in update_data.items():
            if field in allowed_fields and value is not None:
                setattr(position, field, value)
        
        return self.position_repo.save(position)

    def delete_position(self, position_id: int) -> bool:
        """
        Delete a position.
        
        Args:
            position_id: ID of the position to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.position_repo.delete(position_id)

    def assign_crew(self, crew_member_id: int, position_id: int, assignment_date: date) -> CrewAssignment:
        """
        Assign a crew member to a position on a specific date.
        
        Validates that both the crew member and position exist before creating the assignment.
        
        Args:
            crew_member_id: ID of the crew member to assign
            position_id: ID of the position to assign to
            assignment_date: Date of the assignment
            
        Returns:
            The created CrewAssignment
            
        Raises:
            ValueError: If crew member or position not found
        """
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

    def get_crew_assignments(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[CrewAssignment]:
        """
        Get crew assignments, optionally filtered by date range.
        
        Args:
            start_date: Optional start date filter (inclusive)
            end_date: Optional end date filter (inclusive)
            
        Returns:
            List of CrewAssignment objects that fall within the date range,
            or all assignments if no date range specified
        """
        if start_date and end_date:
            return self.crew_assignment_repo.get_by_date_range(start_date, end_date)
        return self.crew_assignment_repo.get_all()

    def delete_crew_assignment(self, assignment_id: int) -> bool:
        """
        Delete a crew assignment.
        
        Args:
            assignment_id: ID of the crew assignment to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.crew_assignment_repo.delete(assignment_id)

    def get_crew_calendar(
        self, 
        start_date: date, 
        end_date: date, 
        team: Optional[Team] = None
    ) -> Dict[str, Any]:
        """
        Get daily crew planning overview for a date range.
        
        Returns a calendar view with assignments grouped by date. Each date contains
        a list of assignments with crew member and position details.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range (inclusive)
            team: Optional team filter
            
        Returns:
            Dictionary with structure:
            {
                "start_date": "2025-06-01",
                "end_date": "2025-06-30",
                "team": "SURF" or None,
                "calendar": {
                    "2025-06-01": [list of assignments],
                    "2025-06-02": [list of assignments],
                    ...
                }
            }
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
        """
        Get all accommodations.
        
        Returns:
            List of all Accommodation objects
        """
        return self.accommodation_repo.get_all()

    def create_accommodation(self, accommodation: Accommodation) -> Accommodation:
        """
        Create a new accommodation.
        
        Args:
            accommodation: Accommodation domain object with accommodation details
            
        Returns:
            The created Accommodation with assigned ID
        """
        return self.accommodation_repo.save(accommodation)

    def get_accommodation_by_id(self, accommodation_id: int) -> Optional[Accommodation]:
        """
        Get an accommodation by ID.
        
        Args:
            accommodation_id: ID of the accommodation
            
        Returns:
            Accommodation object or None if not found
        """
        return self.accommodation_repo.get_by_id(accommodation_id)

    def update_accommodation(self, accommodation_id: int, update_data: Dict[str, Any]) -> Optional[Accommodation]:
        """
        Update an existing accommodation.
        
        Args:
            accommodation_id: ID of the accommodation to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated Accommodation or None if not found
        """
        accommodation = self.accommodation_repo.get_by_id(accommodation_id)
        if not accommodation:
            return None
        
        # Whitelist of allowed fields to update (excluding id)
        allowed_fields = {'name', 'accommodation_type', 'capacity', 'notes'}
        
        # Update only allowed fields
        for field, value in update_data.items():
            if field in allowed_fields and value is not None:
                setattr(accommodation, field, value)
        
        return self.accommodation_repo.save(accommodation)

    def delete_accommodation(self, accommodation_id: int) -> bool:
        """
        Delete an accommodation.
        
        Args:
            accommodation_id: ID of the accommodation to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.accommodation_repo.delete(accommodation_id)

    def assign_accommodation(
        self, 
        crew_member_id: int, 
        accommodation_id: int, 
        start_date: date, 
        end_date: date
    ) -> AccommodationAssignment:
        """
        Assign accommodation to a crew member with conflict checking.
        
        Validates two critical business rules:
        1. No double booking - the accommodation must have available capacity
        2. No tent changes - crew member cannot switch accommodations during their stay
        
        Args:
            crew_member_id: ID of the crew member
            accommodation_id: ID of the accommodation
            start_date: Start date of the accommodation assignment
            end_date: End date of the accommodation assignment
            
        Returns:
            The created AccommodationAssignment
            
        Raises:
            ValueError: If crew member or accommodation not found, capacity exceeded,
                       or crew member already assigned to different accommodation during this period
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
        """
        Get accommodation assignments, optionally filtered by date range.
        
        Args:
            start_date: Optional start date filter (inclusive)
            end_date: Optional end date filter (inclusive)
            
        Returns:
            List of AccommodationAssignment objects that overlap with the date range,
            or all assignments if no date range specified
        """
        if start_date and end_date:
            return self.accommodation_assignment_repo.get_by_date_range(start_date, end_date)
        return self.accommodation_assignment_repo.get_all()

    def delete_accommodation_assignment(self, assignment_id: int) -> bool:
        """
        Delete an accommodation assignment.
        
        Args:
            assignment_id: ID of the accommodation assignment to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.accommodation_assignment_repo.delete(assignment_id)
