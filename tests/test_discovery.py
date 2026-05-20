import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mdguard.discovery import discover_markdown_files


class TestDiscovery(unittest.TestCase):
    def test_skips_ignored_directories(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "ok.md").write_text("# ok\n", encoding="utf-8")

            ignored_dirs = [
                ".git",
                ".hg",
                ".svn",
                "__pycache__",
                ".mypy_cache",
                ".pytest_cache",
                ".ruff_cache",
                ".tox",
                ".nox",
                ".venv",
                "venv",
                "env",
                "node_modules",
                "build",
                "dist",
                ".eggs",
            ]
            for name in ignored_dirs:
                d = root / name
                d.mkdir(parents=True, exist_ok=True)
                (d / "ignored.md").write_text("# ignored\n", encoding="utf-8")

            files, missing, empty = discover_markdown_files([str(root)])
            self.assertEqual(missing, [])
            self.assertEqual(empty, [])
            self.assertEqual(files, [docs / "ok.md"])

    def test_nested_markdown_still_discovered(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "docs" / "sub"
            nested.mkdir(parents=True)
            a = root / "docs" / "a.md"
            b = nested / "b.markdown"
            a.write_text("# a\n", encoding="utf-8")
            b.write_text("# b\n", encoding="utf-8")

            files, missing, empty = discover_markdown_files([str(root / "docs")])
            self.assertEqual(missing, [])
            self.assertEqual(empty, [])
            self.assertEqual(files, [a, b])

    def test_parent_path_named_ignored_directory_does_not_hide_repo_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "env" / "project"
            docs = project / "docs"
            docs.mkdir(parents=True)
            markdown = docs / "a.md"
            markdown.write_text("# a\n", encoding="utf-8")

            files, missing, empty = discover_markdown_files([str(project)])
            self.assertEqual(missing, [])
            self.assertEqual(empty, [])
            self.assertEqual(files, [markdown])

    def test_mixed_targets_include_direct_file(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            direct = root / "README.md"
            direct.write_text("# readme\n", encoding="utf-8")
            docs = root / "docs"
            docs.mkdir()
            nested = docs / "guide.md"
            nested.write_text("# guide\n", encoding="utf-8")

            files, missing, empty = discover_markdown_files([str(direct), str(root)])
            self.assertEqual(missing, [])
            self.assertEqual(empty, [])
            self.assertEqual(files, [direct, nested])


if __name__ == "__main__":
    unittest.main()
