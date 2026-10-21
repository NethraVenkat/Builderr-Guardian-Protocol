"""Generate versioned inventory v4 of all tracked, untracked, and ignored repository files with SHA-256."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def get_git_files() -> tuple[list[str], list[str], list[str]]:
    # Tracked files
    res_tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    tracked = [f.strip() for f in res_tracked.stdout.splitlines() if f.strip()]

    # Untracked files
    res_untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    untracked = [f.strip() for f in res_untracked.stdout.splitlines() if f.strip()]

    # Ignored files
    res_ignored = subprocess.run(
        ["git", "ls-files", "--others", "-i", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    ignored = [f.strip() for f in res_ignored.stdout.splitlines() if f.strip()]

    return tracked, untracked, ignored


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    tracked, untracked, ignored = get_git_files()
    all_files = []

    for rel_path in sorted(tracked):
        p = ROOT / rel_path
        if p.is_file():
            all_files.append({
                "path": rel_path.replace("\\", "/"),
                "status": "tracked",
                "size_bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            })

    for rel_path in sorted(untracked):
        p = ROOT / rel_path
        if p.is_file():
            all_files.append({
                "path": rel_path.replace("\\", "/"),
                "status": "untracked",
                "size_bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            })

    for rel_path in sorted(ignored):
        p = ROOT / rel_path
        if p.is_file():
            all_files.append({
                "path": rel_path.replace("\\", "/"),
                "status": "ignored",
                "size_bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            })

    inventory = {
        "inventory_version": "v4",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "git_branch": subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "total_files": len(all_files),
        "tracked_count": len(tracked),
        "untracked_count": len(untracked),
        "ignored_count": len(ignored),
        "files": all_files,
    }

    out_file = ROOT / "research" / "evidence" / "baseline_file_inventory_v4.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)

    print(f"Generated {out_file} with {len(all_files)} files (tracked: {len(tracked)}, untracked: {len(untracked)}, ignored: {len(ignored)}).")


if __name__ == "__main__":
    main()
