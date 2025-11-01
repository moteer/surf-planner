from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional
from enum import Enum


@dataclass
class Booking:
    booking_id: str
    booker_id: str
    first_name: str
    last_name: str
    birthday: date
    gender: str
    group: str
    level: str
    arrival: date
    departure: date
    booking_status: date
    number_of_surf_lessons: int
    surf_lesson_package_name: str
    diet: str
    notes_one: str
    tent: str
    number_of_yoga_lessons: int = 0
    number_of_skate_lessons: int = 0


@dataclass
class Student:
    id: int
    first_name: str
    last_name: str
    birthday: date
    gender: str
    age_group: str
    level: str
    booking_number: str
    arrival: date
    departure: date
    booking_status: date
    number_of_surf_lessons: int
    surf_lesson_package_name: str
    tent: str
    single_parent: bool = False


@dataclass
class Instructor:
    name: str
    certification: str


@dataclass
class Group:
    level: str
    age_group: str
    students: List[Student] = field(default_factory=list)
    instructors: List[Instructor] = field(default_factory=list)


@dataclass
class Slot:
    slot_time: datetime
    groups: List[Group] = field(default_factory=list)


@dataclass
class SurfPlan:
    plan_date: date
    slots: List[Slot] = field(default_factory=list)
    id: int = None
    non_participating_guests: List[Student] = field(default_factory=list)


# Crew Planner Models

class Team(str, Enum):
    """Team enum for positions"""
    SURF = "SURF"
    SKATE = "SKATE"
    YOGA = "YOGA"
    KITCHEN = "KITCHEN"
    CLEANING = "CLEANING"
    RECEPTION = "RECEPTION"


@dataclass
class CrewMember:
    """Crew member model"""
    id: Optional[int]
    first_name: str
    last_name: str
    email: str
    phone: str
    team: Team
    skills: str = ""
    notes: str = ""


@dataclass
class Position:
    """Position model with team"""
    id: Optional[int]
    name: str
    team: Team
    description: str = ""


@dataclass
class CrewAssignment:
    """Crew assignment model - who is assigned to which position and when"""
    id: Optional[int]
    crew_member_id: int
    position_id: int
    assignment_date: date
    crew_member: Optional[CrewMember] = None
    position: Optional[Position] = None


@dataclass
class Accommodation:
    """Accommodation model - tent, caravan, etc."""
    id: Optional[int]
    name: str
    accommodation_type: str  # tent, caravan, room, etc.
    capacity: int
    notes: str = ""


@dataclass
class AccommodationAssignment:
    """Assignment of crew member to accommodation"""
    id: Optional[int]
    crew_member_id: int
    accommodation_id: int
    start_date: date
    end_date: date
    crew_member: Optional[CrewMember] = None
    accommodation: Optional[Accommodation] = None
