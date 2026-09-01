from __future__ import annotations

import unittest

import _test_unified_live_proof_base as _base
import unified_live_proof as u

for _name in dir(_base):
    if not _name.startswith("__") and _name != "UnifiedProofTests":
        globals()[_name] = getattr(_base, _name)

_ADMISSION = "+ 房间 room-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
_FATAL = "WOF-052L 采集器没有正常完成"


class UnifiedProofTests(_base.UnifiedProofTests):
    def test_recovery_requires_new_current_recorder_positive_generation(self):
        r = u.RecorderEvidence()
        r.begin_source_generation("test-recorder-generation-1")
        r.feed(_ADMISSION, source_generation="test-recorder-generation-1")
        first_generation = r.admission_generation
        r.feed(_FATAL, source_generation="test-recorder-generation-1")
        self.assertFalse(r.current_healthy)
        self.assertFalse(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST), u.normalize_pylaunch(fresh_proof()),
            r, live_processes()
        ))

        # Recovery is a new Recorder runtime/admission generation. The revoked
        # generation cannot re-admit itself.
        r.begin_source_generation("test-recorder-generation-2")
        r.feed(_ADMISSION, source_generation="test-recorder-generation-2")
        self.assertTrue(r.current_healthy)
        self.assertGreater(r.admission_generation, first_generation)
        self.assertEqual(r.admission_source_generation, "test-recorder-generation-2")
        self.assertTrue(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST), u.normalize_pylaunch(fresh_proof()),
            r, live_processes()
        ))

    def test_sticky_run_blocker_prevents_recovered_state_from_passing_same_run(self):
        r = u.RecorderEvidence()
        r.begin_source_generation("test-recorder-generation-1")
        r.feed(_ADMISSION, source_generation="test-recorder-generation-1")
        r.feed(_FATAL, source_generation="test-recorder-generation-1")
        sticky = ["Recorder 曾发生 fatal"]

        r.begin_source_generation("test-recorder-generation-2")
        r.feed(_ADMISSION, source_generation="test-recorder-generation-2")
        payload = self.status(
            recorder=r,
            playability="CONFIRMED",
            blockers=sticky,
        )
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertTrue(payload["live"]["recorderDiscoveryV2Admission"]["admitted"])
        self.assertEqual(
            payload["live"]["recorderDiscoveryV2Admission"]["admissionSourceGeneration"],
            "test-recorder-generation-2",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
