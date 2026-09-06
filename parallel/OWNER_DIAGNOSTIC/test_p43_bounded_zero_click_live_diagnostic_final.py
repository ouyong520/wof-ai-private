from __future__ import annotations
import types
import unittest
from unittest import mock

import p43_bounded_zero_click_live_diagnostic_final as f


class FinalEntryTests(unittest.TestCase):
    def test_preflight_fails_closed_before_p42_on_candidate_error(self):
        args = types.SimpleNamespace(repo_root='r',metadata_commit='m',source_commit='s',pointer='p',provenance='v',source_checkout='c')
        with mock.patch.object(f.core, 'GitReader', side_effect=RuntimeError('bad')):
            ok, reason = f._preflight_before_p42(args)
        self.assertFalse(ok)
        self.assertIn('bad', reason)

    def test_preflight_requires_dedicated_python_after_exact_binding(self):
        args = types.SimpleNamespace(repo_root='r',metadata_commit='m',source_commit='s',pointer='p',provenance='v',source_checkout='c')
        with mock.patch.object(f.core, 'GitReader', return_value=object()), \
             mock.patch.object(f.core, 'verify_candidate_binding', return_value={'state':'PASS'}), \
             mock.patch.object(f.core, 'verify_source_checkout', return_value={'clean':True}), \
             mock.patch.object(f.core, 'verify_dedicated_python', side_effect=RuntimeError('wrong venv')):
            ok, reason = f._preflight_before_p42(args)
        self.assertFalse(ok)
        self.assertIn('wrong venv', reason)

    def test_preflight_pass_path(self):
        args = types.SimpleNamespace(repo_root='r',metadata_commit='m',source_commit='s',pointer='p',provenance='v',source_checkout='c')
        with mock.patch.object(f.core, 'GitReader', return_value=object()), \
             mock.patch.object(f.core, 'verify_candidate_binding', return_value={'state':'PASS'}), \
             mock.patch.object(f.core, 'verify_source_checkout', return_value={'clean':True}), \
             mock.patch.object(f.core, 'verify_dedicated_python', return_value={'dedicated':True}):
            ok, reason = f._preflight_before_p42(args)
        self.assertTrue(ok)
        self.assertIsNone(reason)


if __name__ == '__main__':
    unittest.main()
