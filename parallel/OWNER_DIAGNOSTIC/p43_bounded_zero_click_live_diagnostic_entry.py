from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

import p43_bounded_zero_click_live_diagnostic as core

P42_TESTED_COMMIT = "7b523187a955179b04155b758847c82aaf569a0d"
P42_REL = "parallel/RENDER_AUTHORITY_V2/gstyphoon_renderer_submit_correlation_probe.js"
P42_TESTED_BLOB = "32b9c50e8a72de1a097b8ce5dc91b69bdcef0219"
P42_INSTANCE_GLOBAL = "WOFP43P42CORRELATIONPROBE"


def _raw_binding_artifacts(args: Any, binding: Mapping[str, Any]) -> dict[str, Any]:
    """Archive exact metadata bytes already accepted by the core binding gate."""
    if binding.get("state") != "PASS":
        return {}
    git = core.GitReader(args.repo_root)
    metadata_commit = str(binding["metadataCommit"])
    out_root = args.output_root.expanduser().resolve()
    records: dict[str, Any] = {}
    for name in ("pointer", "provenance", "candidate", "attestation", "manifest"):
        descriptor = binding.get(name)
        if not isinstance(descriptor, Mapping):
            raise core.DiagnosticError(f"accepted binding descriptor missing: {name}")
        rel = descriptor.get("path")
        if not isinstance(rel, str) or not rel:
            raise core.DiagnosticError(f"accepted binding path missing: {name}")
        data = git.read_blob(metadata_commit, rel)
        sha = core.sha256_bytes(data)
        blob = core.git_blob_sha(data)
        if sha != descriptor.get("sha256") or blob != descriptor.get("gitBlobSha"):
            raise core.DiagnosticError(f"accepted binding bytes changed during archive: {name}")
        dest = out_root / "raw" / "candidate_binding" / f"{name.upper()}.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        records[name] = {
            "sourcePath": rel,
            "path": str(dest),
            "sha256": sha,
            "gitBlobSha": blob,
            "size": len(data),
            "metadataCommit": metadata_commit,
        }
    return records


def _p16_binding(args: Any) -> tuple[dict[str, str] | None, str | None]:
    raw, error = core._load_optional_json(args.p16_evidence)
    if raw is None:
        return None, error
    runtime = raw.get("runtime") if isinstance(raw.get("runtime"), Mapping) else {}
    world = raw.get("world") if isinstance(raw.get("world"), Mapping) else {}
    values = {
        "runtimeEpoch": runtime.get("epoch"),
        "rendererEpoch": runtime.get("rendererEpoch"),
        "authorityKey": runtime.get("authorityKey"),
        "pageTargetId": world.get("pageTargetId"),
    }
    if not all(isinstance(values[k], str) and values[k] for k in values):
        return None, "P16_EXACT_P42_BINDING_INCOMPLETE"
    return values, None


