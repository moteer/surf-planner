from datetime import date
from app.domain.repositories_interfaces import StudentRepositoryInterface


def is_adult(student):
    age_group = student.age_group if student.age_group else "adult"
    print(age_group)
    return 'Adult' in age_group


def is_teen(student):
    age_group = student.age_group if student.age_group else "adult"
    return 'Teens' in age_group


def is_kid(student):
    age_group = student.age_group if student.age_group else "adult"
    return 'Kids' in age_group


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
        if not isinstance(start_date, date):
            raise Exception("Parameter must be a date")

        if start_date > end_date:
            raise Exception("Start date must be before end date")

        students = [student for student in self.student_repository.get_all() if
                    student.arrival <= end_date and student.departure >= start_date]

        adults = [student for student in students if is_adult(student)]
        print("adults:")
        print(len(adults))
        print(adults)
        # have kids or teens and no other parent with same booking number
        for parent in adults:
            print("check potential parent:")
            print(parent)
            if (0 == len([student for student in students if
                          is_adult(parent) and
                          student != parent and
                          student.booking_number == parent.booking_number and
                          is_adult(student)])):
                print("is a single parent:")
                print(parent)
                if (0 < len([student for student in students if
                             student != parent and student.booking_number == parent.booking_number and
                             (is_kid(student) or is_teen(student))])):
                    print("single parent has kids:")
                    print(parent)
                    parent.single_parent = True

        return [student for student in students if student.number_of_surf_lessons > 0]

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
