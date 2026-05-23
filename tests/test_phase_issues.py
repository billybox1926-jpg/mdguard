import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from mdguard.api import lint_paths


class TestPhaseIssues(unittest.TestCase):
    def run_cli(self, *args, input_text=None, cwd=None):
        env = {**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent / "src")}
        return subprocess.run(
            [sys.executable, "-m", "mdguard.cli", *map(str, args)],
            input=input_text,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

    def test_stdin_json_uses_supplied_filename(self):
        proc = self.run_cli("-", "--stdin-filename", "README.md", "--json", input_text="# ok\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(report["files"][0]["path"], "README.md")

    def test_pyproject_config_disables_missing_h1_and_sets_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[tool.mdguard]\nmax_length = 10\ndisable = ["missing-h1"]\n', encoding="utf-8"
            )
            (root / "README.md").write_text("short\n", encoding="utf-8")
            proc = self.run_cli("README.md", cwd=root)
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_inline_suppression_hides_selected_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("<!-- mdguard-disable-next-line line-length -->\nthis line is intentionally far too long\n", encoding="utf-8")
            proc = self.run_cli(p, "--max-length", "10", "--disable", "missing-h1")
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_internal_anchor_reports_missing_heading_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("# Title\n[missing](#nope)\n", encoding="utf-8")
            proc = self.run_cli(p)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("internal heading anchor not found", proc.stderr)

    def test_front_matter_is_not_linted_as_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text('---\ntitle: x\n---\n# Title\n', encoding="utf-8")
            proc = self.run_cli(p, "--max-length", "20")
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_markdown_line_length_exceptions(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("# Title\nhttps://example.com/this/is/a/very/long/url\n| very | long | table | row |\n", encoding="utf-8")
            proc = self.run_cli(p, "--max-length", "10")
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_baseline_suppresses_existing_issue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "README.md"
            baseline = root / ".mdguard-baseline.json"
            p.write_text("no h1\n", encoding="utf-8")
            write_proc = self.run_cli(p, "--write-baseline", baseline)
            self.assertEqual(write_proc.returncode, 0, write_proc.stderr)
            lint_proc = self.run_cli(p, "--baseline", baseline)
            self.assertEqual(lint_proc.returncode, 0, lint_proc.stderr)

    def test_github_annotations_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("no h1\n", encoding="utf-8")
            proc = self.run_cli(p, "--format", "github", "--enable", "missing-h1")
            self.assertEqual(proc.returncode, 1)
            self.assertIn("::warning file=", proc.stdout)

    def test_public_api_and_batch_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("# Title\n", encoding="utf-8")
            result = lint_paths([p])
            self.assertEqual(result.issue_count, 0)
            self.assertEqual(result.files_checked, [p])

    def test_verbose_rule_metadata(self):
        proc = self.run_cli("--list-rules", "--verbose")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("fixable", proc.stdout)
        self.assertIn("internal-anchor", proc.stdout)

    def test_precommit_hook_metadata_exists(self):
        hook = Path(__file__).parent.parent / ".pre-commit-hooks.yaml"
        self.assertIn("entry: mdguard", hook.read_text(encoding="utf-8"))

    def test_design_docs_exist_for_research_issues(self):
        docs = Path(__file__).parent.parent / "docs" / "DESIGN.md"
        text = docs.read_text(encoding="utf-8")
        self.assertIn("Dependency and extras policy", text)
        self.assertIn("CommonMark/GFM parser strategy", text)
        self.assertIn("Remote link cache design", text)


if __name__ == "__main__":
    unittest.main()
