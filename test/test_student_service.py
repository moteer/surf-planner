import unittest
from unittest.mock import Mock
from datetime import date, datetime

from app.domain.models import SurfPlan, Slot, Group, Student, Instructor
from app.domain.repositories_interfaces import StudentRepositoryInterface
from app.services.student_service import StudentService
from test.test_helpers import create_test_student



class TestStudentService(unittest.TestCase):
    # range: start: 2025, 7, 1  end: 25, 7, 3
    # 1 student_exact_range: 2025, 7, 1 – 25, 7, arrival = start, dep = end
    # 2 student_starts_before: 2025, 6, 29 – 25, 7, 3, arrival < start, dep = end
    # 3 student_ends_after: 2025, 7, 01 – 25, 7, 5, arrival = start, dep > end
    # 4 student_starts_before_ends_after 2025, 6, 29 – 25, 7, 5, arrival < start, dep > end
    # 5 student_inside_range 2025, 7, 2 – 25, 7, 3, arrival > start, dep = end
    # 6 student_start_before_ends_within 2025, 6, 29 – 25, 7, 2, arrival < start, dep < end
    # 7 student_starts_within_ends_after 2025, 7, 2 – 25, 7, 5, arrival > start, dep > end
    # 8 student_completely_before 2025, 6, 2 – 25, 6, 29, arrival > start, dep < start
    # 9 student_completely_after 2025, 7, 5 – 25, 7, 29, arrival > end, dep > end

    student_exact_range = create_test_student(
        id=1,
        first_name="Anna",
        last_name="Schmidt",
        birthday=date(2010, 5, 14),
        gender="female",
        age_group="child",
        level="beginner",
        booking_number="BN12345",
        arrival=date(2025, 7, 1),
        departure=date(2025, 7, 3),
        number_of_surf_lessons=3
    )

    student_starts_before = create_test_student(
        id=2,
        first_name="Lukas",
        last_name="Meier",
        birthday=date(2005, 8, 22),
        gender="male",
        age_group="teen",
        level="beginner",
        booking_number="BN67890",
        arrival=date(2025, 6, 29),
        departure=date(2025, 7, 3),
        number_of_surf_lessons=3
    )

    student_ends_after = create_test_student(
        id=3,
        first_name="Erik",
        last_name="Müller",
        birthday=date(1950, 8, 22),
        gender="male",
        age_group="teen",
        level="intermediate",
        booking_number="BN67890",
        arrival=date(2025, 7, 1),
        departure=date(2025, 7, 5),
        number_of_surf_lessons=3
    )
    
    student_starts_before_ends_after = create_test_student(
        id=4,
        first_name="Mia",
        last_name="Hoffmann",
        birthday=date(2011, 3, 12),
        gender="female",
        age_group="child",
        level="beginner",
        booking_number="BN11111",
        arrival=date(2025, 6, 29),
        departure=date(2025, 7, 5),
        number_of_surf_lessons=3
    )
    
    student_inside_range = create_test_student(
        id=5,
        first_name="Ben",
        last_name="Schneider",
        birthday=date(2008, 11, 5),
        gender="male",
        age_group="teen",
        level="beginner",
        booking_number="BN22222",
        arrival=date(2025, 7, 2),
        departure=date(2025, 7, 3),
        number_of_surf_lessons=3
    )
    
    student_start_before_ends_within = create_test_student(
        id=6,
        first_name="Lea",
        last_name="Fischer",
        birthday=date(2012, 6, 21),
        gender="female",
        age_group="child",
        level="intermediate",
        booking_number="BN33333",
        arrival=date(2025, 6, 29),
        departure=date(2025, 7, 2),
        number_of_surf_lessons=3
    )
    
    student_starts_within_ends_after = create_test_student(
        id=7,
        first_name="Paul",
        last_name="Weber",
        birthday=date(2007, 9, 17),
        gender="male",
        age_group="teen",
        level="advanced",
        booking_number="BN44444",
        arrival=date(2025, 7, 2),
        departure=date(2025, 7, 5),
        number_of_surf_lessons=3
    )
    
    student_completely_before = create_test_student(
        id=8,
        first_name="Emma",
        last_name="Wagner",
        birthday=date(2009, 1, 3),
        gender="female",
        age_group="teen",
        level="intermediate",
        booking_number="BN55555",
        arrival=date(2025, 6, 2),
        departure=date(2025, 6, 29),
        number_of_surf_lessons=3
    )
    
    student_completely_after = create_test_student(
        id=9,
        first_name="Tom",
        last_name="Becker",
        birthday=date(2010, 10, 30),
        gender="male",
        age_group="child",
        level="beginner",
        booking_number="BN66666",
        arrival=date(2025, 7, 5),
        departure=date(2025, 7, 29),
        number_of_surf_lessons=3
    )

    fake_students = []

    def setup_range_students(self):

        self.fake_students.clear()

        self.fake_students.extend([
        self.student_exact_range, self.student_starts_before, self.student_ends_after, self.student_starts_before_ends_after,
        self.student_inside_range, self.student_start_before_ends_within, self.student_starts_within_ends_after, self.student_completely_before,
        self.student_completely_after
    ])

    # further test cases:
    # Test Error when end date precedes start_date
    # Test: Type error when non-date inputs are passed
    # Test: Repository error (e.g., database call failure)

    # Test: Checking students that overlap with a valid date range
    def test_get_students_for_complete_range (self):

        mock_repository : StudentRepositoryInterface = Mock()
        mock_repository.get_all.return_value = self.fake_students

        self.setup_range_students()
        student_service = StudentService(mock_repository)

        present_students = student_service.get_students_with_booked_lessons_by_date_range(date(2025, 7, 1), date(2025, 7, 3))
        self.assertEqual(
            present_students,
            [
                self.student_exact_range,
                self.student_starts_before,
                self.student_ends_after,
                self.student_starts_before_ends_after,
                self.student_inside_range,
                self.student_start_before_ends_within,
                self.student_starts_within_ends_after            ]
        )

        # Verify repository methods were called
        mock_repository.get_all.assert_called_once()

    #  Test: Checking students that overlap with a range where start date == end date
    def test_returns_students_for_single_day_range (self):

        mock_repository : StudentRepositoryInterface = Mock()
        mock_repository.get_all.return_value = self.fake_students

        self.setup_range_students()
        student_service = StudentService(mock_repository)

        present_students = student_service.get_students_with_booked_lessons_by_date_range(date(2025, 7, 3), date(2025, 7, 3))
        self.assertEqual(
            present_students,
            [
                self.student_exact_range,
                self.student_starts_before,
                self.student_ends_after,
                self.student_starts_before_ends_after,
                self.student_inside_range,
                self.student_starts_within_ends_after            ]
        )

        # Verify repository methods were called
        mock_repository.get_all.assert_called_once()
