import json
import os
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

    def test_exclude_option_skips_matching_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            generated = docs / "generated"
            generated.mkdir(parents=True)
            keep = docs / "keep.md"
            skipped = generated / "api.md"
            keep.write_text("# keep\n", encoding="utf-8")
            skipped.write_text("This generated line is intentionally far too long for the default line length limit and should not be linted when excluded.\n", encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "mdguard.cli",
                    str(root),
                    "--exclude",
                    "docs/generated/**",
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0)
            report = json.loads(proc.stdout)
            self.assertEqual(report["issue_count"], 0)
            self.assertEqual([Path(f["path"]).name for f in report["files"]], ["keep.md"])

    def test_mdguardignore_skips_matching_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.md").write_text("# a\n", encoding="utf-8")
            (root / "b.md").write_text("# b\n", encoding="utf-8")
            (root / ".mdguardignore").write_text("b.md\n", encoding="utf-8")

            # Must run from 'root' so .mdguardignore is found by Path(".mdguardignore").
            src_dir = str(Path(__file__).parent.parent / "src")
            env = {**os.environ, "PYTHONPATH": src_dir}

            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", "."],
                cwd=str(root),
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertIn("a.md", proc.stderr)
            self.assertNotIn("b.md", proc.stderr)

    def test_final_newline_fix_preserves_crlf_style(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "windows-no-final-newline.md"
            p.write_bytes(b"# title\r\nbody")

            fix_proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(p), "--fix"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(fix_proc.returncode, 0)
            self.assertEqual(p.read_bytes(), b"# title\r\nbody\r\n")

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


    def test_missing_rules_config_file_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "README.md"
            target.write_text("# title\n", encoding="utf-8")
            missing = Path(tmp) / "missing-rules.json"
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(target), "--rules", str(missing)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("rules config file not found", proc.stderr)

    def test_malformed_rules_config_json_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "README.md"
            target.write_text("# title\n", encoding="utf-8")
            cfg = Path(tmp) / "rules.json"
            cfg.write_text('{"rules": ', encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(target), "--rules", str(cfg)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("invalid JSON in rules config", proc.stderr)

    def test_rules_config_requires_object_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "README.md"
            target.write_text("# title\n", encoding="utf-8")
            cfg = Path(tmp) / "rules.json"
            cfg.write_text('{"rules": []}', encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(target), "--rules", str(cfg)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("rules config must contain an object at 'rules'", proc.stderr)

    def test_rules_config_requires_top_level_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "README.md"
            target.write_text("# title\n", encoding="utf-8")
            cfg = Path(tmp) / "rules.json"
            cfg.write_text("[]", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(target), "--rules", str(cfg)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("rules config must contain a JSON object", proc.stderr)

    def test_unknown_enable_rule_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "README.md"
            target.write_text("# title\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(target), "--enable", "no-such-rule"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("Unknown rule 'no-such-rule' in --enable", proc.stderr)
            self.assertIn("Valid rule names:", proc.stderr)

    def test_unknown_disable_rule_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "README.md"
            target.write_text("# title\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(target), "--disable", "no-such-rule"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("Unknown rule 'no-such-rule' in --disable", proc.stderr)

    def test_unknown_rule_in_rules_config_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "README.md"
            target.write_text("# title\n", encoding="utf-8")
            cfg = Path(tmp) / "rules.json"
            cfg.write_text('{"rules": {"no-such-rule": true}}', encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(target), "--rules", str(cfg)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("Unknown rule 'no-such-rule'", proc.stderr)
            self.assertIn("Valid rule names:", proc.stderr)

    def test_valid_rules_config_path_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "README.md"
            target.write_text("Paragraph with trailing spaces  \n", encoding="utf-8")
            cfg = Path(tmp) / "rules.json"
            cfg.write_text('{"rules": {"trailing-whitespace": false}}', encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(target), "--rules", str(cfg)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0)

    def test_json_output_with_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("# title\nline with trailing spaces  \n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(p), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 1)
            report = json.loads(proc.stdout)
            self.assertEqual(report["schema_version"], 1)
            self.assertEqual(report["tool"]["name"], "mdguard")
            self.assertEqual(report["issue_count"], 1)
            self.assertEqual(report["files"][0]["path"], str(p))
            self.assertEqual(report["files"][0]["issues"][0]["rule"], "trailing-whitespace")

    def test_json_output_with_clean_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("# title\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(p), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0)
            report = json.loads(proc.stdout)
            self.assertEqual(report["issue_count"], 0)
            self.assertEqual(report["files"][0]["path"], str(p))
            self.assertEqual(report["files"][0]["issues"], [])

    def test_json_output_parseable_and_no_human_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("bad  \n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(p), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            json.loads(proc.stdout)
            self.assertNotIn("✅", proc.stdout)
            self.assertNotIn("⚠️", proc.stdout)
            self.assertNotIn("No issues found", proc.stdout)

    def test_fix_json_reports_only_remaining_unfixed_issues(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  \n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "mdguard.cli", str(p), "--fix", "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 1)
            report = json.loads(proc.stdout)
            self.assertEqual(report["issue_count"], 1)
            self.assertEqual(report["files"][0]["issues"][0]["rule"], "line-length")
            self.assertTrue(p.read_text(encoding="utf-8").endswith("\n"))


if __name__ == "__main__":
    unittest.main()
