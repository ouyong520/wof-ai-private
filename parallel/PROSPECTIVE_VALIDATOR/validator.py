from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

MANIFEST_SCHEMA = "wof-prospective-candidate-v1"
CORPUS_SCHEMA = "wof-prospective-corpus-v1"
RESULT_SCHEMA = "wof-prospective-result-v1"
SESSION_SCHEMA = "wof-prospective-session-v1"
RECORDER_SCHEMA = "wof-052l-recorder-v1"
ALLOWED_SEQUENCE_KINDS = {"tail2": 2, "pair": 2, "tail3": 3, "triple": 3}
ALLOWED_OPS = {"eq", "ne", "in", "not_in", "lt", "lte", "gt", "gte", "exists"}
SUPPORTED_GATES = {
    "minProspectiveSignals",
    "minProspectiveRooms",
    "requireZeroHardMiss",
    "minDistinctTargets",
    "minObservedTypes",
    "requireLifecycleReset",
}

_SIGNATURE_RE = re.compile(
    r"^S(?P<state99>\d+)/A(?P<action2A>\d+)/B(?P<b2B>\d+)\|BODY(?P<body>\d+)"
    r"\|FE(?P<frameEnd>[0-9a-fA-F]+)\|NX(?P<next>[0-9a-fA-F]+)"
    r"\|V(?P<value30>[0-9a-fA-F]+)\|TM(?P<timer34>\d+|\*)\|P6C(?P<payload6C>\d+)$"
)


class ValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def family_signature(signature: str) -> str:
    return re.sub(r"\|TM[^|]*", "|TM*", str(signature or ""))


def parse_signature(signature: str) -> dict[str, Any]:
    m = _SIGNATURE_RE.match(str(signature or ""))
    if not m:
        return {"signature": signature, "family": family_signature(signature)}
    out: dict[str, Any] = {"signature": signature, "family": family_signature(signature)}
    for key, value in m.groupdict().items():
        if key in {"frameEnd", "next", "value30"}:
            out[key] = int(value, 16)
        elif value != "*":
            out[key] = int(value)
        else:
            out[key] = value
    return out


