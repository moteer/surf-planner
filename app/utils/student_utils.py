"""Student utility functions for categorization and filtering."""
from typing import List, Dict
from app.domain.models import Student


def is_adult(student: Student) -> bool:
    """
    Check if a student is an adult based on their age group.
    
    Args:
        student: The student to check
        
    Returns:
        True if the student is an adult (18+ years), False otherwise
    """
    age_group = student.age_group if student.age_group else "adult"
    age_group_lower = age_group.lower()
    # Check for teen or kid first, if found it's not an adult
    if 'teen' in age_group_lower or 'kid' in age_group_lower:
        return False
    # Otherwise check for adult indicators or default to adult
    return 'adult' in age_group_lower or '>18' in age_group or '18 - 60' in age_group or not age_group


def is_teen(student: Student) -> bool:
    """
    Check if a student is a teenager based on their age group.
    
    Args:
        student: The student to check
        
    Returns:
        True if the student is a teenager (13-18 years), False otherwise
    """
    age_group = student.age_group if student.age_group else "adult"
    age_group_lower = age_group.lower()
    return 'teen' in age_group_lower or '13 - 18' in age_group or '13-18' in age_group


def is_kid(student: Student) -> bool:
    """
    Check if a student is a kid based on their age group.
    
    Args:
        student: The student to check
        
    Returns:
        True if the student is a kid (5-12 years), False otherwise
    """
    age_group = student.age_group if student.age_group else "adult"
    age_group_lower = age_group.lower()
    return 'kid' in age_group_lower or '5 - 12' in age_group or '5-12' in age_group


def is_level(student: Student, level: str) -> bool:
    """
    Check if a student has a specific skill level.
    
    Args:
        student: The student to check
        level: The skill level to compare (e.g., "BEGINNER", "INTERMEDIATE")
        
    Returns:
        True if the student's level matches the specified level
    """
    student_level = (student.level or "BEGINNER").strip().upper()
    return student_level == level


def filter_active_students(students: List[Student]) -> List[Student]:
    """
    Filter out students with cancelled or expired bookings.
    
    Args:
        students: List of students to filter
        
    Returns:
        List of students with active bookings
    """
    return [
        student for student in students
        if student.booking_status != "cancelled" and student.booking_status != "expired"
    ]


def filter_students_with_lessons(students: List[Student]) -> List[Student]:
    """
    Filter students who have booked surf lessons.
    
    Args:
        students: List of students to filter
        
    Returns:
        List of students who have at least one surf lesson booked
    """
    return [student for student in students if student.number_of_surf_lessons > 0]


def group_students_by_level_and_age(students: List[Student]) -> Dict[str, List[Student]]:
    """
    Categorize students into groups by skill level and age group.
    
    Args:
        students: List of students to categorize
        
    Returns:
        Dictionary with keys: 'beginner', 'beginner_plus', 'intermediate', 
        'advanced', 'teens', 'kids' containing lists of students
    """
    groups = {
        'beginner': [],
        'beginner_plus': [],
        'intermediate': [],
        'advanced': [],
        'teens': [],
        'kids': []
    }
    
    for student in students:
        if is_teen(student):
            groups['teens'].append(student)
        elif is_kid(student):
            groups['kids'].append(student)
        elif is_adult(student):
            if is_level(student, "BEGINNER"):
                groups['beginner'].append(student)
            elif is_level(student, "BEGINNER PLUS"):
                groups['beginner_plus'].append(student)
            elif is_level(student, "INTERMEDIATE"):
                groups['intermediate'].append(student)
            elif is_level(student, "ADVANCED"):
                groups['advanced'].append(student)
            else:
                # Default to beginner for unknown levels
                groups['beginner'].append(student)
    
    return groups
