from __future__ import annotations

import unittest

import p47_bounded_owner_diagnostic_readiness_gate as core
import p47_bounded_owner_diagnostic_readiness_gate_final as final
from test_p47_bounded_owner_diagnostic_readiness_gate import happy_snapshot


class P47TerminalResultByteTests(unittest.TestCase):
    def test_exact_terminal_result_bytes_pass(self):
        s = happy_snapshot()
        s["terminalResultBytesMatch"] = {"p43": True, "p45": True, "p46": True}
        self.assertEqual(core.READY, final.evaluate(s)["decision"])

    def test_drifted_terminal_result_bytes_block(self):
        s = happy_snapshot()
        s["terminalResultBytesMatch"] = {"p43": True, "p45": False, "p46": True}
        out = final.evaluate(s)
        self.assertEqual(core.BLOCKED, out["decision"])
        self.assertEqual(0, out["runBudget"])
        self.assertIn("P45_TERMINAL_RESULT_BYTES_DRIFTED", out["blockerCodes"])


if __name__ == "__main__":
    unittest.main()
