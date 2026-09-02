#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import repository_preflight as base

ROOT = base.ROOT
PLAYER_HEAD_REQUIREMENT = "parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md"
PLAYER_HEAD_CLAIM = "parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION_V1.json"
PLAYER_HEAD_PASS = "COMPLETE — ALPHA V1 PLAYER-HEAD DANGER WARNING PRODUCTION INTEGRATED — READY FOR FRESH QA / BOUNDED DYNAMIC LIVE PROOF"


def _load_claims(root: Path, pattern: str) -> list[tuple[Path, dict[str, Any]]]:
    claims: list[tuple[Path, dict[str, Any]]] = []
    claim_dir = root / "parallel/PM/STAGE_CLAIMS"
    if not claim_dir.exists():
        return claims
    for path in sorted(claim_dir.glob(pattern)):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(value, dict):
            claims.append((path, value))
    return claims


def _check_formal_current_successor(root: Path, blob_resolver: base.BlobResolver) -> tuple[bool, str]:
    observations: list[str] = []
    for path, claim in _load_claims(root, "ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION*.json"):
        state = claim.get("state")
        verdicts = base._candidate_verdicts(claim)
        if state != "COMPLETE" or base.FORMAL_PASS not in verdicts:
            observations.append(f"{path.name}: state={state} verdicts={verdicts!r}")
            continue
        pins = base._extract_blob_map(claim)
        pin_blockers = base._check_current_pins(
            f"Formal current-blob successor {path.name}",
            pins,
            base.FORMAL_FRESH_PATHS,
            blob_resolver,
        )
        if not pin_blockers:
            return True, f"Formal current-blob authoritative successor={path.name} COMPLETE/PASS 且 freshness-sensitive blobs current。"
        observations.append(f"{path.name}: {'；'.join(pin_blockers)}")
    detail = "；".join(observations[-4:]) if observations else "未找到 current-blob revalidation claim"
    return False, f"Formal current-blob 没有可消费的 current successor PASS: {detail}"


def _is_head_label_fresh_qa_pass(claim: dict[str, Any]) -> bool:
    if claim.get("state") != "COMPLETE":
        return False
    for verdict in base._candidate_verdicts(claim):
        upper = verdict.upper()
        if (
            upper.startswith("PASS")
            and "ENEMY TARGET HEAD LABEL" in upper
            and ("FRESH QA" in upper or "INDEPENDENT QA" in upper)
        ):
            return True
    return False


def _check_head_labels_current_successor(root: Path, blob_resolver: base.BlobResolver) -> tuple[bool, str]:
    impl, error = base._read_json(root, base.HEAD_LABEL_IMPL_CLAIM)
    if error or impl is None or impl.get("state") != "COMPLETE":
        return False, f"Head Labels mandatory implementation 未 COMPLETE/current: {error or impl.get('state')}"

    try:
        current_helper = blob_resolver(base.HEAD_LABEL_PRODUCT)
    except Exception as exc:
        return False, f"Head Labels 无法读取当前 helper blob: {exc}"

    observations: list[str] = []
    for path, claim in _load_claims(root, "ALPHA_ENEMY_TARGET_HEAD_LABELS_QA*.json"):
        if not _is_head_label_fresh_qa_pass(claim):
            observations.append(
                f"{path.name}: state={claim.get('state')} verdicts={base._candidate_verdicts(claim)!r}"
            )
            continue
        pins = base._extract_blob_map(claim)
        helper_pin = pins.get(base.HEAD_LABEL_PRODUCT)
        if helper_pin != current_helper:
            observations.append(
                f"{path.name}: helper pin stale/missing expected-current={current_helper} qa-pin={helper_pin}"
            )
            continue
        projection_path = "product/alpha/wof_alpha_enemy_head_projection.json"
        projection_pin = pins.get(projection_path)
        if projection_pin:
            try:
                projection_current = blob_resolver(projection_path)
            except Exception as exc:
                observations.append(f"{path.name}: projection currentness read failed: {exc}")
                continue
            if projection_pin != projection_current:
                observations.append(
                    f"{path.name}: projection pin stale current={projection_current} qa-pin={projection_pin}"
                )
                continue
        return True, (
            f"Head Labels authoritative fresh-QA successor={path.name} PASS on current helper "
            f"{current_helper}; bounded live 1P/2P/3P projection proof remains separate."
        )

    detail = "；".join(observations[-6:]) if observations else "未找到 Head Labels fresh-QA claim"
    return False, f"Head Labels 没有可消费的 current-product fresh QA PASS: {detail}"


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
    _, _, gates = base.release_gate(root, resolve, run_offline=False)

    replacements = {
        "formalCurrentBlob": _check_formal_current_successor(root, resolve),
        "enemyTargetHeadLabels": _check_head_labels_current_successor(root, resolve),
    }
    reconciled: list[dict[str, Any]] = []
    for gate in gates:
        replacement = replacements.get(gate["name"])
        if replacement is None:
            reconciled.append(gate)
        else:
            reconciled.append(base._gate(gate["name"], replacement[0], replacement[1]))
    gates = reconciled
    blockers = [gate["tail"] for gate in gates if not gate["pass"]]

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
