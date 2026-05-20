import unittest

from mdguard.core import load_rules


class TestCore(unittest.TestCase):
    def test_load_rules_includes_line_length(self):
        rules = load_rules()
        self.assertIn("line-length", rules)
        self.assertIn("final-newline", rules)


if __name__ == "__main__":
    unittest.main()
