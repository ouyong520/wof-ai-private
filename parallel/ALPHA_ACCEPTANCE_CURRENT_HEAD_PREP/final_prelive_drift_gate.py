#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PM = ROOT / "parallel" / "PM"
CLAIMS = PM / "DEDUP_CLAIMS"
STAGE_CLAIMS = PM / "STAGE_CLAIMS"

HARDENING_KEY = "alpha.v1.anchored-overlays.proof-authority-hardening-fix-v2"
HARDENING_STAGE = "ALPHA_V1_ANCHORED_OVERLAYS_PROOF_AUTHORITY_HARDENING_FIX_V2"
HARDENING_PASS = (
    "COMPLETE — ALPHA V1 DUAL-OVERLAY PROOF-AUTHORITY HARDENING FIX V2 — "
    "LIVE ROOT / AUTHORITY REVOCATION / LIFECYCLE / TERMINAL FALSE-PROOF PATHS CLOSED — READY FOR ONE FRESH QA"
)
RUN_MANIFEST = (
    "parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/RUN_MANIFEST.json"
)

ONECLICK_RESULT = "parallel/OWNER_ONECLICK/RESULT.md"
ONECLICK_MANIFEST = "parallel/OWNER_ONECLICK/package_manifest.json"
ONECLICK_V4_PASS = (
    "PASS — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V4 — "
    "IMMUTABLE PLAYER-TEST CANDIDATE READY FOR BOUNDED REAL WOF ACCEPTANCE"
)
ONECLICK_SCHEMA = "wof-owner-oneclick-package-v1"
ONECLICK_POLICY = "owner-oneclick-runtime-v2"

OWNER_FLOW_STAGE = "ALPHA_V1_BOUNDED_LIVE_ACCEPTANCE_OWNER_FLOW_V2"
OWNER_FLOW_PASS = (
    "COMPLETE — ALPHA V1 BOUNDED LIVE ACCEPTANCE OWNER FLOW V2 — "
    "ACTIVE-ROOM 5–10 MINUTE FINAL SESSION DEFINED"
)
OWNER_FLOW_ARTIFACT = "parallel/PM/ALPHA_V1_BOUNDED_LIVE_ACCEPTANCE_OWNER_FLOW_V2.md"

FINAL_QA_KEY_TERMS = ("proof-authority", "hardening-v2", "final-fresh-qa")
FINAL_QA_EXCLUDE_TERMS = ("fixture-prep", "fixture_prep", "prep")

REQUIRED_HARDENED_SUFFIXES = (
    "RUN_MANIFEST.json",
    "proof_core.js",
    "wof_alpha_v1_dual_live_proof_top.js",
    "wof_alpha_v1_dual_live_proof_worker.js",
    "wof_alpha_v1_dual_live_proof.js",
    "wof_alpha_real_worker.js",
    "wof_alpha_player_head_warning.js",
    "wof_alpha_enemy_target_labels.js",
    "LIVE_PROOF_EVIDENCE_SCHEMA.json",
)

PROOF_AUTHORITY_TERMS = (
    "proof-authority",
    "proof authority",
    "live-proof authority",
    "anchored-overlays-one-session-live-proof-tooling",
    "anchored_overlays_one_session_live_proof_tooling",
)

NON_IMPLEMENTATION_TERMS = (
    "fresh qa",
    "independent qa",
    "qa ",
    " qa",
    "audit",
    "cross-check",
    "crosscheck",
    "review",
    "reconciliation",
    "readiness",
    "prep",
    "owner flow",
    "fixture",
    "mapping live-proof prep",
)
IMPLEMENTATION_TERMS = (
    "implementation fix",
    "implementation",
    "production integration",
    "hardening fix",
    "strict fix",
    "fix v",
    "release refresh",
    "runtime fix",
)
RELEASE_DOMAIN_TERMS = (
    "alpha v1",
    "product/alpha",
    "oneclick",
    "one-click",
    "transport",
    "pylaunch",
    "recorder",
    "live proof",
    "live-proof",
    "browser fleet",
    "package-selected",
    "proof-authority",
    "proof authority",
    "anchored_overlays_one_session_live_proof_tooling",
)
NEGATIVE_SCOPE_TERMS = (
    "do not modify",
    "must not modify",
    "without modifying",
    "not modify",
    "no modification",
    "not affect",
    "do not affect",
    "不修改",
    "不得修改",
    "禁止修改",
    "不影响",
    "不要改",
    "不得改",
)

