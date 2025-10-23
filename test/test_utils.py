"""Tests for utility functions."""
import unittest
from datetime import date, timedelta

from app.utils.date_utils import get_next_sunday, get_saturday_after_sunday, is_sunday, get_week_dates
from app.utils.student_utils import (
    is_adult, is_teen, is_kid, is_level, 
    filter_active_students, filter_students_with_lessons,
    group_students_by_level_and_age
)
from test.test_helpers import create_test_student


class TestDateUtils(unittest.TestCase):
    """Tests for date utility functions."""

    def test_get_next_sunday_from_monday(self):
        """Test getting next Sunday from a Monday."""
        monday = date(2025, 6, 2)  # This is a Monday
        next_sunday = get_next_sunday(monday)
        self.assertEqual(next_sunday, date(2025, 6, 8))
        self.assertTrue(is_sunday(next_sunday))

    def test_get_next_sunday_when_already_sunday(self):
        """Test that Sunday returns itself."""
        sunday = date(2025, 6, 1)  # This is a Sunday
        next_sunday = get_next_sunday(sunday)
        self.assertEqual(next_sunday, sunday)

    def test_get_saturday_after_sunday(self):
        """Test getting the Saturday following a Sunday."""
        sunday = date(2025, 6, 1)
        saturday = get_saturday_after_sunday(sunday)
        self.assertEqual(saturday, date(2025, 6, 7))

    def test_is_sunday(self):
        """Test Sunday detection."""
        sunday = date(2025, 6, 1)
        monday = date(2025, 6, 2)
        self.assertTrue(is_sunday(sunday))
        self.assertFalse(is_sunday(monday))

    def test_get_week_dates(self):
        """Test getting all dates in a week."""
        sunday = date(2025, 6, 1)
        week_dates = get_week_dates(sunday)
        self.assertEqual(len(week_dates), 7)
        self.assertEqual(week_dates[0], sunday)
        self.assertEqual(week_dates[-1], date(2025, 6, 7))


class TestStudentUtils(unittest.TestCase):
    """Tests for student utility functions."""

    def test_is_adult(self):
        """Test adult detection."""
        adult = create_test_student(age_group="Adults >18 years")
        teen = create_test_student(age_group="Teens 13-18")
        self.assertTrue(is_adult(adult))
        self.assertFalse(is_adult(teen))

    def test_is_teen(self):
        """Test teenager detection."""
        teen = create_test_student(age_group="Teens 13-18")
        adult = create_test_student(age_group="Adults >18 years")
        self.assertTrue(is_teen(teen))
        self.assertFalse(is_teen(adult))

    def test_is_kid(self):
        """Test kid detection."""
        kid = create_test_student(age_group="Kids 5-12")
        adult = create_test_student(age_group="Adults >18 years")
        self.assertTrue(is_kid(kid))
        self.assertFalse(is_kid(adult))

    def test_is_level(self):
        """Test skill level detection."""
        beginner = create_test_student(level="BEGINNER")
        intermediate = create_test_student(level="INTERMEDIATE")
        self.assertTrue(is_level(beginner, "BEGINNER"))
        self.assertFalse(is_level(beginner, "INTERMEDIATE"))
        self.assertTrue(is_level(intermediate, "INTERMEDIATE"))

    def test_filter_active_students(self):
        """Test filtering active students."""
        active = create_test_student(id=1, booking_status="confirmed")
        cancelled = create_test_student(id=2, booking_status="cancelled")
        expired = create_test_student(id=3, booking_status="expired")
        
        students = [active, cancelled, expired]
        active_students = filter_active_students(students)
        
        self.assertEqual(len(active_students), 1)
        self.assertEqual(active_students[0].id, 1)

    def test_filter_students_with_lessons(self):
        """Test filtering students with lessons."""
        with_lessons = create_test_student(id=1, number_of_surf_lessons=3)
        without_lessons = create_test_student(id=2, number_of_surf_lessons=0)
        
        students = [with_lessons, without_lessons]
        filtered = filter_students_with_lessons(students)
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].id, 1)

    def test_group_students_by_level_and_age(self):
        """Test grouping students by level and age."""
        beginner = create_test_student(id=1, level="BEGINNER", age_group="Adults >18 years")
        intermediate = create_test_student(id=2, level="INTERMEDIATE", age_group="Adults >18 years")
        teen = create_test_student(id=3, level="BEGINNER", age_group="Teens 13-18")
        kid = create_test_student(id=4, level="BEGINNER", age_group="Kids 5-12")
        
        students = [beginner, intermediate, teen, kid]
        groups = group_students_by_level_and_age(students)
        
        self.assertEqual(len(groups['beginner']), 1)
        self.assertEqual(len(groups['intermediate']), 1)
        self.assertEqual(len(groups['teens']), 1)
        self.assertEqual(len(groups['kids']), 1)
        self.assertEqual(groups['beginner'][0].id, 1)
        self.assertEqual(groups['intermediate'][0].id, 2)
        self.assertEqual(groups['teens'][0].id, 3)
        self.assertEqual(groups['kids'][0].id, 4)


if __name__ == '__main__':
    unittest.main()
