from datetime import date, datetime, timedelta
from app.domain.repositories_interfaces import SurfPlanRepositoryInterface
from app.services.student_service import StudentService
from app.domain.models import Slot, SurfPlan, Student, Group, Instructor
from typing import Dict, Tuple, List
import math

from app.services.tide_service_interface import TideServiceInterface



class SurfPlanService:
    def __init__(self, surf_plan_repository: SurfPlanRepositoryInterface,
                 student_service: StudentService,
                 tide_service: TideServiceInterface):

        self.surf_plan_repository = surf_plan_repository
        self.student_service = student_service
        self.tide_service = tide_service

    def generate_surf_plan_for_day_and_location(self, plan_date: date, location_id: int) -> SurfPlan:
        # Check if plan exists for this date already
        existing_plan = self.surf_plan_repository.get_by_date_and_location(plan_date, location_id)
        if existing_plan:
            return existing_plan

        #If no plan exists create a new plan
        # get Students for date from StudentService
        students: List[Student] = self.student_service.get_students_by_date_range(plan_date, plan_date)

        # group Student by level, age_group
        filtered_beginner_adults = list(filter(lambda s: s.level == "BEGINNER" and s.age_group == "18 - 60", students))
        beginner_adults_group = Group("BEGINNER", filtered_beginner_adults,[Instructor("Fabrizio", "L1 Portugal License")])

        filtered_beginner_plus_adults = list(filter(lambda s: s.level == "BEGINNER+" and s.age_group == "18 - 60", students))
        beginner_plus_adults_group = Group("BEGINNER+", filtered_beginner_plus_adults,[Instructor("Lara", "L2 Portugal License")])

        # grouped_students = self._group_students(students)
        slotA_start_time, slotB_start_time = self._get_start_times(plan_date)

        new_plan = SurfPlan(plan_date, [Slot(slotA_start_time, [beginner_adults_group, beginner_plus_adults_group]), Slot(slotB_start_time)], 1)
        return new_plan


    def _get_start_times(self, day: date) -> Tuple[datetime, datetime]:
        low_tides = self.tide_service.get_low_tides(day)
        slotA_start_time = low_tides[1] - timedelta(hours=1.5)
        slotB_start_time = low_tides[1]
        return slotA_start_time, slotB_start_time

    def _group_students(self, students: List[Student]):
        grouped_students = {}
        for student in students:
            key = (student.level, student.age_group)
            grouped_students.setdefault(key, []).append(student)
        return grouped_students


# determine how many groups to form — based on the max number of students per group
# determine how many slots to form — based on the available number of instructors per slot
# instructor anzahl: 5, funktion needed die currently available instructor returned

def distribute_students_evenly(self, grouped_students: Dict[Tuple[str, str], List[Student]], max_group_size):
    distributed_groups = []

    for (level, age_group), students in grouped_students.items():
        # calculate nr_students for each sub group (level, age_group)
        nr_students = len(students)
        # calculate nr_groups needed for sub group: nr_of_students / max_group_size, rounded up
        nr_groups = math.ceil(nr_students / max_group_size)
        # calculate group_size: nr_students/nr_groups, modulo
        base_group_size = nr_students // nr_groups
        extra_students = nr_students % nr_groups  # This is the number of groups that will have one extra student

        # Initialize empty groups
        groups = [[] for _ in range(nr_groups)]

        # Distribute students in a round-robin fashion
        student_index = 0

        # add students to the groups that have an extra student
        for i in range(extra_students):
            for _ in range(base_group_size + 1):  # Add one extra student to these groups
                groups[i].append(students[student_index])
                student_index += 1

        # add students to the other groups
        for i in range(extra_students, nr_groups):
            for _ in range(base_group_size):  # Add base number of students to remaining groups
                groups[i].append(students[student_index])
                student_index += 1

        # Create Group objects and add them to the distributed_groups list
        for group in groups:
            distributed_groups.append(Group(level=level, students=group))

    return distributed_groups
