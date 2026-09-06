from __future__ import annotations

from contextlib import contextmanager
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import traceback
from typing import Any, Iterator, Mapping, Sequence

import p43_bounded_zero_click_live_diagnostic as core
import p43_bounded_zero_click_live_diagnostic_entry as legacy_integrated

P45_TESTED_COMMIT = "3dac7a9e2cbe4a23c3de44eb15cf45f19b136149"
P45_SOURCE_REL = "parallel/PYLAUNCH/wof_launcher/live_diagnostic_staging.py"
P45_SOURCE_BLOB = "752a172911d76eb3573684b200d597926c819716"
P45_P39_TESTED_COMMIT = "ac5387f00d8c2382dcf3ed435ffcfa0acc1a2f05"
P45_P42_TESTED_COMMIT = "7b523187a955179b04155b758847c82aaf569a0d"
P45_SCHEMA = "wof-alpha-p45-live-diagnostic-staging-v1"
P45_EXACT_FILES = {
    P45_SOURCE_REL: P45_SOURCE_BLOB,
    "parallel/PYLAUNCH/wof_launcher/auto_baseline_hud.py": "05a1a6e8632f62dac6ff9bedf8897b3f2df6e685",
    "parallel/AUTO_MARKER_BASELINE/native_marker_auto_acquisition_baseline.js": "2a0094b3588d4a27c8c7a6f9940b8a3b1941f8c4",
    "product/alpha/wof_alpha_auto_baseline_hud_adapter.js": "933f35389bfbd3337bde31906707919fd7a3f626",
    "product/alpha/wof_alpha_auto_baseline_visible_hud.js": "97b1ed594722a8539f21c76f7e44ec01e460ef26",
    "parallel/RENDER_AUTHORITY_V2/gstyphoon_renderer_submit_correlation_probe.js": "32b9c50e8a72de1a097b8ce5dc91b69bdcef0219",
}

P46_TESTED_COMMIT = "210efdda5bbf3715989c751eb90442f26f42d0a9"
P46_SOURCE_REL = "parallel/RENDER_AUTHORITY_V2/wasm_webgl_callsite_fingerprint_probe.js"
P46_SOURCE_BLOB = "efd71e25e28f171e080774eb5aa1309a0d7bbe2b"
P46_SCHEMA = "wof-wasm-webgl-callsite-fingerprint-probe-v1"
P46_INSTANCE_GLOBAL = "__WOF_P43_P46_CALLSITE_PROBE_V1__"
P46_START_IDENTITY_GLOBAL = "__WOF_P43_P46_START_IDENTITY_V1__"

P39_CLASSIFICATION = "UNVERIFIED_AUTO_BASELINE"
P42_SCHEMA = "wof-gstyphoon-renderer-correlation-probe-v1"
P42_CLASSIFICATION = "BOUNDED_LIVE_DIAGNOSTIC_MAPPING_ONLY"

DUPLICATE_CORE_GATES = {
    "CANDIDATE_BINDING",
    "DEDICATED_RUNTIME_ENVIRONMENT",
    "BROWSER_ENDPOINT",
    "PAGE_WORKER_WASM_ASSOCIATION",
    "P16_GATE",
    "ALPHA_LIVE_SAFETY",
}


class ContinuationError(RuntimeError):
    pass


class _UnusedRuntime:
    """P45 attach-only seam sentinel.

    P43 never asks P45 to recreate/rebind the maintained Alpha runtime. P43 calls
    only P45's exact diagnostic install/readout/teardown seam against the already
    P16-bound page. Any accidental production-runtime delegation fails closed.
    """

    def __getattr__(self, name: str) -> Any:
        raise ContinuationError(f"P43 P45 attach-only seam forbids runtime delegation: {name}")


def _same_binding(a: Mapping[str, Any] | None, b: Mapping[str, Any] | None) -> bool:
    if not isinstance(a, Mapping) or not isinstance(b, Mapping):
        return False
    return all(
        isinstance(a.get(key), str)
        and a.get(key)
        and a.get(key) == b.get(key)
        for key in ("runtimeEpoch", "rendererEpoch", "authorityKey")
    )


def dependency_pins() -> dict[str, Any]:
    return {
        "p45": {
            "testedCommit": P45_TESTED_COMMIT,
            "sourcePath": P45_SOURCE_REL,
            "sourceGitBlobSha": P45_SOURCE_BLOB,
            "p39TestedCommit": P45_P39_TESTED_COMMIT,
            "p42TestedCommit": P45_P42_TESTED_COMMIT,
            "exactFiles": dict(P45_EXACT_FILES),
        },
        "p46": {
            "testedCommit": P46_TESTED_COMMIT,
            "sourcePath": P46_SOURCE_REL,
            "sourceGitBlobSha": P46_SOURCE_BLOB,
        },
        "composition": {
            "installOrder": ["P45_P39", "P45_P42", "P46"],
            "webglWrapperStackTopToBottom": ["P46", "P45_P42", "ORIGINAL_RUNTIME_WEBGL"],
            "teardownOrder": ["P46", "P45_P42_AND_P39"],
            "selectionByTiming": False,
            "selectionByOrder": False,
            "selectionByNearest": False,
            "guessedWasmSymbol": False,
            "guessedWasmOffset": False,
        },
    }


def _write_bytes(path: Path, data: bytes) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {
        "path": str(path),
        "sha256": core.sha256_bytes(data),
        "gitBlobSha": core.git_blob_sha(data),
        "size": len(data),
    }