def _start_p42(args: Any) -> dict[str, Any]:
    """Install exact tested P42 on the P16-bound Page before the core capture."""
    identity, reason = _p16_binding(args)
    if identity is None:
        return {"state": "P42_CORRELATION_PROBE_NOT_PRESENT", "present": False, "reason": reason, "testedCommit": P42_TESTED_COMMIT}
    git = core.GitReader(args.repo_root)
    if not git.commit_exists(P42_TESTED_COMMIT):
        return {"state": "P42_CORRELATION_PROBE_NOT_PRESENT", "present": False, "reason": "P42_EXACT_TESTED_COMMIT_NOT_PRESENT_LOCALLY", "testedCommit": P42_TESTED_COMMIT}
    data = git.read_blob(P42_TESTED_COMMIT, P42_REL)
    actual_blob = core.git_blob_sha(data)
    if actual_blob != P42_TESTED_BLOB:
        raise core.DiagnosticError(f"P42 exact blob mismatch: expected={P42_TESTED_BLOB} actual={actual_blob}")

    pylaunch = args.source_checkout.expanduser().resolve() / "parallel" / "PYLAUNCH"
    before = list(sys.path)
    sys.path.insert(0, str(pylaunch))
    client = None
    session = None
    try:
        from wof_launcher.cdp import CdpClient
        client = CdpClient(args.browser_websocket_url, timeout=min(5.0, args.duration))
        client.connect()
        session = client.attach(identity["pageTargetId"])
        session.request("Runtime.enable")
        source = data.decode("utf-8")
        session.evaluate(f"(0,eval)({json.dumps(source)}); true", timeout=15.0)
        binding = {k: identity[k] for k in ("runtimeEpoch", "rendererEpoch", "authorityKey")}
        expression = """(()=>{
const api=globalThis.WOFGStyphoonRendererCorrelationProbeP42;
if(!api||api.schema!=='wof-gstyphoon-renderer-correlation-probe-v1'||typeof api.createProbe!=='function')throw new Error('P42 exact API unavailable after injection');
try{globalThis.WOFP43P42CORRELATIONPROBE?.stop?.('P43_RESTART_BEFORE_CAPTURE');}catch(_){}
const probe=api.createProbe({root:globalThis,gl:globalThis.I_fdC8Q,baselineProvider:now=>{try{return globalThis.WOFALPHAAUTOBASELINEHUD?.status?.(now)||null;}catch(_){return null;}}});
globalThis.WOFP43P42CORRELATIONPROBE=probe;
try{delete globalThis.WOFGStyphoonRendererCorrelationProbeP42;}catch(_){globalThis.WOFGStyphoonRendererCorrelationProbeP42=null;}
return probe.start(BINDING);
})()""".replace("BINDING", json.dumps(binding, separators=(",", ":")))
        status = session.evaluate(expression, timeout=10.0)
        return {
            "state": "P42_CORRELATION_PROBE_STARTED",
            "present": True,
            "testedCommit": P42_TESTED_COMMIT,
            "testedBlob": P42_TESTED_BLOB,
            "sourcePath": P42_REL,
            "pageTargetId": identity["pageTargetId"],
            "binding": binding,
            "startStatus": status,
        }
    except Exception as exc:
        return {
            "state": "P42_CORRELATION_PROBE_NOT_PRESENT",
            "present": False,
            "reason": f"P42_START_FAILED:{type(exc).__name__}:{exc}",
            "testedCommit": P42_TESTED_COMMIT,
            "testedBlob": P42_TESTED_BLOB,
        }
    finally:
        if session is not None:
            try:
                session.close()
            except Exception:
                pass
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
        sys.path[:] = before


def _stop_p42(args: Any, page_target_id: str | None) -> dict[str, Any]:
    if not isinstance(page_target_id, str) or not page_target_id:
        return {"state": "P42_CORRELATION_PROBE_NOT_PRESENT", "present": False, "reason": "P42_PAGE_TARGET_UNAVAILABLE_FOR_FINAL_READBACK"}
    pylaunch = args.source_checkout.expanduser().resolve() / "parallel" / "PYLAUNCH"
    before = list(sys.path)
    sys.path.insert(0, str(pylaunch))
    client = None
    session = None
    try:
        from wof_launcher.cdp import CdpClient
        client = CdpClient(args.browser_websocket_url, timeout=min(5.0, args.duration))
        client.connect()
        session = client.attach(page_target_id)
        session.request("Runtime.enable")
        expression = """(()=>{const p=globalThis.WOFP43P42CORRELATIONPROBE;if(!p||p.schema!=='wof-gstyphoon-renderer-correlation-probe-v1')return{present:false,reason:'P42_LIVE_INSTANCE_MISSING'};let stop=null;try{stop=p.stop('P43_FINAL_TEARDOWN');}catch(ex){stop={error:String(ex&&ex.stack||ex)}}let bundle=null;try{bundle=p.result();}catch(ex){return{present:true,surface:'WOFP43P42CORRELATIONPROBE',stop,error:String(ex&&ex.stack||ex),bundle:null}}try{delete globalThis.WOFP43P42CORRELATIONPROBE;}catch(_){globalThis.WOFP43P42CORRELATIONPROBE=null;}return{present:true,surface:'WOFP43P42CORRELATIONPROBE',stop,bundle};})()"""
        raw = session.evaluate(expression, timeout=10.0)
        if not isinstance(raw, Mapping) or raw.get("present") is not True:
            return {"state": "P42_CORRELATION_PROBE_NOT_PRESENT", "present": False, "reason": (raw or {}).get("reason") if isinstance(raw, Mapping) else "P42_FINAL_READBACK_INVALID", "raw": raw}
        return {
            "state": "P42_CORRELATION_PROBE_PRESENT",
            "present": True,
            "schema": core.P42_SCHEMA,
            "surface": raw.get("surface"),
            "bundle": raw.get("bundle"),
            "stop": raw.get("stop"),
            "error": raw.get("error"),
            "testedCommit": P42_TESTED_COMMIT,
            "testedBlob": P42_TESTED_BLOB,
            "authorityEligible": False,
        }
    except Exception as exc:
        return {"state": "P42_CORRELATION_PROBE_NOT_PRESENT", "present": False, "reason": f"P42_FINAL_READBACK_FAILED:{type(exc).__name__}:{exc}"}
    finally:
        if session is not None:
            try:
                session.close()
            except Exception:
                pass
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
        sys.path[:] = before


