from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time
from typing import Any, Mapping, Sequence

from p21_candidate import (
    ATTESTATION_SCHEMA, CANDIDATE_SCHEMA, POINTER_REL, POINTER_SCHEMA, REQUIRED_STAGES,
    WAITING_FOR_P19, StagingError, WaitingForP19, compare_git_state, ensure_candidate_commit,
    observe_git_state, resolve_p19_candidate, sha256_file,
)
from p21_runtime import (
    RUNTIME_REL, cleanup_staging_worktree, collect_p18_from_p16, create_staging_worktree,
    default_permanent_repo, default_results_dir, default_staging_root, discover_browser_websocket,
    discover_permanent_alpha_runtimes, resolve_python, restart_permanent_runtime,
    runtime_environment, build_runtime_command, stage_candidate_manifest, start_runtime,
    stop_permanent_alpha_runtimes, stop_runtime,
)
from p21_acceptance import P17_REL, archive_existing, run_p17, wait_for_staged_p16

compare_permanent_state = compare_git_state

P16_NAME = "ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.json"
P18_NAME = "ALPHA_CANONICAL_DRAW_EVIDENCE.json"
W3_LATEST_NAME = "LATEST_W3_RENDER_SOURCE_QUALIFICATION.json"
RECEIPT_NAME = "ALPHA_P21_STAGING_RECEIPT.json"
READY_FOR_OWNER_VISUAL_CONFIRMATION = "READY_FOR_OWNER_VISUAL_CONFIRMATION"
P27_INTERPOSER_NAME = "p27_canonical_feed_interposer.py"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data); fh.flush(); os.fsync(fh.fileno())
        os.replace(temp_name, path)
    finally:
        Path(temp_name).unlink(missing_ok=True)


def _wrap_staged_runtime_command(command: Sequence[str], checkout: Path) -> list[str]:
    """Keep the exact candidate checkout immutable while adding the P27 P10-feed interposer.

    P25 may replace build_runtime_command with its own tee builder, so wrapping happens
    after the builder returns. The original script and arguments are preserved after `--`.
    """
    values = list(command)
    if len(values) < 2:
        raise StagingError("staged runtime command is incomplete")
    interposer = Path(__file__).with_name(P27_INTERPOSER_NAME).resolve()
    if not interposer.is_file():
        raise StagingError(f"P27 canonical-feed interposer missing: {interposer}")
    return [values[0], str(interposer), "--candidate-root", str(checkout.resolve()), "--", *values[1:]]


