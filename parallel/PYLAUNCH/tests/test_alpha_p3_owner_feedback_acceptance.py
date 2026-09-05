from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.owner_feedback_acceptance import (
    EXPECTED_ORIGIN,
    FIXED_MODE,
    FIXED_STATUS_NAME,
    MAX_FIXED_STATUS_AGE_SECONDS,
    MAX_UPDATE_FETCH_AGE_SECONDS,
    OUTPUT_NAME,
    ROUTING_STATES,
    classify,
    load_launcher_snapshot,
    render_feedback,
    write_feedback,
)


def launcher(**changes):
    data = {
        "currentReleaseSha": "1234567890abcdef1234567890abcdef12345678",
        "liveMode": FIXED_MODE,
        "managedRepoReady": True,
        "updateChannelReady": True,
    }
    data.update(changes)
    return data


def fixed(state="READY_FOR_OWNER_FIXED_TEST", **changes):
    data = {
        "state": state,
        "hudInjected": True,
        "gameCanvasContextPresent": True,
        "drawHooked": True,
        "callbackCount": 0,
        "drawCount": 0,
        "drawingBuffer": {"width": 768, "height": 448},
        "nativeWidth": 384,
        "nativeHeight": 224,
        "nativeX": 192,
        "nativeY": 112,
        "label": "TEST",
        "lastError": None,
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
    }
    data.update(changes)
    return data


_DEFAULT = object()


