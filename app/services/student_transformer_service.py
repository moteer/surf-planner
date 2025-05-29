from app.data.orm_models import Student
from app.domain.repositories_interfaces import BookingRawRepositoryInterface, StudentRepositoryInterface
from collections import Counter
from deepdiff import DeepDiff

class StudentTransformerService:

    def __init__(self, bookings_repository: BookingRawRepositoryInterface,
                 student_repository: StudentRepositoryInterface):
        self.bookings_repository = bookings_repository
        self.student_repository = student_repository

    def match_save_students(self, students_to_merge, students_in_db):
        """
        Matches students from CSV (students_to_merge) to existing students in DB (students_in_db),
        and performs create/update operations via repository.
        """
        matched_indices = set()

        for incoming_student in students_to_merge:
            match = None

            # Try to find the best match in students_in_db
            for i, existing_student in enumerate(students_in_db):
                if i in matched_indices:
                    continue

                if self._is_probable_match(incoming_student, existing_student):
                    match = existing_student
                    matched_indices.add(i)
                    break

            if match:
                if self._has_changed(incoming_student, match):
                    print(f"🔁 Updating student {incoming_student.booking_number}: {incoming_student.first_name} {incoming_student.last_name}")
                    self.student_repository.update(match.id, incoming_student)
                # else:
                #     print(f"✅ No change for student {incoming_student.booking_number}: {incoming_student.first_name} {incoming_student.last_name}")
            else:
                print(f"➕ Adding new student {incoming_student.booking_number}: {incoming_student.first_name} {incoming_student.last_name}")
                self.student_repository.save(incoming_student)


    def _is_probable_match(self, student1, student2):
        """Basic heuristic to guess if two students are the same person."""
        return (
                student1.booking_number == student2.booking_number and
                student1.gender == student2.gender and
                student1.age_group == student2.age_group and
                student1.arrival == student2.arrival and
                student1.departure == student2.departure
        )

    def _has_changed(self, student_new, student_existing):
        """Check and log differences between two Student instances."""
        diff = DeepDiff(
            student_existing.__dict__,
            student_new.__dict__,
            ignore_order=True,
            exclude_paths={"root['id']"}
        )

        if diff:
            print(f"🔍 Changes detected for booking #{student_new.booking_number}:")
            print(diff.pretty())  # ← nicely formatted output
            return True
        return False

    def transform_all_bookings_into_students(self):
        incoming_students = {}
        incoming_bookings = self.bookings_repository.get_all()
        for incoming_booking in incoming_bookings:
            incoming_students.setdefault(incoming_booking.booker_id, []).append(Student(
                id=None,
                first_name=incoming_booking.first_name,
                last_name=incoming_booking.last_name,
                birthday=incoming_booking.birthday,
                gender=incoming_booking.gender,
                age_group=incoming_booking.group,
                level=incoming_booking.level,
                booking_number=incoming_booking.booker_id,
                arrival=incoming_booking.arrival,
                departure=incoming_booking.departure,
                booking_status=incoming_booking.booking_status,
                number_of_surf_lessons=incoming_booking.number_of_surf_lessons,
                surf_lesson_package_name=incoming_booking.surf_lesson_package_name)
            )

        for booking_number, _students in incoming_students.items():
            students_in_db = self.student_repository.get_by_booking_number(booking_number)
            if not students_in_db:
                self.student_repository.save_all(_students)
            else:
                self.match_save_students(_students, students_in_db)

        return incoming_students

    def determine_age_group(age_raw):
        """Converts age string or number into a group label."""
        try:
            age = int(float(age_raw))
            if age < 13:
                return "child"
            elif age < 18:
                return "teen"
            else:
                return "adult"
        except Exception:
            return "unknown"
