from __future__ import annotations

import io
import queue
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

TARGET_DIR = Path(__file__).resolve().parents[1] / "LIVE_PROOF_BUNDLE"
sys.path.insert(0, str(TARGET_DIR))

import unified_live_proof as u  # noqa: E402


SAFE_MANIFEST = {
    "version": "wof-browser-fleet-v1",
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
    "windowWorkerReplacement": False,
    "workerStatusAuthority": "cheap-indicator-only",
    "world921031IdentityAuthoritative": False,
    "instances": [{
        "id": 1,
        "host": "127.0.0.1",
        "port": 9423,
        "profileDir": "Proof_01",
        "pid": 123,
        "status": {
            "browser": "OK",
            "page": "OK",
            "worker": "OK",
            "workerDiscovery": "fresh-independent-qa",
            "relatedTopologyCount": 1,
        },
    }],
}

PASS_PROOF_BASE = {
    "schema": "wof-python-launcher-windows-proof-v1",
    "automatedResult": "PASS",
    "checks": {
        "Browser": "OK",
        "WOF page": "OK",
        "Worker": "OK",
        "WASM / heap": "OK",
        "World 921031": "OK",
        "READ ONLY / RAM writes: 0": "OK",
    },
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
    "worldSha256": "qa-freshness-fixture",
}


def iso_offset(seconds: float = 0.0) -> str:
    value = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    return value.isoformat(timespec="microseconds")


def fresh_pass_proof() -> dict:
    proof = dict(PASS_PROOF_BASE)
    proof["checks"] = dict(PASS_PROOF_BASE["checks"])
    proof["lastUpdateUtc"] = iso_offset(0)
    return proof


def live_processes(*, generation: int = 100, seconds: float = 0.0) -> dict:
    return {
        "observedAtUtc": iso_offset(seconds),
        "observationGeneration": generation,
        "launcherRequired": True,
        "recorderRequired": True,
        "launcherLive": True,
        "recorderLive": True,
        "launcherExitCode": None,
        "recorderExitCode": None,
    }


class FreshnessIndependentAdversarialQA(unittest.TestCase):
    def recorder(self) -> u.RecorderEvidence:
        rec = u.RecorderEvidence()
        rec.feed("+ 房间 qa-fresh 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
        return rec

    def status(self, *, recorder=None, proof=None, process_state=None, playability="CONFIRMED"):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return u.build_status(
            run_id="fresh-independent-freshness-qa",
            run_dir=Path(td.name),
            fleet_manifest=SAFE_MANIFEST,
            pylaunch_proof=fresh_pass_proof() if proof is None else proof,
            recorder=self.recorder() if recorder is None else recorder,
            playability=playability,
            stage="FRESHNESS_ADVERSARIAL_QA",
            blockers=[],
            process_state=live_processes() if process_state is None else process_state,
        )

    def test_malformed_health_fresh_fixture_fails_closed(self):
        vectors = [
            {},
            {"observedAtUtc": iso_offset(0), "observationGeneration": True},
            {
                **live_processes(),
                "launcherLive": True,
                "launcherExitCode": 7,
            },
            {
                **live_processes(),
                "recorderRequired": "yes",
            },
        ]
        for process in vectors:
            with self.subTest(process=process):
                out = self.status(process_state=process)
                self.assertFalse(out["live"]["processes"]["healthy"])
                self.assertFalse(out["live"]["automatedChecksReady"])
                self.assertNotEqual(out["overallResult"], "PASS")
                self.assertFalse(out["tenRoomLongCaptureReady"])

    def test_live_but_hung_recent_pass_cannot_cross_generation_gate(self):
        now = iso_offset(0)
        before = {"pylaunch": now, "recorder": 50, "process": 80}
        # Recorder/process keep moving, but the recent PYLAUNCH PASS is hung and
        # therefore keeps the exact same proof generation.
        after = {"pylaunch": now, "recorder": 51, "process": 81}
        self.assertFalse(u.authority_generations_advanced(before, after))

    def test_owner_gate_requires_all_three_generations_to_advance_again(self):
        before_owner = {"pylaunch": iso_offset(-1), "recorder": 60, "process": 90}
        after_owner = {"pylaunch": iso_offset(0), "recorder": 61, "process": 91}
        self.assertTrue(u.authority_generations_advanced(before_owner, after_owner))
        # A second gate with no fresh PYLAUNCH generation must fail closed.
        final = {"pylaunch": after_owner["pylaunch"], "recorder": 62, "process": 92}
        self.assertFalse(u.authority_generations_advanced(after_owner, final))

    def test_valid_carriage_return_supervisor_heartbeat_is_seen(self):
        class FakeProc:
            stdout = io.StringIO("Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0\r")

        rec = self.recorder()
        rec._last_output_monotonic = time.monotonic() - u.RECORDER_FRESHNESS_SECONDS - 1
        self.assertFalse(rec.current_healthy)
        q = queue.Queue()
        u.reader(FakeProc(), "RECORDER", rec, q)
        self.assertTrue(rec.current_healthy)
        self.assertGreaterEqual(rec.output_generation, 2)

    def test_arbitrary_carriage_return_text_must_not_restore_stale_admission_authority(self):
        class FakeProc:
            # Deliberately not a Recorder supervisor heartbeat, not a fresh
            # admission, and not a fatal marker. It represents arbitrary stale
            # diagnostic text becoming visible through the CR-aware reader.
            stdout = io.StringIO("arbitrary stale diagnostic text\r")

        rec = self.recorder()
        rec._last_output_monotonic = time.monotonic() - u.RECORDER_FRESHNESS_SECONDS - 1
        self.assertFalse(rec.current_healthy)

        q = queue.Queue()
        u.reader(FakeProc(), "RECORDER", rec, q)

        # Requirement: CR handling must not let arbitrary stale text become new
        # success authority. Current implementation is expected to fail here by
        # refreshing RecorderEvidence on every non-empty stdout fragment.
        out = self.status(recorder=rec)
        self.assertFalse(rec.current_healthy, "arbitrary text incorrectly refreshed stale Recorder admission")
        self.assertNotEqual(out["overallResult"], "PASS")
        self.assertFalse(out["tenRoomLongCaptureReady"])

    def test_stale_missing_malformed_and_future_pylaunch_timestamps_do_not_authorize_pass(self):
        bad_values = [
            None,
            "not-a-time",
            iso_offset(-(u.PYLAUNCH_FRESHNESS_SECONDS + 30)),
            iso_offset(u.CLOCK_SKEW_TOLERANCE_SECONDS + 30),
        ]
        for value in bad_values:
            proof = fresh_pass_proof()
            if value is None:
                proof.pop("lastUpdateUtc", None)
            else:
                proof["lastUpdateUtc"] = value
            with self.subTest(value=value):
                out = self.status(proof=proof)
                py = out["live"]["pylaunchAuthoritativeProof"]
                self.assertTrue(py["automatedPass"])
                self.assertFalse(py["currentAutomatedPass"])
                self.assertNotEqual(out["overallResult"], "PASS")

    def test_long_capture_never_auto_starts(self):
        out = self.status()
        self.assertFalse(out["longCaptureAutoStarted"])

    def test_safety_contract_remains_read_only(self):
        out = self.status()
        self.assertTrue(out["live"]["safety"]["pass"])
        self.assertTrue(out["live"]["safety"]["readOnly"])
        self.assertEqual(out["live"]["safety"]["ramWrites"], 0)
        self.assertFalse(out["live"]["safety"]["inputInjection"])
        self.assertFalse(out["live"]["safety"]["workerReplacement"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
