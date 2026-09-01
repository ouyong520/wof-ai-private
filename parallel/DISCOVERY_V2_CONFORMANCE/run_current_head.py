from __future__ import annotations

"""Current-HEAD wrapper for the Discovery V2 conformance harness.

The base runner executes component fixture tests. This wrapper additionally pins the
current WOF-052L public owner entrypoint, which is intentionally checked in the
harness lane rather than by modifying Recorder tests.
"""

from pathlib import Path

import run_conformance as h


REC_ENTRY_PROBE = "rec.entry"

h.SOURCE_FILES["WOF052L_RECORDER"] = [
    "parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd",
    "parallel/WOF052L_RECORDER/owner_zh_cn.py",
    "parallel/WOF052L_RECORDER/owner_v2_zh_cn.py",
    "parallel/WOF052L_RECORDER/discovery_v2_sync.py",
    "parallel/WOF052L_RECORDER/hardening_v2.py",
    "parallel/WOF052L_RECORDER/recorder.py",
]

h.PROBES[REC_ENTRY_PROBE] = h.Probe(
    REC_ENTRY_PROBE,
    "parallel/WOF052L_RECORDER",
    "@builtin-public-entrypoint",
    "Recorder public CMD/frontend installs Discovery V2 hardening",
)

for _scenario_id, _zh, policy in h.SCENARIOS:
    expected, probes = policy["WOF052L_RECORDER"]
    if REC_ENTRY_PROBE not in probes:
        policy["WOF052L_RECORDER"] = (expected, [*probes, REC_ENTRY_PROBE])

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


h._run_probe = _run_probe


if __name__ == "__main__":
    raise SystemExit(h.main())
