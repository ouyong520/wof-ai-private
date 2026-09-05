from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.canonical_acceptance_evidence import build_acceptance_evidence
from wof_launcher.canonical_owner_status import normalize_owner_status
from wof_launcher.state import StatusStore
from wof_launcher.tray import TrayApp


def accepted(**changes):
    data = {
        "browser_connected": True,
        "wof_page_found": True,
        "worker_found": True,
        "wasm_module_found": True,
        "heap_found": True,
        "world_921031": True,
        "identity_sha256": "a" * 64,
        "page_target_id": "page-1",
        "worker_target_id": "worker-1",
        "alpha_requested": True,
        "alpha_running": True,
        "alpha_runtime_epoch": "runtime-1",
        "alpha_package_version": "package-1",
        "alpha_error": None,
        "last_error": None,
        "read_only": True,
        "ram_writes": 0,
        "input_injection": False,
    }
    data.update(changes)
    return data


class AlphaP16CanonicalOwnerStatusTests(unittest.TestCase):
    def test_normalized_owner_state_progression_is_fail_closed(self):
        waiting = normalize_owner_status({"alpha_requested": True})
        self.assertEqual(waiting["state"], "WAITING_WOF")

        verifying = normalize_owner_status(accepted(world_921031=False, alpha_running=False, alpha_status=None))
        self.assertEqual(verifying["state"], "VERIFYING_WORLD")

        stack = normalize_owner_status(accepted(alpha_status={
            "running": True,
            "authorityKey": "authority-1",
            "page": {
                "canonicalOverlayCapable": True,
                "canonicalOverlayStatus": {"bound": False, "state": "SUPPRESSED", "reason": "NOT_BOUND"},
            },
        }))
        self.assertEqual(stack["state"], "CANONICAL_STACK_READY")

        source = normalize_owner_status(accepted(alpha_status={
            "running": True,
            "canonical": {
                "state": "SUPPRESSED",
                "reason": "RENDERER_SOURCE_UNPROVEN",
                "rendererSource": {"proven": False, "rendererEpoch": "renderer-1"},
            },
        }))
        self.assertEqual(source["state"], "WAITING_RENDERER_SOURCE")

        identity = normalize_owner_status(accepted(alpha_status={
            "running": True,
            "canonical": {"state": "SUPPRESSED", "reason": "ACTOR_ASSOCIATION_UNPROVEN"},
        }))
        self.assertEqual(identity["state"], "IDENTITY_SUPPRESSED")

        hidden = normalize_owner_status(accepted(alpha_status={
            "running": True,
            "canonical": {"state": "SUPPRESSED", "reason": "STALE_AUTHORITY_OR_RENDERER_EPOCH"},
        }))
        self.assertEqual(hidden["state"], "ANCHORS_SUPPRESSED")

        anchors = normalize_owner_status(accepted(alpha_status={
            "running": True,
            "canonical": {
                "rendererSource": {"proven": True, "rendererEpoch": "renderer-1"},
                "anchors": {"state": "READY", "reason": "CURRENT_FRAME_READY"},
            },
        }))
        self.assertEqual(anchors["state"], "ANCHORS_READY")

        hud = normalize_owner_status(accepted(alpha_status={
            "running": True,
            "canonical": {
                "anchors": {"state": "READY"},
                "hud": {"state": "INGEST_ACCEPTED", "reason": "READY_RECORDS_ACCEPTED"},
            },
        }))
        self.assertEqual(hud["state"], "HUD_INGEST_ACCEPTED")
        self.assertNotIn("可见", hud["labelZh"])
        self.assertNotIn("PASS", hud["humanZh"].upper())

        error = normalize_owner_status(accepted(alpha_error="bridge/CDP failure", alpha_status={"running": False}))
        self.assertEqual(error["state"], "CANONICAL_RUNTIME_ERROR")
        self.assertIn("bridge/CDP failure", error["humanZh"])

    def test_current_p15_runtime_contract_maps_wait_and_hud_acceptance(self):
        waiting = normalize_owner_status(accepted(alpha_status={
            "running": True,
            "runtimeEpoch": "runtime-1",
            "authorityKey": "authority-1",
            "packageVersion": "package-1",
            "canonicalOverlay": {
                "state": "WAITING",
                "reason": "WAITING_FOR_W3_FRAME_SOURCE_QUALIFICATION",
                "active": True,
                "stackInstalled": True,
                "capabilityPresent": True,
                "bound": False,
                "authorityKey": "authority-1",
                "runtimeEpoch": "runtime-1",
                "rendererEpoch": None,
                "frameResolution": {"state": "WAITING", "reason": "WAITING_FOR_W3_FRAME", "descriptorCount": 0},
                "latestIngest": {
                    "state": "SUPPRESSED",
                    "reason": "WAITING_FOR_W3_FRAME",
                    "recordCount": 0,
                    "readyRecordCount": 0,
                    "suppressedRecordCount": 0,
                    "hudState": None,
                    "hudReason": None,
                },
                "rendererSourceProvenInLatestFrame": False,
                "bridge": {"hud": None, "authorityBinding": None},
            },
        }))
        self.assertEqual(waiting["state"], "WAITING_RENDERER_SOURCE")

        accepted_hud = normalize_owner_status(accepted(alpha_status={
            "running": True,
            "runtimeEpoch": "runtime-1",
            "authorityKey": "authority-1",
            "packageVersion": "package-1",
            "canonicalOverlay": {
                "state": "READY",
                "reason": "CANONICAL_ANCHORS_READY",
                "active": True,
                "stackInstalled": True,
                "capabilityPresent": True,
                "bound": True,
                "authorityKey": "authority-1",
                "runtimeEpoch": "runtime-1",
                "rendererEpoch": "renderer-1",
                "frameResolution": {"state": "READY", "reason": "READY", "descriptorCount": 2},
                "latestIngest": {
                    "state": "READY",
                    "reason": "READY",
                    "recordCount": 2,
                    "readyRecordCount": 2,
                    "suppressedRecordCount": 0,
                    "hudState": "READY",
                    "hudReason": "READY",
                },
                "rendererSourceProvenInLatestFrame": True,
                "bridge": {
                    "hud": {"state": "READY", "reason": "READY", "bound": True},
                    "authorityBinding": {
                        "authorityKey": "authority-1",
                        "runtimeEpoch": "runtime-1",
                        "rendererEpoch": "renderer-1",
                        "worldSha256": "a" * 64,
                    },
                },
            },
        }))
        self.assertEqual(accepted_hud["state"], "HUD_INGEST_ACCEPTED")
        self.assertEqual(accepted_hud["rendererEpoch"], "renderer-1")
        self.assertEqual(accepted_hud["hudCanonicalStatus"]["state"], "READY")

    def test_status_store_records_only_meaningful_canonical_transitions(self):
        store = StatusStore(persist_acceptance_evidence=False)
        store.update(alpha_requested=True)
        base = accepted()
        stack = {
            "running": True,
            "authorityKey": "authority-1",
            "page": {"canonicalOverlayCapable": True, "canonicalOverlayStatus": {"state": "SUPPRESSED", "reason": "NOT_BOUND"}},
        }
        store.update(**base, alpha_status=stack, state="CONNECTED")
        before = [e for e in store.get().significant_events if e.get("kind") == "canonical-state-transition"]
        store.update(alpha_status=stack)
        after = [e for e in store.get().significant_events if e.get("kind") == "canonical-state-transition"]
        self.assertEqual(len(before), len(after))

        store.update(alpha_status={
            "running": True,
            "canonical": {"rendererSource": {"proven": False, "rendererEpoch": "renderer-1"}, "state": "SUPPRESSED", "reason": "RENDERER_SOURCE_UNPROVEN"},
        })
        store.update(alpha_status={
            "running": True,
            "canonical": {"rendererSource": {"proven": True, "rendererEpoch": "renderer-1"}, "anchors": {"state": "READY"}},
        })
        store.update(alpha_status={
            "running": True,
            "canonical": {"anchors": {"state": "READY"}, "hud": {"state": "INGEST_ACCEPTED"}},
        })
        events = [e for e in store.get().significant_events if e.get("kind") == "canonical-state-transition"]
        self.assertEqual(events[-1]["canonicalState"], "HUD_INGEST_ACCEPTED")
        self.assertEqual(events[-1]["runtimeEpoch"], "runtime-1")
        self.assertEqual(events[-1]["worldSha256"], "a" * 64)

        store.reset_runtime()
        ended = [e for e in store.get().significant_events if e.get("kind") == "canonical-state-transition"][-1]
        self.assertEqual(ended["canonicalState"], "WAITING_WOF")

    def test_status_store_and_acceptance_timeline_are_bounded(self):
        store = StatusStore(persist_acceptance_evidence=False)
        store.update(alpha_requested=True)
        for i in range(140):
            store.update(**accepted(
                alpha_runtime_epoch=f"runtime-{i}",
                alpha_status={
                    "running": True,
                    "authorityKey": f"authority-{i}",
                    "canonical": {
                        "rendererSource": {"proven": False, "rendererEpoch": f"renderer-{i}"},
                        "state": "SUPPRESSED",
                        "reason": "RENDERER_SOURCE_UNPROVEN",
                    },
                },
            ))
        snap = store.get().snapshot()
        self.assertLessEqual(len(snap["significant_events"]), store.EVENT_LIMIT)
        evidence = build_acceptance_evidence(snap, generated_at_utc="2026-09-05T00:00:00Z")
        self.assertLessEqual(len(evidence["canonicalTransitionTimeline"]), 32)
        self.assertEqual(evidence["canonicalTransitionTimeline"][-1]["runtimeEpoch"], "runtime-139")

    def test_tray_canonical_text_outranks_legacy_calibration(self):
        store = StatusStore(persist_acceptance_evidence=False)
        store.update(**accepted(
            alpha_status={
                "running": True,
                "canonical": {"state": "SUPPRESSED", "reason": "RENDERER_SOURCE_UNPROVEN", "rendererSource": {"proven": False}},
                "projectionRecovery": {
                    "ui": {
                        "samples": 8,
                        "cameraQuality": {"targetSamples": 20, "reason": "legacy-calibration"},
                        "guidance": {"actionZh": "继续旧校准"},
                    },
                },
            },
            state="CONNECTED",
        ))
        text = TrayApp._format_status(store.get())
        self.assertIn("等待渲染坐标来源", text)
        self.assertIn("最终可见性：尚未证明", text)
        self.assertNotIn("头顶校准", text)
        self.assertNotIn("继续旧校准", text)
        self.assertNotIn("自动验证已通过", text)

    def test_evidence_is_automatic_shape_and_never_promotes_fixture_to_visible(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.json"
            store = StatusStore(acceptance_evidence_path=path)
            store.update(**accepted(
                alpha_status={
                    "running": True,
                    "authorityKey": "authority-1",
                    "canonical": {
                        "rendererSource": {"proven": True, "rendererEpoch": "renderer-1", "authorityKey": "renderer-authority"},
                        "anchors": {"state": "READY"},
                        "hud": {"state": "INGEST_ACCEPTED", "accepted": True},
                    },
                },
                state="CONNECTED",
            ))
            self.assertTrue(path.is_file())
            evidence = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(evidence["schema"], "wof-alpha-canonical-owner-acceptance-evidence-v1")
            self.assertEqual(evidence["canonical"]["state"], "HUD_INGEST_ACCEPTED")
            self.assertEqual(evidence["visibleProof"], "NOT_PROVEN")
            self.assertEqual(evidence["world"]["pageTargetId"], "page-1")
            self.assertEqual(evidence["world"]["workerTargetId"], "worker-1")
            self.assertEqual(evidence["runtime"]["rendererEpoch"], "renderer-1")
            self.assertEqual(evidence["safety"], {"readOnly": True, "ramWrites": 0, "inputInjection": False})


if __name__ == "__main__":
    unittest.main()