def _stable_receipts(args: Any, receipt: dict[str, Any], p42_start: Mapping[str, Any], p42_final: Mapping[str, Any], bound_raw: Mapping[str, Any]) -> dict[str, Any]:
    root = args.output_root.expanduser().resolve()
    artifacts = dict(receipt.get("artifacts") or {})
    artifacts.pop("receipt", None)
    artifacts.pop("humanReceipt", None)
    receipt["p42Start"] = dict(p42_start)
    receipt["p42"] = dict(p42_final)
    if p42_final.get("present") is True:
        p42_artifact = core._write_artifact(root, "raw/P42_CORRELATION_BUNDLE.json", p42_final)
        receipt["p42"]["artifact"] = p42_artifact
        artifacts["p42Correlation"] = p42_artifact
    elif (root / "raw" / "P42_CORRELATION_BUNDLE.json").exists():
        try:
            (root / "raw" / "P42_CORRELATION_BUNDLE.json").unlink()
        except OSError:
            pass
    if bound_raw:
        artifacts["candidateBindingRaw"] = dict(bound_raw)
        receipt["candidateBindingRaw"] = dict(bound_raw)
    receipt["artifacts"] = artifacts
    receipt_path = root / "P43_DIAGNOSTIC_RECEIPT.json"
    human_path = root / "P43_DIAGNOSTIC_RECEIPT.md"
    receipt["receiptPath"] = str(receipt_path)
    receipt["humanReceiptPath"] = str(human_path)
    receipt_path.write_bytes(core.pretty_bytes(receipt))
    human_path.write_bytes(core.build_human_receipt(receipt).encode("utf-8"))
    return {
        "receiptPath": str(receipt_path),
        "receiptSha256": core.sha256_bytes(receipt_path.read_bytes()),
        "humanReceiptPath": str(human_path),
        "humanReceiptSha256": core.sha256_bytes(human_path.read_bytes()),
    }


def run(args: Any) -> tuple[dict[str, Any], int]:
    p42_start = _start_p42(args)
    receipt, rc = core.run_live_diagnostic(args)
    bound_raw: dict[str, Any] = {}
    try:
        bound_raw = _raw_binding_artifacts(args, receipt.get("candidateBinding") or {})
    except Exception as exc:
        receipt.setdefault("errors", []).append({"atUtc": core.utc_now(), "where": "CANDIDATE_BINDING_RAW_ARCHIVE", "type": type(exc).__name__, "message": str(exc), "repr": repr(exc)})
    page_target = (receipt.get("authoritativeAssociation") or {}).get("pageTargetId")
    if not page_target:
        identity, _ = _p16_binding(args)
        page_target = identity.get("pageTargetId") if identity else None
    p42_final = _stop_p42(args, page_target) if p42_start.get("present") is True else dict(p42_start)
    stable = _stable_receipts(args, receipt, p42_start, p42_final, bound_raw)
    receipt["stableReceipt"] = stable
    # Stable metadata is reported to stdout; it is intentionally not self-inserted into
    # the persisted JSON because a receipt cannot contain its own stable hash.
    return receipt, rc


def main(argv: Sequence[str] | None = None) -> int:
    args = core._parser().parse_args(argv)
    if not (0.1 <= args.duration <= 60.0):
        raise SystemExit("--duration must be in [0.1, 60] seconds")
    receipt, rc = run(args)
    first = receipt.get("firstFailingGate")
    stable = receipt.get("stableReceipt") or {}
    print(f"receipt={stable.get('receiptPath')}")
    print(f"receiptSha256={stable.get('receiptSha256')}")
    print(f"firstFailingGate={first.get('gate') if isinstance(first, Mapping) else 'NONE'}")
    print("passedBeforeFirstFailure=" + ",".join(receipt.get("passedBeforeFirstFailure") or []))
    print(f"p42={((receipt.get('p42') or {}).get('state'))}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
