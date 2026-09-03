from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.render_authority_capture import RenderAuthorityCapture, SCHEMA

AUTHORITY_KEY = "alpha-streaming-authority"
RUNTIME_EPOCH = "0123456789abcdef"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False, "overlayEnabled": False}


class _Session:
    def __init__(self, target_id: str, remote: dict, result: dict, expressions: list[str]) -> None:
        self.target_id = target_id
        self.remote = remote
        self.result = result
        self.expressions = expressions

    def request(self, *_args, **_kwargs) -> None:
        return None

    def evaluate(self, expression: str, timeout: float | None = None):
        del timeout
        self.expressions.append(expression)
        if "WOFRENDERAUTHV2?.status" in expression:
            return self.remote
        if "WOFRENDERAUTHV2?.result" in expression:
            return self.result
        if "WOFALPHARELATIVEENEMY?.ingestActorSnapshot" in expression:
            return True
        raise AssertionError(f"unexpected expression: {expression}")

    def close(self) -> None:
        return None


class _Client:
    def __init__(self, remote: dict, result: dict) -> None:
        self.remote = remote
        self.result = result
        self.expressions: list[str] = []

    def attach(self, target_id: str) -> _Session:
        return _Session(target_id, self.remote, self.result, self.expressions)


def _streaming_remote() -> dict:
    return {
        "schema": SCHEMA,
        "authorityKey": AUTHORITY_KEY,
        "runtimeEpoch": RUNTIME_EPOCH,
        "state": "ANCHOR_STREAMING",
        "terminal": False,
        "captureComplete": True,
        "actors": {"players": [{"name": "P1"}], "enemies": [{"slot": 0}]},
        **SAFETY,
    }


def _streaming_result() -> dict:
    return {
        **_streaming_remote(),
        "resultVerdict": "BOUNDED_CAPTURE_READY_FOR_RENDER_AUTHORITY_ANALYSIS",
    }


def _bound_capture() -> RenderAuthorityCapture:
    capture = RenderAuthorityCapture(lambda _path: "")
    capture._authority_key = AUTHORITY_KEY
    capture._runtime_epoch = RUNTIME_EPOCH
    capture._worker_id = "worker"
    capture._page_id = "page"
    capture._state = "MEASURING"
    return capture


class RenderAuthorityStreamingCaptureTests(unittest.TestCase):
    def test_capture_result_is_preserved_while_actor_streaming_continues(self) -> None:
        remote = _streaming_remote()
        result = _streaming_result()
        client = _Client(remote, result)

        out = _bound_capture().poll(client, AUTHORITY_KEY, RUNTIME_EPOCH)

        self.assertEqual("ANCHOR_STREAMING", out["state"])
        self.assertTrue(out["captureComplete"])
        self.assertTrue(out["actorStreaming"])
        self.assertEqual("BOUNDED_CAPTURE_READY_FOR_RENDER_AUTHORITY_ANALYSIS", out["result"]["resultVerdict"])
        self.assertTrue(any("ingestActorSnapshot" in expression for expression in client.expressions))
        self.assertTrue(any("WOFRENDERAUTHV2?.result" in expression for expression in client.expressions))

    def test_incomplete_streaming_result_fails_closed(self) -> None:
        remote = _streaming_remote()
        result = _streaming_result()
        result["captureComplete"] = False

        out = _bound_capture().poll(_Client(remote, result), AUTHORITY_KEY, RUNTIME_EPOCH)

        self.assertEqual("ERROR", out["state"])
        self.assertIn("bounded capture result is not complete", str(out["error"]))

    def test_runner_consumes_ready_result_instead_of_waiting_for_terminal_state(self) -> None:
        runner = (PYLAUNCH.parent / "RENDER_AUTHORITY_V3" / "measurement_runner.py").read_text(encoding="utf-8")
        self.assertIn('capture_result=polled.get("result")', runner)
        self.assertIn("if terminal_capture is None and isinstance(capture_result,dict):", runner)
        self.assertNotIn('if polled.get("state")=="MEASUREMENT_COMPLETE" and terminal_capture is None:', runner)


if __name__ == "__main__":
    unittest.main()