def canonical_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    return json.dumps(manifest, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def candidate_sha256(manifest: dict[str, Any]) -> str:
    validate_manifest(manifest)
    return hashlib.sha256(canonical_manifest_bytes(manifest)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def make_session(manifest: dict[str, Any], frozen_at: str | None = None) -> dict[str, Any]:
    validate_manifest(manifest)
    return {
        "schema": SESSION_SCHEMA,
        "candidateId": manifest["id"],
        "candidateSha256": candidate_sha256(manifest),
        "frozenAt": frozen_at or utc_now(),
        "evidencePolicy": "only evidence whose room/session starts at or after frozenAt is prospective",
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "windowWorkerReplacement": False},
    }


def validate_session(session: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(session, dict) and session.get("schema") == SESSION_SCHEMA, f"session schema must be {SESSION_SCHEMA}")
    _require(session.get("candidateId") == manifest.get("id"), "session candidateId does not match manifest")
    _require(session.get("candidateSha256") == candidate_sha256(manifest), "session candidateSha256 does not match frozen manifest")
    _require(isinstance(session.get("frozenAt"), str) and session["frozenAt"], "session.frozenAt is required")
    return session


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def started_after_freeze(started_at: Any, session: dict[str, Any] | None) -> bool:
    if not session:
        return False
    started = parse_time(started_at)
    frozen = parse_time(session.get("frozenAt"))
    return bool(started and frozen and started >= frozen)


def _validate_predicates(predicates: Any, label: str) -> None:
    _require(isinstance(predicates, list), f"{label} must be a list")
    for idx, pred in enumerate(predicates):
        _require(isinstance(pred, dict), f"{label}[{idx}] must be an object")
        _require(isinstance(pred.get("path"), str) and pred["path"], f"{label}[{idx}].path is required")
        op = pred.get("op", "eq")
        _require(op in ALLOWED_OPS, f"{label}[{idx}] unsupported op {op}")
        if op != "exists":
            _require("value" in pred, f"{label}[{idx}].value is required for op {op}")


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(manifest, dict), "manifest must be a JSON object")
    _require(manifest.get("schema") == MANIFEST_SCHEMA, f"schema must be {MANIFEST_SCHEMA}")
    _require(isinstance(manifest.get("id"), str) and manifest["id"].strip(), "manifest.id is required")
    _require(manifest.get("promotion") == "research-only", "promotion must be research-only")
    rule = manifest.get("rule")
    _require(isinstance(rule, dict), "rule object is required")
    sequence = rule.get("sequence")
    predicates = rule.get("currentPredicates") or []
    _require(sequence is not None or predicates, "rule needs sequence and/or currentPredicates")
    if sequence is not None:
        _require(isinstance(sequence, dict), "rule.sequence must be an object")
        kind = sequence.get("kind")
        _require(kind in ALLOWED_SEQUENCE_KINDS, f"unsupported sequence kind: {kind}")
        states = sequence.get("states")
        _require(isinstance(states, list) and len(states) == ALLOWED_SEQUENCE_KINDS[kind], f"{kind} requires {ALLOWED_SEQUENCE_KINDS[kind]} states")
        for idx, matcher in enumerate(states):
            _require(isinstance(matcher, dict), f"sequence.states[{idx}] must be an object")
            _require(any(k in matcher for k in ("signature", "family", "predicates")), f"sequence.states[{idx}] needs signature, family, or predicates")
            _validate_predicates(matcher.get("predicates") or [], f"sequence.states[{idx}].predicates")
    _validate_predicates(predicates, "rule.currentPredicates")
    outcome = manifest.get("outcome") or {}
    expected = outcome.get("expectedAttacks") or []
    _require(isinstance(expected, list) and expected and all(isinstance(x, int) for x in expected), "outcome.expectedAttacks must be a non-empty integer list")
    windows = manifest.get("windows") or {}
    strict = float(windows.get("strictMaxMs", 150))
    jitter = float(windows.get("jitterMaxMs", max(strict, 220)))
    late = float(windows.get("lateMaxMs", max(jitter, 1000)))
    miss = float(windows.get("hardMissMs", max(late, 1500)))
    _require(0 <= strict <= jitter <= late <= miss, "windows must satisfy strict <= jitter <= late <= hardMiss")
    identity = manifest.get("identity") or {}
    if identity:
        _require(identity.get("world") in (None, "Warriors of Fate (World 921031)"), "unsupported identity.world")
    gate = manifest.get("gate") or {}
    _require(isinstance(gate, dict), "gate must be an object")
    unknown = sorted(set(gate) - SUPPORTED_GATES)
    _require(not unknown, "unsupported conservative gate(s): " + ", ".join(unknown))
    return manifest


