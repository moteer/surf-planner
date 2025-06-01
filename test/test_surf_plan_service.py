import unittest
from unittest.mock import Mock
from datetime import date, datetime

from deepdiff import DeepDiff
from pprint import pprint

from app.domain.models import SurfPlan, Slot, Group, Student, Instructor
from app.domain.repositories_interfaces import SurfPlanRepositoryInterface
from app.services.surf_plan_service import SurfPlanService


class TestSurfPlanRepositoryImplForSurfPlanExitsAlready(SurfPlanRepositoryInterface):
    def save(self, surf_plan: SurfPlan) -> SurfPlan:
        print("test save")

    def get_by_date_and_location(self, plan_date: date, location_id: int) -> SurfPlan:
        return SurfPlan(date(2,2,3), [Slot], 1)


class TestSurfPlanService(unittest.TestCase):

    def setUp(self):
        self.test_location_id = 42
        self.test_surf_plan_date = date(2025, 5, 7)
        self.slot_date_time = datetime(2025, 5, 7, 12, 0, 0)
        self.slot_date_time_2 = datetime(2025, 5, 7, 13, 30, 0)
        self.test_surf_plan_id = 1
        self.test_low_tides = (datetime(2025, 5, 7, 1, 30, 0), datetime(2025, 5, 7, 13, 30, 0))
        self.test_adult_beginner_student = Student("Max", "Maler", date(2000, 1, 1), "M", "18 - 60", "BEGINNER", "id-1", date(2025, 5, 5), date(2025, 5, 12))
        self.test_adult_beginner_student2 = Student("Lisa", "Maler", date(2001, 1, 1), "M", "18 - 60", "BEGINNER", "id-2", date(2025, 5, 5), date(2025, 5, 12))
        self.test_adult_beginner_plus_student = Student("Tina", "Schmidt", date(1999, 6, 15), "F", "18 - 60", "BEGINNER+", "id-3", date(2025, 5, 5), date(2025, 5, 12))
        self.test_adult_beginner_plus_student2 = Student("Kevin", "Dorn", date(2002, 4, 5), "M", "18 - 60", "BEGINNER+", "id-4", date(2025, 5, 5), date(2025, 5, 12))


        self.test_students = [
            self.test_adult_beginner_student,
            self.test_adult_beginner_student2,
            self.test_adult_beginner_plus_student,
            self.test_adult_beginner_plus_student2
        ]

        self.test_instructors = [
            Instructor("Fabrizio", "L1 Portugal License"),
            Instructor("Lara", "L2 Portugal License")
        ]
        self.beginner_adults_group = Group(
            "BEGINNER",
            "18 - 60",
            students = [self.test_adult_beginner_student, self.test_adult_beginner_student2]
            # instructors=[self.test_instructors[0]]
        )
        self.beginner_plus_adults_group = Group(
            "BEGINNER+",
            "18 - 60",
            students = [self.test_adult_beginner_plus_student, self.test_adult_beginner_plus_student2]
            # instructors=[self.test_instructors[0]]
        )

        self.test_groups = [
            self.beginner_adults_group,
            self.beginner_plus_adults_group
        ]


        # self.test_surf_plan = SurfPlan(
        #     self.test_surf_plan_date,
        #     [Slot(self.slot_date_time, self.test_groups)],
        #     self.test_location_id
        # )

        self.test_surf_plan = SurfPlan(self.test_surf_plan_date,
                                       [Slot(self.slot_date_time, [self.beginner_adults_group, self.beginner_plus_adults_group]), Slot(self.slot_date_time_2)], self.test_surf_plan_id)

    ## make service call student mock it should return all students that are on camp for the given date
    ## the service should generate the correct groups depending on the level of the students and save them into the surf plan
    def test_generate_surf_plan_when_no_surf_plan_exists(self):
        # Create mock repository
        mock_repository : SurfPlanRepositoryInterface = Mock()
        mock_repository.get_by_date_and_location.return_value = None

        # Create mock Student Service
        mock_student_service = Mock()
        mock_student_service.get_students_with_booked_lessons_by_date_range.return_value = self.test_students

        # Create mock Tide Service
        mock_tide_service = Mock()
        mock_tide_service.get_low_tides.return_value = self.test_low_tides


        # When save is called, return the plan with an ID
        def mock_save(plan):
            plan.id = 1
            return plan

        mock_repository.save.side_effect = mock_save

        # Create service with mock repository
        service = SurfPlanService(mock_repository, mock_student_service, mock_tide_service)

        # Execute service method
        surf_plan = service.generate_surf_plan_for_day(self.test_surf_plan_date, self.test_location_id)


        # Assertions
        self.assertIsNotNone(surf_plan)
        self.assertEqual(self.test_surf_plan, surf_plan)

        # Verify repository methods were called
        mock_repository.get_by_date_and_location.assert_called_once_with(self.test_surf_plan_date, self.test_location_id)
        # mock_repository.save.assert_called_once()

    # def test_generate_surf_plan_with_already_existing_surf_plan(self):

    #     # Create mock Surfplan repository
    #     mock_repository = Mock()
    #     mock_repository.get_by_date_and_location.return_value = self.test_surf_plan

    #     # Create mock Student Service
    #     mock_student_service = Mock()
    #     mock_student_service.get_students_for_day_and_location.return_value = self.test_students

    #     # Create service with mock Surfplan repository and mock student_service
    #     service = SurfPlanService(mock_repository, mock_student_service)

    #     # Execute service method
    #     result = service.generate_surf_plan_for_day_and_location(self.test_surf_plan_date, self.test_location_id)

    #     # Assertions
    #     self.assertIsNotNone(result)
    #     self.assertEqual(result, self.test_surf_plan)

    #     # Verify repository methods were called
    #     mock_repository.get_by_date_and_location.assert_called_once_with(self.test_surf_plan_date, self.test_location_id)