SHA40 = re.compile(r"^[0-9a-f]{40}$")


class GateBlocked(RuntimeError):
    pass


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _read_text(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8-sig")
    except Exception as exc:
        raise GateBlocked(f"cannot read {rel}: {exc}") from exc


def _read_json(rel: str) -> dict[str, Any]:
    try:
        value = json.loads(_read_text(rel))
    except GateBlocked:
        raise
    except Exception as exc:
        raise GateBlocked(f"cannot parse JSON {rel}: {exc}") from exc
    if not isinstance(value, dict):
        raise GateBlocked(f"malformed JSON object {rel}")
    return value


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and cp.returncode:
        raise GateBlocked(
            f"git {' '.join(args)} failed: {(cp.stderr or cp.stdout).strip()}"
        )
    return cp


def _head() -> str:
    value = _git("rev-parse", "HEAD").stdout.strip().lower()
    if not SHA40.fullmatch(value):
        raise GateBlocked(f"cannot resolve current HEAD: {value!r}")
    return value


def _is_ancestor(older: str, newer: str) -> bool:
    if not SHA40.fullmatch(older or "") or not SHA40.fullmatch(newer or ""):
        return False
    return _git("merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def _blob_at(commit: str, rel: str) -> str:
    cp = _git("rev-parse", f"{commit}:{rel}")
    value = cp.stdout.strip().lower()
    if not SHA40.fullmatch(value):
        raise GateBlocked(f"bad blob identity {commit}:{rel}: {value!r}")
    return value


def _claim_rel(key: str) -> str:
    return f"parallel/PM/DEDUP_CLAIMS/{key}.json"


def _stage_rel(stage_id: str) -> str:
    return f"parallel/PM/STAGE_CLAIMS/{stage_id}.json"


def _claim_pair_complete(
    key: str,
    stage_id: str,
    exact_marker: str,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    canonical = _read_json(_claim_rel(key))
    stage = _read_json(_stage_rel(stage_id))
    for label, obj in (("canonical", canonical), ("stage", stage)):
        if obj.get("state") != "COMPLETE":
            raise GateBlocked(f"{stage_id} {label} claim is not terminal COMPLETE: state={obj.get('state')}")
        if obj.get("claimToken") != canonical.get("claimToken"):
            raise GateBlocked(f"{stage_id} claimToken mismatch between canonical/stage")
    if canonical.get("dedupKey") != key or stage.get("dedupKey") != key:
        raise GateBlocked(f"{stage_id} dedupKey mismatch")
    if canonical.get("stageId") != stage_id or stage.get("stageId") != stage_id:
        raise GateBlocked(f"{stage_id} stage identity mismatch")

    result_path = canonical.get("resultPath") or stage.get("resultPath")
    result_commit = canonical.get("resultCommit") or stage.get("resultCommit")
    if not isinstance(result_path, str) or not result_path:
        raise GateBlocked(f"{stage_id} COMPLETE claim lacks resultPath")
    if not isinstance(result_commit, str) or not SHA40.fullmatch(result_commit.lower()):
        raise GateBlocked(f"{stage_id} COMPLETE claim lacks valid resultCommit")
    result_commit = result_commit.lower()
    if canonical.get("resultPath") and stage.get("resultPath") and canonical["resultPath"] != stage["resultPath"]:
        raise GateBlocked(f"{stage_id} canonical/stage resultPath disagree")
    if canonical.get("resultCommit") and stage.get("resultCommit") and canonical["resultCommit"] != stage["resultCommit"]:
        raise GateBlocked(f"{stage_id} canonical/stage resultCommit disagree")
    result_text = _read_text(result_path)
    if exact_marker not in result_text:
        raise GateBlocked(f"{stage_id} durable result lacks authoritative terminal marker")
    return canonical, stage, result_path, result_commit


def _collect_manifest_pins(value: Any) -> dict[str, str]:
    pins: dict[str, str] = {}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            path = node.get("path")
            sha = node.get("sha")
            if isinstance(path, str) and isinstance(sha, str):
                norm = path.replace("\\", "/").lstrip("./")
                if norm in pins and pins[norm].lower() != sha.lower():
                    raise GateBlocked(f"RUN_MANIFEST has conflicting pins for {norm}")
                pins[norm] = sha.lower()
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return pins


def _hardening_gate(head: str) -> tuple[str, dict[str, str], str]:
    _, _, _, result_commit = _claim_pair_complete(
        HARDENING_KEY, HARDENING_STAGE, HARDENING_PASS
    )
    manifest = _read_json(RUN_MANIFEST)
    fixed = manifest.get("implementationCommit")
    if not isinstance(fixed, str) or not SHA40.fullmatch(fixed.lower()):
        raise GateBlocked("post-Hardening RUN_MANIFEST lacks valid implementationCommit")
    fixed = fixed.lower()
    if not _is_ancestor(fixed, result_commit):
        raise GateBlocked(
            f"Hardening resultCommit is not descended from fixed implementationCommit: fixed={fixed} result={result_commit}"
        )
    if not _is_ancestor(result_commit, head):
        raise GateBlocked(f"Hardening durable result {result_commit} is not on current HEAD history")

    pins = _collect_manifest_pins(manifest)
    pins[RUN_MANIFEST] = _blob_at(fixed, RUN_MANIFEST)
    for suffix in REQUIRED_HARDENED_SUFFIXES:
        if not any(path.endswith(suffix) for path in pins):
            raise GateBlocked(f"post-Hardening RUN_MANIFEST missing authority-critical pin: {suffix}")
    for path, wanted in sorted(pins.items()):
        if not SHA40.fullmatch(wanted):
            raise GateBlocked(f"post-Hardening RUN_MANIFEST has malformed blob SHA: {path}={wanted}")
        at_fixed = _blob_at(fixed, path)
        if at_fixed != wanted:
            raise GateBlocked(
                f"post-Hardening manifest pin mismatch at fixed commit: {path} expected={wanted} fixed={at_fixed}"
            )
        current = _blob_at(head, path)
        if current != wanted:
            raise GateBlocked(
                f"authority-critical post-Hardening blob drifted after fixed tree: {path} expected={wanted} current={current}"
            )
    return fixed, pins, result_commit


def _final_qa_candidates() -> list[tuple[Path, dict[str, Any]]]:
    found: list[tuple[Path, dict[str, Any]]] = []
    if not CLAIMS.is_dir():
        raise GateBlocked("canonical claim directory missing")
    for path in sorted(CLAIMS.glob("*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        key = str(obj.get("dedupKey", "")).lower()
        if not all(term in key for term in FINAL_QA_KEY_TERMS):
            continue
        if any(term in key for term in FINAL_QA_EXCLUDE_TERMS):
            continue
        found.append((path, obj))
    return found


def _final_qa_gate(
    head: str,
    fixed: str,
    hardened_pins: dict[str, str],
    hardening_result_commit: str,
) -> tuple[dict[str, Any], str]:
    candidates = _final_qa_candidates()
    if not candidates:
        raise GateBlocked("the single Final Fresh QA claim/result does not exist yet")
    if len(candidates) != 1:
        names = ", ".join(path.name for path, _ in candidates)
        raise GateBlocked(f"ambiguous Final Fresh QA authority: expected exactly one claim, found {len(candidates)} [{names}]")

    path, canonical = candidates[0]
    stage_id = canonical.get("stageId")
    key = canonical.get("dedupKey")
    if not isinstance(stage_id, str) or not stage_id:
        raise GateBlocked(f"Final Fresh QA canonical claim lacks stageId: {_rel(path)}")
    if not isinstance(key, str) or not key:
        raise GateBlocked(f"Final Fresh QA canonical claim lacks dedupKey: {_rel(path)}")
    stage = _read_json(_stage_rel(stage_id))
    if canonical.get("state") != "COMPLETE" or stage.get("state") != "COMPLETE":
        raise GateBlocked(
            f"Final Fresh QA is not terminal COMPLETE: canonical={canonical.get('state')} stage={stage.get('state')}"
        )
    if stage.get("claimToken") != canonical.get("claimToken") or stage.get("dedupKey") != key:
        raise GateBlocked("Final Fresh QA canonical/stage authority mismatch")

    result_path = canonical.get("resultPath") or stage.get("resultPath")
    result_commit = canonical.get("resultCommit") or stage.get("resultCommit")
    if not isinstance(result_path, str) or not result_path:
        raise GateBlocked("Final Fresh QA COMPLETE claim lacks resultPath")
    if not isinstance(result_commit, str) or not SHA40.fullmatch(result_commit.lower()):
        raise GateBlocked("Final Fresh QA COMPLETE claim lacks valid resultCommit")
    result_commit = result_commit.lower()
    if not _is_ancestor(hardening_result_commit, result_commit):
        raise GateBlocked(
            "Final Fresh QA result is not descended from the terminal Hardening V2 result"
        )
    if not _is_ancestor(result_commit, head):
        raise GateBlocked("Final Fresh QA durable result is not on current HEAD history")

    text = _read_text(result_path)
    normalized = text.upper()
    if "PASS" not in normalized or "HARDENING V2" not in normalized or "FRESH QA" not in normalized:
        raise GateBlocked("Final Fresh QA durable result lacks authoritative PASS / HARDENING V2 / FRESH QA markers")
    if "17/17" not in text and "17 / 17" not in text:
        raise GateBlocked("Final Fresh QA durable result does not record the frozen 17/17 independent case set")
    if fixed not in text.lower():
        raise GateBlocked(
            f"Final Fresh QA result does not pin exact hardened implementationCommit {fixed}"
        )
    missing_pins = [
        f"{path}={sha}"
        for path, sha in sorted(hardened_pins.items())
        if sha.lower() not in text.lower()
    ]
    if missing_pins:
        preview = ", ".join(missing_pins[:3])
        extra = "" if len(missing_pins) <= 3 else f" (+{len(missing_pins) - 3} more)"
        raise GateBlocked(
            "Final Fresh QA PASS is not exact-blob authoritative; missing hardened pin evidence: "
            + preview
            + extra
        )
    return canonical, result_commit


def _load_refresh_manifest_module():
    path = ROOT / "parallel" / "OWNER_ONECLICK" / "refresh_manifest.py"
    spec = importlib.util.spec_from_file_location("owner_oneclick_refresh_manifest", path)
    if spec is None or spec.loader is None:
        raise GateBlocked("cannot load Owner OneClick deterministic selector")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _oneclick_gate(head: str) -> str:
    result = _read_text(ONECLICK_RESULT)
    if ONECLICK_V4_PASS not in result:
        raise GateBlocked("Owner OneClick V4 durable PASS marker is absent/current result was replaced")
    manifest = _read_json(ONECLICK_MANIFEST)
    if manifest.get("schema") != ONECLICK_SCHEMA:
        raise GateBlocked(f"OneClick manifest schema drift: {manifest.get('schema')!r}")
    if manifest.get("selectionPolicy") != ONECLICK_POLICY:
        raise GateBlocked(f"OneClick manifest selection policy drift: {manifest.get('selectionPolicy')!r}")
    safety = manifest.get("safety")
    if safety != {"readOnly": True, "ramWrites": 0, "inputInjection": False}:
        raise GateBlocked(f"OneClick safety boundary changed: {safety!r}")
    source = manifest.get("sourceCommit")
    if not isinstance(source, str) or not SHA40.fullmatch(source.lower()):
        raise GateBlocked("OneClick V4 manifest lacks valid immutable sourceCommit")
    source = source.lower()
    if source not in result.lower():
        raise GateBlocked("OneClick V4 result does not identify the manifest immutable sourceCommit")

    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        raise GateBlocked("OneClick V4 manifest files list missing/malformed")
    expected: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise GateBlocked("OneClick V4 manifest contains malformed file row")
        rel = row.get("path")
        sha = row.get("gitBlobSha")
        if not isinstance(rel, str) or not isinstance(sha, str) or not SHA40.fullmatch(sha.lower()):
            raise GateBlocked(f"OneClick V4 manifest contains malformed path/blob row: {row!r}")
        if rel in expected:
            raise GateBlocked(f"OneClick V4 manifest duplicates selected path: {rel}")
        expected[rel] = sha.lower()

    selector = _load_refresh_manifest_module()
    if getattr(selector, "SELECTION_POLICY", None) != ONECLICK_POLICY:
        raise GateBlocked(
            f"current OneClick selector policy changed: {getattr(selector, 'SELECTION_POLICY', None)!r}"
        )
    try:
        current = selector.selected_paths_from_commit(ROOT, head)
    except Exception as exc:
        raise GateBlocked(f"cannot deterministically resolve current package-selected runtime: {exc}") from exc
    current = {str(path): str(sha).lower() for path, sha in current.items()}

    missing_from_manifest = sorted(set(current) - set(expected))
    stale_manifest_paths = sorted(set(expected) - set(current))
    if missing_from_manifest:
        raise GateBlocked(
            "new package-selected runtime path is outside OneClick V4 manifest: "
            + ", ".join(missing_from_manifest[:6])
        )
    if stale_manifest_paths:
        raise GateBlocked(
            "OneClick V4 manifest path is no longer selected by current runtime policy: "
            + ", ".join(stale_manifest_paths[:6])
        )
    drift = [
        (path, expected[path], current[path])
        for path in sorted(expected)
        if expected[path] != current[path]
    ]
    if drift:
        path, wanted, actual = drift[0]
        raise GateBlocked(
            f"package-selected runtime drift after OneClick V4 freeze: {path} expected={wanted} current={actual}"
        )
    return source


def _owner_flow_gate(head: str) -> None:
    stage = _read_json(_stage_rel(OWNER_FLOW_STAGE))
    if stage.get("state") != "COMPLETE":
        raise GateBlocked(f"Owner Flow V2 is not COMPLETE: state={stage.get('state')}")
    result_path = stage.get("resultPath")
    result_commit = stage.get("resultCommit")
    if not isinstance(result_path, str) or not isinstance(result_commit, str) or not SHA40.fullmatch(result_commit.lower()):
        raise GateBlocked("Owner Flow V2 COMPLETE claim lacks durable result authority")
    if OWNER_FLOW_PASS not in _read_text(result_path):
        raise GateBlocked("Owner Flow V2 durable COMPLETE marker absent")
    if not (ROOT / OWNER_FLOW_ARTIFACT).is_file():
        raise GateBlocked(f"Owner Flow V2 artifact missing: {OWNER_FLOW_ARTIFACT}")
    if not _is_ancestor(result_commit.lower(), head):
        raise GateBlocked("Owner Flow V2 result is not on current HEAD history")


def _claim_generation_commit(path: Path, claim: dict[str, Any]) -> str | None:
    start = claim.get("startCommit")
    if isinstance(start, str) and SHA40.fullmatch(start.lower()):
        return start.lower()
    cp = _git("log", "--diff-filter=A", "--format=%H", "-1", "--", _rel(path), check=False)
    value = cp.stdout.strip().lower()
    return value if SHA40.fullmatch(value) else None


def _prompt_text_for_claim(claim: dict[str, Any]) -> str:
    prompt = claim.get("promptPath")
    if not isinstance(prompt, str) or not prompt:
        raise GateBlocked(
            f"post-freeze ACTIVE claim lacks promptPath: dedupKey={claim.get('dedupKey')!r}"
        )
    return _read_text(prompt)


def _priority_p0_p1(text: str) -> bool:
    head = "\n".join(text.splitlines()[:80])
    return bool(re.search(r"\bP[01]\b", head, re.IGNORECASE))


def _positive_scope_text(text: str) -> str:
    kept: list[str] = []
    for line in text.splitlines():
        low = line.lower()
        if any(term in low for term in NEGATIVE_SCOPE_TERMS):
            continue
        kept.append(line)
    return "\n".join(kept).lower()


def _looks_like_release_implementation_owner(text: str) -> bool:
    low = text.lower()
    title = low.splitlines()[0] if low.splitlines() else ""
    if any(term in title for term in NON_IMPLEMENTATION_TERMS):
        return False
    if not any(term in low for term in IMPLEMENTATION_TERMS):
        return False
    positive = _positive_scope_text(text)
    return any(term in positive for term in RELEASE_DOMAIN_TERMS)


def _is_proof_authority_text(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in PROOF_AUTHORITY_TERMS)


def _post_freeze_active_owner_gate(v4_source: str) -> None:
    if not CLAIMS.is_dir():
        raise GateBlocked("canonical claims directory missing")
    for path in sorted(CLAIMS.glob("*.json")):
        try:
            claim = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(claim, dict) or claim.get("state") != "ACTIVE":
            continue
        if claim.get("dedupKey") == HARDENING_KEY:
            continue
        generation = _claim_generation_commit(path, claim)
        if generation is None:
            raise GateBlocked(
                f"cannot establish generation for ACTIVE canonical claim {_rel(path)}"
            )
        if generation == v4_source or _is_ancestor(generation, v4_source):
            # Historical ACTIVE claims at/before immutable V4 were already reconciled
            # by the durable V4 PASS and are not mechanically re-opened here.
            continue
        if not _is_ancestor(v4_source, generation):
            raise GateBlocked(
                f"ACTIVE claim generation is not comparable to OneClick V4 baseline: {_rel(path)} start={generation}"
            )
        text = _prompt_text_for_claim(claim)
        if _priority_p0_p1(text) and _looks_like_release_implementation_owner(text):
            raise GateBlocked(
                "new ACTIVE P0/P1 release implementation owner after OneClick V4 freeze: "
                f"{claim.get('stageId') or claim.get('dedupKey')}"
            )


def _after(commit: str, generation: str | None) -> bool:
    if generation is None or generation == commit or _is_ancestor(generation, commit):
        return False
    return _is_ancestor(commit, generation)


def _post_qa_proof_blocker_gate(qa_result_commit: str) -> None:
    # Canonical claims are the primary authority.
    for path in sorted(CLAIMS.glob("*.json")):
        try:
            claim = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(claim, dict) or claim.get("state") not in {"ACTIVE", "BLOCKED"}:
            continue
        generation = _claim_generation_commit(path, claim)
        if not _after(qa_result_commit, generation):
            continue
        text = _prompt_text_for_claim(claim)
        if not _is_proof_authority_text(text):
            continue
        if claim.get("state") == "BLOCKED":
            raise GateBlocked(
                "new mandatory proof-authority blocker opened after Final Fresh QA: "
                f"{claim.get('stageId') or claim.get('dedupKey')}"
            )
        if _priority_p0_p1(text) and _looks_like_release_implementation_owner(text):
            raise GateBlocked(
                "new ACTIVE mandatory proof-authority implementation owner opened after Final Fresh QA: "
                f"{claim.get('stageId') or claim.get('dedupKey')}"
            )

    # Fail closed if a stage was durably BLOCKED but its canonical file has not yet
    # caught up. This protects against the small multi-file claim/result update window.
    for path in sorted(STAGE_CLAIMS.glob("*.json")):
        try:
            stage = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(stage, dict) or stage.get("state") != "BLOCKED":
            continue
        generation = _claim_generation_commit(path, stage)
        if not _after(qa_result_commit, generation):
            continue
        evidence = ""
        canonical_path = stage.get("canonicalClaimPath")
        if isinstance(canonical_path, str) and (ROOT / canonical_path).is_file():
            canonical = _read_json(canonical_path)
            prompt = canonical.get("promptPath")
            if isinstance(prompt, str) and (ROOT / prompt).is_file():
                evidence += "\n" + _read_text(prompt)
        result_path = stage.get("resultPath")
        if isinstance(result_path, str) and (ROOT / result_path).is_file():
            evidence += "\n" + _read_text(result_path)
        if _is_proof_authority_text(evidence):
            raise GateBlocked(
                "new mandatory proof-authority BLOCKED stage after Final Fresh QA: "
                f"{stage.get('stageId') or path.name}"
            )


def evaluate() -> tuple[bool, str, dict[str, Any]]:
    head = _head()
    fixed, hardened_pins, hardening_result_commit = _hardening_gate(head)
    qa_claim, qa_result_commit = _final_qa_gate(
        head, fixed, hardened_pins, hardening_result_commit
    )
    v4_source = _oneclick_gate(head)
    _owner_flow_gate(head)
    _post_freeze_active_owner_gate(v4_source)
    _post_qa_proof_blocker_gate(qa_result_commit)
    return True, "AUTHORIZED FOR START BOUNDED REAL WOF ACCEPTANCE", {
        "head": head,
        "hardeningFixedCommit": fixed,
        "hardeningResultCommit": hardening_result_commit,
        "finalFreshQaDedupKey": qa_claim.get("dedupKey"),
        "finalFreshQaResultCommit": qa_result_commit,
        "oneClickV4SourceCommit": v4_source,
        "selectedRuntimeDrift": False,
        "proofAuthorityDrift": False,
        "ownerFlowV2": "COMPLETE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Narrow one-shot post-Hardening/Final-QA authorization drift gate"
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable result")
    args = parser.parse_args(argv)
    try:
        ok, line, detail = evaluate()
    except GateBlocked as exc:
        ok = False
        line = f"WAITING/BLOCKED — {exc}"
        detail = {"reason": str(exc)}
    if args.json:
        print(json.dumps({"authorized": ok, "line": line, **detail}, ensure_ascii=False, sort_keys=True))
    else:
        print(line)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
