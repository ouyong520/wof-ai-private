#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import repository_preflight as base

ROOT = base.ROOT
PLAYER_HEAD_REQUIREMENT = "parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md"
PLAYER_HEAD_CLAIM = "parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION_V1.json"
PLAYER_HEAD_PASS = "COMPLETE — ALPHA V1 PLAYER-HEAD DANGER WARNING PRODUCTION INTEGRATED — READY FOR FRESH QA / BOUNDED DYNAMIC LIVE PROOF"


def _player_head_product_pins(claim: dict[str, Any]) -> dict[str, str]:
    pins = {
        path: sha
        for path, sha in base._extract_blob_map(claim).items()
        if path.startswith("product/alpha/")
    }
    changed = claim.get("changedBlobs")
    if isinstance(changed, dict):
        for path, sha in changed.items():
            if isinstance(path, str) and isinstance(sha, str) and path.startswith("product/alpha/"):
                pins[path] = sha
    return pins


def _check_player_head_warning(root: Path, blob_resolver: base.BlobResolver) -> tuple[bool, str]:
    if not (root / PLAYER_HEAD_REQUIREMENT).exists():
        return True, "Player-head warning requirement 在该 snapshot 尚未成为 Alpha V1 mandatory policy；不反向施加未来 gate。"

    claim, blockers = base._claim_complete(
        root,
        PLAYER_HEAD_CLAIM,
        "Player-head danger warning production integration",
        PLAYER_HEAD_PASS,
    )
    if claim:
        pins = _player_head_product_pins(claim)
        if not pins:
            blockers.append("Player-head danger warning integration COMPLETE/PASS 但缺少 machine-readable product blob pins")
        else:
            blockers.extend(base._check_current_pins(
                "Player-head danger warning production integration",
                pins,
                sorted(pins),
                blob_resolver,
            ))
    if blockers:
        return False, "；".join(blockers)
    return True, "Player-head danger warning production integration COMPLETE/current；bounded dynamic live non-drift proof 仍由真实 Acceptance 承担。"


def release_gate(
    root: Path = ROOT,
    blob_resolver: base.BlobResolver | None = None,
    run_offline: bool = True,
) -> tuple[bool, list[str], list[dict[str, Any]]]:
    root = Path(root)
    resolve = blob_resolver or base._default_blob_resolver(root)
    _, blockers, gates = base.release_gate(root, resolve, run_offline=False)

    player_ok, player_detail = _check_player_head_warning(root, resolve)
    gates.append(base._gate("playerHeadDangerWarning", player_ok, player_detail))
    if not player_ok:
        blockers.append(player_detail)

    if not blockers and run_offline:
        offline = (
            (["node", "parallel/ALPHA_TRANSPORT_IMPL/run_all.mjs"], "transportFrozenCatalog"),
            (["node", "parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs"], "formalIntegration"),
            ([sys.executable, "-m", "unittest", "discover", "-s", "parallel/PYLAUNCH/tests", "-p", "test*.py"], "pylaunch"),
        )
        for cmd, name in offline:
            gate = base._command_gate(root, cmd, name)
            gates.append(gate)
            if not gate["pass"]:
                blockers.append(f"离线 gate 失败: {name}")

    return not blockers, blockers, gates


def preflight_only_success_message() -> str:
    return (
        base.preflight_only_success_message()
        + " Player-head danger warning 仍需真实快速移动/跳跃/卷屏 non-drift live proof。"
    )
