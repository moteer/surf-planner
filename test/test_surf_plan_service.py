import unittest
from unittest.mock import Mock
from datetime import date
from app.services.surf_plan_service import SurfPlanService


class TestSurfPlanService(unittest.TestCase):
    def test_generate_surf_plan_when_no_existing_plan(self):
        # Create mock repository
        mock_repository = Mock()
        mock_repository.get_by_date_and_location.return_value = None

        # When save is called, return the plan with an ID
        def mock_save(plan):
            plan.id = 1
            return plan

        mock_repository.save.side_effect = mock_save

        # Create service with mock repository
        service = SurfPlanService(mock_repository)

        # Test parameters
        test_date = date(2024, 3, 27)
        test_location_id = 42

        # Execute service method
        result = service.generate_surf_plan_for_day_and_location(test_date, test_location_id)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.plan_date, test_date)
        self.assertEqual(len(result.slots), 0)

        # Verify repository methods were called
        mock_repository.get_by_date_and_location.assert_called_once_with(test_date, test_location_id)
        mock_repository.save.assert_called_once()