def materialize_exact_dependencies(args: Any) -> tuple[Path, Path, dict[str, Any]]:
    """Materialize only exact terminal-tested diagnostic dependency bytes.

    This is output-root-local materialization, not installation. Nothing is written
    to PATH, site-packages, the source checkout, the game runtime, or alpha-live.
    """
    git = core.GitReader(args.repo_root)
    root = args.output_root.expanduser().resolve() / "raw" / "exact_dependencies"
    p45_root = root / "P45" / P45_TESTED_COMMIT / "root"
    records: dict[str, Any] = {"p45": {}, "p46": {}}

    if not git.commit_exists(P45_TESTED_COMMIT):
        raise ContinuationError("P45 exact tested commit is not present locally; no implicit HEAD/fetch fallback")
    for rel, wanted_blob in P45_EXACT_FILES.items():
        data = git.read_blob(P45_TESTED_COMMIT, rel)
        actual_blob = core.git_blob_sha(data)
        if actual_blob != wanted_blob:
            raise ContinuationError(
                f"P45 exact dependency blob mismatch: {rel} expected={wanted_blob} actual={actual_blob}"
            )
        rec = _write_bytes(p45_root / rel, data)
        rec.update({"sourceCommit": P45_TESTED_COMMIT, "sourcePath": rel})
        records["p45"][rel] = rec

    if not git.commit_exists(P46_TESTED_COMMIT):
        raise ContinuationError("P46 exact tested commit is not present locally; no implicit HEAD/fetch fallback")
    p46_data = git.read_blob(P46_TESTED_COMMIT, P46_SOURCE_REL)
    actual_p46 = core.git_blob_sha(p46_data)
    if actual_p46 != P46_SOURCE_BLOB:
        raise ContinuationError(
            f"P46 exact dependency blob mismatch: expected={P46_SOURCE_BLOB} actual={actual_p46}"
        )
    p46_path = root / "P46" / P46_TESTED_COMMIT / P46_SOURCE_REL
    rec = _write_bytes(p46_path, p46_data)
    rec.update({"sourceCommit": P46_TESTED_COMMIT, "sourcePath": P46_SOURCE_REL})
    records["p46"][P46_SOURCE_REL] = rec
    records["pins"] = dependency_pins()
    return p45_root, p46_path, records


