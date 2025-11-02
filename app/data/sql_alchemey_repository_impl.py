from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.repositories_interfaces import (
    BookingRawRepositoryInterface, SurfPlanRepositoryInterface,
    StudentRepositoryInterface, InstructorRepository, GroupRepository,
    SlotRepository, CrewMemberRepositoryInterface, PositionRepositoryInterface,
    CrewAssignmentRepositoryInterface, AccommodationRepositoryInterface,
    AccommodationAssignmentRepositoryInterface
)
from app.domain.models import SurfPlan, Student, Instructor, Group, Slot, CrewMember, Position, CrewAssignment, Accommodation, AccommodationAssignment, Team
from app.data.orm_models import SurfPlanORM, StudentORM, InstructorORM, GroupORM, SlotORM, RawBookingORM, CrewMemberORM, PositionORM, CrewAssignmentORM, AccommodationORM, AccommodationAssignmentORM
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


# Crew Planner Repository Implementations

class SQLAlchemyCrewMemberRepositoryImpl(CrewMemberRepositoryInterface):
    """SQLAlchemy implementation of the CrewMemberRepository interface"""
    
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[CrewMember]:
        """Get all crew members"""
        orm_crew_members = self.session.query(CrewMemberORM).all()
        return [crew.to_domain() for crew in orm_crew_members]

    def get_by_id(self, id: int) -> Optional[CrewMember]:
        """Get a crew member by ID"""
        orm_crew = self.session.query(CrewMemberORM).filter(
            CrewMemberORM.id == id
        ).first()
        return orm_crew.to_domain() if orm_crew else None

    def get_by_team(self, team: Team) -> List[CrewMember]:
        """Get all crew members for a specific team"""
        orm_crew_members = self.session.query(CrewMemberORM).filter(
            CrewMemberORM.team == team
        ).all()
        return [crew.to_domain() for crew in orm_crew_members]

    def save(self, crew_member: CrewMember) -> CrewMember:
        """Save or update a crew member"""
        orm_crew = CrewMemberORM.from_domain(crew_member)
        if crew_member.id:
            self.session.merge(orm_crew)
        else:
            self.session.add(orm_crew)
        self.session.commit()
        self.session.refresh(orm_crew)
        return orm_crew.to_domain()

    def delete(self, id: int) -> bool:
        """Delete a crew member by ID"""
        result = self.session.query(CrewMemberORM).filter(
            CrewMemberORM.id == id
        ).delete()
        self.session.commit()
        return result > 0


class SQLAlchemyPositionRepositoryImpl(PositionRepositoryInterface):
    """SQLAlchemy implementation of the PositionRepository interface"""
    
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Position]:
        """Get all positions"""
        orm_positions = self.session.query(PositionORM).all()
        return [pos.to_domain() for pos in orm_positions]

    def get_by_id(self, id: int) -> Optional[Position]:
        """Get a position by ID"""
        orm_position = self.session.query(PositionORM).filter(
            PositionORM.id == id
        ).first()
        return orm_position.to_domain() if orm_position else None

    def get_by_team(self, team: Team) -> List[Position]:
        """Get all positions for a specific team"""
        orm_positions = self.session.query(PositionORM).filter(
            PositionORM.team == team
        ).all()
        return [pos.to_domain() for pos in orm_positions]

    def save(self, position: Position) -> Position:
        """Save or update a position"""
        orm_position = PositionORM.from_domain(position)
        if position.id:
            self.session.merge(orm_position)
        else:
            self.session.add(orm_position)
        self.session.commit()
        self.session.refresh(orm_position)
        return orm_position.to_domain()

    def delete(self, id: int) -> bool:
        """Delete a position by ID"""
        result = self.session.query(PositionORM).filter(
            PositionORM.id == id
        ).delete()
        self.session.commit()
        return result > 0


class SQLAlchemyCrewAssignmentRepositoryImpl(CrewAssignmentRepositoryInterface):
    """SQLAlchemy implementation of the CrewAssignmentRepository interface"""
    
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[CrewAssignment]:
        """Get all crew assignments"""
        orm_assignments = self.session.query(CrewAssignmentORM).all()
        return [assign.to_domain() for assign in orm_assignments]

    def get_by_id(self, id: int) -> Optional[CrewAssignment]:
        """Get a crew assignment by ID"""
        orm_assignment = self.session.query(CrewAssignmentORM).filter(
            CrewAssignmentORM.id == id
        ).first()
        return orm_assignment.to_domain() if orm_assignment else None

    def get_by_date_range(self, start_date: date, end_date: date) -> List[CrewAssignment]:
        """Get crew assignments within a date range"""
        orm_assignments = self.session.query(CrewAssignmentORM).filter(
            and_(
                CrewAssignmentORM.assignment_date >= start_date,
                CrewAssignmentORM.assignment_date <= end_date
            )
        ).all()
        return [assign.to_domain() for assign in orm_assignments]

    def get_by_crew_member(self, crew_member_id: int) -> List[CrewAssignment]:
        """Get all assignments for a specific crew member"""
        orm_assignments = self.session.query(CrewAssignmentORM).filter(
            CrewAssignmentORM.crew_member_id == crew_member_id
        ).all()
        return [assign.to_domain() for assign in orm_assignments]

    def save(self, assignment: CrewAssignment) -> CrewAssignment:
        """Save or update a crew assignment"""
        orm_assignment = CrewAssignmentORM.from_domain(assignment)
        if assignment.id:
            self.session.merge(orm_assignment)
        else:
            self.session.add(orm_assignment)
        self.session.commit()
        self.session.refresh(orm_assignment)
        return orm_assignment.to_domain()

    def delete(self, id: int) -> bool:
        """Delete a crew assignment by ID"""
        result = self.session.query(CrewAssignmentORM).filter(
            CrewAssignmentORM.id == id
        ).delete()
        self.session.commit()
        return result > 0


