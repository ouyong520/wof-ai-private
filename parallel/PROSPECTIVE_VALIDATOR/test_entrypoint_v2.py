import unittest
from pathlib import Path

import discovery_v2 as d

HERE = Path(__file__).resolve().parent


class EntryPointV2Tests(unittest.TestCase):
    def test_direct_and_imported_python_entry_route_to_v2(self):
        text = (HERE / "live_validator.py").read_text(encoding="utf-8")
        self.assertIn('from live_validator_v2 import main', text)
        self.assertIn('from live_validator_v2 import main as _v2_main', text)
        self.assertIn('from live_validator_core import *', text)
        self.assertNotIn('GSTYPHOON_RE.search', text)

    def test_owner_cmd_routes_to_v2(self):
        text = (HERE / "RUN_PROSPECTIVE_VALIDATOR.cmd").read_text(encoding="utf-8")
        self.assertIn('live_validator_v2.py', text)
        self.assertIn('Discovery V2', text)
        self.assertNotIn('%PY% live_validator.py', text)

    def test_v2_live_path_has_no_legacy_url_type_gate(self):
        text = (HERE / "live_validator_v2.py").read_text(encoding="utf-8")
        self.assertIn('discover_candidates(', text)
        self.assertIn('validate_session(self.session, self.manifest)', text)
        self.assertNotIn('GSTYPHOON_RE.search', text)
        self.assertNotIn('target.get("type") == "worker"', text)

    def test_discovery_module_keeps_input_methods_out(self):
        self.assertIn("Target.setAutoAttach", d.DISCOVERY_CDP_METHODS)
        self.assertFalse(any(method.startswith("Input.") for method in d.DISCOVERY_CDP_METHODS))
        self.assertNotIn("Runtime.callFunctionOn", d.DISCOVERY_CDP_METHODS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
