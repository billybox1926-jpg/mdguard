"""Configuration discovery and parsing."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Tuple

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


def _unquote(value: str) -> str:
    return value.strip().strip('"').strip("'")


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_unquote(item) for item in inner.split(",")]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        return _unquote(value)


def _parse_tool_mdguard_subset(text: str) -> dict[str, Any]:
    in_section = False
    data: dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            in_section = line == "[tool.mdguard]"
            continue
        if in_section and "=" in line:
            key, value = line.split("=", 1)
            data[key.strip()] = _parse_scalar(value)
    return data


def load_pyproject_config(
    start: Optional[Path] = None,
) -> Tuple[dict[str, Any], Optional[Path], Optional[str]]:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for directory in (current, *current.parents):
        pyproject = directory / "pyproject.toml"
        if not pyproject.exists():
            continue
        try:
            text = pyproject.read_text(encoding="utf-8")
            if tomllib is not None:
                data = tomllib.loads(text)
                config = data.get("tool", {}).get("mdguard", {})
            else:
                config = _parse_tool_mdguard_subset(text)
        except Exception as exc:
            return {}, pyproject, f"invalid pyproject config {pyproject}: {exc}"
        if config:
            if not isinstance(config, dict):
                return {}, pyproject, f"[tool.mdguard] in {pyproject} must be a table"
            return dict(config), pyproject, None
    return {}, None, None


def apply_tool_config(
    base: dict[str, object], tool_config: dict[str, Any]
) -> tuple[dict[str, object], list[str]]:
    config = dict(base)
    excludes: list[str] = []
    if "max_length" in tool_config:
        config["max_length"] = int(tool_config["max_length"])
    for name in tool_config.get("enable", []) or []:
        config[str(name)] = True
    for name in tool_config.get("disable", []) or []:
        config[str(name)] = False
    for pattern in tool_config.get("exclude", []) or []:
        excludes.append(str(pattern))
    return config, excludes
