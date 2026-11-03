# LifeSession Core

**An open-source operational terminal for maintainers and small teams.**

LifeSession turns work into reviewable sessions — bounded units of operational attention with missions, events, decisions, and structured close records. Think of it as a lightweight structured log for anything your team or agent does.

![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Status](https://img.shields.io/badge/status-active-green)

---

## Why LifeSession

Modern teams and AI agents produce a constant stream of decisions, events, and state changes — but most of that work is invisible. There is no structured record of what happened, why it was decided, or how to review it later.

LifeSession solves this with a simple operational model:

```
Mission → Session → Events → Decisions → State → Review
```

Each session is self-contained, reviewable, and safe to share. The schema layer makes sessions machine-readable. The boundary checker ensures the public package stays clean.

---

## What Is Included

| Component | Description |
|-----------|-------------|
| `schemas/` | JSON schemas — mission, event, decision, session state |
| `examples/` | Fake end-to-end workflows: maintainer, commerce, gallery, simulation |
| `src/lifesession/` | Demo Python package — session lifecycle, boundary checker |
| `tests/` | 15 unit tests covering session, boundary, schemas, examples |
| `docs/` | Architecture, vision, Codex workflows, public/private boundary |
| `.github/` | Issue templates, PR templates, CI stub |

---

## Quickstart

```bash
git clone https://github.com/your-org/lifesession-core
cd lifesession-core
python -m unittest discover -s tests -v
```

Expected output: `Ran 15 tests in ...s — OK`

No external dependencies required.

---

## How Codex Maintains This Project

LifeSession Core is actively maintained by [Codex](https://openai.com/codex) through structured work sessions.

Each Codex session follows the same lifecycle that LifeSession itself models:

1. **Read context** — task card, previous session handoff, git log
2. **Execute** — schema updates, test fixes, doc improvements, issue triage
3. **Verify** — run `unittest discover`, run `boundary_checker.py`
4. **Commit** — clean commit with task reference
5. **Handoff** — write session report for next agent or human review

This creates a self-referential loop: the tool that manages sessions is itself maintained through sessions. Every Codex contribution is traceable, reviewable, and bounded.

**Codex tasks this project:**
- Schema evolution and validation
- Test coverage expansion
- Documentation and roadmap updates
- Issue triage and PR review assistance
- Boundary compliance checking before any public push
- Release preparation

See [docs/codex-workflows.md](docs/codex-workflows.md) for the full workflow spec.

---

## Architecture

```text
                    ┌─────────────┐
                    │   Mission   │  goal + constraints
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Session   │  bounded unit of attention
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼────┐ ┌─────▼────┐ ┌────▼──────┐
       │  Events   │ │Decisions │ │   State   │
       └──────┬────┘ └─────┬────┘ └────┬──────┘
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │   Review    │  close record + summary
                    └─────────────┘
```

**Components:**
- **Mission** — the goal and constraints for a work period
- **Event** — observation, signal, user action, or system update
- **Decision** — reviewable choice with rationale and outcome
- **Session state** — current snapshot, safe to serialize and share
- **Boundary checker** — scans files for private-data patterns before any push

---

## Example Session (fake data)

```json
{
  "session_id": "sess-demo-001",
  "mission": "review open pull requests",
  "status": "closed",
  "events": [
    { "type": "pr_opened", "source": "github", "ref": "pr-42" },
    { "type": "review_requested", "source": "agent", "assignee": "maintainer" }
  ],
  "decisions": [
    { "title": "Merge PR-42", "outcome": "approved", "rationale": "tests pass, boundary clean" }
  ],
  "closed_at": "2026-06-06T10:00:00Z"
}
```

All examples in `examples/` use fake data only. See [docs/public-private-boundary.md](docs/public-private-boundary.md).

For a complete fictional bug-triage walkthrough, see
[`examples/maintainer/api_triage_session.json`](examples/maintainer/api_triage_session.json).
It records a mission, two events, a reviewable decision and a close summary.
It is a demonstration envelope, not a complete JSON Schema validation example.

---

## Safety Boundary

This repository is simulation-first and public-safe by design:

- ✅ Schemas, fake examples, docs, demo stubs
- ❌ No production code, no live APIs, no secrets, no real user data
- ❌ No exchange integrations, no private infrastructure references

The `boundary_checker.py` tool enforces this automatically:

```bash
python src/lifesession/safety/boundary_checker.py .
# OK — no private-data patterns found.
```

---

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Public skeleton — schemas, examples, docs, tests | ✅ Done |
| 1 | Local session runtime — validation, replay, text dashboard | 🔜 Next |
| 2 | Maintainer workflows — issue triage, decision review, close summaries | 📋 Planned |
| 3 | Integrations — optional adapters, strict boundary checks | 📋 Planned |

See [ROADMAP.md](ROADMAP.md) and [open issues](../../issues) for details.

---

## Contributing

Contributions welcome. Before submitting:

- Run `python -m unittest discover -s tests`
- Run `python src/lifesession/safety/boundary_checker.py .`
- No secrets, internal paths, or real data in any file

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## License

MIT. See [LICENSE](LICENSE).

## Export a local session report

From the repository root, render a session JSON file as Markdown:

```bash
PYTHONPATH=src python -m lifesession report examples/maintainer/session_close.json
```

The command writes to standard output. To save a report, redirect it to a file
of your choice. It uses only the Python standard library and makes no network
requests. Invalid JSON, unreadable files, and missing or empty `session_id`
values return exit code 2 without printing input contents.

The exporter supports session snapshots and `Session.close()` records. Common
fields get readable sections; additional fields are preserved as literal JSON.
Text is fenced to prevent embedded Markdown or HTML from becoming report markup.
This checks the session envelope, not full schema conformance.

**Review before sharing:** exporting is not sanitization. The report preserves
input data, including any sensitive values you supply. Use the fake examples for
public demos. Python callers can use `lifesession.report.render_markdown(record)`.
