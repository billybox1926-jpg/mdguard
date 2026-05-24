import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mdguard.core import load_rules, process_file


class TestRules(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules()

    def _lint(self, text: str, config: dict, fix: bool = False):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            issues = process_file(path, self.rules, config, fix=fix)
            with path.open("r", encoding="utf-8", newline="") as handle:
                return issues, handle.read()

    def test_duplicate_headings_reports_repeated_heading(self):
        config = {"duplicate-headings": True}
        issues, _ = self._lint("# Title\n## Intro\n# title\n", config)
        duplicate = [i for i in issues if i.rule == "duplicate-headings"]
        self.assertEqual(len(duplicate), 1)
        self.assertIn("first at line 1", duplicate[0].message)

    def test_duplicate_headings_default_disabled(self):
        issues, _ = self._lint("# Title\n# Title\n", {})
        self.assertFalse(any(i.rule == "duplicate-headings" for i in issues))

    def test_heading_jump_reports_skipped_level(self):
        issues, _ = self._lint("# H1\n### H3\n", {})
        jump = [i for i in issues if i.rule == "heading-jump"]
        self.assertEqual(len(jump), 1)
        self.assertIn("jumps from 1 to 3", jump[0].message)

    def test_missing_h1_reports_when_enabled(self):
        issues, _ = self._lint("## Section\nText\n", {"missing-h1": True})
        missing = [i for i in issues if i.rule == "missing-h1"]
        self.assertEqual(len(missing), 1)

    def test_missing_h1_default_disabled(self):
        issues, _ = self._lint("## Section\n", {})
        self.assertFalse(any(i.rule == "missing-h1" for i in issues))

    def test_empty_link_reports_empty_destination(self):
        issues, _ = self._lint("See [docs]() for more.\n", {})
        empty = [i for i in issues if i.rule == "empty-link"]
        self.assertEqual(len(empty), 1)

    def test_trailing_whitespace_reports_and_fixes(self):
        issues, fixed = self._lint("hello  \n", {"trailing-whitespace": True}, fix=True)
        self.assertTrue(any(i.rule == "trailing-whitespace" for i in issues))
        self.assertEqual(fixed, "hello\n")

    def test_line_length_respects_rule_specific_max_and_combining_chars(self):
        # "e\u0301" has display width 1; max=3 should still fail due to trailing "ab".
        issues, _ = self._lint("e\u0301abZ\n", {"line-length": {"max": 3}})
        long_lines = [i for i in issues if i.rule == "line-length"]
        self.assertEqual(len(long_lines), 1)
        self.assertIn("exceeds 3 columns", long_lines[0].message)

    def test_line_length_can_be_disabled_explicitly(self):
        issues, _ = self._lint(
            "This line is very long indeed.\n", {"line-length": False, "max_length": 5}
        )
        self.assertFalse(any(i.rule == "line-length" for i in issues))

    def test_final_newline_detects_and_fixes_when_enabled(self):
        issues, fixed = self._lint("# Title", {"final-newline": True}, fix=True)
        self.assertTrue(any(i.rule == "final-newline" for i in issues))
        self.assertEqual(fixed, "# Title\n")

    def test_rules_ignore_fenced_code_blocks(self):
        text = (
            "# Real H1\n"
            "```\n"
            "# Heading inside code block\n"
            "This line is definitely longer than ten characters.\n"
            "[link]()\n"
            "```\n"
        )
        # Enable rules that should ignore code blocks
        config = {
            "line-length": {"max": 10},
            "empty-link": True,
            "heading-jump": True,
            "missing-h1": True,
            "duplicate-headings": True,
        }
        issues, _ = self._lint(text, config)
        # None of these should fire inside the block
        self.assertEqual(
            len(issues), 0, f"Expected 0 issues, got: {[str(i) for i in issues]}"
        )


if __name__ == "__main__":
    unittest.main()
