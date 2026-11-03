import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lifesession.report import render_markdown
from lifesession.core.session import Session


class ReportTests(unittest.TestCase):
    def test_existing_session_examples(self):
        for path in (ROOT / "examples").rglob("*.json"):
            data = json.loads(path.read_text())
            if "session_id" in data:
                with self.subTest(path=path.name):
                    result = render_markdown(data)
                    self.assertIn(data["session_id"], result)
                    self.assertIn("## Note", result)

    def test_close_record(self):
        record = Session("maintainer", "demo").close("Reviewed demo queue")
        result = render_markdown(record)
        self.assertIn("## Closed at", result)
        self.assertIn("Reviewed demo queue", result)

    def test_unknown_fields_are_preserved(self):
        data = {"session_id": "demo", "custom": {"count": 0}, "empty": [], "flag": False}
        result = render_markdown(data)
        self.assertIn('"count": 0', result)
        self.assertIn('"flag": false', result)
        self.assertIn('"empty": []', result)

    def test_markup_is_literal(self):
        result = render_markdown({"session_id": "demo", "summary": "```\n<script>alert(1)</script>\n# injected"})
        self.assertIn("````\n```\n<script>", result)
        self.assertTrue(result.endswith("# injected\n````\n"))

    def test_deterministic_unicode_and_no_mutation(self):
        data = {"session_id": "demo", "summary": "Обзор ✓", "events": []}
        before = json.dumps(data)
        self.assertEqual(render_markdown(data), render_markdown(data))
        self.assertIn("Обзор ✓", render_markdown(data))
        self.assertEqual(json.dumps(data), before)

    def test_invalid_envelopes(self):
        for data in ([], None, {}, {"session_id": 42}, {"session_id": "  "}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                render_markdown(data)

    def run_cli(self, path):
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, "-m", "lifesession", "report", str(path)],
                              capture_output=True, text=True, env=env)

    def test_cli_existing_example(self):
        result = self.run_cli(ROOT / "examples/maintainer/session_close.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertTrue(result.stdout.startswith("# LifeSession report\n"))

    def test_cli_rejects_invalid_input_without_echoing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for content in (b"PRIVATE-DEMO malformed", b"\xff", b'[]', b'{"session_id":"demo","value":NaN}'):
                path.write_bytes(content)
                result = self.run_cli(path)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("PRIVATE-DEMO", result.stderr)
                self.assertNotIn(str(path), result.stderr)

    def test_cli_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli(Path(directory) / "missing.json")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
