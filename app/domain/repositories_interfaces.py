from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

from app.domain.models import Booking, SurfPlan, Student, Instructor, Group, Slot


class BookingRawRepositoryInterface(ABC):

    @abstractmethod
    def get_all(self) -> List[Booking]:
        pass


class SurfPlanRepositoryInterface(ABC):
    @abstractmethod
    def get_by_date_and_location(self, plan_date: date, location_id: int) -> SurfPlan:
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
