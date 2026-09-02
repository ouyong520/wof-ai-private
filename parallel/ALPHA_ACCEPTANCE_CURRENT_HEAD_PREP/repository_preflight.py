#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

ROOT = Path(__file__).resolve().parents[2]

FORMAL_CLAIM = "parallel/PM/STAGE_CLAIMS/ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION_V1.json"
HISTORICAL_FORMAL_BLOCKED = "parallel/PM/STAGE_CLAIMS/ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1.json"
PYLAUNCH_CLAIM = "parallel/PM/STAGE_CLAIMS/PYLAUNCH_STARTUP_ATTESTATION_QA_V1.json"
PYLAUNCH_RESULT = "parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.json"
RECORDER_CLAIM = "parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_QA_V1.json"
RECORDER_RESULT = "parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/RESULT.json"
UNIFIED_PREFLIGHT_CLAIM = "parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_CURRENT_HEAD_PREFLIGHT_QA_V2.json"
HEAD_LABEL_IMPL_CLAIM = "parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_V1.json"
HEAD_LABEL_STRICT_FIX_CLAIM = "parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TARGET_TYPE_FIX_V1.json"
HEAD_LABEL_QA_CLAIM = "parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2.json"
ONECLICK_CLAIM = "parallel/PM/STAGE_CLAIMS/OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V3.json"
ONECLICK_MANIFEST = "parallel/OWNER_ONECLICK/package_manifest.json"
ENDURANCE_CLAIM = "parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_RECOVERY_V2.json"

FORMAL_PASS = "PASS"
PYLAUNCH_PASS = "PASS — PYLAUNCH STARTUP ATTESTATION FRESH QA — RELEASE GATE CLOSED"
RECORDER_PASS = "PASS — RECORDER IN-FLIGHT GENERATION ATOMICITY FRESH QA — READY FOR CURRENT-HEAD UNIFIED PREFLIGHT"
UNIFIED_PREFLIGHT_PASS = "PASS — UNIFIED LIVE PROOF CURRENT-HEAD PREFLIGHT FRESH QA V2 — REPOSITORY PREFLIGHT GREEN"
HEAD_LABEL_STRICT_FIX_COMPLETE = "COMPLETE — ALPHA ENEMY TARGET HEAD LABEL STRICT TYPE FIX — READY FOR FRESH INDEPENDENT QA"
HEAD_LABEL_QA_PASS = "PASS — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V2 — STRICT TYPE FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED"
ONECLICK_PASS = "PASS — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V3 — PACKAGE GATE CLOSED"
ENDURANCE_PASS = "ALPHA TRANSPORT TRUE 5H ENDURANCE V2 PASS — READY AS CURRENT-SNAPSHOT ROBUSTNESS EVIDENCE"

FORMAL_FRESH_PATHS = (
    "product/alpha/wof_alpha_real_worker.js",
    "product/alpha/wof_alpha_hud.js",
    "product/alpha/wof_alpha_bootstrap.user.js",
    "product/alpha/wof_alpha_loader.js",
    "product/alpha/wof_alpha_core.js",
    "parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py",
)
PYLAUNCH_FRESH_PATHS = (
    "parallel/PYLAUNCH/wof_launcher/browser.py",
    "parallel/PYLAUNCH/wof_launcher/monitor.py",
    "parallel/PYLAUNCH/wof_launcher/discovery_v2.py",
)
UNIFIED_PREFLIGHT_FRESH_PATHS = (
    "parallel/LIVE_PROOF_BUNDLE/unified_preflight.py",
    "parallel/LIVE_PROOF_BUNDLE/unified_preflight_entrypoint.py",
)
HEAD_LABEL_PRODUCT = "product/alpha/wof_alpha_enemy_target_labels.js"

BlobResolver = Callable[[str], str]


def _read_json(root: Path, rel: str) -> tuple[dict[str, Any] | None, str | None]:
    path = root / rel
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"缺少 {rel}"
    except Exception as exc:
        return None, f"无法读取/解析 {rel}: {exc}"
    if not isinstance(value, dict):
        return None, f"{rel} 顶层不是 JSON object"
    return value, None


