from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.repositories_interfaces import BookingRawRepositoryInterface, SurfPlanRepositoryInterface, \
    StudentRepositoryInterface, InstructorRepository, GroupRepository, \
    SlotRepository
from app.domain.models import SurfPlan, Student, Instructor, Group, Slot
from app.data.orm_models import SurfPlanORM, StudentORM, InstructorORM, GroupORM, SlotORM, RawBookingORM
from sqlalchemy import and_


class SQLAlchemyBookingRawRepositoryImpl(BookingRawRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[RawBookingORM]:
        raw_booking_orms = self.session.query(RawBookingORM).all()
        return [raw_booking_orm.to_domain() for raw_booking_orm in raw_booking_orms]

    def get_for_date(self, start_date: date, end_date: date):
        orm_bookings = self.session.query(RawBookingORM).filter(
            and_(RawBookingORM.guest_arrival_date < start_date, RawBookingORM.guest_departure_date > end_date)
        ).all()

        return [bookings.to_domain() for bookings in orm_bookings]

    def get_for_date_inclusive(self, start_date: date, end_date: date):
        orm_bookings = self.session.query(RawBookingORM).filter(
            and_(
                RawBookingORM.guest_arrival_date < end_date,
                RawBookingORM.guest_departure_date > start_date
            )
        ).all()

        return [bookings.to_domain() for bookings in orm_bookings]


class SQLAlchemySurfPlanRepositoryImpl(SurfPlanRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def get_by_date(self, plan_date: date) -> Optional[SurfPlan]:
        orm_surf_plan = self.session.query(SurfPlanORM).filter(
            SurfPlanORM.plan_date == plan_date
        ).first()

        return orm_surf_plan.to_domain() if orm_surf_plan else None

    def get_by_id(self, id: int) -> Optional[SurfPlan]:
        orm_surf_plan = self.session.query(SurfPlanORM).filter(
            SurfPlanORM.id == id
        ).first()

        return orm_surf_plan.to_domain() if orm_surf_plan else None

    def get_all(self) -> List[SurfPlan]:
        orm_surf_plans = self.session.query(SurfPlanORM).all()
        return [orm_surf_plan.to_domain() for orm_surf_plan in orm_surf_plans]

    def save(self, surf_plan: SurfPlan) -> SurfPlan:
        orm_surf_plan = SurfPlanORM.from_domain(surf_plan)

        if orm_surf_plan.id is None:
            self.session.add(orm_surf_plan)
        else:
            self.session.merge(orm_surf_plan)

        self.session.commit()
        return orm_surf_plan.to_domain()

    def delete(self, id: int) -> bool:
        result = self.session.query(SurfPlanORM).filter(
            SurfPlanORM.id == id
        ).delete()
        self.session.commit()
        return result > 0


class SQLAlchemyStudentRepositoryImpl(StudentRepositoryInterface):

    def __init__(self, session: Session):
        self.session = session

    # TODO: include_arriving: bool = False, include_departing: bool = False
    def get_all_by_date_range(self, start_date: date, end_date: date) -> List[Student]:
        orm_students = self.session.query(StudentORM).filter(
            and_(StudentORM.arrival < start_date, StudentORM.departure > end_date)
        ).all()

        return [orm_student.to_domain() for orm_student in orm_students]

    def get_by_id(self, id: int) -> Optional[Student]:
        orm_student = self.session.query(StudentORM).filter(
            StudentORM.id == id
        ).first()

        return orm_student.to_domain() if orm_student else None

    def get_by_booking_number(self, booking_number: str) -> List[Student]:

        orm_students = self.session.query(StudentORM).filter(
            StudentORM.booking_number == booking_number
        )
        return [orm_student.to_domain() for orm_student in orm_students]

    def get_all(self) -> List[Student]:
        orm_students = self.session.query(StudentORM).all()
        return [orm_student.to_domain() for orm_student in orm_students]

    def get_students_with_booked_lessons(self) -> List[Student]:
        orm_students = self.session.query(StudentORM).filter(
            StudentORM.number_of_surf_lessons > 0
        ).all()

        result = [orm_student.to_domain() for orm_student in orm_students]
        return result

    # WRONG !!!!! need to find id
    def update(self, id: int, student: Student) -> Student:
        orm_student = StudentORM.from_domain(student)

        existing_student = self.session.query(StudentORM).filter(
            StudentORM.id == id
        ).first()

        if existing_student:
            # Update existing student
            for key, value in vars(orm_student).items():
                if key != '_sa_instance_state' and key != 'id':
                    setattr(existing_student, key, value)
            orm_student = existing_student
        else:
            # Add new student
            self.session.add(orm_student)

        self.session.commit()
        return orm_student.to_domain()

    def delete(self, id: int) -> bool:
        result = self.session.query(StudentORM).filter(
            StudentORM.id == id
        ).delete()
        self.session.commit()
        return result > 0

    def save(self, student: Student) -> Student:
        orm_student = StudentORM.from_domain(student)
        print("💾 save student:")
        print(orm_student)
        self.session.add(orm_student)
        self.session.commit()
        return orm_student.to_domain()

    def save_all(self, students: List[Student]) -> List[Student]:
        saved_students = []
        for student in students:
            saved_student = self.save(StudentORM.from_domain(student))
            saved_students.append(saved_student)
        return saved_students


class SQLAlchemyInstructorRepository(InstructorRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[Instructor]:
        orm_instructor = self.session.query(InstructorORM).filter(
            InstructorORM.id == id
        ).first()

        return orm_instructor.to_domain() if orm_instructor else None

    def get_by_name(self, name: str) -> Optional[Instructor]:
        orm_instructor = self.session.query(InstructorORM).filter(
            InstructorORM.name == name
        ).first()

        return orm_instructor.to_domain() if orm_instructor else None

    def get_all(self) -> List[Instructor]:
        orm_instructors = self.session.query(InstructorORM).all()
        return [orm_instructor.to_domain() for orm_instructor in orm_instructors]

    def save(self, instructor: Instructor) -> Instructor:
        orm_instructor = InstructorORM.from_domain(instructor)

        existing_instructor = self.session.query(InstructorORM).filter(
            InstructorORM.name == orm_instructor.name
        ).first()

        if existing_instructor:
            # Update existing instructor
            for key, value in vars(orm_instructor).items():
                if key != '_sa_instance_state' and key != 'id':
                    setattr(existing_instructor, key, value)
            orm_instructor = existing_instructor
        else:
            # Add new instructor
            self.session.add(orm_instructor)

        self.session.commit()
        return orm_instructor.to_domain()

    def delete(self, id: int) -> bool:
        result = self.session.query(InstructorORM).filter(
            InstructorORM.id == id
        ).delete()
        self.session.commit()
        return result > 0


class SQLAlchemyGroupRepository(GroupRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[Group]:
        orm_group = self.session.query(GroupORM).filter(
            GroupORM.id == id
        ).first()

        return orm_group.to_domain() if orm_group else None

    def get_by_level(self, level: str) -> List[Group]:
        orm_groups = self.session.query(GroupORM).filter(
            GroupORM.level == level
        ).all()

        return [orm_group.to_domain() for orm_group in orm_groups]

    def get_all(self) -> List[Group]:
        orm_groups = self.session.query(GroupORM).all()
        return [orm_group.to_domain() for orm_group in orm_groups]

    def save(self, group: Group) -> Group:
        # This is complex due to relationships. A simplified approach:
        orm_group = GroupORM.from_domain(group)

        if orm_group.id is None:
            self.session.add(orm_group)
        else:
            # Update existing group
            existing_group = self.session.query(GroupORM).get(orm_group.id)
            if existing_group:
                existing_group.level = orm_group.level
                # Handle relationships - this needs more sophisticated logic
                # for student and instructor relationships

        self.session.commit()
        return self.get_by_id(orm_group.id)

    def delete(self, id: int) -> bool:
        result = self.session.query(GroupORM).filter(
            GroupORM.id == id
        ).delete()
        self.session.commit()
        return result > 0


class SQLAlchemySlotRepository(SlotRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[Slot]:
        orm_slot = self.session.query(SlotORM).filter(
            SlotORM.id == id
        ).first()

        return orm_slot.to_domain() if orm_slot else None

    def get_all(self) -> List[Slot]:
        orm_slots = self.session.query(SlotORM).all()
        return [orm_slot.to_domain() for orm_slot in orm_slots]

    def get_by_surf_plan_id(self, surf_plan_id: int) -> List[Slot]:
        orm_slots = self.session.query(SlotORM).filter(
            SlotORM.surf_plan_id == surf_plan_id
        ).all()

        return [orm_slot.to_domain() for orm_slot in orm_slots]

    def save(self, slot: Slot, surf_plan_id: int) -> Slot:
        orm_slot = SlotORM.from_domain(slot)
        orm_slot.surf_plan_id = surf_plan_id

        if orm_slot.id is None:
            self.session.add(orm_slot)
        else:
            # Update with relationships is complex
            # This would need more sophisticated handling for the groups relationship
            self.session.merge(orm_slot)

        self.session.commit()
        return orm_slot.to_domain()

    def delete(self, id: int) -> bool:
        result = self.session.query(SlotORM).filter(
            SlotORM.id == id
        ).delete()
        self.session.commit()
        return result > 0
