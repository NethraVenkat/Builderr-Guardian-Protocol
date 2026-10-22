#!/usr/bin/env python3
"""Generate non-destructive baseline file inventory V10 for Guardian Alpha Protocol V10."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def get_git_tracked_files() -> list[str]:
    res = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]


def get_git_untracked_files() -> list[str]:
    res = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True)
    untracked = []
    for line in res.stdout.splitlines():
        if line.startswith("?? "):
            untracked.append(line[3:].strip())
    return untracked


def get_git_ignored_files() -> list[str]:
    res = subprocess.run(["git", "status", "--ignored", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True)
    ignored = []
    for line in res.stdout.splitlines():
        if line.startswith("!! "):
            ignored.append(line[3:].strip())
    return ignored


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    tracked = get_git_tracked_files()
    untracked = get_git_untracked_files()
    ignored = get_git_ignored_files()

    inventory = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip(),
        "total_files": len(tracked) + len(untracked) + len(ignored),
        "tracked_count": len(tracked),
        "untracked_count": len(untracked),
        "ignored_count": len(ignored),
        "files": {},
    }

    for rel_path in tracked:
        p = ROOT / rel_path
        if p.is_file():
            inventory["files"][rel_path] = {
                "status": "tracked",
                "bytes": p.stat().st_size,
                "sha256": file_sha256(p),
            }

    for rel_path in untracked:
        p = ROOT / rel_path
        if p.is_file():
            inventory["files"][rel_path] = {
                "status": "untracked",
                "bytes": p.stat().st_size,
                "sha256": file_sha256(p),
            }

    for rel_path in ignored:
        p = ROOT / rel_path
        if p.is_file():
            inventory["files"][rel_path] = {
                "status": "ignored",
                "bytes": p.stat().st_size,
                "sha256": file_sha256(p),
            }

    out_file = ROOT / "research" / "evidence" / "baseline_file_inventory_v10.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)

    print(f"Generated {out_file} with {inventory['total_files']} files (tracked: {len(tracked)}, untracked: {len(untracked)}, ignored: {len(ignored)}).")


if __name__ == "__main__":
    main()
