#!/usr/bin/env python3
"""Scan for bidirectional Unicode characters in text files."""

import os
import sys

BIDI_BYTES = {
    0x200E,
    0x200F,  # LRM, RLM
    0x202A,
    0x202B,
    0x202C,
    0x202D,
    0x202E,  # LRE, RLE, PDF, LRO, RLO
    0x2066,
    0x2067,
    0x2068,
    0x2069,  # LRI, RLI, FSI, PDI
}

EXTENSIONS = {".py", ".md", ".toml", ".yml", ".json"}

bad = []
for root, dirs, files in os.walk("."):
    # Skip hidden dirs and common non-project dirs
    dirs[:] = [
        d
        for d in dirs
        if not d.startswith(".")
        and d not in ("node_modules", "__pycache__", ".venv", "dist")
    ]
    for f in files:
        if any(f.endswith(ext) for ext in EXTENSIONS):
            path = os.path.join(root, f)
            try:
                data = open(path, "rb").read()
                for i, b in enumerate(data):
                    if b in BIDI_BYTES:
                        bad.append(f"{path}: byte 0x{b:02x} at offset {i}")
            except Exception:
                pass

if bad:
    for b in bad:
        print(b)
    sys.exit(1)

print("No bidirectional Unicode found.")
