"""Strict R0.4 fork plan, identity, layout, and checkpoint contracts."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .adapter import RamBlockSnapshot, TrainingFarmError
from .determinism import MAX_HORIZON_FRAMES, ReplayStep, action_sequence_sha256, canonical_action_payload, parse_action_sequence
from .identity import SOURCE_NAMESPACE, sha256_file

PLAN_SCHEMA = "wof-training-farm-savestate-fork-plan-v1"
RESULT_SCHEMA = "wof-training-farm-savestate-fork-result-v1"
ROOT_SCHEMA = "wof-training-farm-fork-root-authority-v1"
LAYOUT_SCHEMA = "wof-training-farm-fork-memory-layout-v1"
PROOF_SCOPE_FIXTURE = "IMPLEMENTATION_FIXTURE"
PROOF_SCOPE_REAL = "REAL_WOF_FORK"
MAX_BRANCHES = 256
MAX_FORK_REPETITIONS = 10
MAX_CHECKPOINTS = 64
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_FORK_FILES = (
    "adapter.py", "fake_backend.py", "stable_retro_backend.py", "identity.py",
    "determinism.py", "determinism.schema.json", "observation_discovery.py",
    "savestate_fork_contract.py", "savestate_fork_execution.py", "savestate_fork.py",
    "savestate_fork_plan.schema.json", "savestate_fork_result.schema.json",
)

class ForkContractError(TrainingFarmError):
    """Malformed/coercible fork plan or resume evidence."""

@dataclass(frozen=True)
class BranchSpec:
    branch_id: str
    horizon_frames: int
    steps: tuple[ReplayStep, ...]
    label: str | None

@dataclass(frozen=True)
class ForkPlan:
    fork_set_id: str
    root_id: str
    expected_root_savestate_sha256: str | None
    repetitions: int
    branches: tuple[BranchSpec, ...]

def _sha_bytes(v: bytes) -> str:
    return hashlib.sha256(v).hexdigest()

def _sha_json(v: object) -> str:
    return _sha_bytes(json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii"))

def _strict_int(v: object, name: str, lo: int, hi: int) -> int:
    if type(v) is not int or not lo <= v <= hi:
        raise ForkContractError(f"{name} must be a strict integer in range {lo}..{hi}")
    return v

def _strict_id(v: object, name: str) -> str:
    if type(v) is not str or not _ID.fullmatch(v):
        raise ForkContractError(f"{name} must be a 1..128 canonical identifier")
    return v

def _strict_sha(v: object, name: str) -> str:
    if type(v) is not str or not _SHA.fullmatch(v):
        raise ForkContractError(f"{name} must be lowercase SHA-256 hex")
    return v

def _parse_actions(v: object, name: str) -> tuple[ReplayStep, ...]:
    try:
        return parse_action_sequence(v)
    except (TrainingFarmError, TypeError, ValueError) as exc:
        raise ForkContractError(f"{name}: {exc}") from exc

def parse_fork_plan(v: object) -> ForkPlan:
    keys = {"schema", "forkSetId", "root", "repetitions", "branches"}
    if type(v) is not dict or set(v) != keys:
        raise ForkContractError("fork plan must contain exactly schema, forkSetId, root, repetitions, branches")
    if v["schema"] != PLAN_SCHEMA:
        raise ForkContractError("fork plan schema mismatch")
    fsid = _strict_id(v["forkSetId"], "forkSetId")
    root = v["root"]
    if type(root) is not dict or set(root) != {"rootId", "expectedSavestateSha256"}:
        raise ForkContractError("root must contain exactly rootId and expectedSavestateSha256")
    rid = _strict_id(root["rootId"], "root.rootId")
    expected = root["expectedSavestateSha256"]
    if expected is not None:
        expected = _strict_sha(expected, "root.expectedSavestateSha256")
    reps = _strict_int(v["repetitions"], "repetitions", 2, MAX_FORK_REPETITIONS)
    raw = v["branches"]
    if type(raw) is not list or not 1 <= len(raw) <= MAX_BRANCHES:
        raise ForkContractError(f"branches must contain 1..{MAX_BRANCHES} entries")
    out: list[BranchSpec] = []
    seen: set[str] = set()
    for i, item in enumerate(raw):
        if type(item) is not dict or set(item) != {"branchId", "horizonFrames", "actions", "metadata"}:
            raise ForkContractError(f"branches[{i}] has a non-canonical structure")
        bid = _strict_id(item["branchId"], f"branches[{i}].branchId")
        if bid in seen:
            raise ForkContractError(f"duplicate branchId: {bid}")
        seen.add(bid)
        horizon = _strict_int(item["horizonFrames"], f"branches[{i}].horizonFrames", 1, MAX_HORIZON_FRAMES)
        steps = _parse_actions(item["actions"], f"branches[{i}].actions")
        if sum(s.frames for s in steps) != horizon:
            raise ForkContractError(f"branch {bid} action sequence does not exactly cover horizon {horizon}")
        metadata = item["metadata"]
        if type(metadata) is not dict or set(metadata) != {"label"}:
            raise ForkContractError(f"branches[{i}].metadata must contain exactly label")
        label = metadata["label"]
        if label is not None and (type(label) is not str or len(label) > 256):
            raise ForkContractError(f"branches[{i}].metadata.label must be null/string <=256 chars")
        out.append(BranchSpec(bid, horizon, steps, label))
    out.sort(key=lambda b: b.branch_id)
    return ForkPlan(fsid, rid, expected, reps, tuple(out))

def canonical_branch_execution_payload(b: BranchSpec) -> dict[str, object]:
    return {"branchId": b.branch_id, "horizonFrames": b.horizon_frames,
            "actions": canonical_action_payload(b.steps), "actionSequenceSha256": action_sequence_sha256(b.steps)}

def branch_identity_sha256(b: BranchSpec) -> str:
    return _sha_json(canonical_branch_execution_payload(b))

def branch_specification_payload(b: BranchSpec) -> dict[str, object]:
    x = canonical_branch_execution_payload(b)
    x.update(branchIdentitySha256=branch_identity_sha256(b), metadata={"label": b.label})
    return x

def fork_plan_authority_payload(p: ForkPlan) -> dict[str, object]:
    # Human label is deliberately not execution authority.
    return {"schema": PLAN_SCHEMA, "forkSetId": p.fork_set_id,
            "root": {"rootId": p.root_id, "expectedSavestateSha256": p.expected_root_savestate_sha256},
            "repetitions": p.repetitions,
            "branches": [canonical_branch_execution_payload(b) for b in p.branches]}

def fork_plan_authority_sha256(p: ForkPlan) -> str:
    return _sha_json(fork_plan_authority_payload(p))

def load_fork_plan(path: str | Path) -> ForkPlan:
    try:
        return parse_fork_plan(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ForkContractError(f"failed to load plan: {type(exc).__name__}: {exc}") from exc

def fork_source_identity() -> tuple[str, dict[str, str]]:
    base = Path(__file__).resolve().parent
    files: dict[str, str] = {}
    for name in _FORK_FILES:
        path = base / name
        if not path.is_file():
            raise ForkContractError(f"R0.4 source identity file missing: {name}")
        files[name] = sha256_file(path)
    return _sha_json(files), files

def blocks_snapshot_sha(blocks: tuple[RamBlockSnapshot, ...]) -> str:
    h = hashlib.sha256()
    for b in blocks:
        h.update(b.base_address.to_bytes(8, "big")); h.update(b.length.to_bytes(8, "big")); h.update(b.data)
    return h.hexdigest()

def memory_layout_identity(blocks: tuple[RamBlockSnapshot, ...]) -> dict[str, object]:
    desc = [{"index": i, "baseAddress": b.base_address, "length": b.length} for i, b in enumerate(blocks)]
    body: dict[str, object] = {"schema": LAYOUT_SCHEMA, "sourceNamespace": SOURCE_NAMESPACE,
                              "addressKind": "stable-retro-memory-block-key-plus-byte-offset", "blocks": desc}
    body["layoutIdentitySha256"] = _sha_json(body)
    return body

def stable_runtime_authority(identity: dict[str, object]) -> dict[str, object]:
    # processId is run-local; every other validated runtime/ROM/source/backend field remains bound.
    return {k: copy.deepcopy(v) for k, v in identity.items() if k != "processId"}

def root_hash_payload(root: dict[str, object]) -> dict[str, object]:
    keys = ("schema", "sourceNamespace", "forkSetId", "rootId", "rootCaptureMode", "rootLogicalFrame",
            "rootSavestateSha256", "rootRamSha256", "rootRamBlocksSha256", "memoryLayoutIdentity",
            "stableRuntimeAuthority", "romSha256", "farmCandidateSha256", "forkCandidateSha256",
            "forkSourceFiles", "inputIsolationMode")
    return {k: copy.deepcopy(root[k]) for k in keys}

def checkpoint_frames(branch: BranchSpec) -> tuple[int, ...]:
    h = branch.horizon_frames
    if h <= MAX_CHECKPOINTS:
        return tuple(range(1, h + 1))
    return tuple(sorted({(i * h + MAX_CHECKPOINTS - 1) // MAX_CHECKPOINTS for i in range(1, MAX_CHECKPOINTS + 1)}))
