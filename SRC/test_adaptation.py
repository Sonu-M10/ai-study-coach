
import unittest

from main import update_difficulty

class TestAdaptiveDifficulty(unittest.TestCase):

    def test_incorrect_answer_decreases_difficulty(self):
        self.assertEqual(update_difficulty(3, 0), 2)
        self.assertEqual(update_difficulty(2, 0), 1)

    def test_beginner_is_minimum_difficulty(self):
        self.assertEqual(update_difficulty(1, 0), 1)

    def test_partially_correct_keeps_difficulty(self):
        self.assertEqual(update_difficulty(1, 1), 1)
        self.assertEqual(update_difficulty(2, 1), 2)

    def test_correct_answer_increases_difficulty(self):
        self.assertEqual(update_difficulty(1, 2), 2)
        self.assertEqual(update_difficulty(2, 2), 3)

    def test_advanced_is_maximum_difficulty(self):
        self.assertEqual(update_difficulty(3, 2), 3)


if __name__ == "__main__":
    unittest.main()
