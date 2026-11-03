"""Command-line tools that operate on local session files only."""
import argparse
import json
from pathlib import Path
import sys

from .report import render_markdown


def _reject_constant(value):
    raise ValueError("non-finite JSON number")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m lifesession")
    commands = parser.add_subparsers(dest="command", required=True)
    report = commands.add_parser("report", help="render a local JSON session as Markdown")
    report.add_argument("session", type=Path, help="local UTF-8 JSON file")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.session.read_text(encoding="utf-8"), parse_constant=_reject_constant)
        output = render_markdown(data)
    except (OSError, UnicodeError, ValueError, RecursionError):
        # Do not echo file contents, paths, or parser snippets into diagnostics.
        print("error: cannot render session; use readable UTF-8 JSON with a non-empty session_id", file=sys.stderr)
        return 2
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
