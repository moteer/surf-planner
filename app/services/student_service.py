from datetime import date
from app.domain.repositories_interfaces import StudentRepositoryInterface


class StudentService:

    def __init__(self, student_repository: StudentRepositoryInterface):
        self.student_repository = student_repository
        self.students = []

    def get_all_students(self):
        return self.student_repository.get_all()

    def get_students_by_date_range(self, start_date: date, end_date: date):
        if not isinstance(start_date, date):
            raise Exception("Parameter must be a date")

        if start_date > end_date:
            raise Exception("Start date must be before end date")

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
