from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List

@dataclass
class Student:
    first_name: str
    last_name: str
    birthday: date
    gender: str
    age_group: str
    level: str
    booking_number: str

@dataclass
class Instructor:
    name: str
    certification: str

@dataclass
class Group:
    level: str
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
