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
        students: List[Student] = self.student_service.get_students_by_date_range(plan_date, plan_date)

        slotA_start_time, slotB_start_time = self._get_start_times(plan_date)

        groups_by_level_and_age = self._create_groups(students)
        slot1 = Slot(slotA_start_time, groups_by_level_and_age)
        slot2 = self._create_second_slot(slot1)

        # distributed_groups = self._create_even_groups(groups_by_level_and_age, 5)

        # nr_of_instructors = 5
        # slots = self._create_slots(plan_date, distributed_groups, nr_of_instructors)

        new_plan = SurfPlan(plan_date, [slot1, slot2], 1)
        return new_plan

    def _extract_unique_levels_and_age_groups(self, students: List[Student]):
        levels = {student.level for student in students}
        age_groups = {student.age_group for student in students}
        return list(levels), list(age_groups)

    def _get_start_times(self, day: date) -> Tuple[datetime, datetime]:
        low_tides = self.tide_service.get_low_tides(day)
        slotA_start_time = low_tides[1] - timedelta(hours=1.5)
        slotB_start_time = low_tides[1]
        return slotA_start_time, slotB_start_time

    def _create_groups(self, students: List[Student]):
        groups = {}
        groups_by_level_and_age = []

        for student in students:
            key = (student.level, student.age_group)
            groups.setdefault(key, []).append(student)

        for (level, age_group), students_in_group in groups.items():
            groups_by_level_and_age.append(Group(level=level, age_group=age_group, students=students_in_group))

        return groups_by_level_and_age

    def _create_second_slot(self, slot1: Slot) -> Slot:
        slot2_start_time = slot1.slot_time + timedelta(hours=1.5)
        slot2 = Slot(slot2_start_time)

        for group in slot1.groups:
            nr_students = len(group.students)
            if nr_students > 5:
                second_group = Group(group.level, group.age_group, group.students[5:])
                del group.students[5:]
                slot2.groups.append(second_group)

        return slot2
# instructor anzahl: 5, funktion needed die currently available instructor returned


    # def _create_even_groups (self, groups_by_level_and_age: List[Group], max_group_size):

    #     distributed_groups = []

    #     for group in groups_by_level_and_age:
    #         nr_students = len(group.students)
    #         nr_groups = math.ceil(nr_students / max_group_size)
    #         # group_size = nr_students / nr_groups

    #         if nr_students > max_group_size:
    #             for i in range(nr_groups):
    #                 start_index = i * max_group_size
    #                 end_index = (i + 1) * max_group_size
    #                 subgroup_students = group.students[start_index:end_index]  # Get a slice of students

    #                 subgroup = Group(group.level, group.age_group, students=subgroup_students, instructors=group.instructors)
    #                 distributed_groups.append(subgroup)
    #         else:
    #             distributed_groups.append(group)

    # def _create_slots(self, plan_date: date, distributed_groups: List[Group], nr_of_instructors: int) -> List[Slot]:
    #     slotA_start_time, slotB_start_time = self._get_start_times(plan_date)

    #     nr_groups = len(distributed_groups)

    #     if nr_groups > nr_of_instructors:
    #         half = (nr_groups + 1) // 2
    #         slot_a_groups = distributed_groups[:half]
    #         slot_b_groups = distributed_groups[half:]

    #         return [
    #             Slot(slotA_start_time, slot_a_groups),
    #             Slot(slotB_start_time, slot_b_groups)
    #         ]
    #     else:
    #         return [
    #             Slot(slotA_start_time, distributed_groups)
    #         ]


    # def _distribute_students_evenly(self, grouped_students: Dict[Tuple[str, str], List[Student]], max_group_size):
    #         distributed_groups = []

    #         for (level, age_group), students in grouped_students.items():
    #             # calculate nr_students for each sub group (level, age_group)
    #             nr_students = len(students)
    #             # calculate nr_groups needed for sub group: nr_of_students / max_group_size, rounded up
    #             nr_groups = math.ceil(nr_students / max_group_size)
    #             # calculate group_size: nr_students/nr_groups, modulo
    #             base_group_size = nr_students // nr_groups
    #             extra_students = nr_students % nr_groups  # This is the number of groups that will have one extra student

    #             # Initialize empty groups
    #             groups = [[] for _ in range(nr_groups)]

    #             # Distribute students in a round-robin fashion
    #             student_index = 0

    #             # add students to the groups that have an extra student
    #             for i in range(extra_students):
    #                 for _ in range(base_group_size + 1):  # Add one extra student to these groups
    #                     groups[i].append(students[student_index])
    #                     student_index += 1

    #             # add students to the other groups
    #             for i in range(extra_students, nr_groups):
    #                 for _ in range(base_group_size):  # Add base number of students to remaining groups
    #                     groups[i].append(students[student_index])
    #                     student_index += 1

    #             # Create Group objects and add them to the distributed_groups list
    #             for group in groups:
    #                 distributed_groups.append(Group(level=level, students=group))

    #         return distributed_groups