class TestSurfPlanServiceForLargeGroup(unittest.TestCase):

    def setUp(self):
        # Define date and times for slots
        self.test_location_id = 42
        self.test_surf_plan_date = date(2025, 5, 7)
        self.slot_date_time = datetime(2025, 5, 7, 12, 0, 0)
        self.slot_date_time_2 = datetime(2025, 5, 7, 13, 30, 0)
        self.test_surf_plan_id = 1
        self.test_low_tides = (datetime(2025, 5, 7, 1, 30, 0), datetime(2025, 5, 7, 13, 30, 0))

        # Define students for each age group and level
        # Adults (All 3 levels with 10 students each)
        # BEGINNER
        self.test_adult_beginner_students = [
            Student("Max", "Maler", date(2000, 1, 1), "M", "18 - 60", "BEGINNER", "id-1", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Lisa", "Maler", date(2001, 1, 1), "M", "18 - 60", "BEGINNER", "id-2", date(2025, 5, 5), date(2025, 5, 12)),
            Student("John", "Doe", date(1999, 6, 1), "M", "18 - 60", "BEGINNER", "id-3", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Alice", "Doe", date(2000, 3, 15), "F", "18 - 60", "BEGINNER", "id-4", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Robert", "Smith", date(1998, 8, 10), "M", "18 - 60", "BEGINNER", "id-5", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Mary", "Jones", date(2000, 5, 25), "F", "18 - 60", "BEGINNER", "id-6", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Steve", "Green", date(1997, 7, 10), "M", "18 - 60", "BEGINNER", "id-7", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Sophia", "Miller", date(2001, 2, 15), "F", "18 - 60", "BEGINNER", "id-8", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Mark", "White", date(1999, 9, 20), "M", "18 - 60", "BEGINNER", "id-9", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Tina", "Brown", date(2000, 4, 4), "F", "18 - 60", "BEGINNER", "id-10", date(2025, 5, 5), date(2025, 5, 12)),
        ]
        # BEGINNER+
        self.test_adult_beginner_plus_students = [
            Student("Tina", "Schmidt", date(1999, 6, 15), "F", "18 - 60", "BEGINNER+", "id-11", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Kevin", "Dorn", date(2002, 4, 5), "M", "18 - 60", "BEGINNER+", "id-12", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Sarah", "Johnson", date(1995, 11, 22), "F", "18 - 60", "BEGINNER+", "id-13", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Tom", "Green", date(2001, 5, 18), "M", "18 - 60", "BEGINNER+", "id-14", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Jane", "Wilson", date(1997, 12, 12), "F", "18 - 60", "BEGINNER+", "id-15", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Oliver", "Brown", date(1999, 10, 2), "M", "18 - 60", "BEGINNER+", "id-16", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Diana", "Taylor", date(1998, 3, 15), "F", "18 - 60", "BEGINNER+", "id-17", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Charlie", "King", date(2000, 7, 1), "M", "18 - 60", "BEGINNER+", "id-18", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Liam", "Adams", date(1999, 12, 9), "M", "18 - 60", "BEGINNER+", "id-19", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Emma", "Lee", date(2001, 8, 11), "F", "18 - 60", "BEGINNER+", "id-20", date(2025, 5, 5), date(2025, 5, 12)),
        ]
        # INTERMEDIATE
        self.test_adult_intermediate_students = [
            Student("George", "Lee", date(1994, 6, 15), "M", "18 - 60", "INTERMEDIATE", "id-21", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Emma", "Khan", date(1992, 10, 5), "F", "18 - 60", "INTERMEDIATE", "id-22", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Jake", "Parker", date(1993, 7, 14), "M", "18 - 60", "INTERMEDIATE", "id-23", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Sophia", "Mitchell", date(1991, 11, 24), "F", "18 - 60", "INTERMEDIATE", "id-24", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Matthew", "Clark", date(1995, 5, 30), "M", "18 - 60", "INTERMEDIATE", "id-25", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Olivia", "Scott", date(1992, 1, 15), "F", "18 - 60", "INTERMEDIATE", "id-26", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Max", "Taylor", date(1990, 7, 22), "M", "18 - 60", "INTERMEDIATE", "id-27", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Isla", "Harris", date(1993, 10, 18), "F", "18 - 60", "INTERMEDIATE", "id-28", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Nate", "Wright", date(1994, 2, 2), "M", "18 - 60", "INTERMEDIATE", "id-29", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Zara", "Robinson", date(1992, 9, 9), "F", "18 - 60", "INTERMEDIATE", "id-30", date(2025, 5, 5), date(2025, 5, 12)),
        ]

        # Teenagers
        # BEGINNER
        self.test_teenager_beginner_students = [
            Student("Ethan", "Taylor", date(2003, 12, 1), "M", "13 - 18", "BEGINNER", "id-31", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Isabella", "Moore", date(2004, 8, 19), "F", "13 - 18", "BEGINNER", "id-32", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Cameron", "Scott", date(2005, 2, 12), "M", "13 - 18", "BEGINNER", "id-33", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Zoe", "Miller", date(2006, 4, 3), "F", "13 - 18", "BEGINNER", "id-34", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Logan", "Davis", date(2005, 11, 15), "M", "13 - 18", "BEGINNER", "id-35", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Grace", "Dunn", date(2003, 6, 21), "F", "13 - 18", "BEGINNER", "id-36", date(2025, 5, 5), date(2025, 5, 12)),
            Student("James", "Wilson", date(2004, 9, 5), "M", "13 - 18", "BEGINNER", "id-37", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Ava", "Roberts", date(2005, 1, 13), "F", "13 - 18", "BEGINNER", "id-38", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Oliver", "King", date(2006, 2, 4), "M", "13 - 18", "BEGINNER", "id-39", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Mia", "Wilson", date(2005, 5, 3), "F", "13 - 18", "BEGINNER", "id-40", date(2025, 5, 5), date(2025, 5, 12)),
        ]

        # Kids
        # BEGINNER
        self.test_kids_beginner_students = [
            Student("Anna", "Wood", date(2012, 3, 17), "F", "5 - 12", "BEGINNER", "id-41", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Ben", "Jones", date(2010, 6, 1), "M", "5 - 12", "BEGINNER", "id-42", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Clara", "White", date(2011, 11, 3), "F", "5 - 12", "BEGINNER", "id-43", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Danny", "Black", date(2012, 5, 9), "M", "5 - 12", "BEGINNER", "id-44", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Eva", "Taylor", date(2011, 4, 18), "F", "5 - 12", "BEGINNER", "id-45", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Felix", "Gray", date(2010, 10, 5), "M", "5 - 12", "BEGINNER", "id-46", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Grace", "Nelson", date(2011, 7, 21), "F", "5 - 12", "BEGINNER", "id-47", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Henry", "Clark", date(2012, 1, 15), "M", "5 - 12", "BEGINNER", "id-48", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Isabel", "Harris", date(2010, 12, 3), "F", "5 - 12", "BEGINNER", "id-49", date(2025, 5, 5), date(2025, 5, 12)),
            Student("Jack", "Adams", date(2011, 8, 14), "M", "5 - 12", "BEGINNER", "id-50", date(2025, 5, 5), date(2025, 5, 12)),
        ]


        # Combine all students in the test data
        self.test_students = (
            self.test_adult_beginner_students + self.test_adult_beginner_plus_students + self.test_adult_intermediate_students +
            self.test_kids_beginner_students + self.test_teenager_beginner_students
        )

        self.test_instructors = [
            Instructor("Fabrizio", "L1 Portugal License"),
            Instructor("Lara", "L2 Portugal License"),
            Instructor("Erik", "L2 Portugal License"),
            Instructor("Roy", "L2 Portugal License"),
            Instructor("Johnny", "L2 Portugal License")
        ]
        self.beginner_adults_group_1 = Group(
            "BEGINNER",
            "18 - 60",
            students = self.test_adult_beginner_students[:5]
            # instructors=[self.test_instructors[0]]
        )
        self.beginner_adults_group_2 = Group(
            "BEGINNER",
            "18 - 60",
            students = self.test_adult_beginner_students[-5:]
            # instructors=[self.test_instructors[0]]
        )
        self.beginner_plus_adults_group_1 = Group(
            "BEGINNER+",
            "18 - 60",
            students = self.test_adult_beginner_plus_students[:5]
            # instructors=[self.test_instructors[0]]
        )
        self.beginner_plus_adults_group_2 = Group(
            "BEGINNER+",
            "18 - 60",
            students = self.test_adult_beginner_plus_students[-5:]
            # instructors=[self.test_instructors[0]]
        )
        self.intermediate_plus_adults_group_1 = Group(
            "INTERMEDIATE",
            "18 - 60",
            students = self.test_adult_intermediate_students[:5]
            # instructors=[self.test_instructors[0]]
        )
        self.intermediate_plus_adults_group_2 = Group(
            "INTERMEDIATE",
            "18 - 60",
            students = self.test_adult_intermediate_students[-5:]
            # instructors=[self.test_instructors[0]]
        )
        self.beginner_teenager_group_1 = Group(
            "BEGINNER",
            "13 - 18",
            students = self.test_teenager_beginner_students[:5]
            # instructors=[self.test_instructors[0]]
        )
        self.beginner_teenager_group_2 = Group(
            "BEGINNER",
            "13 - 18",
            students = self.test_teenager_beginner_students[-5:]
            # instructors=[self.test_instructors[0]]
        )
        self.beginner_kids_group_1 = Group(
            "BEGINNER",
            "5 - 12",
            students = self.test_kids_beginner_students[:5]
            # instructors=[self.test_instructors[0]]
        )
        self.beginner_kids_group_2 = Group(
            "BEGINNER",
            "5 - 12",
            students = self.test_kids_beginner_students[-5:]
            # instructors=[self.test_instructors[0]]
        )

        self.test_groups = [
            self.beginner_adults_group_1,
            self.beginner_plus_adults_group_1,
            self.intermediate_plus_adults_group_1,
            self.beginner_kids_group_1,
            self.beginner_teenager_group_1,
            self.beginner_adults_group_2,
            self.beginner_plus_adults_group_2,
            self.intermediate_plus_adults_group_2,
            self.beginner_kids_group_2,
            self.beginner_teenager_group_2
        ]

        self.test_surf_plan = SurfPlan(self.test_surf_plan_date,
                                        [Slot(self.slot_date_time,
                                            [self.beginner_adults_group_1,
                                            self.beginner_plus_adults_group_1,
                                            self.intermediate_plus_adults_group_1,
                                            self.beginner_kids_group_1,
                                            self.beginner_teenager_group_1,]),
                                        Slot(self.slot_date_time_2,
                                            [self.beginner_adults_group_2,
                                            self.beginner_plus_adults_group_2,
                                            self.intermediate_plus_adults_group_2,
                                            self.beginner_kids_group_2,
                                            self.beginner_teenager_group_2])],
                                        self.test_surf_plan_id)

    def test_generate_surf_plan_with_two_slots(self):
        # Create mock repository
        mock_repository : SurfPlanRepositoryInterface = Mock()
        mock_repository.get_by_date_and_location.return_value = None

        # Create mock Student Service
        mock_student_service = Mock()
        mock_student_service.get_students_with_booked_lessons_by_date_range.return_value = self.test_students

        # Create mock Tide Service
        mock_tide_service = Mock()
        mock_tide_service.get_low_tides.return_value = self.test_low_tides


        # When save is called, return the plan with an ID
        def mock_save(plan):
            plan.id = 1
            return plan

        mock_repository.save.side_effect = mock_save

        # Create service with mock repository
        service = SurfPlanService(mock_repository, mock_student_service, mock_tide_service)

        # Execute service method
        surf_plan = service.generate_surf_plan_for_day(self.test_surf_plan_date, self.test_location_id)

        # Assertions
        self.assertIsNotNone(surf_plan)
        diff = DeepDiff(self.test_surf_plan, surf_plan)
        if diff != {}:
            pprint(diff)
        self.assertEqual(diff, {})

        # Verify repository methods were called
        mock_repository.get_by_date_and_location.assert_called_once_with(self.test_surf_plan_date, self.test_location_id)
        # mock_repository.save.assert_called_once()
