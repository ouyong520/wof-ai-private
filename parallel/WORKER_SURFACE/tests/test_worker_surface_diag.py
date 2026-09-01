from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "worker_surface_diag.py"
SPEC = importlib.util.spec_from_file_location("worker_surface_diag", MODULE_PATH)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class WorkerSurfaceClassifierTests(unittest.TestCase):
    def codes(self, capture):
        return {row["code"] for row in MOD.classify(capture)}

    def test_url_filter_mismatch(self):
        self.assertIn("WORKER_URL_FILTER_MISMATCH", self.codes({
            "directTargets": [{"targetId":"w","type":"worker","url":"https://cdn/runtime.js"}],
            "relatedTargets": [],
            "probes": [{"targetId":"w","targetType":"worker","targetUrl":"https://cdn/runtime.js","moduleOk":True}],
            "events": [],
        }))

    def test_related_target_only(self):
        self.assertIn("RELATED_TARGET_ONLY", self.codes({
            "directTargets": [{"targetId":"p","type":"page","url":"https://game/"}],
            "relatedTargets": [{"targetId":"w","type":"worker","url":""}],
            "probes": [{"targetId":"w","targetType":"worker","targetUrl":"","moduleOk":True}],
            "events": [],
        }))

    def test_page_or_frame_runtime(self):
        self.assertIn("RUNTIME_IN_PAGE_OR_FRAME_CONTEXT", self.codes({
            "directTargets": [{"targetId":"p","type":"page","url":"https://game/"}],
            "relatedTargets": [],
            "probes": [{"targetId":"p","targetType":"page","moduleOk":True,"contextId":7}],
            "events": [],
        }))

    def test_target_info_lifecycle(self):
        self.assertIn("TARGET_INFO_LIFECYCLE", self.codes({
            "directTargets": [], "relatedTargets": [], "probes": [],
            "events": [
                {"method":"Target.targetCreated","params":{"targetInfo":{"targetId":"w","url":""}}},
                {"method":"Target.targetInfoChanged","params":{"targetInfo":{"targetId":"w","url":"https://x/gstyphoon.js"}}},
            ],
        }))

    def test_read_only_method_boundary(self):
        self.assertFalse(any(x.startswith("Input.") for x in MOD.SAFE))
        self.assertNotIn("Runtime.callFunctionOn", MOD.SAFE)


if __name__ == "__main__":
    unittest.main()
