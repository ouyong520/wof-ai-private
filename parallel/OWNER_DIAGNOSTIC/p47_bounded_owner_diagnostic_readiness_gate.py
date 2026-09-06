from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

READY = "READY_FOR_ONE_BOUNDED_OWNER_DIAGNOSTIC"
BLOCKED = "BLOCKED"
P40_BLOCKER = "NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT"
TRUTH_STATES = ["AVAILABLE", "NOT_AVAILABLE", "UNRESOLVED"]
P43_TESTED = "0c23e22b0387d0b3042c5601ab0a9e897ce1c476"
P43_TREE = "e6da807b9efa29d5ab819013dbe2da4ded995aa6"
P45_TESTED = "3dac7a9e2cbe4a23c3de44eb15cf45f19b136149"
P46_TESTED = "210efdda5bbf3715989c751eb90442f26f42d0a9"

STAGES = {
    "p43": {
        "stage": "ALPHA_V1_PRODUCT_TAKEOVER_P43_BOUNDED_ZERO_CLICK_LIVE_DIAGNOSTIC_HARNESS",
        "dedup": "alpha.v1.product-takeover.bounded-zero-click-live-diagnostic-harness-v2",
        "tested": P43_TESTED,
        "resultCommit": "2c916da0bdaa10777e75d356e8a9975698e99835",
        "result": "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P43_BOUNDED_ZERO_CLICK_LIVE_DIAGNOSTIC_HARNESS_RESULT.json",
        "canonical": "parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.bounded-zero-click-live-diagnostic-harness-v2.json",
        "claim": "parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P43_BOUNDED_ZERO_CLICK_LIVE_DIAGNOSTIC_HARNESS.json",
    },
    "p45": {
        "stage": "ALPHA_V1_PRODUCT_TAKEOVER_P45_P42_P39_LIVE_DIAGNOSTIC_STAGING_INTEGRATION",
        "dedup": "alpha.v1.product-takeover.p42-p39-live-diagnostic-staging-integration-v1",
        "tested": P45_TESTED,
        "resultCommit": "034911b98001318e0be7d0e42ffe60df13c95d78",
        "result": "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P45_P42_P39_LIVE_DIAGNOSTIC_STAGING_INTEGRATION_RESULT.json",
        "canonical": "parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.p42-p39-live-diagnostic-staging-integration-v1.json",
        "claim": "parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P45_P42_P39_LIVE_DIAGNOSTIC_STAGING_INTEGRATION.json",
    },
    "p46": {
        "stage": "ALPHA_V1_PRODUCT_TAKEOVER_P46_WASM_WEBGL_CALLSITE_FINGERPRINT_PROBE",
        "dedup": "alpha.v1.product-takeover.wasm-webgl-callsite-fingerprint-probe-v1",
        "tested": P46_TESTED,
        "resultCommit": "90a8abe2368f2c8b172aee13b7531a389985017b",
        "result": "parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P46_WASM_WEBGL_CALLSITE_FINGERPRINT_PROBE_RESULT.json",
        "canonical": "parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.wasm-webgl-callsite-fingerprint-probe-v1.json",
        "claim": "parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P46_WASM_WEBGL_CALLSITE_FINGERPRINT_PROBE.json",
    },
}

