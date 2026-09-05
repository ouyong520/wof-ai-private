from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import time
from typing import Any, Mapping

from p21_candidate import StagingError, load_json, sha256_file

P17_REL = Path("parallel/OWNER_ACCEPTANCE/final_acceptance_orchestrator.py")
P17_BUNDLE_NAME = "ALPHA_FINAL_ACCEPTANCE_BUNDLE.json"
EXPECTED_WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
EARLY_P16_STATES = frozenset({"WAITING_WOF", "VERIFYING_WORLD"})


def archive_existing(path: Path, archive_dir: Path) -> dict[str, Any] | None:
    if not path.is_file(): return None
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / f"PREEXISTING_{path.name}"
    shutil.copy2(path, target)
    return {"source": str(path), "copy": str(target), "sha256": sha256_file(path), "mtime": path.stat().st_mtime}


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _renderer_authority_present(value: Any) -> bool:
    return _nonempty_string(value) or (isinstance(value, Mapping) and bool(value))


def staged_p16_readiness(raw: Mapping[str, Any], candidate: Mapping[str, Any]) -> tuple[bool, str]:
    """Return whether a fresh P16 snapshot is usable by staged P17/P18.

    Fresh file metadata alone is not authority. The staged bridge may copy P16 only
    after exact World acceptance and the runtime/renderer identity required by the
    downstream P17/P18 contracts is present. VERIFYING_WORLD is therefore a waiting
    state, never terminal staged evidence.
    """
    if raw.get("schema") != "wof-alpha-canonical-owner-acceptance-evidence-v1" or raw.get("version") != 1:
        return False, "P16_SCHEMA_OR_VERSION_MISMATCH"
    if raw.get("packageVersion") != candidate.get("packageVersion"):
        return False, "P16_PACKAGE_MISMATCH"
    if raw.get("visibleProof") != "NOT_PROVEN":
        return False, "P16_VISIBLE_PROOF_BOUNDARY_MISMATCH"

    world = raw.get("world") if isinstance(raw.get("world"), Mapping) else {}
    runtime = raw.get("runtime") if isinstance(raw.get("runtime"), Mapping) else {}
    canonical = raw.get("canonical") if isinstance(raw.get("canonical"), Mapping) else {}
    safety = raw.get("safety") if isinstance(raw.get("safety"), Mapping) else {}

    if world.get("accepted") is not True:
        return False, "P16_WORLD_NOT_ACCEPTED"
    if world.get("sha256") != EXPECTED_WORLD_SHA256:
        return False, "P16_WORLD_IDENTITY_MISMATCH"
    if not _nonempty_string(world.get("pageTargetId")):
        return False, "P16_PAGE_TARGET_MISSING"
    if not _nonempty_string(world.get("workerTargetId")):
        return False, "P16_WORKER_TARGET_MISSING"

    state = canonical.get("state")
    if not _nonempty_string(state) or state in EARLY_P16_STATES:
        return False, f"P16_CANONICAL_STATE_NOT_USABLE:{state or 'MISSING'}"
    if not _nonempty_string(runtime.get("epoch")):
        return False, "P16_RUNTIME_EPOCH_MISSING"
    if not _nonempty_string(runtime.get("authorityKey")):
        return False, "P16_AUTHORITY_KEY_MISSING"
    if not _nonempty_string(runtime.get("rendererEpoch")):
        return False, "P16_RENDERER_EPOCH_MISSING"
    if not _renderer_authority_present(runtime.get("rendererAuthority")):
        return False, "P16_RENDERER_AUTHORITY_MISSING"

    if safety.get("readOnly") is not True or safety.get("ramWrites") != 0 or safety.get("inputInjection") is not False:
        return False, "P16_SAFETY_MISMATCH"
    return True, "USABLE"


def wait_for_staged_p16(default_path: Path, output_path: Path, candidate: Mapping[str, Any], started_epoch: float, prior: Mapping[str, Any] | None, timeout: float) -> dict[str, Any] | None:
    deadline, prior_sha = time.time() + max(0.0, timeout), prior.get("sha256") if isinstance(prior, Mapping) else None
    while True:
        if default_path.is_file():
            try:
                raw, digest = load_json(default_path), sha256_file(default_path)
                fresh = default_path.stat().st_mtime >= started_epoch - 1.0 and digest != prior_sha
                usable, readiness = staged_p16_readiness(raw, candidate)
                if fresh and usable:
                    output_path.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(default_path, output_path)
                    return {"path": str(output_path), "sha256": sha256_file(output_path), "canonicalState": ((raw.get("canonical") or {}).get("state")), "packageVersion": raw.get("packageVersion"), "world": raw.get("world"), "runtime": raw.get("runtime"), "readiness": readiness}
            except (OSError, ValueError):
                pass
        if time.time() >= deadline: return None
        time.sleep(0.5)


def run_p17(python_exe: str, checkout: Path, candidate: Mapping[str, Any], output_dir: Path, p16_path: Path, p18_path: Path, *, invoke_w3: bool, w3_path: Path | None = None, w3_output_root: Path | None = None) -> dict[str, Any]:
    script = checkout / P17_REL
    if not script.is_file(): raise StagingError(f"P17 orchestrator missing from staged candidate: {script}")
    cmd = [python_exe, str(script), "--repo-root", str(checkout), "--output-dir", str(output_dir), "--candidate-metadata", str(candidate["candidatePath"]), "--p16-evidence", str(p16_path), "--p18-evidence", str(p18_path)]
    if invoke_w3:
        cmd.append("--invoke-w3")
        if w3_output_root is not None: cmd.extend(["--w3-output-root", str(w3_output_root)])
    elif w3_path is not None:
        cmd.extend(["--w3-qualification", str(w3_path)])
    cp = subprocess.run(cmd, cwd=checkout, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    bundle = output_dir / P17_BUNDLE_NAME
    if not bundle.is_file(): raise StagingError(f"P17 did not write acceptance bundle; exit={cp.returncode}: {cp.stderr[-1000:]}")
    raw = load_json(bundle); c = raw.get("candidate") if isinstance(raw.get("candidate"), Mapping) else {}
    if c.get("sourceCommit") != candidate.get("sourceCommit") or c.get("packageVersion") != candidate.get("packageVersion") or c.get("contentSha256") != candidate.get("candidateSha256"):
        raise StagingError("P17 bundle is not bound to exact P19 candidate metadata")
    if raw.get("visibleProof") != "NOT_PROVEN" or (raw.get("safety") or {}).get("alphaLiveMoved") is not False:
        raise StagingError("P17 bundle violates visual/promotion proof boundary")
    return {"exitCode": cp.returncode, "command": cmd, "bundlePath": str(bundle), "bundleSha256": sha256_file(bundle), "automaticDecision": raw.get("automaticDecision"), "visibleProof": raw.get("visibleProof"), "w3Qualification": raw.get("w3Qualification"), "p16CanonicalRuntime": raw.get("p16CanonicalRuntime"), "p18DrawEvidence": raw.get("p18DrawEvidence"), "stdoutTail": cp.stdout[-2000:], "stderrTail": cp.stderr[-2000:]}
