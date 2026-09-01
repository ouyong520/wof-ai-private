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
        "READ ONLY / RAM writes: 0": bool(
            snapshot.get("read_only") is True
            and snapshot.get("ram_writes") == 0
            and snapshot.get("input_injection") is False
        ),
    }
    automated_pass = all(checks.values())
    return {
        "schema": "wof-python-launcher-windows-proof-v1",
        "automatedResult": "PASS" if automated_pass else "WAITING",
        "ownerPlayabilityConfirmation": "REQUIRED" if automated_pass else "NOT_READY",
        "checks": {name: "OK" if ok else "--" for name, ok in checks.items()},
        "launcherState": snapshot.get("state"),
        "browser": snapshot.get("browser_name"),
        "browserEndpoint": snapshot.get("browser_endpoint"),
        "pageUrl": snapshot.get("page_url"),
        "workerUrl": snapshot.get("worker_url"),
        "wasmModuleKey": snapshot.get("wasm_module_key"),
        "heapBytes": snapshot.get("heap_bytes"),
        "worldSha256": snapshot.get("identity_sha256"),
        "identityReason": snapshot.get("identity_reason"),
        "readOnly": snapshot.get("read_only") is True,
        "ramWrites": snapshot.get("ram_writes"),
        "inputInjection": snapshot.get("input_injection"),
        "lastError": snapshot.get("last_error"),
        "lastUpdateUtc": snapshot.get("last_update_utc"),
    }


def write_proof_json(path: Path, snapshot: dict[str, Any]) -> None:
    target = path.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = compact_proof_snapshot(snapshot)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, target)