def get_path(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def predicate_match(obj: dict[str, Any], pred: dict[str, Any]) -> bool:
    actual = get_path(obj, pred["path"])
    op = pred.get("op", "eq")
    expected = pred.get("value")
    if op == "exists":
        return actual is not None if expected is not False else actual is None
    if op == "eq": return actual == expected
    if op == "ne": return actual != expected
    if op == "in": return actual in expected
    if op == "not_in": return actual not in expected
    if actual is None: return False
    if op == "lt": return actual < expected
    if op == "lte": return actual <= expected
    if op == "gt": return actual > expected
    if op == "gte": return actual >= expected
    return False


def all_predicates(obj: dict[str, Any], predicates: list[dict[str, Any]]) -> bool:
    return all(predicate_match(obj, pred) for pred in predicates)


def normalize_state(raw: dict[str, Any]) -> dict[str, Any]:
    signature = str(raw.get("signature") or "")
    parsed = parse_signature(signature) if signature else {}
    merged = {**parsed, **raw}
    merged["signature"] = signature or str(merged.get("signature") or "")
    merged["family"] = str(raw.get("family") or family_signature(merged["signature"]))
    return merged


def state_match(state: dict[str, Any], matcher: dict[str, Any]) -> bool:
    if "signature" in matcher and state.get("signature") != matcher["signature"]: return False
    if "family" in matcher and state.get("family") != matcher["family"]: return False
    predicates = matcher.get("predicates") or []
    return all_predicates(state, predicates) if predicates else True


def trace_matches(trace: dict[str, Any], manifest: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    rule = manifest["rule"]
    states = [normalize_state(x) for x in (trace.get("states") or []) if isinstance(x, dict)]
    current = dict(trace.get("current") or (states[-1] if states else {}))
    if states and "signature" not in current:
        current = {**states[-1], **current}
    predicates = rule.get("currentPredicates") or []
    current_ok = all_predicates(current, predicates) if predicates else True
    sequence = rule.get("sequence")
    sequence_ok = True
    matched_states: list[dict[str, Any]] = []
    if sequence is not None:
        n = ALLOWED_SEQUENCE_KINDS[sequence["kind"]]
        tail = states[-n:]
        sequence_ok = len(tail) == n and all(state_match(state, matcher) for state, matcher in zip(tail, sequence["states"]))
        if sequence_ok: matched_states = tail
    return sequence_ok and current_ok, {
        "sequenceMatched": sequence_ok,
        "currentPredicatesMatched": current_ok,
        "matchedSignatures": [x.get("signature") for x in matched_states],
        "current": current,
    }


def classify_trace(trace: dict[str, Any], manifest: dict[str, Any]) -> str:
    if trace.get("hardMissReason") or trace.get("category") == "hardMiss": return "hardMiss"
    if trace.get("censored") is True or trace.get("activeAttack") is None: return "censored"
    expected = set(manifest["outcome"]["expectedAttacks"])
    attack = int(trace["activeAttack"])
    if attack not in expected: return "hardMiss"
    lead = trace.get("leadMs", trace.get("candidateLastLeadMs", trace.get("signalLeadMs", 0.0)))
    lead = float(0.0 if lead is None else lead)
    windows = manifest.get("windows") or {}
    strict = float(windows.get("strictMaxMs", 150))
    jitter = float(windows.get("jitterMaxMs", max(strict, 220)))
    late = float(windows.get("lateMaxMs", max(jitter, 1000)))
    if lead <= strict: return "strict"
    if lead <= jitter: return "jitter"
    if lead <= late: return "late"
    return "hardMiss"


def _trace_room(trace: dict[str, Any], fallback: str) -> str:
    return str(trace.get("roomId") or trace.get("room") or fallback)


def recorder_traces(payload: dict[str, Any], source: str, session: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    traces: list[dict[str, Any]] = []
    if isinstance(payload.get("t18CandidateEvidence"), list): traces.extend(x for x in payload["t18CandidateEvidence"] if isinstance(x, dict))
    if isinstance(payload.get("t23SequenceEvidence"), list): traces.extend(x for x in payload["t23SequenceEvidence"] if isinstance(x, dict))
    if isinstance(payload.get("t18"), dict):
        traces.extend(x for x in payload["t18"].get("candidateTraces", []) if isinstance(x, dict))
        traces.extend(x for x in payload["t18"].get("otherTraces", []) if isinstance(x, dict))
    if isinstance(payload.get("t23"), dict): traces.extend(x for x in payload["t23"].get("traces", []) if isinstance(x, dict))
    if isinstance(payload.get("t23SequenceSummary"), dict) and not traces: return []
    room = str(payload.get("roomId") or payload.get("runId") or source)
    room_started = {str(r.get("roomId")): r.get("startedAt") for r in (payload.get("rooms") or []) if isinstance(r, dict) and r.get("roomId")}
    root_started = payload.get("startedAt")
    out = []
    for tr in traces:
        item = dict(tr); item.setdefault("roomId", room)
        started_at = room_started.get(str(item.get("roomId"))) or root_started
        item["evidenceClass"] = "prospective" if started_after_freeze(started_at, session) else "discovery"
        item["prospectiveStartedAt"] = started_at; item.setdefault("source", source); out.append(item)
    return out


def unified_traces(payload: dict[str, Any], source: str, session: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    out = []; default_class = payload.get("evidenceClass"); root_started = payload.get("startedAt") or payload.get("capturedAt")
    for tr in payload.get("traces") or []:
        if not isinstance(tr, dict): continue
        item = dict(tr); item.setdefault("roomId", payload.get("roomId") or payload.get("runId") or source)
        if session is not None: item["evidenceClass"] = "prospective" if started_after_freeze(item.get("startedAt") or root_started, session) else "discovery"
        else: item.setdefault("evidenceClass", default_class or "discovery")
        item.setdefault("source", source); out.append(item)
    return out


def load_traces(paths: Iterable[str | Path], session: dict[str, Any] | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    traces: list[dict[str, Any]] = []; sources: list[dict[str, Any]] = []
    for raw_path in paths:
        path = Path(raw_path); payload = load_json(path)
        if not isinstance(payload, dict): raise ValidationError(f"{path}: corpus root must be object")
        schema = payload.get("schema")
        if schema == CORPUS_SCHEMA: rows = unified_traces(payload, str(path), session); adapter = CORPUS_SCHEMA
        elif schema == RECORDER_SCHEMA: rows = recorder_traces(payload, str(path), session); adapter = RECORDER_SCHEMA
        else: raise ValidationError(f"{path}: unsupported corpus schema {schema!r}")
        traces.extend(rows); sources.append({"path": str(path), "schema": schema, "adapter": adapter, "traces": len(rows)})
    return traces, sources


def _target_key(trace: dict[str, Any], current: dict[str, Any]) -> str | None:
    for value in (trace.get("targetStart7E"), trace.get("targetAtActive7E"), current.get("target7E"), trace.get("target"), current.get("target")):
        if value not in (None, ""): return str(value)
    return None


def _type_key(trace: dict[str, Any], current: dict[str, Any]) -> str | None:
    for value in (trace.get("type"), current.get("type")):
        if value not in (None, ""): return str(value)
    return None


def validate(manifest: dict[str, Any], traces: list[dict[str, Any]], sources: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    validate_manifest(manifest)
    counters = {"prospective": Counter(), "discovery": Counter()}
    attack_counts = {"prospective": Counter(), "discovery": Counter()}
    room_counts = {"prospective": Counter(), "discovery": Counter()}
    prospective_targets: set[str] = set(); prospective_types: set[str] = set(); lifecycle_reset_observed = False
    evidence_rows: list[dict[str, Any]] = []; total_seen = 0
    for index, trace in enumerate(traces):
        total_seen += 1
        evidence_class = str(trace.get("evidenceClass") or "discovery")
        if evidence_class not in counters: evidence_class = "discovery"
        matched, detail = trace_matches(trace, manifest)
        if not matched: continue
        counters[evidence_class]["signal"] += 1
        room = _trace_room(trace, f"trace-{index}"); room_counts[evidence_class][room] += 1
        category = classify_trace(trace, manifest); counters[evidence_class][category] += 1
        attack = trace.get("activeAttack"); attack_counts[evidence_class]["A" + str(attack) if attack is not None else "none"] += 1
        current = detail.get("current") if isinstance(detail.get("current"), dict) else {}
        if evidence_class == "prospective":
            target_key = _target_key(trace, current)
            type_key = _type_key(trace, current)
            if target_key is not None: prospective_targets.add(target_key)
            if type_key is not None: prospective_types.add(type_key)
            lifecycle_reset_observed = lifecycle_reset_observed or trace.get("lifecycleReset") is True
        evidence_rows.append({
            "evidenceClass": evidence_class, "roomId": room, "activeAttack": attack, "category": category,
            "leadMs": trace.get("leadMs", trace.get("candidateLastLeadMs", trace.get("signalLeadMs"))),
            "targetStable": trace.get("targetStable"), "sideStable": trace.get("sideStable"), "retargets": trace.get("retargets") or [],
            "target": _target_key(trace, current), "observedType": _type_key(trace, current), "lifecycleReset": trace.get("lifecycleReset") is True,
            "source": trace.get("source"), **detail,
        })
    prospective = counters["prospective"]; gate = manifest.get("gate") or {}
    req_signals = int(gate.get("minProspectiveSignals", 1)); req_rooms = int(gate.get("minProspectiveRooms", 1)); req_zero = bool(gate.get("requireZeroHardMiss", True))
    req_targets = int(gate.get("minDistinctTargets", 0)); req_types = int(gate.get("minObservedTypes", 0)); req_lifecycle = bool(gate.get("requireLifecycleReset", False))
    observed = {
        "minProspectiveSignals": prospective["signal"],
        "minProspectiveRooms": len(room_counts["prospective"]),
        "requireZeroHardMiss": prospective["hardMiss"],
        "minDistinctTargets": len(prospective_targets),
        "minObservedTypes": len(prospective_types),
        "requireLifecycleReset": lifecycle_reset_observed,
    }
    gate_rows = {
        "minProspectiveSignals": {"required": req_signals, "observed": observed["minProspectiveSignals"], "passed": observed["minProspectiveSignals"] >= req_signals},
        "minProspectiveRooms": {"required": req_rooms, "observed": observed["minProspectiveRooms"], "passed": observed["minProspectiveRooms"] >= req_rooms},
        "requireZeroHardMiss": {"required": req_zero, "observed": observed["requireZeroHardMiss"], "passed": observed["requireZeroHardMiss"] == 0 if req_zero else True},
        "minDistinctTargets": {"required": req_targets, "observed": observed["minDistinctTargets"], "passed": observed["minDistinctTargets"] >= req_targets},
        "minObservedTypes": {"required": req_types, "observed": observed["minObservedTypes"], "passed": observed["minObservedTypes"] >= req_types},
        "requireLifecycleReset": {"required": req_lifecycle, "observed": observed["requireLifecycleReset"], "passed": observed["requireLifecycleReset"] is True if req_lifecycle else True},
    }
    pass_gate = all(row["passed"] for row in gate_rows.values())
    verdict = "NO_PROSPECTIVE_EVIDENCE" if prospective["signal"] == 0 else ("PROSPECTIVE_PASS_RESEARCH_ONLY" if pass_gate else "PROSPECTIVE_FAIL_OR_INSUFFICIENT")
    def packed(cls: str) -> dict[str, Any]:
        c = counters[cls]
        return {"signal": c["signal"], "strict": c["strict"], "jitter": c["jitter"], "late": c["late"], "hardMiss": c["hardMiss"], "censored": c["censored"], "rooms": len(room_counts[cls]), "roomSignals": dict(room_counts[cls]), "attacks": dict(attack_counts[cls])}
    return {
        "schema": RESULT_SCHEMA, "candidateId": manifest["id"], "promotion": "research-only", "verdict": verdict,
        "productionPromotionAllowed": False, "counts": {"inputTraces": total_seen, "matchedSignals": len(evidence_rows)},
        "prospective": packed("prospective"), "discovery": packed("discovery"),
        "gate": {**gate_rows, "passed": pass_gate, "supported": sorted(SUPPORTED_GATES), "unsupported": []},
        "safety": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "windowWorkerReplacement": False},
        "sources": sources or [], "evidence": evidence_rows,
        "notes": ["Discovery evidence is reported separately and never satisfies the prospective gate.", "A PASS remains research-only; this framework never promotes a production rule."],
    }


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {k: result[k] for k in ("schema", "candidateId", "verdict", "promotion", "prospective", "discovery", "gate", "safety")} | {"productionPromotionAllowed": False}


def main() -> int:
    ap = argparse.ArgumentParser(description="WOF 通用前瞻验证器（只读）")
    ap.add_argument("manifest"); ap.add_argument("corpus", nargs="+"); ap.add_argument("--session"); ap.add_argument("--output"); ap.add_argument("--compact-output")
    args = ap.parse_args()
    try:
        manifest = validate_manifest(load_json(args.manifest)); session = validate_session(load_json(args.session), manifest) if args.session else None
        traces, sources = load_traces(args.corpus, session); result = validate(manifest, traces, sources)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"验证失败：{exc}"); return 2
    text = json.dumps(compact_result(result), ensure_ascii=False, indent=2); print(text)
    if args.output: Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.compact_output: Path(args.compact_output).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
