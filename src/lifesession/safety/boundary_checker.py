"""Scans files for obvious private-data patterns before public release."""
from __future__ import annotations
import re
from importlib.util import source_from_cache
from pathlib import Path

_PATTERNS = [
    (r"(?i)api[_\-]?key\s*=\s*['\"][^'\"]{8,}", "API key assignment"),
    (r"(?i)token\s*=\s*['\"][^'\"]{8,}", "token assignment"),
    (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "IP address"),
    (r"ssh://[^\s]+", "SSH URL"),
    (r"/home/deploy/", "internal deploy path"),
    (r"/opt/ai-stab", "internal project path"),
]


def scan_directory(path: str | Path) -> list[dict]:
    issues = []
    self_path = Path(__file__).resolve()
    for f in Path(path).rglob("*"):
        if not f.is_file() or f.resolve() == self_path:
            continue
        # The scanner's own bytecode embeds the same detection patterns as its
        # excluded source. Exclude only caches mapped to this exact source;
        # other bytecode and files inside __pycache__ must still be scanned.
        if f.suffix == ".pyc":
            try:
                if Path(source_from_cache(str(f.resolve()))).resolve() == self_path:
                    continue
            except ValueError:
                pass
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        for pattern, label in _PATTERNS:
            for match in re.finditer(pattern, text):
                issues.append({
                    "file": str(f),
                    "line": text[: match.start()].count("\n") + 1,
                    "label": label,
                    "snippet": match.group()[:60],
                })
    return issues


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    found = scan_directory(target)
    if found:
        for i in found:
            print(f"[{i['label']}] {i['file']}:{i['line']} — {i['snippet']}")
        sys.exit(1)
    print("OK — no private-data patterns found.")