CANDIDATE_PATH = "parallel/OWNER_DIAGNOSTIC/P43_POST_P45_P46_INTEGRATED_CANDIDATE.json"
PINS_PATH = "parallel/OWNER_DIAGNOSTIC/P43_POST_P45_P46_DEPENDENCY_PINS.json"
P43_CORE_PATH = "parallel/OWNER_DIAGNOSTIC/p43_bounded_zero_click_live_diagnostic.py"
P43_CONTINUATION_PATH = "parallel/OWNER_DIAGNOSTIC/p43_post_p45_p46_continuation.py"
P46_SOURCE_PATH = "parallel/RENDER_AUTHORITY_V2/wasm_webgl_callsite_fingerprint_probe.js"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _run(repo: Path, *args: str) -> bytes:
    cp = subprocess.run(["git", *args], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if cp.returncode:
        raise RuntimeError(cp.stderr.decode("utf-8", "replace").strip() or f"git {' '.join(args)} failed")
    return cp.stdout


def _head_bytes(repo: Path, rel: str) -> bytes:
    if Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise RuntimeError(f"unbounded path: {rel}")
    return _run(repo, "show", f"HEAD:{rel}")


def _json(repo: Path, rel: str) -> dict[str, Any]:
    value = json.loads(_head_bytes(repo, rel).decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{rel}: JSON root must be object")
    return value


def collect(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    out: dict[str, Any] = {"head": _run(repo, "rev-parse", "HEAD").decode().strip(), "records": {}, "blobs": {}, "texts": {}}
    for key, spec in STAGES.items():
        out["records"][key] = {
            "result": _json(repo, spec["result"]),
            "canonical": _json(repo, spec["canonical"]),
            "claim": _json(repo, spec["claim"]),
        }
    out["candidate"] = _json(repo, CANDIDATE_PATH)
    out["pins"] = _json(repo, PINS_PATH)
    out["p43TestedTree"] = _run(repo, "rev-parse", f"{P43_TESTED}^{{tree}}").decode().strip()

    required = set(out["candidate"].get("testedBlobMap") or {})
    p45 = out["pins"].get("p45") if isinstance(out["pins"].get("p45"), Mapping) else {}
    required.update((p45.get("exactFiles") or {}).keys())
    p46 = out["pins"].get("p46") if isinstance(out["pins"].get("p46"), Mapping) else {}
    if isinstance(p46.get("sourcePath"), str):
        required.add(p46["sourcePath"])
    required.update({CANDIDATE_PATH, PINS_PATH, P43_CORE_PATH, P43_CONTINUATION_PATH, P46_SOURCE_PATH})
    for rel in sorted(required):
        data = _head_bytes(repo, rel)
        out["blobs"][rel] = git_blob_sha(data)
        if rel in {P43_CORE_PATH, P43_CONTINUATION_PATH, P46_SOURCE_PATH}:
            out["texts"][rel] = data.decode("utf-8", "replace")
    return out


def _tested(result: Mapping[str, Any]) -> Any:
    return result.get("testedCommit", result.get("testedCandidateCommit"))


def evaluate(s: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    checks: dict[str, bool] = {}

    def check(name: str, ok: bool, code: str) -> None:
        checks[name] = bool(ok)
        if not ok and code not in blockers:
            blockers.append(code)

    records = s.get("records") if isinstance(s.get("records"), Mapping) else {}
    for key, spec in STAGES.items():
        rec = records.get(key) if isinstance(records.get(key), Mapping) else {}
        result = rec.get("result") if isinstance(rec.get("result"), Mapping) else {}
        canonical = rec.get("canonical") if isinstance(rec.get("canonical"), Mapping) else {}
        claim = rec.get("claim") if isinstance(rec.get("claim"), Mapping) else {}
        check(f"{key}.result.complete", result.get("state") == "COMPLETE", f"{key.upper()}_RESULT_NOT_COMPLETE")
        check(f"{key}.result.stage", result.get("stageId") == spec["stage"], f"{key.upper()}_RESULT_STAGE_MISMATCH")
        check(f"{key}.result.tested", _tested(result) == spec["tested"], f"{key.upper()}_RESULT_TESTED_COMMIT_MISMATCH")
        for label, c in (("canonical", canonical), ("claim", claim)):
            check(f"{key}.{label}.complete", c.get("state") == "COMPLETE", f"{key.upper()}_{label.upper()}_NOT_CLOSED")
            check(f"{key}.{label}.tested", c.get("testedCommit") == spec["tested"], f"{key.upper()}_{label.upper()}_TESTED_COMMIT_MISMATCH")
            check(f"{key}.{label}.resultCommit", c.get("resultCommit") == spec["resultCommit"], f"{key.upper()}_{label.upper()}_RESULT_COMMIT_MISMATCH")
            check(f"{key}.{label}.resultPath", c.get("resultPath") == spec["result"], f"{key.upper()}_{label.upper()}_RESULT_PATH_MISMATCH")
            check(f"{key}.{label}.token", c.get("claimToken") == result.get("claimToken"), f"{key.upper()}_{label.upper()}_CLAIM_TOKEN_MISMATCH")
        check(f"{key}.claims.match", canonical.get("claimToken") == claim.get("claimToken"), f"{key.upper()}_CLAIM_MISMATCH")

    p43 = records.get("p43", {}).get("result", {}) if isinstance(records.get("p43"), Mapping) else {}
    p45 = records.get("p45", {}).get("result", {}) if isinstance(records.get("p45"), Mapping) else {}
    p46 = records.get("p46", {}).get("result", {}) if isinstance(records.get("p46"), Mapping) else {}
    candidate = s.get("candidate") if isinstance(s.get("candidate"), Mapping) else {}
    pins = s.get("pins") if isinstance(s.get("pins"), Mapping) else {}
    blobs = s.get("blobs") if isinstance(s.get("blobs"), Mapping) else {}
    texts = s.get("texts") if isinstance(s.get("texts"), Mapping) else {}

    check("p43.tree", s.get("p43TestedTree") == P43_TREE and p43.get("testedTree") == P43_TREE, "P43_TESTED_TREE_MISMATCH")
    meta = p43.get("testedCandidateMetadata") if isinstance(p43.get("testedCandidateMetadata"), Mapping) else {}
    check("candidate.path", meta.get("path") == CANDIDATE_PATH, "P43_CANDIDATE_PATH_MISMATCH")
    check("candidate.blob", blobs.get(CANDIDATE_PATH) == meta.get("gitBlobSha"), "P43_CANDIDATE_BLOB_MISMATCH")
    check("candidate.stage", candidate.get("stageId") == STAGES["p43"]["stage"], "P43_CANDIDATE_STAGE_MISMATCH")
    check("candidate.token", candidate.get("claimToken") == p43.get("claimToken"), "P43_CANDIDATE_CLAIM_TOKEN_MISMATCH")
    check("candidate.state", candidate.get("state") == "FROZEN_FOR_EXACT_BYTE_TEST", "P43_CANDIDATE_NOT_FROZEN")

    tested_map = candidate.get("testedBlobMap") if isinstance(candidate.get("testedBlobMap"), Mapping) else {}
    for rel, expected in sorted(tested_map.items()):
        check(f"blob.{rel}", blobs.get(rel) == expected, "P43_REQUIRED_IMPLEMENTATION_BLOB_MISMATCH")
    check("pins.blob", blobs.get(PINS_PATH) == tested_map.get(PINS_PATH), "P43_DEPENDENCY_PINS_BLOB_MISMATCH")

    p45_pin = pins.get("p45") if isinstance(pins.get("p45"), Mapping) else {}
    p46_pin = pins.get("p46") if isinstance(pins.get("p46"), Mapping) else {}
    check("pins.p45.commit", p45_pin.get("testedCommit") == P45_TESTED, "P45_DEPENDENCY_PIN_MISMATCH")
    check("pins.p46.commit", p46_pin.get("testedCommit") == P46_TESTED, "P46_DEPENDENCY_PIN_MISMATCH")
    for rel, expected in sorted((p45_pin.get("exactFiles") or {}).items()):
        check(f"p45pin.{rel}", blobs.get(rel) == expected, "P45_REQUIRED_IMPLEMENTATION_BLOB_MISMATCH")
    check("p46pin.source", blobs.get(p46_pin.get("sourcePath")) == p46_pin.get("sourceGitBlobSha"), "P46_REQUIRED_IMPLEMENTATION_BLOB_MISMATCH")

    safety = candidate.get("safety") if isinstance(candidate.get("safety"), Mapping) else {}
    p43s = p43.get("safety") if isinstance(p43.get("safety"), Mapping) else {}
    check("safety.zeroClick", safety.get("zeroClick") is True and p43s.get("zeroClick") is True, "ZERO_CLICK_CONTRACT_MISSING")
    check("safety.manualSeed", safety.get("manualSeedRequired") is False and p43s.get("manualSeedRequired") is False, "MANUAL_SEED_CONTRACT_UNSAFE")
    check("safety.readOnly", safety.get("readOnly") is True and p43s.get("readOnly") is True, "READ_ONLY_CONTRACT_MISSING")
    check("safety.ram", safety.get("ramWrites") == 0 and p43s.get("ramWrites") == 0, "RAM_WRITE_CONTRACT_UNSAFE")
    check("safety.input", safety.get("inputInjection") is False and p43s.get("inputInjection") is False, "INPUT_INJECTION_CONTRACT_UNSAFE")
    check("safety.noPromotion", safety.get("promotionPerformed") is False and safety.get("alphaLiveMoved") is False and p43s.get("promotionPerformed") is False and p43s.get("alphaLiveMoved") is False, "PROMOTION_OR_ALPHA_LIVE_MOVEMENT_PRESENT")

    core_text = str(texts.get(P43_CORE_PATH) or "")
    continuation_text = str(texts.get(P43_CONTINUATION_PATH) or "")
    p46_text = str(texts.get(P46_SOURCE_PATH) or "")
    check("bounds.p43", all(token in core_text for token in ("MAX_CONSOLE_EVENTS = 512", "MAX_LOG_BYTES = 8 * 1024 * 1024", "min(args.duration, 60.0)", "P43_BOUNDED_TEARDOWN")), "P43_BOUNDED_LIMIT_CONTRACT_MISSING")
    check("bounds.p46", all(token in p46_text for token in ("maxWallMs:15000", "maxEvents:384", "BOUNDED_EVENT_LIMIT_REACHED")), "P46_BOUNDED_LIMIT_CONTRACT_MISSING")
    check("binding.failclosed", all(token in continuation_text for token in ("runtimeEpoch", "rendererEpoch", "authorityKey", "P45_STALE_OR_MIXED_AUTHORITY_BINDING", "P46_STALE_OR_MIXED_AUTHORITY_BINDING", "P46_TEARDOWN_CONFLICT")), "BINDING_OR_WRAPPER_FAIL_CLOSED_CONTRACT_MISSING")
    check("moduleAsm.failclosed", "MODULE_OR_ASM_IDENTITY_CHANGED" in p46_text, "MODULE_ASM_DRIFT_FAIL_CLOSED_CONTRACT_MISSING")
    check("wrapper.conflict", "WRAPPER_REPLACED_EXTERNALLY" in p46_text and "P46_TEARDOWN_CONFLICT" in continuation_text, "WRAPPER_CONFLICT_FAIL_CLOSED_CONTRACT_MISSING")

    receipt = p43.get("receiptContract") if isinstance(p43.get("receiptContract"), Mapping) else {}
    check("association.pageWorkerWasm", receipt.get("preservesAllPageTargetsAndAuthoritativePageWorkerWasmAssociation") is True, "PAGE_WORKER_WASM_ASSOCIATION_CONTRACT_MISSING")
    check("raw.p39p42", receipt.get("preservesP39VisibleHiddenLostStaleAmbiguousReacquire") is True and receipt.get("preservesP42CompleteRawBundleBindingSealAndTeardown") is True, "P39_P42_RAW_EVIDENCE_PRESERVATION_MISSING")
    check("raw.p46", receipt.get("preservesP46CompleteRawStackFingerprintWasmTruthJsCallerModuleAsmBindingAssociationsAndTeardown") is True, "P46_RAW_EVIDENCE_PRESERVATION_MISSING")
    check("provenance.pointer", receipt.get("preservesExactCandidatePackageManifestAttestationProvenancePointer") is True, "EXACT_PACKAGE_MANIFEST_ATTESTATION_POINTER_CONTRACT_MISSING")

    staging = p45.get("stagingContract") if isinstance(p45.get("stagingContract"), Mapping) else {}
    check("binding.fields", staging.get("bindingFields") == ["runtimeEpoch", "rendererEpoch", "authorityKey"], "EXACT_RUNTIME_RENDERER_AUTHORITY_BINDING_MISSING")
    check("p45.raw", staging.get("rawBundleFiltering") is False, "P45_RAW_BUNDLE_FILTERING_UNSAFE")
    check("p45.safety", (p45.get("safety") or {}).get("readOnly") is True and (p45.get("safety") or {}).get("ramWrites") == 0 and (p45.get("safety") or {}).get("inputInjection") is False, "P45_SAFETY_CONTRACT_UNSAFE")

    check("p46.truthStates", p43.get("p46TruthBoundary", {}).get("wasmFunctionIndex") == TRUTH_STATES and p43.get("p46TruthBoundary", {}).get("wasmFunctionName") == TRUTH_STATES and p43.get("p46TruthBoundary", {}).get("wasmOffset") == TRUTH_STATES and p46_pin.get("truthStates") == TRUTH_STATES, "P46_WASM_TRUTH_STATE_CONTRACT_MISMATCH")
    p46auth = p46.get("authorityBoundary") if isinstance(p46.get("authorityBoundary"), Mapping) else {}
    check("p46.noGuess", p46auth.get("guessedWasmSymbol") is False and p46auth.get("guessedWasmOffset") is False, "P46_WASM_GUESSING_ENABLED")

    auth = p43.get("authorityBoundary") if isinstance(p43.get("authorityBoundary"), Mapping) else {}
    check("authority.p40", auth.get("p40BlockerResolved") is False and auth.get("p40Blocker") == P40_BLOCKER, "P40_BLOCKER_REWRITTEN")
    check("authority.noMint", auth.get("authorityEligible") is False and auth.get("mappingOnly") is True and auth.get("createsNativeMarkerSourceExport") is False and auth.get("emitsRendererAuthorityProof") is False and auth.get("changesP29Acceptance") is False and auth.get("changesP32Qualification") is False, "DIAGNOSTIC_AUTHORITY_BOUNDARY_VIOLATED")
    check("authority.noRetryPromotion", auth.get("retryEligibilityMinted", False) is False and auth.get("promotionEligibilityMinted", False) is False, "RETRY_OR_PROMOTION_AUTHORITY_MINTED")

    decision = READY if not blockers else BLOCKED
    return {
        "schema": "wof-alpha-p47-bounded-owner-diagnostic-readiness-v1",
        "decision": decision,
        "runBudget": 1 if decision == READY else 0,
        "blockerCodes": blockers,
        "terminalAuthority": "RESULT_AND_CLOSED_CLAIMS_ONLY_PROGRESS_IGNORED",
        "p40": {"state": "BLOCKED", "blocker": P40_BLOCKER, "resolvedByP47": False},
        "wasmTruthStates": {"functionIndex": TRUTH_STATES, "functionName": TRUTH_STATES, "offset": TRUTH_STATES, "guessingAllowed": False},
        "authority": {"diagnosticCorrelationOnly": True, "rendererAuthorityMinted": False, "p29Changed": False, "p32Changed": False, "retryEligibilityMinted": False, "promotionEligibilityMinted": False, "sourceExportMinted": False},
        "provenance": {"head": s.get("head"), "p43TestedCommit": P43_TESTED, "p43TestedTree": s.get("p43TestedTree"), "p45TestedCommit": P45_TESTED, "p46TestedCommit": P46_TESTED, "candidatePath": CANDIDATE_PATH, "candidateBlob": blobs.get(CANDIDATE_PATH), "dependencyPinsPath": PINS_PATH, "dependencyPinsBlob": blobs.get(PINS_PATH)},
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        artifact = evaluate(collect(args.repo_root))
    except Exception as exc:
        artifact = {"schema": "wof-alpha-p47-bounded-owner-diagnostic-readiness-v1", "decision": BLOCKED, "runBudget": 0, "blockerCodes": ["READINESS_INPUT_UNAVAILABLE_OR_INVALID"], "error": f"{type(exc).__name__}: {exc}", "terminalAuthority": "RESULT_AND_CLOSED_CLAIMS_ONLY_PROGRESS_IGNORED"}
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if artifact.get("decision") == READY else 2


if __name__ == "__main__":
    raise SystemExit(main())
