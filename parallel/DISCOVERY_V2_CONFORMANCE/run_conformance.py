from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
RESULT_PATH = HERE / "RESULT.json"
SUMMARY_PATH = HERE / "SUMMARY_ZH_CN.md"

COMPONENTS = ("BROWSER_FLEET", "PYLAUNCH", "WOF052L_RECORDER", "PROSPECTIVE_VALIDATOR")
PASS = "PASS"
FAIL = "FAIL"
ROLE = "EXPECTED_ROLE_DIFFERENCE"

SOURCE_FILES = {
    "BROWSER_FLEET": [
        "parallel/BROWSER_FLEET/fleet_discovery_v2.py",
        "parallel/BROWSER_FLEET/fleet_manager.py",
        "parallel/BROWSER_FLEET/DISCOVERY_CONTRACT.md",
    ],
    "PYLAUNCH": [
        "parallel/PYLAUNCH/wof_launcher/discovery_v2.py",
        "parallel/PYLAUNCH/wof_launcher/browser.py",
        "parallel/PYLAUNCH/wof_launcher/probe.py",
        "parallel/PYLAUNCH/wof_launcher/cdp.py",
    ],
    "WOF052L_RECORDER": [
        "parallel/WOF052L_RECORDER/discovery_v2_sync.py",
        "parallel/WOF052L_RECORDER/hardening_v2.py",
        "parallel/WOF052L_RECORDER/owner_v2_zh_cn.py",
        "parallel/WOF052L_RECORDER/recorder.py",
    ],
    "PROSPECTIVE_VALIDATOR": [
        "parallel/PROSPECTIVE_VALIDATOR/discovery_v2.py",
        "parallel/PROSPECTIVE_VALIDATOR/discovery_v2_hardening.py",
        "parallel/PROSPECTIVE_VALIDATOR/live_validator_v2_hardened.py",
        "parallel/PROSPECTIVE_VALIDATOR/validator.py",
    ],
}


@dataclass(frozen=True)
class Probe:
    probe_id: str
    cwd: str
    test_file: str
    description: str


PROBES = {
    "fleet.discovery": Probe("fleet.discovery", "parallel/BROWSER_FLEET", "tests/test_fleet_discovery_v2.py", "Fleet synthetic Discovery V2 topology"),
    "fleet.manager": Probe("fleet.manager", "parallel/BROWSER_FLEET", "tests/test_fleet_manager_v2.py", "Fleet endpoint/isolation/advisory contract"),
    "py.discovery": Probe("py.discovery", "parallel/PYLAUNCH", "tests/test_discovery_v2.py", "PYLAUNCH exact identity Discovery V2"),
    "py.endpoint": Probe("py.endpoint", "parallel/PYLAUNCH", "tests/test_endpoint_hardening.py", "PYLAUNCH endpoint confinement"),
    "rec.base": Probe("rec.base", "parallel/WOF052L_RECORDER", "test_discovery_v2_sync.py", "Recorder synthetic topology base adapter"),
    "rec.hardening": Probe("rec.hardening", "parallel/WOF052L_RECORDER", "test_hardening_v2.py", "Recorder official V2 hardening integration"),
    "pro.discovery": Probe("pro.discovery", "parallel/PROSPECTIVE_VALIDATOR", "test_discovery_v2.py", "Prospective synthetic Discovery V2"),
    "pro.hardening": Probe("pro.hardening", "parallel/PROSPECTIVE_VALIDATOR", "test_discovery_v2_hardening.py", "Prospective relation/endpoint hardening"),
    "pro.entry": Probe("pro.entry", "parallel/PROSPECTIVE_VALIDATOR", "test_entrypoint_v2.py", "Prospective public entrypoint routes through V2"),
    "pro.validator": Probe("pro.validator", "parallel/PROSPECTIVE_VALIDATOR", "test_validator_hardening.py", "Prospective conservative research-only gates"),
}

