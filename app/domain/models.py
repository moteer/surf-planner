from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List


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
