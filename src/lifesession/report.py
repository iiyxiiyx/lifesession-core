"""Local, deterministic Markdown reports. This is not a data sanitizer."""
from __future__ import annotations

import json
import re


def _literal(value: object) -> str:
    """Use a fence longer than any user-supplied backtick sequence."""
    text = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)
    longest = max((len(m.group()) for m in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}\n{text}\n{fence}"


def render_markdown(session: dict) -> str:
    """Render a session record, preserving unknown fields as literal data.

    Accepts session snapshots and Session.close() records. It checks the record
    envelope, not full JSON-schema conformance. Nothing is fetched or published.
    """
    if not isinstance(session, dict):
        raise ValueError("session must be a JSON object")
    if not isinstance(session.get("session_id"), str) or not session["session_id"].strip():
        raise ValueError("session_id must be a non-empty string")
    sections = ["# LifeSession report"]
    labels = {
        "session_id": "Session ID", "status": "Status", "type": "Type",
        "opened_at": "Opened at", "closed_at": "Closed at", "mission": "Mission",
        "summary": "Summary", "events": "Events", "decisions": "Decisions",
        "note": "Note",
    }
    for key, label in labels.items():
        if key in session:
            sections.append(f"## {label}\n\n{_literal(session[key])}")
    other = {key: value for key, value in session.items() if key not in labels}
    if other:
        sections.append("## Additional fields\n\n" + _literal(other))
    return "\n\n".join(sections) + "\n"
