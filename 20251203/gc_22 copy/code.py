import os
import re
import sys
from pathlib import Path
from uuid import uuid4

#!/usr/bin/env python3
# GitHub Copilot


def main():
    base_dir = Path(os.path.abspath(os.path.dirname(__file__)))
    pattern = re.compile(r"^dat(\d+)\.dat$")
    files = {p.name: p for p in base_dir.iterdir() if p.is_file() and pattern.match(p.name)}
    if not files:
        print("No dat<N>.dat files found.")
        return

    # Remove lines 11,13,15,... (1-based indexing) from each dat file
    for name, path in files.items():
        try:
            with path.open("r", encoding="utf-8", errors="surrogateescape") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Failed to read {path}: {e}")
            continue

        # Keep lines whose 1-based index is NOT 11,13,15,...
        new_lines = [ln for i, ln in enumerate(lines, start=1) if not (i >= 11 and (i - 11) % 2 == 0)]

        if len(new_lines) == len(lines):
            print(f"No lines removed from {name}")
            continue

        # Write to a temp file then atomically replace original
        temp = path.with_name(path.name + f".tmp_{uuid4().hex}")
        try:
            with temp.open("w", encoding="utf-8", errors="surrogateescape") as f:
                f.writelines(new_lines)
            temp.replace(path)
            print(f"Updated {name}: removed {len(lines) - len(new_lines)} lines")
        except Exception as e:
            print(f"Failed to update {path}: {e}")
            if temp.exists():
                temp.unlink()

if __name__ == "__main__":
    main()