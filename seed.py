# seed.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import date, timedelta

from app.data.orm_models import StudentORM  # Your actual model
from app.core.db import Base  # Base from your DB setup

# Set up DB connection (replace with real credentials or use config.py if available)
engine = create_engine("mysql+pymysql://root:rootroot@localhost/surfplanner")
Session = sessionmaker(bind=engine)
session = Session()

# Optional: create tables
Base.metadata.create_all(engine)

# Create 10 sample students
today = date.today()
students = [
    StudentORM(
        first_name="Alice",
        last_name="Smith",
        birthday=date(2005, 5, 15),
        gender="Female",
        age_group="Teen",
        level="Beginner",
        booking_number="BOOK0001",
        arrival=today,
        departure=today + timedelta(days=7)
    ),
    StudentORM(
        first_name="Bob",
        last_name="Johnson",
        birthday=date(2004, 3, 22),
        gender="Male",
        age_group="Teen",
        level="Intermediate",
        booking_number="BOOK0002",
        arrival=today,
        departure=today + timedelta(days=7)
    ),
    StudentORM(
        first_name="Carol",
        last_name="Lee",
        birthday=date(1998, 7, 8),
        gender="Female",
        age_group="Adult",
        level="Advanced",
        booking_number="BOOK0003",
        arrival=today,
        departure=today + timedelta(days=7)
    ),
    StudentORM(
        first_name="Dan",
        last_name="Kim",
        birthday=date(2003, 9, 17),
        gender="Male",
        age_group="Teen",
        level="Beginner",
        booking_number="BOOK0004",
        arrival=today,
        departure=today + timedelta(days=7)
    ),
    StudentORM(
        first_name="Eva",
        last_name="Brown",
        birthday=date(1995, 12, 30),
        gender="Female",
        age_group="Adult",
        level="Intermediate",
        booking_number="BOOK0005",
        arrival=today,
        departure=today + timedelta(days=7)
    ),
    StudentORM(
        first_name="Frank",
        last_name="Green",
        birthday=date(2000, 1, 10),
        gender="Male",
        age_group="Adult",
        level="Advanced",
        booking_number="BOOK0006",
        arrival=today,
        departure=today + timedelta(days=7)
    ),
    StudentORM(
        first_name="Grace",
        last_name="Park",
        birthday=date(2006, 11, 25),
        gender="Female",
        age_group="Teen",
        level="Beginner",
        booking_number="BOOK0007",
        arrival=today,
        departure=today + timedelta(days=10)
    ),
    StudentORM(
        first_name="Hank",
        last_name="White",
        birthday=date(1999, 6, 6),
        gender="Male",
        age_group="Adult",
        level="Intermediate",
        booking_number="BOOK0008",
        arrival=today,
        departure=today + timedelta(days=1)
    ),
    StudentORM(
        first_name="Ivy",
        last_name="Hall",
        birthday=date(2002, 2, 19),
        gender="Female",
        age_group="Adult",
        level="Advanced",
        booking_number="BOOK0009",
        arrival=today,
        departure=today + timedelta(days=3)
    ),
    StudentORM(
        first_name="Jack",
        last_name="Young",
        birthday=date(2001, 4, 3),
        gender="Male",
        age_group="Adult",
        level="Beginner",
        booking_number="BOOK0010",
        arrival=today,
        departure=today + timedelta(days=2)
    ),
]

# Insert into DB
session.add_all(students)
session.commit()

print("✅ Seeded 10 students successfully.")
