from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from app.domain.models import Booking, Student, Instructor, Group, Slot, SurfPlan

# SQLAlchemy Base
Base = declarative_base()

# Association tables for many-to-many relationships
student_group_association = Table(
    'student_group',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

instructor_group_association = Table(
    'instructor_group',
    Base.metadata,
    Column('instructor_id', Integer, ForeignKey('instructors.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

group_slot_association = Table(
    'group_slot',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('slot_id', Integer, ForeignKey('slots.id'))
)





class StudentORM(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    birthday = Column(Date, nullable=True)
    gender = Column(String(100), nullable=True)
    age_group = Column(String(100), nullable=True)
    level = Column(String(100), nullable=True)
    booking_number = Column(String(100), nullable=True)
    arrival = Column(Date, nullable=True)
    departure = Column(Date, nullable=True)
    booking_status = Column(String(100), nullable=True)
    number_of_surf_lessons = Column(Integer, nullable=True)
    surf_lesson_package_name = Column(String(100), nullable=True)
    tent = Column(String(100), nullable=True)

    # Relationships
    groups = relationship("GroupORM", secondary=student_group_association, back_populates="students")

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}, Booking #{self.booking_number}>"

    def to_domain(self) -> Student:
        """Convert ORM model to domain model"""
        print(self.departure)
        return Student(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            birthday=self.birthday,
            gender=self.gender,
            age_group=self.age_group,
            level=self.level,
            booking_number=self.booking_number,
            arrival=self.arrival,
            departure=self.departure,
            booking_status=self.booking_status,
            number_of_surf_lessons=self.number_of_surf_lessons,
            surf_lesson_package_name=self.surf_lesson_package_name,
            tent=self.tent,
            single_parent=False
        )

    @classmethod
    def from_domain(cls, student: Student) -> 'StudentORM':
        """Create ORM model from domain model"""
        print(f"☠️{student}")
        return cls(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            birthday=student.birthday,
            gender=student.gender,
            age_group=student.age_group,
            level=student.level,
            booking_number=student.booking_number,
            arrival=student.arrival,
            departure=student.departure,
            booking_status=student.booking_status,
            number_of_surf_lessons=student.number_of_surf_lessons,
            surf_lesson_package_name=student.surf_lesson_package_name,
            tent=student.tent
        )


class InstructorORM(Base):
    __tablename__ = 'instructors'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    certification = Column(String(100), nullable=False)

    # Relationships
    groups = relationship("GroupORM", secondary=instructor_group_association, back_populates="instructors")

    def __repr__(self):
        return f"<Instructor {self.name}, Cert: {self.certification}>"

    def to_domain(self) -> Instructor:
        """Convert ORM model to domain model"""
        return Instructor(
            name=self.name,
            certification=self.certification
        )

    @classmethod
    def from_domain(cls, instructor: Instructor) -> 'InstructorORM':
        """Create ORM model from domain model"""
        return cls(
            name=instructor.name,
            certification=instructor.certification
        )


class GroupORM(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    level = Column(String(100), nullable=False)

    # Relationships
    students = relationship("StudentORM", secondary=student_group_association, back_populates="groups")
    instructors = relationship("InstructorORM", secondary=instructor_group_association, back_populates="groups")
    slots = relationship("SlotORM", secondary=group_slot_association, back_populates="groups")

    def __repr__(self):
        return f"<Group {self.level}, Students: {len(self.students)}, Instructors: {len(self.instructors)}>"

    def to_domain(self) -> Group:
        """Convert ORM model to domain model"""
        return Group(
            level=self.level,
            students=[student.to_domain() for student in self.students],
            instructors=[instructor.to_domain() for instructor in self.instructors]
        )

    @classmethod
    def from_domain(cls, group: Group) -> 'GroupORM':
        """Create ORM model from domain model"""
        group_orm = cls(level=group.level)

        # We need to handle the relationships separately to avoid circular imports
        # These would typically be populated after object creation
        return group_orm


class SlotORM(Base):
    __tablename__ = 'slots'

    id = Column(Integer, primary_key=True)
    slot_time = Column(DateTime, nullable=False)
    surf_plan_id = Column(Integer, ForeignKey('surf_plans.id'))

    # Relationships
    surf_plan = relationship("SurfPlanORM", back_populates="slots")
    groups = relationship("GroupORM", secondary=group_slot_association, back_populates="slots")

    def __repr__(self):
        return f"<Slot {self.slot_time}>"

    def to_domain(self) -> Slot:
        """Convert ORM model to domain model"""
        return Slot(
            slot_time=self.slot_time,
            groups=[group.to_domain() for group in self.groups]
        )

    @classmethod
    def from_domain(cls, slot: Slot) -> 'SlotORM':
        """Create ORM model from domain model"""
        slot_orm = cls(slot_time=slot.slot_time)

        # Groups relationship would be populated after creation
        return slot_orm


class SurfPlanORM(Base):
    __tablename__ = 'surf_plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_date = Column(Date, nullable=False, unique=True)

    # Relationships
    slots = relationship("SlotORM", back_populates="surf_plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SurfPlan {self.plan_date}, Slots: {len(self.slots)}>"

    def to_domain(self) -> SurfPlan:
        """Convert ORM model to domain model"""
        return SurfPlan(
            id=self.id,
            plan_date=self.plan_date,
            slots=[slot.to_domain() for slot in self.slots]
        )

    @classmethod
    def from_domain(cls, surf_plan: SurfPlan) -> 'SurfPlanORM':
        """Create ORM model from domain model"""
        return cls(
            id=surf_plan.id,
            date=surf_plan.plan_date,
            slots=[SlotORM.from_domain(slot) for slot in surf_plan.slots]
        )


class RawBookingORM(Base):
    __tablename__ = "bookings"
    __mapper_args__ = {
        "primary_key": ["guest_first_name", "guest_last_name", "booking_id"]
    }

    booking_id = Column(String(100), nullable=False)
    booker_id = Column(String(100), nullable=False)
    guest_first_name = Column(String(100), nullable=False)
    guest_last_name = Column(String(100), nullable=False)

    guest_birthday = Column(Date)
    guest_gender = Column(String(100))
    guest_group = Column(String(100))
    guest_level = Column(String(100))
    guest_arrival_date = Column(Date)
    guest_departure_date = Column(Date)
    booking_status = Column(String(100))

    # Surf lesson options
    surf_lesson_adults_main_season_package = Column(String(10))
    surf_lesson_adults_main_season_package_qty = Column(Integer)
    surf_lesson_kids_main_season_package = Column(String(10))
    surf_lesson_kids_main_season_package_qty = Column(Integer)
    surf_course_adults = Column(String(10))
    surf_course_adults_qty = Column(Integer)
    surf_course_kids = Column(String(10))
    surf_course_kids_qty = Column(Integer)
    surf_lessons = Column(String(10))
    surf_lessons_qty = Column(Integer)
    surf_course = Column(String(10))
    surf_course_qty = Column(Integer)
    _5_day_surf_course_teens \
        = Column("5_day_surf_course_teens_from_14____18_years_old", String(10), key="_5_day_surf_course_teens")
    _5_day_surf_course_teens_from_14____18_years_old_qty \
        = Column("5_day_surf_course_teens_from_14____18_years_old_qty", Integer, key="_5_day_surf_course_teens_qty")
    trial_surf_lesson_kids = Column(String(10))
    trial_surf_lesson_kids_qty = Column(Integer)
    guest_diet = Column(String(20))
    notes_one = Column("notes_guest", String(100), key="notes_one")
    accommodations = Column(String(100))

    def to_domain(self) -> Booking:
        """Convert ORM model to domain model"""
        def get_package_name():
            if self.surf_lesson_adults_main_season_package.lower() == "yes":
                return "surf lesson adult main season package"
            if self.surf_lesson_kids_main_season_package.lower() == "yes":
                return "surf lesson kids main season package"
            if self.surf_course_adults.lower() == "yes":
                return "surf course adult"
            if self.surf_course_kids.lower() == "yes":
                return "surf course kids"
            if self.surf_lessons.lower() == "yes":
                return "surf lessons"
            if self.surf_course.lower() == "yes":
                return "surf course"
            if self._5_day_surf_course_teens.lower() == "yes":
                return "5 day surf course teens from 14 - 18 years old"
            if self.trial_surf_lesson_kids.lower() == "yes":
                return "trial surf lesson kids"

            return "No package booked"

        return Booking(
            booking_id=self.booking_id,
            booker_id=self.booker_id,
            first_name=self.guest_first_name,
            last_name=self.guest_last_name,
            birthday=self.extract_date(self.guest_birthday),
            gender=self.guest_gender,
            group=self.guest_group,
            level=self.guest_level,
            arrival=self.extract_date(self.guest_arrival_date),
            departure=self.extract_date(self.guest_departure_date),
            booking_status=self.booking_status,
            number_of_surf_lessons=sum([
                 int(self.surf_lesson_adults_main_season_package_qty),
                 int(self.surf_lesson_kids_main_season_package_qty),
                 int(self.surf_course_adults_qty),
                 int(self.surf_course_kids_qty),
                 int(self.surf_lessons_qty),
                 int(self.surf_course_qty),
                 int(self._5_day_surf_course_teens_from_14____18_years_old_qty),
                 int(self.trial_surf_lesson_kids_qty)
             ]),
            surf_lesson_package_name=get_package_name(),
            diet=self.guest_diet,
            notes_one=self.notes_one,
            tent=self.accommodations
        )

    def extract_date(self, str_to_date):

        return None if not str_to_date else datetime.strptime(str_to_date, '%Y-%m-%d').date()
