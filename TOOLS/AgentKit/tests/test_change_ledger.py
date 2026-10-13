import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from check_change_ledger import LEDGER, validate_snapshot


def record(paths, actor="ai", mode="mixed"):
    return json.dumps({
        "schema_version": 1,
        "actor_type": actor,
        "work_mode": mode,
        "summary": "test changes",
        "paths": paths,
    }, separators=(",", ":"))


class ChangeLedgerTests(unittest.TestCase):
    def test_appended_record_covers_all_changed_files(self):
        changed = {"README.md", "TOOLS/AgentKit/agentkit_ext.py", LEDGER}
        current = record(sorted(changed)) + "\n"
        self.assertEqual(validate_snapshot("", current, changed), [])

    def test_missing_record_is_rejected(self):
        self.assertTrue(any("no new provenance record" in error for error in validate_snapshot("", "", {"README.md", LEDGER})))

    def test_untracked_changed_path_is_rejected(self):
        changed = {"README.md", "TASKS/tasks.md", LEDGER}
        current = record(["README.md", LEDGER]) + "\n"
        self.assertTrue(any("TASKS/tasks.md" in error for error in validate_snapshot("", current, changed)))

    def test_old_records_cannot_be_rewritten(self):
        old = record(["old.md"], actor="human", mode="offline") + "\n"
        rewritten = record(["changed.md"]) + "\n"
        self.assertTrue(any("append-only" in error for error in validate_snapshot(old, rewritten, {"changed.md", LEDGER})))

    def test_actor_and_mode_must_be_explicit_values(self):
        changed = {LEDGER, "README.md"}
        current = record(["README.md"], actor="unknown", mode="remote") + "\n"
        errors = validate_snapshot("", current, changed)
        self.assertTrue(any("actor_type" in error for error in errors))
        self.assertTrue(any("work_mode" in error for error in errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
