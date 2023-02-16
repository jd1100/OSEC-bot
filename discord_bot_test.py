import unittest
import importlib
from discord_bot_utils import is_student, StudentResult


class IsStudentTests(unittest.TestCase):
    def test_valid_student_verifies(self):
        self.assertEqual(is_student("n01367640"), StudentResult.STUDENT)

    def test_invalid_student_fails(self):
        self.assertEqual(is_student("n99999999"), StudentResult.NOT_FOUND)