# Every required topology appears explicitly. A cell is PASS when the component's
# fixture probes prove its own role contract. EXPECTED_ROLE_DIFFERENCE means the
# behavior intentionally differs by role, not that the probe is skipped.
SCENARIOS = [
    ("one-page-one-worker", "单页面 / 单 Worker", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery"]),
        "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.base", "rec.hardening"]),
        "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery", "pro.hardening"]),
    }),
    ("two-pages-two-workers", "双页面 / 双独立 Worker", {
        "BROWSER_FLEET": (ROLE, ["fleet.discovery", "fleet.manager"]),
        "PYLAUNCH": (ROLE, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]),
        "PROSPECTIVE_VALIDATOR": (PASS, ["pro.hardening"]),
    }),
    ("two-pages-same-shared-worker", "双页面 / 同一 shared Worker", {
        "BROWSER_FLEET": (ROLE, ["fleet.manager"]),
        "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]),
        "PROSPECTIVE_VALIDATOR": (PASS, ["pro.hardening"]),
    }),
    ("iframe-to-worker", "iframe -> Worker", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery"]),
        "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.base", "rec.hardening"]),
        "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("direct-worker-fallback", "direct Worker fallback", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery"]),
        "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.base", "rec.hardening"]),
        "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery", "pro.hardening"]),
    }),
    ("misleading-opener-id", "误导 openerId", {
        "BROWSER_FLEET": (ROLE, ["fleet.manager"]),
        "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]),
        "PROSPECTIVE_VALIDATOR": (PASS, ["pro.hardening"]),
    }),
    ("worker-url-gstyphoon", "Worker URL: gstyphoon", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.base", "rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("worker-url-hashed", "Worker URL: hashed", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("worker-url-blob", "Worker URL: blob", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("worker-url-data", "Worker URL: data", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("worker-url-no-extension", "Worker URL: no extension", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("remote-host", "remote host", {
        "BROWSER_FLEET": (PASS, ["fleet.manager"]), "PYLAUNCH": (PASS, ["py.endpoint"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.hardening"]),
    }),
    ("cross-port-websocket", "cross-port websocket", {
        "BROWSER_FLEET": (PASS, ["fleet.manager"]), "PYLAUNCH": (PASS, ["py.endpoint"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.hardening"]),
    }),
    ("loopback-alias", "loopback alias", {
        "BROWSER_FLEET": (PASS, ["fleet.manager"]), "PYLAUNCH": (PASS, ["py.endpoint"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.hardening"]),
    }),
    ("reload-recreated-worker", "reload / recreated Worker", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.base", "rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("stale-target-session", "stale target / session", {
        "BROWSER_FLEET": (PASS, ["fleet.discovery", "fleet.manager"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.base", "rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("exact-supported-identity", "exact supported identity", {
        "BROWSER_FLEET": (ROLE, ["fleet.manager"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("wrong-identity", "wrong identity", {
        "BROWSER_FLEET": (ROLE, ["fleet.manager"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery"]),
    }),
    ("one-room-failure-isolation", "单房间失败隔离", {
        "BROWSER_FLEET": (PASS, ["fleet.manager"]), "PYLAUNCH": (ROLE, ["py.endpoint"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery", "pro.hardening"]),
    }),
    ("advisory-vs-authoritative-role", "Fleet advisory vs authoritative roles", {
        "BROWSER_FLEET": (ROLE, ["fleet.manager"]), "PYLAUNCH": (PASS, ["py.discovery"]),
        "WOF052L_RECORDER": (PASS, ["rec.hardening"]), "PROSPECTIVE_VALIDATOR": (PASS, ["pro.discovery", "pro.entry"]),
    }),
]

SAFETY_PROBES = {
    "BROWSER_FLEET": ["fleet.manager"],
    "PYLAUNCH": ["py.discovery"],
    "WOF052L_RECORDER": ["rec.base", "rec.hardening"],
    "PROSPECTIVE_VALIDATOR": ["pro.discovery", "pro.entry", "pro.validator"],
}

# These source mutations are never needed for Discovery V2. Keep the regexes
# narrow so harmless text such as `blob:` URL fixtures does not trigger.
FORBIDDEN_MUTATION_PATTERNS = {
    "window-worker-assignment": re.compile(r"window\s*\.\s*Worker\s*="),
    "object-url-creation": re.compile(r"(?:URL|webkitURL)\s*\.\s*createObjectURL\s*\("),
    "blob-construction": re.compile(r"new\s+Blob\s*\("),
    "worker-construction": re.compile(r"new\s+(?:SharedWorker|Worker)\s*\("),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "UNKNOWN"


def _run_probe(probe: Probe, timeout: int) -> dict:
    cwd = REPO_ROOT / probe.cwd
    test_path = cwd / probe.test_file
    if not test_path.exists():
        return {"probeId": probe.probe_id, "status": FAIL, "reason": f"missing test: {probe.cwd}/{probe.test_file}"}
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        cp = subprocess.run(
            [sys.executable, probe.test_file],
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        tail = "\n".join(cp.stdout.splitlines()[-20:])
        return {
            "probeId": probe.probe_id,
            "status": PASS if cp.returncode == 0 else FAIL,
            "returnCode": cp.returncode,
            "outputTail": tail,
        }
    except subprocess.TimeoutExpired as exc:
        return {"probeId": probe.probe_id, "status": FAIL, "reason": f"timeout after {timeout}s", "outputTail": str(exc)}


def _scan_mutations(component: str) -> dict:
    findings = []
    for rel in SOURCE_FILES[component]:
        path = REPO_ROOT / rel
        if not path.exists() or path.suffix not in {".py", ".js", ".mjs", ".cjs"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for rule, pattern in FORBIDDEN_MUTATION_PATTERNS.items():
            if pattern.search(text):
                findings.append({"rule": rule, "path": rel})
    return {"status": PASS if not findings else FAIL, "findings": findings}


def _fingerprints() -> dict:
    result = {}
    for component, rels in SOURCE_FILES.items():
        rows = []
        for rel in rels:
            path = REPO_ROOT / rel
            rows.append({"path": rel, "exists": path.exists(), "sha256": _sha256(path) if path.exists() else None})
        result[component] = rows
    return result


def _probe_ok(probe_results: dict, ids: Iterable[str]) -> bool:
    ids = list(ids)
    return bool(ids) and all(probe_results.get(pid, {}).get("status") == PASS for pid in ids)


def _matrix(probe_results: dict) -> list[dict]:
    rows = []
    for scenario_id, zh, policy in SCENARIOS:
        cells = {}
        for component in COMPONENTS:
            expected, probe_ids = policy[component]
            if _probe_ok(probe_results, probe_ids):
                observed = expected
                reason = "fixture/mock probe passed"
            else:
                observed = FAIL
                reason = "one or more required probes failed"
            cells[component] = {"status": observed, "expectedRole": expected, "probes": probe_ids, "reason": reason}
        rows.append({"scenario": scenario_id, "zh": zh, "components": cells})
    return rows


def _safety(probe_results: dict) -> dict:
    result = {}
    for component, probe_ids in SAFETY_PROBES.items():
        mutation = _scan_mutations(component)
        tests_ok = _probe_ok(probe_results, probe_ids)
        status = PASS if tests_ok and mutation["status"] == PASS else FAIL
        result[component] = {
            "status": status,
            "probes": probe_ids,
            "readOnly": status == PASS,
            "ramWrites": 0 if status == PASS else None,
            "inputInjection": False if status == PASS else None,
            "workerReplacementOrWrap": False if status == PASS else None,
            "blobDataObjectUrlCreationOrRewrite": False if mutation["status"] == PASS else None,
            "productionAutoPromotion": False if status == PASS else None,
            "mutationScan": mutation,
        }
    return result


def _summary(payload: dict) -> str:
    counts = {PASS: 0, FAIL: 0, ROLE: 0}
    fail_rows = []
    for row in payload["matrix"]:
        for component, cell in row["components"].items():
            counts[cell["status"]] += 1
            if cell["status"] == FAIL:
                fail_rows.append((row["zh"], component, cell["probes"]))
    safety_fail = [name for name, row in payload["safety"].items() if row["status"] != PASS]
    verdict = "DISCOVERY V2 CONFORMANCE HARNESS READY" if not fail_rows and not safety_fail else "DISCOVERY V2 CONFORMANCE DRIFT DETECTED"
    lines = [
        "# Discovery V2 Cross-Component Conformance — 中文摘要",
        "",
        f"- HEAD: `{payload['head']}`",
        f"- 结论: **{verdict}**",
        f"- Matrix: PASS={counts[PASS]} / EXPECTED_ROLE_DIFFERENCE={counts[ROLE]} / FAIL={counts[FAIL]}",
        "- 运行方式: synthetic fixture/mock；不需要 Owner 真人 Browser。",
        "",
        "## 角色解释",
        "",
        "- Browser Fleet 只提供 cheap indicator，不做 exact World 921031 SHA-256 authority。",
        "- PYLAUNCH 是单选择 authoritative proof；多 exact pair 会 fail closed。",
        "- Recorder / Prospective 可以按独立 room/page 形成多候选，但 shared Worker 跨 page 必须全局 fail closed。",
        "- `EXPECTED_ROLE_DIFFERENCE` 是设计差异，不等于失败。",
        "",
        "## 安全不变量",
        "",
    ]
    for component, row in payload["safety"].items():
        lines.append(f"- {component}: **{row['status']}** — readOnly / ramWrites=0 / no input injection / no Worker replacement / no Blob-ObjectURL rewrite / no auto-promotion")
    if fail_rows or safety_fail:
        lines.extend(["", "## 当前 drift / FAIL", ""])
        for zh, component, probes in fail_rows:
            lines.append(f"- {component} / {zh}: FAIL — probes={', '.join(probes)}")
        for component in safety_fail:
            lines.append(f"- {component} / safety: FAIL")
    else:
        lines.extend(["", "## 当前 drift", "", "- Harness 未发现阻断性 conformance drift；角色差异均被显式标为 EXPECTED_ROLE_DIFFERENCE。"])
    lines.extend(["", "## Stop condition", "", f"**{verdict}**", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="WOF Discovery V2 cross-component synthetic conformance harness")
    parser.add_argument("--timeout", type=int, default=90, help="per probe timeout seconds")
    parser.add_argument("--no-write", action="store_true", help="print result but do not replace RESULT.json/SUMMARY_ZH_CN.md")
    args = parser.parse_args()

    probe_results = {probe_id: _run_probe(probe, args.timeout) for probe_id, probe in PROBES.items()}
    payload = {
        "schema": "wof-discovery-v2-conformance-v1",
        "generatedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "head": _git_head(),
        "executionMode": "synthetic-fixture-mock",
        "ownerBrowserRequired": False,
        "components": list(COMPONENTS),
        "sourceFingerprints": _fingerprints(),
        "probes": probe_results,
    }
    payload["matrix"] = _matrix(probe_results)
    payload["safety"] = _safety(probe_results)
    payload["failCount"] = sum(
        1 for row in payload["matrix"] for cell in row["components"].values() if cell["status"] == FAIL
    ) + sum(1 for row in payload["safety"].values() if row["status"] == FAIL)
    payload["ready"] = payload["failCount"] == 0
    payload["verdict"] = "DISCOVERY V2 CONFORMANCE HARNESS READY" if payload["ready"] else "DISCOVERY V2 CONFORMANCE DRIFT DETECTED"

    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    summary = _summary(payload)
    if not args.no_write:
        RESULT_PATH.write_text(text, encoding="utf-8")
        SUMMARY_PATH.write_text(summary, encoding="utf-8")
    print(text)
    print(summary)
    return 0 if payload["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
