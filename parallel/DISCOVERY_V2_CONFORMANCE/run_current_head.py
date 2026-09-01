from __future__ import annotations

"""Current-HEAD wrapper for the Discovery V2 conformance harness.

The base runner executes component fixture tests. This wrapper additionally pins
current public-entry/independent-QA evidence that can land after the base matrix.
A conformance FAIL is preserved as FAIL; harness readiness is tracked separately.
"""

import json
from pathlib import Path

import run_conformance as h


REC_ENTRY_PROBE = "rec.entry"
PY_PARENT_FRAME_PROBE = "py.parentframe.qa"
HARNESS_STOP = "DISCOVERY V2 CONFORMANCE HARNESS READY"

h.SOURCE_FILES["WOF052L_RECORDER"] = [
    "parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd",
    "parallel/WOF052L_RECORDER/owner_zh_cn.py",
    "parallel/WOF052L_RECORDER/owner_v2_zh_cn.py",
    "parallel/WOF052L_RECORDER/discovery_v2_sync.py",
    "parallel/WOF052L_RECORDER/hardening_v2.py",
    "parallel/WOF052L_RECORDER/recorder.py",
]
h.SOURCE_FILES["PYLAUNCH"].append(
    "parallel/PYLAUNCH_QA_DISCOVERY_V2_HARDENING/test_adversarial_parent_frame.py"
)

h.PROBES[REC_ENTRY_PROBE] = h.Probe(
    REC_ENTRY_PROBE,
    "parallel/WOF052L_RECORDER",
    "@builtin-public-entrypoint",
    "Recorder public CMD/frontend installs Discovery V2 hardening",
)
h.PROBES[PY_PARENT_FRAME_PROBE] = h.Probe(
    PY_PARENT_FRAME_PROBE,
    "parallel/PYLAUNCH_QA_DISCOVERY_V2_HARDENING",
    "test_adversarial_parent_frame.py",
    "Independent adversarial direct parentFrameId authority fixture",
)

# A broken Recorder public entrypoint invalidates Recorder conformance even if its
# internal helpers still pass.
for _scenario_id, _zh, policy in h.SCENARIOS:
    expected, probes = policy["WOF052L_RECORDER"]
    if REC_ENTRY_PROBE not in probes:
        policy["WOF052L_RECORDER"] = (expected, [*probes, REC_ENTRY_PROBE])

# Current independent QA found a direct-fallback edge that the original PYLAUNCH
# suite did not exercise: two positive WOF pages plus a uniquely mappable
# Worker.parentFrameId. Attach that fixture to the direct-fallback matrix cell so
# current drift cannot be hidden by older green tests.
for scenario_id, _zh, policy in h.SCENARIOS:
    if scenario_id == "direct-worker-fallback":
        expected, probes = policy["PYLAUNCH"]
        if PY_PARENT_FRAME_PROBE not in probes:
            policy["PYLAUNCH"] = (expected, [*probes, PY_PARENT_FRAME_PROBE])

if REC_ENTRY_PROBE not in h.SAFETY_PROBES["WOF052L_RECORDER"]:
    h.SAFETY_PROBES["WOF052L_RECORDER"].append(REC_ENTRY_PROBE)

_ORIGINAL_RUN_PROBE = h._run_probe


def _recorder_public_entry_probe() -> dict:
    root: Path = h.REPO_ROOT
    cmd_path = root / "parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd"
    owner_path = root / "parallel/WOF052L_RECORDER/owner_zh_cn.py"
    missing = [str(path.relative_to(root)) for path in (cmd_path, owner_path) if not path.exists()]
    if missing:
        return {
            "probeId": REC_ENTRY_PROBE,
            "status": h.FAIL,
            "reason": "missing public entrypoint: " + ", ".join(missing),
        }

    cmd = cmd_path.read_text(encoding="utf-8", errors="replace")
    owner = owner_path.read_text(encoding="utf-8", errors="replace")
    checks = {
        "cmdRoutesChineseOwner": "owner_zh_cn.py" in cmd,
        "ownerImportsDiscoveryV2": "import discovery_v2_sync" in owner,
        "ownerImportsHardeningV2": "import hardening_v2" in owner,
        "ownerInstallsDiscoveryV2": "discovery_v2_sync.install(recorder)" in owner,
        "ownerInstallsHardeningV2": "hardening_v2.install(recorder, discovery_v2_sync)" in owner,
    }
    ok = all(checks.values())
    return {
        "probeId": REC_ENTRY_PROBE,
        "status": h.PASS if ok else h.FAIL,
        "checks": checks,
        "reason": None if ok else "Recorder public owner entrypoint does not install hardened Discovery V2",
    }


def _run_probe(probe: h.Probe, timeout: int) -> dict:
    if probe.probe_id == REC_ENTRY_PROBE:
        return _recorder_public_entry_probe()
    return _ORIGINAL_RUN_PROBE(probe, timeout)


def _mark_harness_ready() -> None:
    """Separate harness completion from whether current components conform."""
    if not h.RESULT_PATH.exists():
        return
    payload = json.loads(h.RESULT_PATH.read_text(encoding="utf-8"))
    payload["conformanceReady"] = bool(payload.get("ready"))
    payload["conformanceVerdict"] = payload.get("verdict")
    payload["harnessReady"] = True
    payload["stopCondition"] = HARNESS_STOP
    payload["verdict"] = HARNESS_STOP
    h.RESULT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if h.SUMMARY_PATH.exists():
        summary = h.SUMMARY_PATH.read_text(encoding="utf-8").rstrip()
    else:
        summary = "# Discovery V2 Cross-Component Conformance — 中文摘要"
    summary += (
        "\n\n## Harness stage\n\n"
        f"- Harness ready: **YES**\n"
        f"- Current conformance ready: **{'YES' if payload['conformanceReady'] else 'NO'}**\n"
        "- 注意：Harness ready 不会把 matrix FAIL 改写成 PASS。\n\n"
        "## Stop condition\n\n"
        f"**{HARNESS_STOP}**\n"
    )
    h.SUMMARY_PATH.write_text(summary, encoding="utf-8")


h._run_probe = _run_probe


if __name__ == "__main__":
    rc = h.main()
    _mark_harness_ready()
    raise SystemExit(rc)
