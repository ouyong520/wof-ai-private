from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def compact_proof_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "Browser": bool(snapshot.get("browser_connected")),
        "WOF page": bool(snapshot.get("wof_page_found")),
        "Worker": bool(snapshot.get("worker_found")),
        "WASM / heap": bool(snapshot.get("wasm_module_found") and snapshot.get("heap_found")),
        "World 921031": bool(snapshot.get("world_921031")),
        "READ ONLY / RAM writes: 0": bool(snapshot.get("read_only") is True and snapshot.get("ram_writes") == 0 and snapshot.get("input_injection") is False),
    }
    if snapshot.get("alpha_requested") is True:
        checks["Alpha V1 package runtime"] = bool(snapshot.get("alpha_running") is True)
    checks_zh = {
        "浏览器": checks["Browser"], "WOF 页面": checks["WOF page"], "Worker": checks["Worker"],
        "WASM / 内存": checks["WASM / heap"], "游戏版本 World 921031": checks["World 921031"],
        "只读模式 / 游戏内存写入 0": checks["READ ONLY / RAM writes: 0"],
    }
    if "Alpha V1 package runtime" in checks:
        checks_zh["Alpha V1 固定版本运行时"] = checks["Alpha V1 package runtime"]
    automated_pass = all(checks.values())
    waiting = "正在等待 WOF 页面 / Worker / WASM / World 921031 / Alpha V1 固定版本运行时。游戏本身没有受到影响。" if snapshot.get("alpha_requested") else "正在等待 WOF 页面 / Worker / WASM / World 921031 自动验证。游戏本身没有受到影响。"
    return {
        "schema": "wof-python-launcher-windows-proof-v2",
        "automatedResult": "PASS" if automated_pass else "WAITING",
        "ownerSummaryZh": "自动验证与 Alpha V1 运行时已通过，请进行本次 bounded 观察。" if automated_pass and snapshot.get("alpha_requested") else ("自动验证已通过，请确认游戏仍可正常操作。" if automated_pass else waiting),
        "ownerPlayabilityConfirmation": "REQUIRED" if automated_pass else "NOT_READY",
        "checks": {name: "OK" if ok else "--" for name, ok in checks.items()},
        "checksZh": {name: "通过" if ok else "等待" for name, ok in checks_zh.items()},
        "launcherState": snapshot.get("state"), "browser": snapshot.get("browser_name"), "browserEndpoint": snapshot.get("browser_endpoint"),
        "pageUrl": snapshot.get("page_url"), "workerUrl": snapshot.get("worker_url"), "wasmModuleKey": snapshot.get("wasm_module_key"), "heapBytes": snapshot.get("heap_bytes"),
        "worldSha256": snapshot.get("identity_sha256"), "identityReason": snapshot.get("identity_reason"), "discoveryPath": snapshot.get("discovery_path"),
        "targetTopology": snapshot.get("discovery_diagnostics"),
        "alphaRequested": snapshot.get("alpha_requested") is True, "alphaRunning": snapshot.get("alpha_running") is True,
        "alphaRuntimeEpoch": snapshot.get("alpha_runtime_epoch"), "alphaPackageVersion": snapshot.get("alpha_package_version"),
        "alphaStatus": snapshot.get("alpha_status"), "alphaError": snapshot.get("alpha_error"),
        # These survive a later browser/room shutdown so the final file remains useful
        # for field diagnosis instead of collapsing to an all-empty disconnect state.
        "lastAcceptedAuthority": snapshot.get("last_accepted_authority"),
        "lastAlphaFailure": snapshot.get("last_alpha_failure"),
        "lastCalibrationProgress": snapshot.get("last_calibration_progress"),
        "significantEvents": list(snapshot.get("significant_events") or [])[-96:],
        "readOnly": snapshot.get("read_only") is True, "ramWrites": snapshot.get("ram_writes"),
        "inputInjection": snapshot.get("input_injection"), "lastError": snapshot.get("last_error"), "lastUpdateUtc": snapshot.get("last_update_utc"),
    }


def write_proof_json(path: Path, snapshot: dict[str, Any]) -> None:
    target = path.expanduser().resolve(); target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(json.dumps(compact_proof_snapshot(snapshot), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, target)
