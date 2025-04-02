from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.domain.models import Student, Instructor, Group, Slot, SurfPlan

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
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    age_group = Column(String, nullable=False)
    level = Column(String, nullable=False)
    booking_number = Column(String, nullable=False, unique=True)

    # Relationships
    groups = relationship("GroupORM", secondary=student_group_association, back_populates="students")

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}, Booking #{self.booking_number}>"

    def to_domain(self) -> Student:
        """Convert ORM model to domain model"""
        return Student(
            first_name=self.first_name,
            last_name=self.last_name,
            birthday=self.birthday,
            gender=self.gender,
            age_group=self.age_group,
            level=self.level,
            booking_number=self.booking_number
        )

    @classmethod
    def from_domain(cls, student: Student) -> 'StudentORM':
        """Create ORM model from domain model"""
        return cls(
            first_name=student.first_name,
            last_name=student.last_name,
            birthday=student.birthday,
            gender=student.gender,
            age_group=student.age_group,
            level=student.level,
            booking_number=student.booking_number
        )


class InstructorORM(Base):
    __tablename__ = 'instructors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    certification = Column(String, nullable=False)

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
    level = Column(String, nullable=False)

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
