from __future__ import annotations

import types
import unittest
from unittest import mock

import p43_bounded_zero_click_live_diagnostic_final as f


class FinalEntryTests(unittest.TestCase):
    def test_run_delegates_to_post_p45_p46_continuation(self):
        args = types.SimpleNamespace()
        expected = ({"firstFailingGate": None}, 0, {"receiptPath": "x"})
        with mock.patch.object(f.continuation, "run", return_value=expected) as run:
            self.assertEqual(expected, f.run(args))
        run.assert_called_once_with(args)

    def test_final_surface_no_longer_calls_legacy_standalone_p42_start(self):
        self.assertFalse(hasattr(f, "_preflight_before_p42"))
        self.assertTrue(hasattr(f, "continuation"))


if __name__ == "__main__":
    unittest.main()
