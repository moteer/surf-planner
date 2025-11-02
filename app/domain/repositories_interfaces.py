from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

from app.domain.models import (
    Booking, SurfPlan, Student, Instructor, Group, Slot,
    CrewMember, Position, CrewAssignment, Accommodation, AccommodationAssignment, Team
)


class BookingRawRepositoryInterface(ABC):

    @abstractmethod
    def get_all(self) -> List[Booking]:
        pass


class SurfPlanRepositoryInterface(ABC):
    @abstractmethod
    def get_by_date(self, plan_date: date) -> SurfPlan:
        pass

    @abstractmethod
    def save(self, surf_plan: SurfPlan) -> SurfPlan:
        pass


class StudentRepositoryInterface(ABC):
    @abstractmethod
    def get_all_by_date_range(self, start_date: date, end_date: date) -> List[Student]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Student]:
        pass

    @abstractmethod
    def get_by_booking_number(self, booking_number: str) -> Optional[Student]:
        pass

    @abstractmethod
    def get_all(self) -> List[Student]:
        pass

    @abstractmethod
    def get_students_with_booked_lessons(self) -> List[Student]:
        pass

    @abstractmethod
    def save(self, student: Student) -> Student:
        pass

    @abstractmethod
    def save_all(self, students: List[Student]) -> List[Student]:
        pass
    @abstractmethod
    def update(self, id: int, student: Student) -> Student:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass


class InstructorRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Instructor]:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Instructor]:
        pass

    @abstractmethod
    def get_all(self) -> List[Instructor]:
        pass

    @abstractmethod
    def save(self, instructor: Instructor) -> Instructor:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass


class GroupRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Group]:
        pass

    @abstractmethod
    def get_by_level(self, level: str) -> List[Group]:
        pass

    @abstractmethod
    def get_all(self) -> List[Group]:
        pass

    @abstractmethod
    def save(self, group: Group) -> Group:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass


class SlotRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Slot]:
        pass

    @abstractmethod
    def get_all(self) -> List[Slot]:
        pass

    @abstractmethod
    def get_by_surf_plan_id(self, surf_plan_id: int) -> List[Slot]:
        pass

    @abstractmethod
    def save(self, slot: Slot, surf_plan_id: int) -> Slot:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
       pass


# Crew Planner Repository Interfaces

class CrewMemberRepositoryInterface(ABC):
    """Repository interface for crew member operations"""
    
    @abstractmethod
    def get_all(self) -> List[CrewMember]:
        """Get all crew members"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[CrewMember]:
        """Get a crew member by ID"""
        pass
    
    @abstractmethod
    def get_by_team(self, team: Team) -> List[CrewMember]:
        """Get all crew members for a specific team"""
        pass
    
    @abstractmethod
    def save(self, crew_member: CrewMember) -> CrewMember:
        """Save or update a crew member"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete a crew member by ID"""
        pass


class PositionRepositoryInterface(ABC):
    """Repository interface for position operations"""
    
    @abstractmethod
    def get_all(self) -> List[Position]:
        """Get all positions"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Position]:
        """Get a position by ID"""
        pass
    
    @abstractmethod
    def get_by_team(self, team: Team) -> List[Position]:
        """Get all positions for a specific team"""
        pass
    
    @abstractmethod
    def save(self, position: Position) -> Position:
        """Save or update a position"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete a position by ID"""
        pass


class CrewAssignmentRepositoryInterface(ABC):
    """Repository interface for crew assignment operations"""
    
    @abstractmethod
    def get_all(self) -> List[CrewAssignment]:
        """Get all crew assignments"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[CrewAssignment]:
        """Get a crew assignment by ID"""
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> List[CrewAssignment]:
        """Get crew assignments within a date range"""
        pass
    
    @abstractmethod
    def get_by_crew_member(self, crew_member_id: int) -> List[CrewAssignment]:
        """Get all assignments for a specific crew member"""
        pass
    
    @abstractmethod
    def save(self, assignment: CrewAssignment) -> CrewAssignment:
        """Save or update a crew assignment"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete a crew assignment by ID"""
        pass


class AccommodationRepositoryInterface(ABC):
    """Repository interface for accommodation operations"""
    
    @abstractmethod
    def get_all(self) -> List[Accommodation]:
        """Get all accommodations"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Accommodation]:
        """Get an accommodation by ID"""
        pass
    
    @abstractmethod
    def save(self, accommodation: Accommodation) -> Accommodation:
        """Save or update an accommodation"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an accommodation by ID"""
        pass


class AccommodationAssignmentRepositoryInterface(ABC):
    """Repository interface for accommodation assignment operations"""
    
    @abstractmethod
    def get_all(self) -> List[AccommodationAssignment]:
        """Get all accommodation assignments"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[AccommodationAssignment]:
        """Get an accommodation assignment by ID"""
        pass
    
    @abstractmethod
    def get_by_crew_member(self, crew_member_id: int) -> List[AccommodationAssignment]:
        """Get all accommodation assignments for a specific crew member"""
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> List[AccommodationAssignment]:
        """Get accommodation assignments that overlap with the given date range"""
        pass
    
    @abstractmethod
    def get_by_accommodation_and_date_range(
        self, accommodation_id: int, start_date: date, end_date: date
    ) -> List[AccommodationAssignment]:
        """Get accommodation assignments for a specific accommodation that overlap with the given date range"""
        pass
    
    @abstractmethod
    def save(self, assignment: AccommodationAssignment) -> AccommodationAssignment:
        """Save or update an accommodation assignment"""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an accommodation assignment by ID"""
        pass
