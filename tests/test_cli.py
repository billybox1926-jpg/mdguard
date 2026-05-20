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

    def test_direct_markdown_file_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("# title\n", encoding="utf-8")
            proc = subprocess.run([sys.executable, "-m", "mdguard.cli", str(p)], capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0)
            self.assertIn(f"No issues found in {p}", proc.stderr)

    def test_recursive_directory_discovery_and_markdown_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "docs" / "sub"
            nested.mkdir(parents=True)
            (root / "docs" / "a.md").write_text("# a\n", encoding="utf-8")
            (nested / "b.markdown").write_text("# b\n", encoding="utf-8")
            (nested / "c.txt").write_text("not markdown\n", encoding="utf-8")

            proc = subprocess.run([sys.executable, "-m", "mdguard.cli", str(root / "docs")], capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("a.md", proc.stderr)
            self.assertIn("b.markdown", proc.stderr)
            self.assertNotIn("c.txt", proc.stderr)

    def test_missing_path_exits_nonzero(self):
        proc = subprocess.run([sys.executable, "-m", "mdguard.cli", "definitely-missing-target"], capture_output=True, text=True, check=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("not found", proc.stderr)

    def test_directory_with_no_markdown_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_dir = Path(tmp) / "docs"
            empty_dir.mkdir()
            (empty_dir / "notes.txt").write_text("hello\n", encoding="utf-8")
            proc = subprocess.run([sys.executable, "-m", "mdguard.cli", str(empty_dir)], capture_output=True, text=True, check=False)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("No Markdown files found under directory", proc.stderr)

    def test_final_newline_detect_and_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "no-final-newline.md"
            p.write_text("# title", encoding="utf-8")

            lint_proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(p)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(lint_proc.returncode, 1)
            self.assertIn("file must end with a final newline [final-newline]", lint_proc.stderr)

            fix_proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(p), "--fix"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(fix_proc.returncode, 0)
            self.assertEqual(p.read_text(encoding="utf-8"), "# title\n")


if __name__ == "__main__":
    unittest.main()
