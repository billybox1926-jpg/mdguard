import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from mdguard.core import load_rules, process_file


class TestCore(unittest.TestCase):
    def test_load_rules_includes_line_length(self):
        rules = load_rules()
        self.assertIn("line-length", rules)
        self.assertIn("final-newline", rules)

    def test_process_file_writes_with_newline_disabled(self):
        rules = load_rules()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.md"
            path.write_text("x  \n", encoding="utf-8")
            config = {name: False for name in rules}
            config["trailing-whitespace"] = True

            with patch("pathlib.Path.open", autospec=True, wraps=Path.open) as mocked_open:
                issues = process_file(path, rules, config, fix=True)

            self.assertTrue(any(issue.rule == "trailing-whitespace" for issue in issues))
            write_calls = [c for c in mocked_open.call_args_list if c.args[1] == "w"]
            self.assertEqual(len(write_calls), 1)
            self.assertEqual(write_calls[0].kwargs.get("newline"), "")

    def test_trailing_whitespace_fix_without_final_newline_keeps_no_newline(self):
        rules = load_rules()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "no-final-newline.md"
            path.write_bytes(b"x  ")
            config = {name: False for name in rules}
            config["trailing-whitespace"] = True

            process_file(path, rules, config, fix=True)
            self.assertEqual(path.read_bytes(), b"x")


if __name__ == "__main__":
    unittest.main()
