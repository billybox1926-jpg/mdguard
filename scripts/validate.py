"""Local production-readiness gate for mdguard."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(args: list[str], *, cwd: Path = ROOT) -> None:
    print("$ " + " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def clean() -> None:
    for name in ("build", "dist"):
        shutil.rmtree(ROOT / name, ignore_errors=True)
    for path in (ROOT / "src").glob("*.egg-info"):
        shutil.rmtree(path, ignore_errors=True)


def assert_json_output() -> None:
    proc = subprocess.run(
        [PYTHON, "-m", "mdguard.cli", "README.md", "docs", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    report = json.loads(proc.stdout)
    if report.get("issue_count") != 0:
        raise SystemExit(
            f"expected clean docs, got {report.get('issue_count')} issue(s)"
        )


def smoke_wheel() -> None:
    wheel = next((ROOT / "dist").glob("*.whl"), None)
    if wheel is None:
        raise SystemExit("wheel was not built")
    with tempfile.TemporaryDirectory() as tmp:
        env = Path(tmp) / "venv"
        venv.create(env, with_pip=True)
        scripts = env / ("Scripts" if sys.platform == "win32" else "bin")
        python = scripts / ("python.exe" if sys.platform == "win32" else "python")
        mdguard = scripts / ("mdguard.exe" if sys.platform == "win32" else "mdguard")
        run([str(python), "-m", "pip", "install", str(wheel)])
        run([str(mdguard), "--version"])
        run([str(mdguard), "--list-rules", "--verbose"])
        # Verify the new --security-rules flag is accepted
        run([str(mdguard), "--security-rules", "--list-rules"])


def smoke_security_flags() -> None:
    """Verify the new security rule CLI flags parse without error."""
    for flag in ("--enable", "--disable", "--security-rules"):
        subprocess.run(
            [PYTHON, "-m", "mdguard.cli", flag, "security-xss", "--list-rules"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            [PYTHON, "-m", "mdguard.cli", flag, "security-urls", "--list-rules"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            [PYTHON, "-m", "mdguard.cli", flag, "security-secrets", "--list-rules"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
    print("✅ Security rule flags accepted")


def main() -> int:
    clean()
    run([PYTHON, "-m", "unittest", "discover", "-s", "tests", "-v"])
    py_files = subprocess.check_output(
        ["git", "ls-files", "*.py"], cwd=ROOT, text=True
    ).splitlines()
    run([PYTHON, "-m", "py_compile", *py_files])
    run([PYTHON, "-m", "mdguard.cli", "--help"])
    run([PYTHON, "-m", "mdguard.cli", "--version"])
    run([PYTHON, "-m", "mdguard.cli", "--list-rules", "--verbose"])
    run([PYTHON, "-m", "mdguard.cli", "docs", "README.md", "CONTRIBUTING.md"])
    assert_json_output()
    run([PYTHON, "-m", "build"])
    smoke_wheel()
    smoke_security_flags()
    clean()
    run(["git", "diff", "--check"])
    run(["git", "status", "--short"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