class AlphaP3OwnerFeedbackAcceptanceTests(unittest.TestCase):
    def route(self, l=_DEFAULT, f=_DEFAULT, age=0.0, error=None):
        state, reason, evidence = classify(
            launcher() if l is _DEFAULT else l,
            fixed() if f is _DEFAULT else f,
            fixed_age_seconds=age,
            fixed_source_error=error,
        )
        self.assertIn(state, ROUTING_STATES)
        self.assertTrue(reason)
        return state, evidence

    def test_each_failure_routes_to_one_unique_state(self):
        cases = [
            ("BOOTSTRAP_NOT_READY", launcher(managedRepoReady=False), fixed()),
            ("UPDATE_CHANNEL_NOT_READY", launcher(updateChannelReady=False), fixed()),
            ("LIVE_MODE_NOT_FIXED_DRAW", launcher(liveMode="normal"), fixed()),
            ("RUNTIME_NOT_STARTED", launcher(), fixed(runtimeReady=False)),
            ("HUD_INJECTION_MISSING", launcher(), fixed("HUD_INJECTION_MISSING", hudInjected=False)),
            ("GAME_CANVAS_CONTEXT_MISSING", launcher(), fixed("GAME_CANVAS_CONTEXT_MISSING", gameCanvasContextPresent=False)),
            ("DRAW_HOOK_NOT_FIRING", launcher(), fixed("DRAW_HOOK_NOT_FIRING", drawHooked=False)),
            ("DRAWING_BUFFER_INVALID", launcher(), fixed("DRAWING_BUFFER_INVALID", drawingBuffer=None)),
            ("DRAW_FAILED", launcher(), fixed("DRAW_FAILED", lastError="native draw exception")),
            ("READY_FOR_OWNER_FIXED_TEST", launcher(), fixed()),
        ]
        observed = []
        for expected, l, f in cases:
            state, _ = self.route(l, f)
            self.assertEqual(expected, state)
            observed.append(state)
        self.assertEqual(len(observed), len(set(observed)))
        sparse, _, _ = classify(launcher(), {"state": "HUD_INJECTION_MISSING"})
        self.assertEqual("HUD_INJECTION_MISSING", sparse)

    def test_stale_missing_and_malformed_inputs_never_false_green(self):
        self.assertEqual("BOOTSTRAP_NOT_READY", self.route({}, fixed())[0])
        self.assertEqual("RUNTIME_NOT_STARTED", self.route(launcher(), None)[0])
        self.assertEqual(
            "RUNTIME_NOT_STARTED",
            self.route(launcher(), fixed(), age=MAX_FIXED_STATUS_AGE_SECONDS + 0.01)[0],
        )
        self.assertEqual("RUNTIME_NOT_STARTED", self.route(launcher(), fixed(), error="missing")[0])
        self.assertEqual("FEEDBACK_INPUT_MALFORMED", self.route(launcher(), fixed(drawCount="abc"))[0])
        self.assertEqual("FEEDBACK_INPUT_MALFORMED", self.route(launcher(), fixed("ALIEN_GREEN_STATE"))[0])

    def test_p2_running_text_needs_fresh_read_only_git_update_proof(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            git = repo / ".git"
            results = root / "results"
            git.mkdir(parents=True)
            results.mkdir()
            sha = "1234567890abcdef1234567890abcdef12345678"
            (git / "HEAD").write_text(sha + "\n", encoding="utf-8")
            (git / "config").write_text(f'[remote "origin"]\n    url = {EXPECTED_ORIGIN}\n', encoding="utf-8")
            fetch = git / "FETCH_HEAD"
            fetch.write_text(f"{sha}\t\tbranch 'alpha-live' of github\n", encoding="utf-8")
            (results / OUTPUT_NAME).write_text(
                "status=RUNNING\n" f"alphaLiveCommit={sha}\n" "liveMode=fixed-draw-first-gate\n",
                encoding="utf-8",
            )
            snap = load_launcher_snapshot(results, repo_root=repo)
            self.assertTrue(snap.data["managedRepoReady"])
            self.assertTrue(snap.data["updateChannelReady"])
            stale = datetime.now(timezone.utc).timestamp() - MAX_UPDATE_FETCH_AGE_SECONDS - 1
            os.utime(fetch, (stale, stale))
            snap = load_launcher_snapshot(results, repo_root=repo)
            self.assertTrue(snap.data["managedRepoReady"])
            self.assertFalse(snap.data["updateChannelReady"])
            self.assertEqual("UPDATE_CHANNEL_NOT_READY", classify(snap.data, fixed())[0])

    def test_machine_draw_proof_cannot_become_owner_visual_pass(self):
        drawn = fixed("FIXED_TEST_ACTUALLY_DRAWN", callbackCount=9, drawCount=3)
        state, evidence = self.route(launcher(ownerVisualPass=True), drawn)
        self.assertEqual("MACHINE_DRAW_PROOF_PRESENT_AWAITING_OWNER_VISUAL", state)
        self.assertTrue(evidence["machineDrawProof"])
        text = render_feedback(
            state,
            "machine only",
            evidence,
            fixed_status_path=Path(FIXED_STATUS_NAME),
            fixed_age_seconds=0.5,
            generated_at=datetime(2026, 9, 5, tzinfo=timezone.utc),
        )
        self.assertIn("machineDrawProof=PRESENT", text)
        self.assertIn("ownerVisualConfirmation=NOT_RECORDED", text)
        self.assertNotIn("OWNER VISUAL PASS", text)
        self.assertNotIn("ownerVisualPass=true", text)

    def test_inconsistent_drawn_state_routes_back_to_exact_machine_layer(self):
        base = {"callbackCount": 1, "drawCount": 1}
        self.assertEqual("HUD_INJECTION_MISSING", self.route(launcher(), fixed("FIXED_TEST_ACTUALLY_DRAWN", hudInjected=False, **base))[0])
        self.assertEqual("GAME_CANVAS_CONTEXT_MISSING", self.route(launcher(), fixed("FIXED_TEST_ACTUALLY_DRAWN", gameCanvasContextPresent=False, **base))[0])
        self.assertEqual("DRAW_HOOK_NOT_FIRING", self.route(launcher(), fixed("FIXED_TEST_ACTUALLY_DRAWN", drawHooked=False, **base))[0])
        self.assertEqual("DRAWING_BUFFER_INVALID", self.route(launcher(), fixed("FIXED_TEST_ACTUALLY_DRAWN", drawingBuffer={"width": 0, "height": 448}, **base))[0])
        self.assertEqual("DRAW_FAILED", self.route(launcher(), fixed("FIXED_TEST_ACTUALLY_DRAWN", nativeX=191, **base))[0])

    def test_one_feedback_artifact_is_sufficient_for_pm_routing(self):
        state, evidence = self.route(launcher(), fixed("FIXED_TEST_ACTUALLY_DRAWN", callbackCount=5, drawCount=2))
        text = render_feedback(
            state,
            "machine only",
            evidence,
            fixed_status_path=Path(r"C:\Users\owner\Documents\WOF_RESULTS\ALPHA_FIXED_DRAW_STATUS.json"),
            fixed_age_seconds=1.25,
            generated_at=datetime(2026, 9, 5, tzinfo=timezone.utc),
        )
        for marker in (
            "currentReleaseSha=", "alphaLive=alpha-live", "liveMode=fixed-draw-first-gate",
            "managedRepoReady=true", "updateChannelReady=true", "runtimeReady=true",
            "fixedSmokeStatusPath=", "fixedSmokeState=FIXED_TEST_ACTUALLY_DRAWN",
            "drawHooked=true", "callbackCount=5", "drawCount=2", "drawingBuffer=768x448",
            "native=384x224", "center=192,112", "label=TEST", "lastError=NONE",
            "routingClassification=MACHINE_DRAW_PROOF_PRESENT_AWAITING_OWNER_VISUAL",
        ):
            self.assertIn(marker, text)

    def test_default_helper_writes_the_single_obvious_feedback_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            git = repo / ".git"
            results = root / "results"
            git.mkdir(parents=True)
            results.mkdir()
            sha = "1234567890abcdef1234567890abcdef12345678"
            (git / "HEAD").write_text(sha + "\n", encoding="utf-8")
            (git / "config").write_text(f'[remote "origin"]\n    url = {EXPECTED_ORIGIN}\n', encoding="utf-8")
            (git / "FETCH_HEAD").write_text(f"{sha}\t\tbranch 'alpha-live' of github\n", encoding="utf-8")
            (results / OUTPUT_NAME).write_text(
                "status=RUNNING\n" f"alphaLiveCommit={sha}\n" "liveMode=fixed-draw-first-gate\n",
                encoding="utf-8",
            )
            (results / FIXED_STATUS_NAME).write_text(
                json.dumps(fixed("FIXED_TEST_ACTUALLY_DRAWN", callbackCount=1, drawCount=1)),
                encoding="utf-8",
            )
            path, state = write_feedback(results, repo_root=repo)
            self.assertEqual(results / OUTPUT_NAME, path)
            self.assertEqual("MACHINE_DRAW_PROOF_PRESENT_AWAITING_OWNER_VISUAL", state)
            text = path.read_text(encoding="utf-8")
            self.assertIn("routingClassification=MACHINE_DRAW_PROOF_PRESENT_AWAITING_OWNER_VISUAL", text)
            self.assertIn("ownerVisualConfirmation=NOT_RECORDED", text)

    def test_coherent_p1_p2_candidate_is_directly_accepted(self):
        state, evidence = self.route(launcher(), fixed())
        self.assertEqual("READY_FOR_OWNER_FIXED_TEST", state)
        self.assertFalse(evidence["machineDrawProof"])


if __name__ == "__main__":
    unittest.main()