def _default_blob_resolver(root: Path) -> BlobResolver:
    def resolve(rel: str) -> str:
        return subprocess.check_output(
            ["git", "rev-parse", f"HEAD:{rel}"],
            cwd=root,
            text=True,
            encoding="utf-8",
            stderr=subprocess.STDOUT,
        ).strip()
    return resolve


def _normalize_pin_path(path: str) -> str:
    p = path.replace("\\", "/").lstrip("./")
    if p.startswith(("parallel/", "product/", ".github/")) or "/" not in p:
        return p
    if p.startswith(("ALPHA_", "LIVE_", "PYLAUNCH/", "OWNER_", "WOF052", "BROWSER_", "OPTOOLKIT/")):
        return "parallel/" + p
    return p


def _candidate_verdicts(obj: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("result", "decision", "stopCondition", "verdict", "status"):
        value = obj.get(key)
        if isinstance(value, str):
            out.append(value.strip())
    return out


def _has_exact_verdict(obj: dict[str, Any], expected: str) -> bool:
    return expected in _candidate_verdicts(obj)


def _extract_blob_map(obj: Any) -> dict[str, str]:
    if not isinstance(obj, dict):
        return {}
    direct_keys = (
        "audited_blobs",
        "auditedBlobs",
        "auditedProductBlobs",
        "auditedPreflightBlobs",
        "validatedProductBlobs",
        "productBlobs",
        "productionBlobs",
        "observedBlobShas",
        "pinnedBlobs",
        "sutBlobs",
        "selectedRuntimeBlobs",
    )
    merged: dict[str, str] = {}
    for key in direct_keys:
        value = obj.get(key)
        if isinstance(value, dict):
            for p, sha in value.items():
                if isinstance(p, str) and isinstance(sha, str):
                    merged[_normalize_pin_path(p)] = sha
    production = obj.get("production")
    if isinstance(production, dict):
        path, blob = production.get("path"), production.get("blob")
        if isinstance(path, str) and isinstance(blob, str):
            merged[_normalize_pin_path(path)] = blob
    source_integrity = obj.get("sourceIntegrity")
    if isinstance(source_integrity, dict):
        merged.update(_extract_blob_map(source_integrity))
    for key in ("releaseConsumed", "provenance", "runtimeProvenance", "snapshot"):
        value = obj.get(key)
        if isinstance(value, dict):
            merged.update(_extract_blob_map(value))
    return merged


def _load_evidence_objects(
    root: Path,
    claim: dict[str, Any],
    fallback_paths: Iterable[str] = (),
) -> list[dict[str, Any]]:
    out = [claim]
    seen: set[str] = set()
    for key in ("machineResultPath", "resultJsonPath", "machine_result_path", "resultPath"):
        value = claim.get(key)
        if isinstance(value, str) and value.endswith(".json") and value not in seen:
            seen.add(value)
            obj, _ = _read_json(root, value)
            if obj:
                out.append(obj)
    for rel in fallback_paths:
        if rel in seen:
            continue
        seen.add(rel)
        obj, _ = _read_json(root, rel)
        if obj:
            out.append(obj)
    return out


def _gate(name: str, ok: bool, detail: str) -> dict[str, Any]:
    return {
        "name": name,
        "pass": bool(ok),
        "exitCode": 0 if ok else 3,
        "tail": detail[-1200:],
    }


def _check_current_pins(
    label: str,
    pins: dict[str, str],
    required_paths: Iterable[str],
    blob_resolver: BlobResolver,
) -> list[str]:
    blockers: list[str] = []
    for rel in required_paths:
        expected = pins.get(rel)
        if not expected:
            blockers.append(f"{label} 缺少 currentness pin: {rel}")
            continue
        try:
            actual = blob_resolver(rel)
        except Exception as exc:
            blockers.append(f"{label} 无法读取当前 blob {rel}: {exc}")
            continue
        if actual != expected:
            blockers.append(f"{label} blob 已漂移: {rel} expected={expected} current={actual}")
    return blockers


def _claim_complete(
    root: Path,
    rel: str,
    label: str,
    exact_verdict: str | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    obj, error = _read_json(root, rel)
    if error or obj is None:
        return None, [f"{label}: {error}"]
    blockers: list[str] = []
    if obj.get("state") != "COMPLETE":
        blockers.append(f"{label} 尚未 COMPLETE: state={obj.get('state')}")
    if exact_verdict is not None and not _has_exact_verdict(obj, exact_verdict):
        blockers.append(f"{label} verdict 非 authoritative PASS: observed={_candidate_verdicts(obj)!r}")
    return obj, blockers


def _check_formal(root: Path, blob_resolver: BlobResolver) -> tuple[bool, str]:
    claim, blockers = _claim_complete(root, FORMAL_CLAIM, "Formal current-blob successor", FORMAL_PASS)
    if claim:
        pins = _extract_blob_map(claim)
        blockers.extend(_check_current_pins("Formal current-blob successor", pins, FORMAL_FRESH_PATHS, blob_resolver))
    # Historical adversarial BLOCKED evidence is intentionally not a gate after the current successor PASS.
    historical, _ = _read_json(root, HISTORICAL_FORMAL_BLOCKED)
    historical_state = historical.get("state") if historical else "MISSING"
    if blockers:
        return False, "；".join(blockers)
    return True, f"当前 Formal current-blob successor COMPLETE/PASS 且 freshness-sensitive blobs current；历史 adversarial state={historical_state} 仅保留为历史证据。"


def _check_pylaunch(root: Path, blob_resolver: BlobResolver) -> tuple[bool, str]:
    claim, blockers = _claim_complete(root, PYLAUNCH_CLAIM, "PYLAUNCH Startup Attestation", PYLAUNCH_PASS)
    result, error = _read_json(root, PYLAUNCH_RESULT)
    if error or result is None:
        blockers.append(f"PYLAUNCH Startup Attestation: {error}")
    else:
        if result.get("status") != "PASS" or not _has_exact_verdict(result, PYLAUNCH_PASS):
            blockers.append(f"PYLAUNCH Startup Attestation machine result 非 PASS: {_candidate_verdicts(result)!r}")
        pins = _extract_blob_map(result)
        blockers.extend(_check_current_pins("PYLAUNCH Startup Attestation", pins, PYLAUNCH_FRESH_PATHS, blob_resolver))
    return not blockers, "；".join(blockers) if blockers else "PYLAUNCH Startup Attestation COMPLETE/PASS，production blobs current。"


def _check_recorder(root: Path, blob_resolver: BlobResolver) -> tuple[bool, str]:
    claim, blockers = _claim_complete(root, RECORDER_CLAIM, "Unified Recorder in-flight atomicity", RECORDER_PASS)
    result, error = _read_json(root, RECORDER_RESULT)
    if error or result is None:
        blockers.append(f"Unified Recorder in-flight atomicity: {error}")
    else:
        if result.get("result") != "PASS" or not _has_exact_verdict(result, RECORDER_PASS):
            blockers.append(f"Unified Recorder in-flight machine result 非 PASS: {_candidate_verdicts(result)!r}")
        pins = _extract_blob_map(result)
        production = result.get("production")
        required = []
        if isinstance(production, dict) and isinstance(production.get("path"), str):
            required = [_normalize_pin_path(production["path"])]
        if not required:
            required = ["parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py"]
        blockers.extend(_check_current_pins("Unified Recorder in-flight atomicity", pins, required, blob_resolver))
    return not blockers, "；".join(blockers) if blockers else "Unified Recorder in-flight atomicity COMPLETE/PASS，current runtime blob 匹配。"


def _check_unified_preflight(root: Path, blob_resolver: BlobResolver) -> tuple[bool, str]:
    claim, blockers = _claim_complete(root, UNIFIED_PREFLIGHT_CLAIM, "Unified current-head preflight Fresh QA V2", UNIFIED_PREFLIGHT_PASS)
    if claim:
        pins = _extract_blob_map(claim)
        blockers.extend(_check_current_pins(
            "Unified current-head preflight Fresh QA V2",
            pins,
            UNIFIED_PREFLIGHT_FRESH_PATHS,
            blob_resolver,
        ))
    return not blockers, "；".join(blockers) if blockers else "Unified current-head preflight Fresh QA V2 COMPLETE/PASS，release-consumed preflight blobs current。"


def _check_head_labels(root: Path, blob_resolver: BlobResolver) -> tuple[bool, str]:
    blockers: list[str] = []
    impl, impl_error = _read_json(root, HEAD_LABEL_IMPL_CLAIM)
    if impl_error or impl is None:
        blockers.append(f"Head Labels implementation: {impl_error}")
    elif impl.get("state") != "COMPLETE":
        blockers.append(f"Head Labels implementation 尚未 COMPLETE: state={impl.get('state')}")

    strict, strict_blockers = _claim_complete(
        root,
        HEAD_LABEL_STRICT_FIX_CLAIM,
        "Head Labels strict-type fix",
        HEAD_LABEL_STRICT_FIX_COMPLETE,
    )
    blockers.extend(strict_blockers)
    strict_pins = _extract_blob_map(strict) if strict else {}
    blockers.extend(_check_current_pins("Head Labels strict-type fix", strict_pins, (HEAD_LABEL_PRODUCT,), blob_resolver))

    qa, qa_blockers = _claim_complete(root, HEAD_LABEL_QA_CLAIM, "Head Labels Fresh QA V2", HEAD_LABEL_QA_PASS)
    blockers.extend(qa_blockers)
    if qa:
        evidence = _load_evidence_objects(
            root,
            qa,
            (
                "parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2/RESULT.json",
                "parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2/MACHINE_RESULT.json",
            ),
        )
        qa_pins: dict[str, str] = {}
        for obj in evidence:
            qa_pins.update(_extract_blob_map(obj))
        if not qa_pins.get(HEAD_LABEL_PRODUCT):
            blockers.append(f"Head Labels Fresh QA V2 缺少 exact current product pin: {HEAD_LABEL_PRODUCT}")
        else:
            blockers.extend(_check_current_pins("Head Labels Fresh QA V2", qa_pins, (HEAD_LABEL_PRODUCT,), blob_resolver))
    if blockers:
        return False, "；".join(blockers)
    return True, "Head Labels implementation + strict-type fix + Fresh QA V2 全部 current/PASS；真实 1P/2P/3P 可视化仍属于 bounded live acceptance。"


def _check_oneclick(root: Path, blob_resolver: BlobResolver) -> tuple[bool, str]:
    claim, blockers = _claim_complete(root, ONECLICK_CLAIM, "Owner OneClick V3", ONECLICK_PASS)
    manifest, error = _read_json(root, ONECLICK_MANIFEST)
    if error or manifest is None:
        blockers.append(f"Owner OneClick V3 manifest: {error}")
    else:
        files = manifest.get("files")
        if not isinstance(files, list) or not files:
            blockers.append("Owner OneClick V3 manifest files 为空/无效")
        else:
            for item in files:
                if not isinstance(item, dict):
                    blockers.append("Owner OneClick V3 manifest 存在非 object file entry")
                    continue
                rel, expected = item.get("path"), item.get("gitBlobSha")
                if not isinstance(rel, str) or not isinstance(expected, str):
                    blockers.append(f"Owner OneClick V3 manifest file entry 缺少 path/gitBlobSha: {item!r}")
                    continue
                try:
                    actual = blob_resolver(_normalize_pin_path(rel))
                except Exception as exc:
                    blockers.append(f"Owner OneClick V3 无法读取当前 blob {rel}: {exc}")
                    continue
                if actual != expected:
                    blockers.append(f"Owner OneClick V3 package stale: {rel} manifest={expected} current={actual}")
    return not blockers, "；".join(blockers) if blockers else "Owner OneClick V3 COMPLETE/PASS，manifest 与当前 selected runtime blobs 全量一致。"


def _check_endurance(root: Path, blob_resolver: BlobResolver) -> tuple[bool, str]:
    claim, blockers = _claim_complete(root, ENDURANCE_CLAIM, "True 5h Endurance V2", ENDURANCE_PASS)
    if claim:
        evidence = _load_evidence_objects(
            root,
            claim,
            (
                "parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE_V2/RESULT.json",
                "parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE_V2/final-summary.json",
                "parallel/ALPHA_TRANSPORT_TRUE_ENDURANCE_V2/final_summary.json",
            ),
        )
        pins: dict[str, str] = {}
        for obj in evidence:
            pins.update(_extract_blob_map(obj))
        sut_pins = {p: sha for p, sha in pins.items() if p.startswith("parallel/ALPHA_TRANSPORT_IMPL/")}
        if not sut_pins:
            blockers.append("True 5h Endurance V2 COMPLETE/PASS 但缺少 machine-readable Safe Transport snapshot pins")
        else:
            blockers.extend(_check_current_pins("True 5h Endurance V2", sut_pins, sorted(sut_pins), blob_resolver))
    return not blockers, "；".join(blockers) if blockers else "True 5h Endurance V2 COMPLETE/PASS，pinned Safe Transport snapshot current。"


def _command_gate(root: Path, cmd: list[str], name: str) -> dict[str, Any]:
    p = subprocess.run(
        cmd,
        cwd=root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return _gate(name, p.returncode == 0, (p.stdout + "\n" + p.stderr)[-1200:])


def release_gate(
    root: Path = ROOT,
    blob_resolver: BlobResolver | None = None,
    run_offline: bool = True,
) -> tuple[bool, list[str], list[dict[str, Any]]]:
    """Repository-only current-HEAD Alpha acceptance release gate.

    Returns the legacy orchestrator-compatible (ok, blockers, gates) tuple.
    Historical BLOCKED evidence is not rewritten; authoritative successor
    COMPLETE/PASS + exact currentness is required instead.
    """
    root = Path(root)
    resolve = blob_resolver or _default_blob_resolver(root)
    blockers: list[str] = []
    gates: list[dict[str, Any]] = []

    checks = (
        ("formalCurrentBlob", _check_formal),
        ("pylaunchStartupAttestation", _check_pylaunch),
        ("recorderInflightAtomicity", _check_recorder),
        ("unifiedCurrentHeadPreflight", _check_unified_preflight),
        ("ownerOneClickV3", _check_oneclick),
        ("true5hEnduranceV2", _check_endurance),
        ("enemyTargetHeadLabels", _check_head_labels),
    )
    for name, fn in checks:
        ok, detail = fn(root, resolve)
        gates.append(_gate(name, ok, detail))
        if not ok:
            blockers.append(detail)

    if not blockers and run_offline:
        offline = (
            (["node", "parallel/ALPHA_TRANSPORT_IMPL/run_all.mjs"], "transportFrozenCatalog"),
            (["node", "parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs"], "formalIntegration"),
            ([sys.executable, "-m", "unittest", "discover", "-s", "parallel/PYLAUNCH/tests", "-p", "test*.py"], "pylaunch"),
        )
        for cmd, name in offline:
            gate = _command_gate(root, cmd, name)
            gates.append(gate)
            if not gate["pass"]:
                blockers.append(f"离线 gate 失败: {name}")

    return not blockers, blockers, gates


def preflight_only_success_message() -> str:
    return (
        "REPO PREFLIGHT-ONLY PASS — authoritative successor gates current；"
        "未连接 Browser/WOF。仍需 bounded real target-label visual acceptance："
        "正确 1P/2P/3P、移动/镜头跟随、真实改锁无旧标签、uncertainty fail-closed。"
    )
