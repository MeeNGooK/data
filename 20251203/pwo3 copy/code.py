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

    # Build mapping old -> new
    mapping = {}
    for name, path in files.items():
        m = pattern.match(name)
        idx = int(m.group(1))
        new_name = f"dat{idx + 240}.dat"
        mapping[path] = base_dir / new_name

    # Check for accidental overwrite of files not in source set
    dests = set(mapping.values())
    external_conflicts = [d for d in dests if d.exists() and d not in mapping]
    if external_conflicts:
        print("Refusing to overwrite existing files not part of source set:")
        for d in external_conflicts:
            print("  ", d)
        sys.exit(1)

    # Phase 1: rename sources to unique temp names
    temp_map = {}
    for src in mapping:
        temp = src.with_name(src.name + f".tmp_rename_{uuid4().hex}")
        src.replace(temp)
        temp_map[temp] = mapping[src]

    # Phase 2: rename temps to final destinations
    for temp, dest in temp_map.items():
        # If a dest exists and is one of the original sources, it was moved to a temp above,
        # so dest should not exist now. Still check defensively.
        if dest.exists():
            print(f"Unexpected existing destination: {dest}. Aborting.")
            sys.exit(1)
        temp.replace(dest)

    print(f"Renamed {len(mapping)} files in {base_dir}")

if __name__ == "__main__":
    main()