"""Secret and credential scanner across the workspace."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["\'][A-Za-z0-9_\-]{16,}["\']'),
    re.compile(r'ghp_[A-Za-z0-9]{36}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{82}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
]

IGNORE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}


def scan():
    matches = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            p = Path(root) / f
            if p.suffix in (".py", ".json", ".md", ".log", ".txt", ".yaml", ".yml"):
                try:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    for pat in PATTERNS:
                        found = pat.findall(text)
                        if found:
                            matches.append((str(p.relative_to(ROOT)), found))
                except Exception as e:
                    pass

    print(f"Secret scan completed. Found {len(matches)} suspicious matches.")
    for path, items in matches:
        print(f"  {path}: {items}")
    return len(matches)


if __name__ == "__main__":
    scan()
