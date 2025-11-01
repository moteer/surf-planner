"""Test helper functions for creating test data."""
from datetime import date
from app.domain.models import Student


def create_test_student(
    id: int = 1,
    first_name: str = "Test",
    last_name: str = "Student",
    birthday: date = date(2000, 1, 1),
    gender: str = "M",
    age_group: str = "Adults >18 years",
    level: str = "BEGINNER",
    booking_number: str = "TEST001",
    arrival: date = date(2025, 6, 1),
    departure: date = date(2025, 6, 7),
    booking_status: str = "confirmed",
    number_of_surf_lessons: int = 3,
    surf_lesson_package_name: str = "Standard Package",
    tent: str = "T1",
    single_parent: bool = False
) -> Student:
    """
    Create a test student with sensible defaults.
    
    This helper function reduces test code duplication by providing
    default values for all required Student fields.
    
    Args:
        All Student fields with sensible defaults
        
    Returns:
        A Student instance with the specified or default values
    """
    return Student(
        id=id,
        first_name=first_name,
        last_name=last_name,
        birthday=birthday,
        gender=gender,
        age_group=age_group,
        level=level,
        booking_number=booking_number,
        arrival=arrival,
        departure=departure,
        booking_status=booking_status,
        number_of_surf_lessons=number_of_surf_lessons,
        surf_lesson_package_name=surf_lesson_package_name,
        tent=tent,
        single_parent=single_parent
    )
