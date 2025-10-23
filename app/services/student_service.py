import logging
from datetime import date
from app.domain.repositories_interfaces import StudentRepositoryInterface
from app.utils.student_utils import is_adult, is_teen, is_kid

logger = logging.getLogger(__name__)


class StudentService:

    def __init__(self, student_repository: StudentRepositoryInterface):
        self.student_repository = student_repository
        self.students = []

    def get_all_students(self):
        return self.student_repository.get_all()

    def get_all_students_for_date(self, _date):
        return [student for student in self.student_repository.get_all_by_date_range(_date, _date)
                if student.booking_status != "cancelled"]

    def get_students_with_booked_lessons_by_date_range(self, start_date: date, end_date: date):
        """
        Get students with booked surf lessons in the specified date range.
        Also identifies and marks single parents.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of students with booked lessons
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not isinstance(start_date, date):
            raise ValueError("Parameter must be a date")

        if start_date > end_date:
            raise ValueError("Start date must be before end date")

        students = [student for student in self.student_repository.get_all() if
                    student.arrival <= end_date and student.departure >= start_date]

        adults = [student for student in students if is_adult(student)]
        logger.debug(f"Found {len(adults)} adult students")
        
        # Identify single parents: have kids or teens and no other parent with same booking number
        for parent in adults:
            logger.debug(f"Checking potential parent: {parent.first_name} {parent.last_name}")
            if (0 == len([student for student in students if
                          is_adult(parent) and
                          student != parent and
                          student.booking_number == parent.booking_number and
                          is_adult(student)])):
                logger.debug(f"Parent {parent.first_name} is potentially single parent")
                if (0 < len([student for student in students if
                             student != parent and student.booking_number == parent.booking_number and
                             (is_kid(student) or is_teen(student))])):
                    logger.info(f"Marking {parent.first_name} {parent.last_name} as single parent")
                    parent.single_parent = True

        return [student for student in students if student.number_of_surf_lessons > 0]

    def get_students_by_date_range(self, start_date: date, end_date: date):
        """
        Get all students in the specified date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            List of students whose stay overlaps with the date range
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not isinstance(start_date, date):
            raise ValueError("Parameter must be a date")

        if start_date > end_date:
            raise ValueError("Start date must be before end date")

        students = self.student_repository.get_all()

        return [student for student in students if student.arrival <= end_date and student.departure >= start_date]

    def get_students_by_level(self, level: str):

        students = self.get_students_from_repo_fake()

        valid_levels = {student.level for student in students}
        if level not in valid_levels:
            return None
        return [student for student in students if student.level == level]

    def save_all(self, students):
        for student in students:
            self.student_repository.save(student)
