import unittest
from unittest.mock import Mock
from datetime import date

from app.domain.models import CrewMember, Position, CrewAssignment, Accommodation, AccommodationAssignment, Team
from app.services.crew_service import CrewService


class TestCrewService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.crew_member_repo = Mock()
        self.position_repo = Mock()
        self.crew_assignment_repo = Mock()
        self.accommodation_repo = Mock()
        self.accommodation_assignment_repo = Mock()
        
        self.crew_service = CrewService(
            crew_member_repo=self.crew_member_repo,
            position_repo=self.position_repo,
            crew_assignment_repo=self.crew_assignment_repo,
            accommodation_repo=self.accommodation_repo,
            accommodation_assignment_repo=self.accommodation_assignment_repo
        )

    def test_get_crew_members_all(self):
        """Test getting all crew members"""
        mock_crew = [
            CrewMember(1, "John", "Doe", "john@test.com", "123", Team.SURF, "", ""),
            CrewMember(2, "Jane", "Smith", "jane@test.com", "456", Team.YOGA, "", "")
        ]
        self.crew_member_repo.get_all.return_value = mock_crew
        
        result = self.crew_service.get_crew_members()
        
        self.assertEqual(len(result), 2)
        self.crew_member_repo.get_all.assert_called_once()

    def test_get_crew_members_by_team(self):
        """Test getting crew members filtered by team"""
        mock_crew = [
            CrewMember(1, "John", "Doe", "john@test.com", "123", Team.SURF, "", "")
        ]
        self.crew_member_repo.get_by_team.return_value = mock_crew
        
        result = self.crew_service.get_crew_members(team=Team.SURF)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].team, Team.SURF)
        self.crew_member_repo.get_by_team.assert_called_once_with(Team.SURF)

    def test_assign_crew_success(self):
        """Test successful crew assignment"""
        crew_member = CrewMember(1, "John", "Doe", "john@test.com", "123", Team.SURF, "", "")
        position = Position(1, "Instructor", Team.SURF, "")
        
        self.crew_member_repo.get_by_id.return_value = crew_member
        self.position_repo.get_by_id.return_value = position
        self.crew_assignment_repo.save.return_value = CrewAssignment(
            1, 1, 1, date(2025, 6, 1), crew_member, position
        )
        
        result = self.crew_service.assign_crew(1, 1, date(2025, 6, 1))
        
        self.assertEqual(result.crew_member_id, 1)
        self.assertEqual(result.position_id, 1)
        self.crew_assignment_repo.save.assert_called_once()

    def test_assign_crew_invalid_crew_member(self):
        """Test crew assignment with invalid crew member"""
        self.crew_member_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.crew_service.assign_crew(999, 1, date(2025, 6, 1))
        
        self.assertIn("not found", str(context.exception))

    def test_assign_crew_invalid_position(self):
        """Test crew assignment with invalid position"""
        crew_member = CrewMember(1, "John", "Doe", "john@test.com", "123", Team.SURF, "", "")
        self.crew_member_repo.get_by_id.return_value = crew_member
        self.position_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.crew_service.assign_crew(1, 999, date(2025, 6, 1))
        
        self.assertIn("not found", str(context.exception))

    def test_get_crew_calendar(self):
        """Test getting crew calendar"""
        crew_member = CrewMember(1, "John", "Doe", "john@test.com", "123", Team.SURF, "", "")
        position = Position(1, "Instructor", Team.SURF, "")
        assignments = [
            CrewAssignment(1, 1, 1, date(2025, 6, 1), crew_member, position),
            CrewAssignment(2, 1, 1, date(2025, 6, 2), crew_member, position)
        ]
        
        self.crew_assignment_repo.get_by_date_range.return_value = assignments
        
        result = self.crew_service.get_crew_calendar(date(2025, 6, 1), date(2025, 6, 2))
        
        self.assertEqual(result["start_date"], "2025-06-01")
        self.assertEqual(result["end_date"], "2025-06-02")
        self.assertIn("2025-06-01", result["calendar"])
        self.assertIn("2025-06-02", result["calendar"])
        self.assertEqual(len(result["calendar"]["2025-06-01"]), 1)

    def test_assign_accommodation_success(self):
        """Test successful accommodation assignment"""
        crew_member = CrewMember(1, "John", "Doe", "john@test.com", "123", Team.SURF, "", "")
        accommodation = Accommodation(1, "Tent A", "tent", 2, "")
        
        self.crew_member_repo.get_by_id.return_value = crew_member
        self.accommodation_repo.get_by_id.return_value = accommodation
        self.accommodation_assignment_repo.get_by_accommodation_and_date_range.return_value = []
        self.accommodation_assignment_repo.get_by_crew_member.return_value = []
        self.accommodation_assignment_repo.save.return_value = AccommodationAssignment(
            1, 1, 1, date(2025, 6, 1), date(2025, 6, 7), crew_member, accommodation
        )
        
        result = self.crew_service.assign_accommodation(1, 1, date(2025, 6, 1), date(2025, 6, 7))
        
        self.assertEqual(result.crew_member_id, 1)
        self.assertEqual(result.accommodation_id, 1)
        self.accommodation_assignment_repo.save.assert_called_once()

    def test_assign_accommodation_at_capacity(self):
        """Test accommodation assignment when at capacity"""
        crew_member = CrewMember(1, "John", "Doe", "john@test.com", "123", Team.SURF, "", "")
        accommodation = Accommodation(1, "Tent A", "tent", 2, "")
        
        # Two different crew members already assigned
        existing_assignments = [
            AccommodationAssignment(1, 2, 1, date(2025, 6, 1), date(2025, 6, 7), None, None),
            AccommodationAssignment(2, 3, 1, date(2025, 6, 1), date(2025, 6, 7), None, None)
        ]
        
        self.crew_member_repo.get_by_id.return_value = crew_member
        self.accommodation_repo.get_by_id.return_value = accommodation
        self.accommodation_assignment_repo.get_by_accommodation_and_date_range.return_value = existing_assignments
        
        with self.assertRaises(ValueError) as context:
            self.crew_service.assign_accommodation(1, 1, date(2025, 6, 1), date(2025, 6, 7))
        
        self.assertIn("at capacity", str(context.exception))

    def test_assign_accommodation_prevents_tent_change(self):
        """Test that accommodation assignment prevents tent changes during stay"""
        crew_member = CrewMember(1, "John", "Doe", "john@test.com", "123", Team.SURF, "", "")
        accommodation = Accommodation(1, "Tent A", "tent", 2, "")
        other_accommodation = Accommodation(2, "Tent B", "tent", 2, "")
        
        # Crew member already assigned to a different accommodation
        existing_crew_assignment = [
            AccommodationAssignment(1, 1, 2, date(2025, 6, 1), date(2025, 6, 7), None, other_accommodation)
        ]
        
        self.crew_member_repo.get_by_id.return_value = crew_member
        self.accommodation_repo.get_by_id.return_value = accommodation
        self.accommodation_assignment_repo.get_by_accommodation_and_date_range.return_value = []
        self.accommodation_assignment_repo.get_by_crew_member.return_value = existing_crew_assignment
        
        with self.assertRaises(ValueError) as context:
            self.crew_service.assign_accommodation(1, 1, date(2025, 6, 3), date(2025, 6, 10))
        
        self.assertIn("already assigned", str(context.exception))
        self.assertIn("Cannot change accommodation", str(context.exception))

    def test_assign_accommodation_allows_same_accommodation_extension(self):
        """Test that extending stay in same accommodation is allowed"""
        crew_member = CrewMember(1, "John", "Doe", "john@test.com", "123", Team.SURF, "", "")
        accommodation = Accommodation(1, "Tent A", "tent", 2, "")
        
        # Crew member already assigned to the same accommodation - this should be OK for counting capacity
        existing_crew_assignment = [
            AccommodationAssignment(1, 1, 1, date(2025, 6, 1), date(2025, 6, 7), None, accommodation)
        ]
        
        self.crew_member_repo.get_by_id.return_value = crew_member
        self.accommodation_repo.get_by_id.return_value = accommodation
        # When checking capacity, the existing assignment for same accommodation is fine
        self.accommodation_assignment_repo.get_by_accommodation_and_date_range.return_value = existing_crew_assignment
        # When checking for overlaps, only different accommodations matter
        self.accommodation_assignment_repo.get_by_crew_member.return_value = existing_crew_assignment
        self.accommodation_assignment_repo.save.return_value = AccommodationAssignment(
            2, 1, 1, date(2025, 6, 8), date(2025, 6, 14), crew_member, accommodation
        )
        
        # This should succeed - no overlap with different accommodation
        result = self.crew_service.assign_accommodation(1, 1, date(2025, 6, 8), date(2025, 6, 14))
        
        self.assertEqual(result.crew_member_id, 1)
        self.assertEqual(result.accommodation_id, 1)


if __name__ == '__main__':
    unittest.main()
