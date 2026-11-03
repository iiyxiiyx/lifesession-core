import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class ExampleTests(unittest.TestCase):
    def test_all_examples_are_valid_json_and_marked_fake(self):
        files = sorted(EXAMPLES.rglob("*.json"))

        self.assertGreater(len(files), 0)
        for path in files:
            with self.subTest(example=str(path.relative_to(ROOT))):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("note", data)

    def test_trading_sim_examples_are_simulation_mode(self):
        files = sorted((EXAMPLES / "trading_sim").glob("*.json"))

        self.assertGreater(len(files), 0)
        for path in files:
            with self.subTest(example=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIs(data.get("simulation_mode"), True)

    def test_api_triage_example_is_reviewable(self):
        path = EXAMPLES / "maintainer" / "api_triage_session.json"
        data = json.loads(path.read_text(encoding="utf-8"))

        self.assertIn("fake", data["note"].lower())
        self.assertEqual(data["status"], "closed")
        self.assertTrue(data["opened_at"] < data["closed_at"])
        self.assertEqual(data["mission"]["status"], "complete")
        self.assertGreaterEqual(len(data["events"]), 2)
        self.assertGreaterEqual(len(data["decisions"]), 1)

        event_ids = set()
        for event in data["events"]:
            self.assertEqual(event["session_id"], data["session_id"])
            self.assertTrue(data["opened_at"] <= event["created_at"] <= data["closed_at"])
            self.assertNotIn(event["id"], event_ids)
            event_ids.add(event["id"])
        for decision in data["decisions"]:
            self.assertEqual(decision["session_id"], data["session_id"])
            self.assertTrue(data["opened_at"] <= decision["created_at"] <= data["closed_at"])
            self.assertTrue(set(decision["evidence"]).issubset(event_ids))
        self.assertIn("Next:", data["summary"])


if __name__ == "__main__":
    unittest.main()
