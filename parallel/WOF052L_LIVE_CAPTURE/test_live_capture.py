import types

import live_capture


def fake_recorder(methods, source_token=True):
    class CdpClient:
        def x(self):
            if source_token:
                marker = "Target.setAutoAttach attachedToTarget iframe"
                return marker

    class RecorderManager:
        pass

    return types.SimpleNamespace(
        READ_ONLY_METHODS=set(methods),
        WORLD_SHA256=live_capture.EXPECTED_WORLD_SHA256,
        CdpClient=CdpClient,
        RecorderManager=RecorderManager,
    )


def test_room_count():
    assert live_capture.choose_room_count("") == 10
    assert live_capture.choose_room_count("1") == 1
    assert live_capture.choose_room_count("5") == 5
    assert live_capture.choose_room_count("10") == 10
    try:
        live_capture.choose_room_count("7")
    except ValueError:
        pass
    else:
        raise AssertionError("7 must be rejected")


def test_status_parse():
    row = live_capture.parse_status_line(
        "Browser OK | Live rooms 2 | Completed 3 | T18 samples 10 | Candidate 4 | "
        "A4704 1 | A4712 3 | T23 8 | READ ONLY / RAM writes 0"
    )
    assert row == {
        "live": 2,
        "completed": 3,
        "t18": 10,
        "candidate": 4,
        "a4704": 1,
        "a4712": 3,
        "t23": 8,
    }


def test_v2_gate_current_old_style_is_blocked():
    ok, _ = live_capture.recorder_discovery_v2_ready(
        fake_recorder({"Target.getTargets", "Runtime.evaluate"})
    )
    assert not ok


def test_v2_gate_forbidden_is_blocked():
    ok, _ = live_capture.recorder_discovery_v2_ready(
        fake_recorder({"Target.setAutoAttach", "Input.dispatchKeyEvent"})
    )
    assert not ok


def test_v2_gate_accepts_safe_autoattach():
    ok, reason = live_capture.recorder_discovery_v2_ready(
        fake_recorder({"Target.getTargets", "Target.setAutoAttach", "Runtime.evaluate"})
    )
    assert ok, reason


if __name__ == "__main__":
    test_room_count()
    test_status_parse()
    test_v2_gate_current_old_style_is_blocked()
    test_v2_gate_forbidden_is_blocked()
    test_v2_gate_accepts_safe_autoattach()
    print("PASS")
