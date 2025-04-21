import unittest
from unittest.mock import Mock
from datetime import date, datetime

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
            students = [self.test_adult_beginner_student, self.test_adult_beginner_student2],
            instructors=[self.test_instructors[0]]
        )
        self.beginner_plus_adults_group = Group(
            "BEGINNER+",
            students = [self.test_adult_beginner_plus_student, self.test_adult_beginner_plus_student2],
            instructors=[self.test_instructors[1]]
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
        mock_student_service.get_students_by_date_range.return_value = self.test_students

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
        surf_plan = service.generate_surf_plan_for_day_and_location(self.test_surf_plan_date, self.test_location_id)

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