def run_staged_acceptance(*, repo_root: Path, pointer_path: Path | None, staging_root: Path, output_root: Path, permanent_repo: Path | None, python_exe: str, browser: str, host: str, port: int, evidence_timeout: float, stop_permanent_runtime: bool) -> tuple[dict[str, Any], int]:
    repo, output_root = repo_root.expanduser().resolve(), output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    receipt: dict[str, Any] = {
        "schema": "wof-alpha-p21-prepromotion-staging-receipt-v1", "version": 1,
        "startedAtUtc": _utc_now(), "state": "STARTING", "candidate": None,
        "runtime": {"started": False, "stopped": False}, "p17": None, "p16": None, "p18": None,
        "ownerVisualAcceptance": "NOT_RUN", "realWofAcceptance": "NOT_RUN", "alphaLiveMoved": False,
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "legacySpatialFallback": False, "screenshotProductionCoordinates": False, "worldProjectionProductionCoordinates": False, "guessedAddresses": False},
    }
    receipt_path, runtime, staging = output_root / RECEIPT_NAME, None, None
    permanent_before, stopped_pids, cleanup_error, rc = None, [], None, 1
    try:
        receipt["sourceRepoBefore"] = observe_git_state(repo)
        try:
            candidate = resolve_p19_candidate(repo, pointer_path)
        except WaitingForP19 as exc:
            receipt.update({"state": WAITING_FOR_P19, "reason": str(exc)}); rc = 4; return receipt, rc
        receipt["candidate"] = candidate
        ensure_candidate_commit(repo, str(candidate["sourceCommit"]))

        permanent = permanent_repo.expanduser().resolve() if permanent_repo is not None else None
        if permanent is not None and permanent.exists():
            permanent_before = observe_git_state(permanent); receipt["permanentRepoBefore"] = permanent_before
            if stop_permanent_runtime:
                rows = discover_permanent_alpha_runtimes(permanent)
                stopped_pids = stop_permanent_alpha_runtimes(rows)
                receipt["permanentRuntimeBefore"] = {"runningCount": len(rows), "stoppedPids": stopped_pids}

        staging = create_staging_worktree(repo, str(candidate["sourceCommit"]), staging_root)
        checkout = Path(staging["checkout"]); receipt["staging"] = staging
        staged_manifest = stage_candidate_manifest(candidate, Path(staging["runDir"]))
        receipt["stagedPackageManifest"] = {"path": str(staged_manifest), "sha256": sha256_file(staged_manifest)}
        owner_results, archive_dir = default_results_dir(), output_root / "preexisting"
        default_p16, default_p18 = owner_results / P16_NAME, owner_results / P18_NAME
        prior_p16, prior_p18 = archive_existing(default_p16, archive_dir), archive_existing(default_p18, archive_dir)
        receipt["preexistingEvidence"] = {"p16": prior_p16, "p18": prior_p18}

        env = runtime_environment(candidate, package_manifest=staged_manifest); runtime_log = output_root / "P21_STAGED_RUNTIME.log"
        runtime_cmd = _wrap_staged_runtime_command(
            build_runtime_command(python_exe, checkout, owner_results, browser), checkout
        )
        runtime_started = time.time(); runtime = start_runtime(runtime_cmd, env, runtime_log)
        receipt["runtime"] = {"started": True, "pid": runtime.pid, "command": runtime_cmd, "logPath": str(runtime_log), "stagingMode": env["WOF_ALPHA_ACCEPTANCE_MODE"], "sourceCommit": env["WOF_ALPHA_ACCEPTANCE_COMMIT"], "packageVersion": env["WOF_ALPHA_ACCEPTANCE_PACKAGE_VERSION"], "packageManifest": env["WOF_ALPHA_PACKAGE_MANIFEST"], "browserPreserved": env["WOF_ALPHA_OWNER_NAVIGATES"] == "1", "inputInjection": False, "stopped": False}

        run_p16, run_p18, w3_root = output_root / "ALPHA_CANONICAL_ACCEPTANCE_EVIDENCE.STAGED.json", output_root / "ALPHA_CANONICAL_DRAW_EVIDENCE.STAGED.json", output_root / "w3"
        first = run_p17(python_exe, checkout, candidate, output_root / "p17-initial", run_p16, run_p18, invoke_w3=True, w3_output_root=w3_root)
        receipt["p17Initial"] = first
        p16 = wait_for_staged_p16(default_p16, run_p16, candidate, runtime_started, prior_p16, evidence_timeout)
        receipt["p16"] = p16 or {"state": "WAITING_CANONICAL_RUNTIME_EVIDENCE", "path": str(run_p16)}
        if p16 is not None:
            browser_ws = discover_browser_websocket(host, port)
            receipt["browserEndpoint"] = {"host": host, "port": port, "websocketDiscovered": bool(browser_ws)}
            receipt["p18"] = collect_p18_from_p16(python_exe, checkout, run_p16, run_p18, browser_ws) if browser_ws else {"state": "WAITING_BROWSER_ENDPOINT", "path": str(run_p18)}
        else:
            receipt["p18"] = {"state": "WAITING_P16", "path": str(run_p18)}

        latest_w3 = w3_root / W3_LATEST_NAME
        final = run_p17(python_exe, checkout, candidate, output_root / "p17", run_p16, run_p18, invoke_w3=False, w3_path=latest_w3 if latest_w3.is_file() else None)
        receipt["p17"], receipt["w3"] = final, final.get("w3Qualification") or first.get("w3Qualification")
        receipt["state"] = final.get("automaticDecision") or "ACCEPTANCE_BUNDLE_WRITTEN"
        rc = 0
    except Exception as exc:
        receipt.update({"state": "STAGING_FAILED", "reason": f"{type(exc).__name__}: {exc}"}); rc = 2
    finally:
        receipt.setdefault("runtime", {}).update(stop_runtime(runtime))
        if staging is not None:
            try:
                receipt["cleanup"] = cleanup_staging_worktree(repo, staging_root, Path(staging["runDir"]), Path(staging["checkout"]))
            except Exception as exc:
                cleanup_error = f"{type(exc).__name__}: {exc}"; receipt["cleanup"] = {"state": "FAILED", "reason": cleanup_error}; rc = 3

        if permanent_before is not None and permanent_repo is not None:
            try:
                after = observe_git_state(permanent_repo); receipt["permanentRepoAfter"] = after
                mismatches = compare_git_state(permanent_before, after)
                receipt.update({"permanentRepoUnchanged": not mismatches, "permanentRepoMismatches": mismatches})
                if mismatches: receipt["state"], rc = "PERMANENT_STATE_CHANGED", 3
                if stopped_pids:
                    restored = restart_permanent_runtime(permanent_repo, str(permanent_before.get("head") or ""), default_results_dir(), browser)
                    receipt["permanentRuntimeRestore"] = restored
                    if not restored.get("restarted"): receipt["state"], rc = "RESTORE_REQUIRED", 3
            except Exception as exc:
                receipt.update({"permanentVerificationError": f"{type(exc).__name__}: {exc}", "state": "RESTORE_REQUIRED", "restoreAction": "Run Desktop\\WOF_ALPHA_TEST.cmd and verify alpha-live before retrying staging."}); rc = 3

        try:
            source_after = observe_git_state(repo); receipt["sourceRepoAfter"] = source_after
            if "sourceRepoBefore" in receipt:
                mismatches = compare_git_state(receipt["sourceRepoBefore"], source_after)
                receipt.update({"sourceRepoRefsUnchanged": not mismatches, "sourceRepoRefMismatches": mismatches})
                if mismatches: receipt["state"], rc = "ALPHA_LIVE_OR_SOURCE_REF_CHANGED", 3
        except Exception as exc:
            receipt["sourceVerificationError"] = f"{type(exc).__name__}: {exc}"; rc = 3

        before, after = receipt.get("sourceRepoBefore") or {}, receipt.get("sourceRepoAfter") or {}
        receipt["alphaLiveBefore"] = {"local": before.get("alphaLiveLocal"), "remote": before.get("alphaLiveRemote")}
        receipt["alphaLiveAfter"] = {"local": after.get("alphaLiveLocal"), "remote": after.get("alphaLiveRemote")}
        receipt["alphaLiveMoved"] = receipt["alphaLiveBefore"] != receipt["alphaLiveAfter"]
        if receipt["alphaLiveMoved"]: receipt["state"], rc = "ALPHA_LIVE_MOVED_EXTERNALLY_OR_UNEXPECTEDLY", 3
        receipt.update({"ownerVisualAcceptance": "NOT_RUN", "realWofAcceptance": "NOT_RUN", "finishedAtUtc": _utc_now(), "cleanupError": cleanup_error, "receiptPath": str(receipt_path)})
        _atomic_json(receipt_path, receipt); receipt["receiptSha256"] = sha256_file(receipt_path)
    return receipt, rc


