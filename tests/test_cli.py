import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestCli(unittest.TestCase):
    def test_module_invocation_lists_rules(self):
        proc = subprocess.run(
            [sys.executable, "-m", "mdguard.cli", "--list-rules"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("line-length", proc.stdout)

    def test_unicode_line_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "u.md"
            p.write_text("漢字漢字\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(p), "--max-length", "6"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("line exceeds 6 columns (8)", proc.stderr)

    def test_fix_preserves_newline(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "t.md"
            p.write_text("x  \n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(p), "--fix"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(p.read_text(encoding="utf-8"), "x\n")


if __name__ == "__main__":
    unittest.main()