def _load_module_from_path(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ContinuationError(f"unable to load exact diagnostic module: {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@contextmanager
def exact_p45_module(args: Any, p45_root: Path) -> Iterator[Any]:
    """Load exact P39/P45 Python bytes inside the source checkout's wof_launcher package.

    P45's production runtime delegation is not used. Relative CDP imports resolve to
    the explicit source checkout while P39 and P45 implementation bytes themselves
    are the exact terminal-tested bytes materialized above.
    """
    pylaunch = (args.source_checkout.expanduser().resolve() / "parallel" / "PYLAUNCH").resolve()
    added = str(pylaunch)
    names = ("wof_launcher.auto_baseline_hud", "wof_launcher.live_diagnostic_staging")
    saved = {name: sys.modules.get(name) for name in names}
    sys.path.insert(0, added)
    try:
        package = importlib.import_module("wof_launcher")
        package_file = getattr(package, "__file__", None)
        if not isinstance(package_file, str) or pylaunch not in Path(package_file).resolve().parents:
            raise ContinuationError(
                f"wof_launcher package is not bound to explicit source checkout: {package_file!r}"
            )
        importlib.import_module("wof_launcher.cdp")
        p39_path = p45_root / "parallel" / "PYLAUNCH" / "wof_launcher" / "auto_baseline_hud.py"
        p45_path = p45_root / P45_SOURCE_REL
        _load_module_from_path("wof_launcher.auto_baseline_hud", p39_path)
        p45_module = _load_module_from_path("wof_launcher.live_diagnostic_staging", p45_path)
        if getattr(p45_module, "SCHEMA", None) != P45_SCHEMA:
            raise ContinuationError("exact P45 module schema mismatch after load")
        yield p45_module
    finally:
        for name, old in saved.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old
        try:
            sys.path.remove(added)
        except ValueError:
            pass


def validate_p45_readout(readout: Any, expected_binding: Mapping[str, Any]) -> tuple[bool, str]:
    if not isinstance(readout, Mapping) or readout.get("schema") != P45_SCHEMA:
        return False, "P45_READOUT_SCHEMA_INVALID"
    if readout.get("enabled") is not True:
        return False, "P45_STAGING_NOT_ENABLED"
    if not _same_binding(readout.get("binding"), expected_binding):
        return False, "P45_STALE_OR_MIXED_AUTHORITY_BINDING"
    p39 = readout.get("p39") if isinstance(readout.get("p39"), Mapping) else {}
    p42 = readout.get("p42") if isinstance(readout.get("p42"), Mapping) else {}
    if p39.get("classification") != P39_CLASSIFICATION:
        return False, "P45_P39_CLASSIFICATION_INVALID"
    if p39.get("testedCommit") != P45_P39_TESTED_COMMIT:
        return False, "P45_P39_TESTED_COMMIT_MISMATCH"
    if p42.get("classification") != P42_CLASSIFICATION or p42.get("testedCommit") != P45_P42_TESTED_COMMIT:
        return False, "P45_P42_IDENTITY_INVALID"
    bundle = p42.get("rawBundle")
    if not isinstance(bundle, Mapping) or bundle.get("schema") != P42_SCHEMA:
        return False, "P45_P42_RAW_BUNDLE_INVALID"
    if bundle.get("authorityEligible") is not False or not _same_binding(bundle.get("binding"), expected_binding):
        return False, "P45_P42_RAW_BUNDLE_AUTHORITY_OR_BINDING_INVALID"
    eligibility = readout.get("authorityEligibility") if isinstance(readout.get("authorityEligibility"), Mapping) else {}
    if any(value is not False for value in eligibility.values()):
        return False, "P45_AUTHORITY_BOUNDARY_INVALID"
    safety = readout.get("safety") if isinstance(readout.get("safety"), Mapping) else {}
    if safety.get("readOnly") is not True or safety.get("ramWrites") != 0 or safety.get("inputInjection") is not False:
        return False, "P45_SAFETY_BOUNDARY_INVALID"
    return True, "P45_P39_P42_BOUND_EXACT"


def validate_p46_bundle(bundle: Any, expected_binding: Mapping[str, Any]) -> tuple[bool, str]:
    if not isinstance(bundle, Mapping) or bundle.get("schema") != P46_SCHEMA:
        return False, "P46_BUNDLE_SCHEMA_INVALID"
    if bundle.get("mappingOnly") is not True or bundle.get("authorityEligible") is not False:
        return False, "P46_AUTHORITY_BOUNDARY_INVALID"
    if not _same_binding(bundle.get("binding"), expected_binding):
        return False, "P46_STALE_OR_MIXED_AUTHORITY_BINDING"
    if not isinstance(bundle.get("moduleSurfaceAtStart"), Mapping):
        return False, "P46_MODULE_IDENTITY_START_SNAPSHOT_MISSING"
    safety = bundle.get("safety") if isinstance(bundle.get("safety"), Mapping) else {}
    if safety.get("readOnly") is not True or safety.get("ramWrites") != 0 or safety.get("inputInjection") is not False:
        return False, "P46_SAFETY_BOUNDARY_INVALID"
    assessment = bundle.get("mappingAssessment") if isinstance(bundle.get("mappingAssessment"), Mapping) else {}
    forbidden_true = (
        assessment.get("selectionMade") is True
        or assessment.get("orderOnlySelection") is True
        or assessment.get("timingOnlySelection") is True
        or assessment.get("nearestSelection") is True
        or assessment.get("guessedWasmSymbol") is True
        or assessment.get("guessedWasmOffset") is True
    )
    if forbidden_true:
        return False, "P46_FORBIDDEN_MAPPING_SELECTION_OR_GUESS"

    allowed_wasm_status = {"AVAILABLE", "NOT_AVAILABLE"}
    allowed_truth = {"AVAILABLE", "NOT_AVAILABLE", "UNRESOLVED"}
    for index, event in enumerate(bundle.get("events") or []):
        if not isinstance(event, Mapping):
            return False, f"P46_EVENT_{index}_INVALID"
        callsite = event.get("callsite") if isinstance(event.get("callsite"), Mapping) else {}
        if callsite.get("rawStackStatus") not in {"AVAILABLE", "NOT_AVAILABLE"}:
            return False, f"P46_EVENT_{index}_RAW_STACK_TRUTH_STATE_INVALID"
        fp = callsite.get("normalizedCallsiteFingerprint") if isinstance(callsite.get("normalizedCallsiteFingerprint"), Mapping) else {}
        if fp.get("status") not in {"AVAILABLE", "NOT_AVAILABLE"}:
            return False, f"P46_EVENT_{index}_FINGERPRINT_TRUTH_STATE_INVALID"
        wasm = callsite.get("wasm") if isinstance(callsite.get("wasm"), Mapping) else {}
        if wasm.get("status") not in allowed_wasm_status:
            return False, f"P46_EVENT_{index}_WASM_TRUTH_STATE_INVALID"
        for field in ("functionIndexStatus", "functionNameStatus", "offsetStatus"):
            if wasm.get(field) not in allowed_truth:
                return False, f"P46_EVENT_{index}_{field}_INVALID"
        js = callsite.get("jsWrapperOrImport") if isinstance(callsite.get("jsWrapperOrImport"), Mapping) else {}
        if js.get("status") not in {"AVAILABLE", "NOT_AVAILABLE"}:
            return False, f"P46_EVENT_{index}_JS_WRAPPER_TRUTH_STATE_INVALID"
        if js.get("semanticRole") not in {"UNRESOLVED", None}:
            return False, f"P46_EVENT_{index}_JS_SEMANTIC_ROLE_WAS_GUESSED"
        module_surface = callsite.get("moduleSurface") if isinstance(callsite.get("moduleSurface"), Mapping) else {}
        for name in ("Module", "ModuleAsm"):
            item = module_surface.get(name) if isinstance(module_surface.get(name), Mapping) else {}
            if item.get("status") not in {"AVAILABLE", "NOT_AVAILABLE"}:
                return False, f"P46_EVENT_{index}_{name}_TRUTH_STATE_INVALID"
    return True, "P46_RAW_CALLSITE_BUNDLE_BOUND_EXACT"


def _p45_snapshot(staging: Any, readout: Any) -> dict[str, Any]:
    return {
        "internalState": getattr(staging, "_state", None),
        "internalReason": getattr(staging, "_reason", None),
        "pageTargetId": getattr(staging, "_page_target_id", None),
        "binding": dict(getattr(staging, "_binding", {}) or {}),
        "readout": readout,
        "testedCommit": P45_TESTED_COMMIT,
        "sourceGitBlobSha": P45_SOURCE_BLOB,
        "authorityEligible": False,
    }


def _p46_start_expression(binding: Mapping[str, Any]) -> str:
    template = """(()=>{
const binding=__P43_BINDING_JSON__;
const current=window.__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1;
if(!current||current.runtimeEpoch!==binding.runtimeEpoch||current.rendererEpoch!==binding.rendererEpoch||current.authorityKey!==binding.authorityKey)throw new Error('P43 P46 requires exact P45 diagnostic binding');
try{window.__WOF_P43_P46_CALLSITE_PROBE_V1__?.stop?.('P43_P46_REBIND');}catch(_){}
try{delete window.__WOF_P43_P46_CALLSITE_PROBE_V1__;}catch(_){}
try{delete window.__WOF_P43_P46_START_IDENTITY_V1__;}catch(_){}
const api=window.WOFWasmWebGLCallsiteFingerprintProbeP46;
if(!api||api.SCHEMA!=='wof-wasm-webgl-callsite-fingerprint-probe-v1'||typeof api.createProbe!=='function')throw new Error('P46 exact API unavailable after injection');
window.__WOF_P43_P46_START_IDENTITY_V1__={Module:window.Module??null,ModuleAsm:(window.Module&&(typeof window.Module==='object'||typeof window.Module==='function'))?(window.Module.asm??null):null,binding:Object.freeze({...binding})};
const probe=api.createProbe({root:window,gl:window.I_fdC8Q,bindingProvider:()=>window.__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1,strictModuleIdentity:true});
window.__WOF_P43_P46_CALLSITE_PROBE_V1__=probe;
return probe.start(binding);
})()"""
    return template.replace("__P43_BINDING_JSON__", json.dumps(dict(binding), separators=(",", ":")))


def _p46_stop_expression(binding: Mapping[str, Any], reason: str) -> str:
    template = """(()=>{
const expected=__P43_BINDING_JSON__;
const p=window.__WOF_P43_P46_CALLSITE_PROBE_V1__;
const start=window.__WOF_P43_P46_START_IDENTITY_V1__;
if(!p)return{present:false,reason:'P46_LIVE_INSTANCE_MISSING'};
const current=window.__WOF_P45_LIVE_DIAGNOSTIC_BINDING_V1;
if(!current||current.runtimeEpoch!==expected.runtimeEpoch||current.rendererEpoch!==expected.rendererEpoch||current.authorityKey!==expected.authorityKey){try{p.reject('STALE_OR_MIXED_AUTHORITY_BINDING');}catch(_){}}
const currentAsm=(window.Module&&(typeof window.Module==='object'||typeof window.Module==='function'))?(window.Module.asm??null):null;
if((start&&(window.Module??null)!==start.Module)||(start&&currentAsm!==start.ModuleAsm)){try{p.reject('MODULE_OR_ASM_IDENTITY_CHANGED');}catch(_){}}
let stop=null;try{stop=p.stop(__P43_REASON_JSON__);}catch(ex){stop={error:String(ex&&ex.stack||ex)}}
let bundle=null;try{bundle=p.result();}catch(ex){return{present:true,stop,error:String(ex&&ex.stack||ex),bundle:null}}
try{delete window.__WOF_P43_P46_CALLSITE_PROBE_V1__;}catch(_){}
try{delete window.__WOF_P43_P46_START_IDENTITY_V1__;}catch(_){}
return{present:true,stop,bundle};
})()"""
    return template.replace("__P43_BINDING_JSON__", json.dumps(dict(binding), separators=(",", ":"))).replace("__P43_REASON_JSON__", json.dumps(str(reason)))


def _start_p46(client: Any, page_target_id: str, p46_source: str, binding: Mapping[str, Any]) -> dict[str, Any]:
    session = client.attach(page_target_id)
    try:
        session.request("Runtime.enable")
        session.evaluate(f"(0,eval)({json.dumps(p46_source)});true", timeout=15.0)
        bundle = session.evaluate(_p46_start_expression(binding), timeout=10.0)
        ok, reason = validate_p46_bundle(bundle, binding)
        return {
            "state": "P46_CALLSITE_PROBE_STARTED" if ok else "P46_CALLSITE_PROBE_REJECTED",
            "present": True,
            "reason": reason,
            "testedCommit": P46_TESTED_COMMIT,
            "testedBlob": P46_SOURCE_BLOB,
            "bundle": bundle,
        }
    except Exception as exc:
        return {
            "state": "P46_CALLSITE_PROBE_NOT_PRESENT",
            "present": False,
            "reason": f"P46_START_FAILED:{type(exc).__name__}:{exc}",
            "testedCommit": P46_TESTED_COMMIT,
            "testedBlob": P46_SOURCE_BLOB,
        }
    finally:
        try:
            session.close()
        except Exception:
            pass


def _stop_p46(client: Any, page_target_id: str, binding: Mapping[str, Any], reason: str) -> dict[str, Any]:
    session = client.attach(page_target_id)
    try:
        session.request("Runtime.enable")
        raw = session.evaluate(_p46_stop_expression(binding, reason), timeout=12.0)
        if not isinstance(raw, Mapping) or raw.get("present") is not True:
            return {
                "state": "P46_CALLSITE_PROBE_NOT_PRESENT",
                "present": False,
                "reason": (raw or {}).get("reason") if isinstance(raw, Mapping) else "P46_FINAL_READBACK_INVALID",
                "raw": raw,
            }
        bundle = raw.get("bundle")
        ok, validation_reason = validate_p46_bundle(bundle, binding)
        state = "P46_CALLSITE_BUNDLE_PRESENT"
        if not ok:
            state = "P46_CALLSITE_BUNDLE_REJECTED"
        elif isinstance(bundle, Mapping) and bundle.get("state") == "REJECTED":
            state = "P46_CALLSITE_BUNDLE_REJECTED"
            validation_reason = str(bundle.get("reason") or validation_reason)
        return {
            "state": state,
            "present": True,
            "reason": validation_reason,
            "testedCommit": P46_TESTED_COMMIT,
            "testedBlob": P46_SOURCE_BLOB,
            "stop": raw.get("stop"),
            "bundle": bundle,
            "authorityEligible": False,
        }
    except Exception as exc:
        return {
            "state": "P46_CALLSITE_PROBE_NOT_PRESENT",
            "present": False,
            "reason": f"P46_FINAL_READBACK_FAILED:{type(exc).__name__}:{exc}",
        }
    finally:
        try:
            session.close()
        except Exception:
            pass


def _first_failure(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((row for row in rows if row.get("state") in {"FAIL", "BLOCKED"}), None)


def _passed_before(rows: list[dict[str, Any]], first: Mapping[str, Any] | None) -> list[str]:
    ceiling = int(first.get("seq")) if isinstance(first, Mapping) else 10**18
    out: list[str] = []
    for row in rows:
        if int(row.get("seq") or 0) >= ceiling:
            break
        if row.get("state") == "PASS" and row.get("gate") not in out:
            out.append(str(row.get("gate")))
    return out


def _resequence(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for seq, row in enumerate(rows, start=1):
        item = dict(row)
        item["seq"] = seq
        out.append(item)
    return out


def merge_gate_timelines(pre_rows: list[dict[str, Any]], core_rows: list[dict[str, Any]], post_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept_core = [row for row in core_rows if row.get("gate") not in DUPLICATE_CORE_GATES]
    duplicate_latest: dict[str, str] = {}
    duplicate_reason: dict[str, Any] = {}
    for row in core_rows:
        gate = str(row.get("gate") or "")
        if gate in DUPLICATE_CORE_GATES and gate != "ALPHA_LIVE_SAFETY":
            duplicate_latest[gate] = str(row.get("state"))
            duplicate_reason[gate] = row.get("reason")
    required = ["CANDIDATE_BINDING", "DEDICATED_RUNTIME_ENVIRONMENT", "BROWSER_ENDPOINT", "PAGE_WORKER_WASM_ASSOCIATION", "P16_GATE"]
    reconfirm_ok = all(duplicate_latest.get(gate) == "PASS" for gate in required)
    reconfirm = {
        "atUtc": core.utc_now(),
        "gate": "CORE_RECONFIRMATION",
        "state": "PASS" if reconfirm_ok else "FAIL",
        "reason": "CORE_RECONFIRMED_PREBOUND_CONTEXT" if reconfirm_ok else "CORE_CONTEXT_DRIFT_OR_RECONFIRMATION_FAILURE",
        "detail": {"states": duplicate_latest, "reasons": duplicate_reason},
    }
    return _resequence([*pre_rows, reconfirm, *kept_core, *post_rows])


def _p42_from_p45(p45_final: Mapping[str, Any] | None) -> dict[str, Any]:
    readout = p45_final.get("readout") if isinstance(p45_final, Mapping) and isinstance(p45_final.get("readout"), Mapping) else {}
    p42 = readout.get("p42") if isinstance(readout.get("p42"), Mapping) else {}
    raw = p42.get("rawBundle")
    if not isinstance(raw, Mapping) or raw.get("schema") != P42_SCHEMA:
        return {
            "state": "P42_CORRELATION_PROBE_NOT_PRESENT",
            "present": False,
            "reason": "P45_P42_RAW_BUNDLE_NOT_AVAILABLE",
            "testedCommit": P45_P42_TESTED_COMMIT,
            "authorityEligible": False,
        }
    return {
        "state": "P42_CORRELATION_PROBE_PRESENT",
        "present": True,
        "classification": P42_CLASSIFICATION,
        "testedCommit": P45_P42_TESTED_COMMIT,
        "bundle": raw,
        "sealReason": p42.get("sealReason"),
        "teardown": p42.get("teardown"),
        "authorityEligible": False,
    }


def build_human_receipt(receipt: Mapping[str, Any]) -> str:
    base = core.build_human_receipt(receipt).rstrip()
    p45 = receipt.get("p45") if isinstance(receipt.get("p45"), Mapping) else {}
    p46 = receipt.get("p46") if isinstance(receipt.get("p46"), Mapping) else {}
    binding = receipt.get("diagnosticBinding") if isinstance(receipt.get("diagnosticBinding"), Mapping) else {}
    extra = [
        "",
        "## Post-P45/P46 convergence",
        "",
        f"- P45 tested commit: `{P45_TESTED_COMMIT}`",
        f"- P45 state/reason: `{p45.get('internalState')}` / `{p45.get('internalReason')}`",
        f"- P46 tested commit: `{P46_TESTED_COMMIT}`",
        f"- P46 state/reason: `{p46.get('state')}` / `{p46.get('reason')}`",
        f"- Shared diagnostic binding: runtimeEpoch=`{binding.get('runtimeEpoch')}`, rendererEpoch=`{binding.get('rendererEpoch')}`, authorityKey=`{binding.get('authorityKey')}`",
        "- Wrapper install order: `P45 P39 -> P45 P42 -> P46`",
        "- Wrapper teardown order: `P46 -> P45 P42/P39`",
        "- P46 raw WASM truth states are preserved as observed: AVAILABLE / NOT_AVAILABLE / UNRESOLVED; no symbol or offset guessing is performed.",
        "",
    ]
    return base + "\n" + "\n".join(extra)


def _persist_receipt(args: Any, receipt: dict[str, Any], bound_raw: Mapping[str, Any]) -> dict[str, Any]:
    root = args.output_root.expanduser().resolve()
    artifacts = dict(receipt.get("artifacts") or {})
    artifacts.pop("receipt", None)
    artifacts.pop("humanReceipt", None)
    if bound_raw:
        receipt["candidateBindingRaw"] = dict(bound_raw)
        artifacts["candidateBindingRaw"] = dict(bound_raw)
    receipt["artifacts"] = artifacts
    receipt_path = root / "P43_DIAGNOSTIC_RECEIPT.json"
    human_path = root / "P43_DIAGNOSTIC_RECEIPT.md"
    receipt["receiptPath"] = str(receipt_path)
    receipt["humanReceiptPath"] = str(human_path)
    receipt_path.write_bytes(core.pretty_bytes(receipt))
    human_path.write_bytes(build_human_receipt(receipt).encode("utf-8"))
    return {
        "receiptPath": str(receipt_path),
        "receiptSha256": core.sha256_bytes(receipt_path.read_bytes()),
        "humanReceiptPath": str(human_path),
        "humanReceiptSha256": core.sha256_bytes(human_path.read_bytes()),
    }


def _add_error(errors: list[dict[str, Any]], where: str, exc: BaseException) -> None:
    errors.append({
        "atUtc": core.utc_now(),
        "where": where,
        "type": type(exc).__name__,
        "message": str(exc),
        "repr": repr(exc),
        "traceback": traceback.format_exc(),
    })


def run(args: Any) -> tuple[dict[str, Any], int, dict[str, Any]]:
    output = args.output_root.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    pre = core.GateLedger()
    post = core.GateLedger()
    wrapper_errors: list[dict[str, Any]] = []
    metadata_git = core.GitReader(args.repo_root)
    alpha_before = {"local": metadata_git.rev("refs/heads/alpha-live"), "remote": metadata_git.rev("refs/remotes/origin/alpha-live")}

    binding: dict[str, Any] = {}
    association: dict[str, Any] = {}
    identity: dict[str, Any] = {}
    environment: dict[str, Any] | None = None
    dependency_records: dict[str, Any] = {}
    p45_start: dict[str, Any] = {"state": "P45_NOT_STARTED", "internalReason": "NOT_REACHED", "readout": None}
    p45_final: dict[str, Any] = dict(p45_start)
    p46_start: dict[str, Any] = {"state": "P46_CALLSITE_PROBE_NOT_PRESENT", "present": False, "reason": "NOT_REACHED"}
    p46_final: dict[str, Any] = dict(p46_start)
    client = None
    staging = None
    module_context = None
    source_path_added: str | None = None
    p46_source = ""

    pre.transition("CANDIDATE_BINDING", "PENDING", "VERIFYING_EXACT_METADATA_SOURCE_AND_CHECKOUT")
    try:
        binding = core.verify_candidate_binding(
            metadata_git,
            metadata_commit=args.metadata_commit,
            source_commit=args.source_commit,
            pointer_path=args.pointer,
            provenance_path=args.provenance,
        )
        binding["sourceCheckout"] = core.verify_source_checkout(args.source_checkout, args.source_commit)
        pre.transition("CANDIDATE_BINDING", "PASS", "EXACT_CANDIDATE_METADATA_SOURCE_AND_CHECKOUT_BOUND")
    except Exception as exc:
        _add_error(wrapper_errors, "CANDIDATE_BINDING", exc)
        pre.transition("CANDIDATE_BINDING", "FAIL", str(exc))

    pre.transition("DEDICATED_RUNTIME_ENVIRONMENT", "PENDING", "VERIFYING_EXISTING_WOF_VENV_NO_INSTALL")
    if pre.latest().get("CANDIDATE_BINDING") == "PASS":
        try:
            environment = core.verify_dedicated_python()
            pre.transition("DEDICATED_RUNTIME_ENVIRONMENT", "PASS", "EXISTING_WOF_DEDICATED_VENV_CONFIRMED", environment)
        except Exception as exc:
            _add_error(wrapper_errors, "DEDICATED_RUNTIME_ENVIRONMENT", exc)
            pre.transition("DEDICATED_RUNTIME_ENVIRONMENT", "FAIL", str(exc))
    else:
        pre.transition("DEDICATED_RUNTIME_ENVIRONMENT", "SKIPPED", "NOT_REACHED_AFTER_CANDIDATE_FAILURE")

    try:
        if pre.latest().get("DEDICATED_RUNTIME_ENVIRONMENT") == "PASS":
            pre.transition("BROWSER_ENDPOINT", "PENDING", "CONNECTING_EXISTING_DEDICATED_BROWSER")
            if not args.browser_websocket_url:
                raise ContinuationError("explicit browser WebSocket URL required; P43 never launches a browser")
            pylaunch = (args.source_checkout.expanduser().resolve() / "parallel" / "PYLAUNCH").resolve()
            source_path_added = str(pylaunch)
            sys.path.insert(0, source_path_added)
            from wof_launcher.cdp import CdpClient
            from wof_launcher.discovery_v2 import discover

            client = CdpClient(args.browser_websocket_url, timeout=min(5.0, args.duration))
            client.connect()
            pre.transition("BROWSER_ENDPOINT", "PASS", "EXISTING_BROWSER_CONNECTED_READ_ONLY")

            pre.transition("PAGE_WORKER_WASM_ASSOCIATION", "PENDING", "RUNNING_P31_AUTHORITATIVE_DISCOVERY")
            choice = discover(client, identity_timeout=min(20.0, max(2.0, args.duration / 2)))
            if not choice.page or not choice.worker or not choice.identity or choice.identity.get("ok") is not True:
                raise ContinuationError(choice.reason or "authoritative Page/Worker/WASM association unavailable")
            association = {
                "pageTargetId": choice.page.get("targetId"),
                "workerTargetId": choice.worker.get("targetId"),
                "worldIdentity": choice.identity,
                "authorityPath": (choice.diagnostics or {}).get("path"),
            }
            pre.transition("PAGE_WORKER_WASM_ASSOCIATION", "PASS", "UNIQUE_AUTHORITATIVE_PAGE_WORKER_WASM_ASSOCIATION", association)

            pre.transition("P16_GATE", "PENDING", "VERIFYING_EXACT_P16_BINDING_BEFORE_DIAGNOSTIC_WRAPPERS")
            p16_raw, p16_error = core._load_optional_json(args.p16_evidence)
            if p16_raw is None:
                pre.transition("P16_GATE", "BLOCKED", f"P16_EVIDENCE_{p16_error}")
            else:
                ok, reason, identity = core.validate_p16(p16_raw, binding, association)
                pre.transition("P16_GATE", "PASS" if ok else "FAIL", reason, identity or p16_raw.get("canonical"))

            if pre.latest().get("P16_GATE") == "PASS":
                p45_root, p46_path, dependency_records = materialize_exact_dependencies(args)
                p46_source = p46_path.read_text(encoding="utf-8")
                module_context = exact_p45_module(args, p45_root)
                p45_module = module_context.__enter__()
                staging = p45_module.P45LiveDiagnosticStagingRuntime(
                    p45_root,
                    enabled=True,
                    runtime=_UnusedRuntime(),
                    renderer_epoch_factory=lambda: str(identity["rendererEpoch"]),
                )

                pre.transition("P45_STAGING_GATE", "PENDING", "INSTALLING_EXACT_P45_P39_THEN_P42_ATTACH_ONLY")
                try:
                    staging._install(
                        client,
                        str(association["pageTargetId"]),
                        str(identity["runtimeEpoch"]),
                        str(identity["authorityKey"]),
                    )
                    readout = staging.live_diagnostic_readout()
                    p45_start = _p45_snapshot(staging, readout)
                    ok, reason = validate_p45_readout(readout, identity)
                    internal_rejected = p45_start.get("internalState") == "REJECTED"
                    pre.transition(
                        "P45_STAGING_GATE",
                        "PASS" if ok and not internal_rejected else "FAIL",
                        p45_start.get("internalReason") if internal_rejected else reason,
                        {"binding": p45_start.get("binding"), "testedCommit": P45_TESTED_COMMIT},
                    )
                except Exception as exc:
                    _add_error(wrapper_errors, "P45_STAGING_GATE", exc)
                    p45_start = {"state": "P45_INSTALL_FAILED", "internalReason": str(exc), "readout": None}
                    pre.transition("P45_STAGING_GATE", "FAIL", str(exc))

                pre.transition("P46_CALLSITE_GATE", "PENDING", "INSTALLING_EXACT_P46_ABOVE_P45_P42_WRAPPER")
                if pre.latest().get("P45_STAGING_GATE") == "PASS":
                    p46_start = _start_p46(
                        client,
                        str(association["pageTargetId"]),
                        p46_source,
                        identity,
                    )
                    start_bundle = p46_start.get("bundle")
                    ok, reason = validate_p46_bundle(start_bundle, identity) if isinstance(start_bundle, Mapping) else (False, str(p46_start.get("reason")))
                    pre.transition("P46_CALLSITE_GATE", "PASS" if ok else "FAIL", reason, {"testedCommit": P46_TESTED_COMMIT, "testedBlob": P46_SOURCE_BLOB})
                else:
                    pre.transition("P46_CALLSITE_GATE", "SKIPPED", "P45_STAGING_GATE_DID_NOT_PASS")
            else:
                pre.transition("P45_STAGING_GATE", "SKIPPED", "P16_GATE_DID_NOT_PASS")
                pre.transition("P46_CALLSITE_GATE", "SKIPPED", "P16_GATE_DID_NOT_PASS")
        else:
            for gate in ("BROWSER_ENDPOINT", "PAGE_WORKER_WASM_ASSOCIATION", "P16_GATE", "P45_STAGING_GATE", "P46_CALLSITE_GATE"):
                pre.transition(gate, "SKIPPED", "NOT_REACHED_AFTER_PRECONDITION_FAILURE")
    except Exception as exc:
        _add_error(wrapper_errors, "P43_CONTINUATION_SETUP", exc)
        latest = pre.latest()
        pending = next((gate for gate in ("BROWSER_ENDPOINT", "PAGE_WORKER_WASM_ASSOCIATION", "P16_GATE", "P45_STAGING_GATE", "P46_CALLSITE_GATE") if latest.get(gate) == "PENDING"), None)
        if pending:
            pre.transition(pending, "FAIL", str(exc))
        for gate in ("BROWSER_ENDPOINT", "PAGE_WORKER_WASM_ASSOCIATION", "P16_GATE", "P45_STAGING_GATE", "P46_CALLSITE_GATE"):
            if gate not in pre.latest():
                pre.transition(gate, "SKIPPED", "NOT_REACHED_AFTER_SETUP_FAILURE")

    core_receipt: dict[str, Any]
    core_rc: int
    try:
        core_receipt, core_rc = core.run_live_diagnostic(args)
    except Exception as exc:
        _add_error(wrapper_errors, "CORE_RUN", exc)
        core_receipt = {
            "schema": core.RECEIPT_SCHEMA,
            "version": 2,
            "candidateBinding": binding,
            "authoritativeAssociation": association,
            "runtimeAuthority": identity,
            "gateTimeline": [],
            "artifacts": {},
            "errors": [],
            "safety": dict(core.SAFETY),
        }
        core_rc = 2

    try:
        if client is not None and p46_start.get("present") is True and association.get("pageTargetId") and identity:
            p46_final = _stop_p46(
                client,
                str(association["pageTargetId"]),
                identity,
                "P43_FINAL_LIFO_TEARDOWN",
            )
            bundle = p46_final.get("bundle")
            ok, reason = validate_p46_bundle(bundle, identity) if isinstance(bundle, Mapping) else (False, str(p46_final.get("reason")))
            conflicts = ((bundle or {}).get("teardown") or {}).get("conflicts") if isinstance(bundle, Mapping) else None
            rejected = isinstance(bundle, Mapping) and bundle.get("state") == "REJECTED"
            post.transition(
                "P46_TEARDOWN",
                "PASS" if ok and not rejected and not conflicts else ("FAIL" if rejected or not ok else "BLOCKED"),
                str((bundle or {}).get("reason") if rejected and isinstance(bundle, Mapping) else ("P46_TEARDOWN_CONFLICT" if conflicts else reason)),
                {"conflicts": conflicts, "testedCommit": P46_TESTED_COMMIT},
            )
        else:
            post.transition("P46_TEARDOWN", "SKIPPED", "P46_WAS_NOT_STARTED")
    except Exception as exc:
        _add_error(wrapper_errors, "P46_TEARDOWN", exc)
        post.transition("P46_TEARDOWN", "FAIL", str(exc))

    try:
        if staging is not None:
            readout = staging.stop_live_diagnostic("P43_FINAL_LIFO_TEARDOWN")
            p45_final = _p45_snapshot(staging, readout)
            ok, reason = validate_p45_readout(readout, identity) if identity else (False, "P16_BINDING_UNAVAILABLE")
            internal_rejected = p45_final.get("internalState") == "REJECTED"
            post.transition(
                "P45_TEARDOWN",
                "PASS" if ok and not internal_rejected else "FAIL",
                str(p45_final.get("internalReason") if internal_rejected else reason),
                {"testedCommit": P45_TESTED_COMMIT},
            )
        else:
            post.transition("P45_TEARDOWN", "SKIPPED", "P45_WAS_NOT_STARTED")
    except Exception as exc:
        _add_error(wrapper_errors, "P45_TEARDOWN", exc)
        post.transition("P45_TEARDOWN", "FAIL", str(exc))
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
        if module_context is not None:
            try:
                module_context.__exit__(None, None, None)
            except Exception as exc:
                _add_error(wrapper_errors, "P45_MODULE_CONTEXT_RESTORE", exc)
        if source_path_added is not None:
            while source_path_added in sys.path:
                try:
                    sys.path.remove(source_path_added)
                except ValueError:
                    break

    alpha_after = {"local": metadata_git.rev("refs/heads/alpha-live"), "remote": metadata_git.rev("refs/remotes/origin/alpha-live")}
    alpha_moved = alpha_before != alpha_after
    post.transition(
        "ALPHA_LIVE_SAFETY",
        "FAIL" if alpha_moved else "PASS",
        "ALPHA_LIVE_REF_CHANGED_DURING_CAPTURE" if alpha_moved else "ALPHA_LIVE_UNCHANGED",
        {"before": alpha_before, "after": alpha_after},
    )

    merged_rows = merge_gate_timelines(pre.rows, list(core_receipt.get("gateTimeline") or []), post.rows)
    first = _first_failure(merged_rows)
    core_receipt["gateTimeline"] = merged_rows
    latest: dict[str, str] = {}
    for row in merged_rows:
        latest[str(row.get("gate"))] = str(row.get("state"))
    core_receipt["gateLatestState"] = latest
    core_receipt["firstFailingGate"] = first
    core_receipt["passedBeforeFirstFailure"] = _passed_before(merged_rows, first)

    p42_final = _p42_from_p45(p45_final)
    p39_readout = p45_final.get("readout") if isinstance(p45_final.get("readout"), Mapping) else {}
    p39 = p39_readout.get("p39") if isinstance(p39_readout.get("p39"), Mapping) else {}
    p46_bundle = p46_final.get("bundle") if isinstance(p46_final.get("bundle"), Mapping) else None
    core_receipt["p45"] = p45_final
    core_receipt["p42"] = p42_final
    core_receipt["p37p39"] = {
        "classification": P39_CLASSIFICATION,
        "testedCommit": P45_P39_TESTED_COMMIT,
        "status": p39.get("status"),
        "lifecycle": p39.get("lifecycle"),
        "authorityEligible": False,
        "source": "EXACT_P45_STAGING_READOUT",
    }
    core_receipt["p46"] = p46_final
    core_receipt["diagnosticBinding"] = {
        "runtimeEpoch": identity.get("runtimeEpoch"),
        "rendererEpoch": identity.get("rendererEpoch"),
        "authorityKey": identity.get("authorityKey"),
        "p45Matches": _same_binding((p45_final.get("readout") or {}).get("binding") if isinstance(p45_final.get("readout"), Mapping) else None, identity),
        "p42Matches": _same_binding((p42_final.get("bundle") or {}).get("binding") if isinstance(p42_final.get("bundle"), Mapping) else None, identity),
        "p46Matches": _same_binding(p46_bundle.get("binding") if isinstance(p46_bundle, Mapping) else None, identity),
    }
    core_receipt["dependencyPins"] = dependency_pins()
    core_receipt["wrapperComposition"] = dependency_pins()["composition"]
    core_receipt["continuationAuthority"] = {
        "prompt": "parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P43_POST_P45_P46_CONTINUATION_PROMPT.md",
        "claimToken": "9b45b04fc8f5e86849c08c07dcf0dc07",
        "p45ConsumedNotReimplemented": True,
        "p46ExactTestedBytesConsumed": True,
        "authorityChanged": False,
    }
    core_receipt.setdefault("errors", []).extend(wrapper_errors)
    core_receipt["safety"] = {
        **dict(core_receipt.get("safety") or {}),
        "readOnly": True,
        "ramWrites": 0,
        "inputInjection": False,
        "alphaLiveMoved": alpha_moved,
        "promotionPerformed": False,
        "realGameLaunchedByHarness": False,
        "installPerformed": False,
        "globalEnvironmentChanged": False,
        "p45RuntimeReboundByContinuation": False,
    }
    core_receipt["realWofAcceptance"] = "NOT_RUN_BY_P43_CONTINUATION_TASK"
    core_receipt["ownerVisualAcceptance"] = "NOT_RUN"
    core_receipt["promotionPerformed"] = False

    artifacts = dict(core_receipt.get("artifacts") or {})
    artifacts["p45Readout"] = core._write_artifact(output, "raw/P45_P39_P42_STAGING_READOUT.json", p45_final)
    artifacts["p42Correlation"] = core._write_artifact(output, "raw/P42_CORRELATION_BUNDLE.json", p42_final)
    artifacts["p46Callsite"] = core._write_artifact(output, "raw/P46_WASM_WEBGL_CALLSITE_BUNDLE.json", p46_final)
    artifacts["exactDependencies"] = core._write_artifact(output, "raw/EXACT_DIAGNOSTIC_DEPENDENCIES.json", dependency_records or {"pins": dependency_pins(), "state": "NOT_MATERIALIZED"})
    artifacts["gateTimeline"] = core._write_artifact(output, "raw/GATE_TRANSITION_TIMELINE.json", merged_rows)
    artifacts["continuationErrors"] = core._write_artifact(output, "raw/POST_P45_P46_ERRORS.json", wrapper_errors)
    core_receipt["artifacts"] = artifacts

    bound_raw: dict[str, Any] = {}
    try:
        bound_raw = legacy_integrated._raw_binding_artifacts(args, core_receipt.get("candidateBinding") or {})
    except Exception as exc:
        _add_error(wrapper_errors, "CANDIDATE_BINDING_RAW_ARCHIVE", exc)
        core_receipt["errors"] = list(core_receipt.get("errors") or []) + [wrapper_errors[-1]]

    stable = _persist_receipt(args, core_receipt, bound_raw)
    rc = 0 if first is None and not alpha_moved else 2
    if core_rc != 0 and first is None:
        rc = core_rc
    return core_receipt, rc, stable


def main(argv: Sequence[str] | None = None) -> int:
    args = core._parser().parse_args(argv)
    if not (0.1 <= args.duration <= 60.0):
        raise SystemExit("--duration must be in [0.1, 60] seconds")
    receipt, rc, stable = run(args)
    first = receipt.get("firstFailingGate")
    print(f"receipt={stable.get('receiptPath')}")
    print(f"receiptSha256={stable.get('receiptSha256')}")
    print(f"humanReceipt={stable.get('humanReceiptPath')}")
    print(f"humanReceiptSha256={stable.get('humanReceiptSha256')}")
    print(f"firstFailingGate={first.get('gate') if isinstance(first, Mapping) else 'NONE'}")
    print("passedBeforeFirstFailure=" + ",".join(receipt.get("passedBeforeFirstFailure") or []))
    print(f"p45={((receipt.get('p45') or {}).get('internalState'))}")
    print(f"p42={((receipt.get('p42') or {}).get('state'))}")
    print(f"p46={((receipt.get('p46') or {}).get('state'))}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