def _parser() -> argparse.ArgumentParser:
    here = Path(__file__).resolve()
    p = argparse.ArgumentParser(description="Stage exact P19 Alpha candidate and run bounded pre-promotion acceptance without moving alpha-live.")
    p.add_argument("--repo-root", type=Path, default=here.parents[2]); p.add_argument("--pointer", type=Path)
    p.add_argument("--staging-root", type=Path, default=default_staging_root()); p.add_argument("--output-root", type=Path)
    p.add_argument("--permanent-repo", type=Path); p.add_argument("--python", type=Path)
    p.add_argument("--browser", choices=["chrome", "edge", "auto"], default="chrome"); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=9223)
    p.add_argument("--evidence-timeout", type=float, default=45.0); p.add_argument("--keep-permanent-runtime", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output = args.output_root or default_results_dir() / "ALPHA_P21_STAGING_ACCEPTANCE" / f"run-{int(time.time())}"
    permanent = args.permanent_repo if args.permanent_repo is not None else default_permanent_repo()
    receipt, rc = run_staged_acceptance(repo_root=args.repo_root, pointer_path=args.pointer, staging_root=args.staging_root, output_root=output, permanent_repo=permanent, python_exe=resolve_python(args.python), browser=args.browser, host=args.host, port=args.port, evidence_timeout=args.evidence_timeout, stop_permanent_runtime=not args.keep_permanent_runtime)
    print(f"state={receipt.get('state')}")
    if receipt.get("candidate"): print(f"candidate={receipt['candidate'].get('sourceCommit')} package={receipt['candidate'].get('packageVersion')}")
    print(f"alphaLiveMoved={receipt.get('alphaLiveMoved')}"); print(f"ownerVisualAcceptance={receipt.get('ownerVisualAcceptance')}")
    if receipt.get("receiptPath"): print(f"receipt={receipt.get('receiptPath')}")
    if receipt.get("state") == READY_FOR_OWNER_VISUAL_CONFIRMATION:
        print("候选版本已达到机器证据边界。请继续正常游玩，并只在后续 P20 单一视觉问题中确认提示是否稳定跟随正确人物。")
    elif receipt.get("state") == WAITING_FOR_P19:
        print("P19 最终 candidate 尚未 READY；未创建 staging、未启动 runtime、未移动 alpha-live。")
    return rc


if __name__ == "__main__": raise SystemExit(main())
