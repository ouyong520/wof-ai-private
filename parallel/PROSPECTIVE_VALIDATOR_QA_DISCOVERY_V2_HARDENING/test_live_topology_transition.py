from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMPL = HERE.parent / "PROSPECTIVE_VALIDATOR" / "live_validator_v2.py"
FIXTURE = HERE / "fixtures" / "live_unique_to_shared_worker.json"


class LiveTopologyTransitionIndependentQATests(unittest.TestCase):
    def test_unique_to_shared_worker_must_finalize_before_any_further_drain(self) -> None:
        """Fail on any positive ambiguity-audit window that still drains a live room."""
        source = IMPL.read_text(encoding="utf-8")
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

        tree = ast.parse(source)
        audit_interval = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "AUDIT_LIVE_TOPOLOGY_INTERVAL":
                        audit_interval = ast.literal_eval(node.value)
        self.assertIsNotNone(audit_interval, "live topology audit interval must be explicit")

        skips_live_pages_between_audits = bool(re.search(
            r"skip_page_ids\s*=\s*set\(\)\s*if\s*audit_live\s*else\s*live_page_ids",
            source,
        ))
        ambiguity_pos = source.find("ambiguous = ambiguous_page_ids(diag)")
        drain_pos = source.find("for tid, room in list(endpoint.rooms.items()):", ambiguity_pos + 1)
        drain_call_pos = source.find("__WOF_PROSPECTIVE_VALIDATOR.drain()", drain_pos)
        unconditional_drain_after_discovery = ambiguity_pos >= 0 and drain_pos > ambiguity_pos and drain_call_pos > drain_pos

        transition_t = float(fixture["transition"]["t"])
        poll_t = float(fixture["adversarialPoll"]["t"])
        last_audit = float(fixture["initial"]["lastTopologyAudit"])
        inside_gap = transition_t < poll_t < last_audit + float(audit_interval)

        unsafe_window_exists = (
            float(audit_interval) > 0
            and inside_gap
            and skips_live_pages_between_audits
            and unconditional_drain_after_discovery
        )

        self.assertFalse(
            unsafe_window_exists,
            "P0: after a unique->ambiguous shared-Worker transition, current live control flow can skip the live page during the audit gap and still drain prospective evidence before ambiguity is detected/finalized",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
