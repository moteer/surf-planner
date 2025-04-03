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

    test_location_id = 42
    test_surf_plan_date = date(2025, 5, 7)
    slot_date_time = datetime(2025, 5, 7, 12, 0, 0)
    groups = [Group("BEGINNER",
                    students=[
                        Student("Max", "Maler", date(2000, 1, 1), "M", "18 - 60",
                                "BEGINNER",
                                "b43858f7-14fa-4615-a6f4-654488fab07e"),
                        Student("Lisa", "Maler", date(2001, 1, 1), "M", "18 - 60",
                                "BEGINNER",
                                "b43858f7-14fa-4615-a6f4-654488fab07e"),
                        Student("Henry", "Maler", date(2002, 1, 1), "M",
                                "18 - 60", "BEGINNER",
                                "b43858f7-14fa-4615-a6f4-654488fab07e"),
                        Student("Sebastian", "Soll", date(2003, 1, 1), "M",
                                "18 - 60", "BEGINNER",
                                "b43858f7-14fa-4615-a6f4-654488fab07e"),
                        Student("Horst", "Maus", date(2004, 1, 1), "M", "18 - 60",
                                "BEGINNER",
                                "b43864f7-14fa-4615-a6f4-654488fab07e"),
                        Student("Christin", "Haug", date(2005, 1, 1), "F",
                                "18 - 60", "BEGINNER",
                                "b87658f7-14fa-4615-a6f4-654488fab07e")],
                    instructors=[Instructor("Fabrizio", "L1 Portugal License")])
        ,
              Group("BEGINNER+",
                    students=[
                        Student("Tina", "Schmidt", date(1999, 6, 15), "F",
                                "18 - 60",
                                "BEGINNER",
                                "c12345a7-89ab-4def-9012-3456789abcde"),
                        Student("Jonas", "Keller", date(1998, 11, 3), "M",
                                "18 - 60",
                                "BEGINNER",
                                "b43858f7-14fa-4615-a6f4-654488fab07e"),
                        Student("Franz", "Bauer", date(1985, 7, 22), "M",
                                "18 - 60",
                                "BEGINNER",
                                "b43864f7-14fa-4615-a6f4-654488fab07e"),
                        Student("Mara", "Lindner", date(1995, 3, 30), "F",
                                "18 - 60",
                                "BEGINNER",
                                "d98765e4-32dc-4ab1-89ef-123456789abc"),
                        Student("Emil", "Wagner", date(2000, 9, 9), "M",
                                "18 - 60",
                                "BEGINNER",
                                "b43858f7-14fa-4615-a6f4-654488fab07e"),
                        Student("Laura", "Neumann", date(2001, 12, 25), "F",
                                "18 - 60",
                                "BEGINNER",
                                "b87658f7-14fa-4615-a6f4-654488fab07e"),
                        Student("Kevin", "Dorn", date(2002, 4, 5), "M", "18 - 60",
                                "BEGINNER",
                                "c12345a7-89ab-4def-9012-3456789abcde"),
                        Student("Sina", "Voigt", date(1997, 8, 19), "F",
                                "18 - 60",
                                "BEGINNER",
                                "b43864f7-14fa-4615-a6f4-654488fab07e")],
                    instructors=[Instructor("Lara", "L2 Portugal License")])

              ]
    test_surf_plan = SurfPlan(test_surf_plan_date, [Slot(slot_date_time, groups)])


    ## make service call student mock it should return all students that are on camp for the given date
    ## the service should generate the correct groups depending on the level of the students and save them into the surf plan
    def test_generate_surf_plan_when_no_surf_plan_exists(self):
        # Create mock repository
        mock_repository : SurfPlanRepositoryInterface = Mock()
        mock_repository.get_by_date_and_location.return_value = None

        # When save is called, return the plan with an ID
        def mock_save(plan):
            plan.id = 1
            return plan

        mock_repository.save.side_effect = mock_save

        # Create service with mock repository
        service = SurfPlanService(mock_repository)

        # Execute service method
        result = service.generate_surf_plan_for_day_and_location(self.test_surf_plan_date, self.test_location_id)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.plan_date, self.test_surf_plan_date)
        self.assertEqual(len(result.slots), 0)

        # Verify repository methods were called
        mock_repository.get_by_date_and_location.assert_called_once_with(self.test_surf_plan_date, self.test_location_id)
        mock_repository.save.assert_called_once()

    def test_generate_surf_plan_with_already_existing_surf_plan(self):

        # Create mock repository
        mock_repository = Mock()
        mock_repository.get_by_date_and_location.return_value = self.test_surf_plan

        # Create service with mock repository
        service = SurfPlanService(mock_repository)

        # Execute service method
        result = service.generate_surf_plan_for_day_and_location(self.test_surf_plan_date, self.test_location_id)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result, self.test_surf_plan)

        # Verify repository methods were called
        mock_repository.get_by_date_and_location.assert_called_once_with(self.test_surf_plan_date, self.test_location_id)