class SQLAlchemyAccommodationRepositoryImpl(AccommodationRepositoryInterface):
    """SQLAlchemy implementation of the AccommodationRepository interface"""
    
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Accommodation]:
        """Get all accommodations"""
        orm_accommodations = self.session.query(AccommodationORM).all()
        return [acc.to_domain() for acc in orm_accommodations]

    def get_by_id(self, id: int) -> Optional[Accommodation]:
        """Get an accommodation by ID"""
        orm_accommodation = self.session.query(AccommodationORM).filter(
            AccommodationORM.id == id
        ).first()
        return orm_accommodation.to_domain() if orm_accommodation else None

    def save(self, accommodation: Accommodation) -> Accommodation:
        """Save or update an accommodation"""
        orm_accommodation = AccommodationORM.from_domain(accommodation)
        if accommodation.id:
            self.session.merge(orm_accommodation)
        else:
            self.session.add(orm_accommodation)
        self.session.commit()
        self.session.refresh(orm_accommodation)
        return orm_accommodation.to_domain()

    def delete(self, id: int) -> bool:
        """Delete an accommodation by ID"""
        result = self.session.query(AccommodationORM).filter(
            AccommodationORM.id == id
        ).delete()
        self.session.commit()
        return result > 0


class SQLAlchemyAccommodationAssignmentRepositoryImpl(AccommodationAssignmentRepositoryInterface):
    """SQLAlchemy implementation of the AccommodationAssignmentRepository interface"""
    
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[AccommodationAssignment]:
        """Get all accommodation assignments"""
        orm_assignments = self.session.query(AccommodationAssignmentORM).all()
        return [assign.to_domain() for assign in orm_assignments]

    def get_by_id(self, id: int) -> Optional[AccommodationAssignment]:
        """Get an accommodation assignment by ID"""
        orm_assignment = self.session.query(AccommodationAssignmentORM).filter(
            AccommodationAssignmentORM.id == id
        ).first()
        return orm_assignment.to_domain() if orm_assignment else None

    def get_by_crew_member(self, crew_member_id: int) -> List[AccommodationAssignment]:
        """Get all accommodation assignments for a specific crew member"""
        orm_assignments = self.session.query(AccommodationAssignmentORM).filter(
            AccommodationAssignmentORM.crew_member_id == crew_member_id
        ).all()
        return [assign.to_domain() for assign in orm_assignments]

    def get_by_date_range(self, start_date: date, end_date: date) -> List[AccommodationAssignment]:
        """Get accommodation assignments that overlap with the given date range"""
        orm_assignments = self.session.query(AccommodationAssignmentORM).filter(
            and_(
                AccommodationAssignmentORM.start_date <= end_date,
                AccommodationAssignmentORM.end_date >= start_date
            )
        ).all()
        return [assign.to_domain() for assign in orm_assignments]

    def get_by_accommodation_and_date_range(self, accommodation_id: int, start_date: date, end_date: date) -> List[AccommodationAssignment]:
        """Get accommodation assignments for a specific accommodation that overlap with the given date range"""
        orm_assignments = self.session.query(AccommodationAssignmentORM).filter(
            and_(
                AccommodationAssignmentORM.accommodation_id == accommodation_id,
                AccommodationAssignmentORM.start_date <= end_date,
                AccommodationAssignmentORM.end_date >= start_date
            )
        ).all()
        return [assign.to_domain() for assign in orm_assignments]

    def save(self, assignment: AccommodationAssignment) -> AccommodationAssignment:
        """Save or update an accommodation assignment"""
        orm_assignment = AccommodationAssignmentORM.from_domain(assignment)
        if assignment.id:
            self.session.merge(orm_assignment)
        else:
            self.session.add(orm_assignment)
        self.session.commit()
        self.session.refresh(orm_assignment)
        return orm_assignment.to_domain()

    def delete(self, id: int) -> bool:
        """Delete an accommodation assignment by ID"""
        result = self.session.query(AccommodationAssignmentORM).filter(
            AccommodationAssignmentORM.id == id
        ).delete()
        self.session.commit()
        return result > 0
