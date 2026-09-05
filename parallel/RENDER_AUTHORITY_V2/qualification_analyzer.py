from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "wof-render-source-qualification-v1"
CAPTURE_SCHEMA = "wof-render-authority-capture-v2"
PROOF_SCHEMA = "wof-renderer-source-proof-v1"
PASS = "PASS"
INCONCLUSIVE = "INCONCLUSIVE"
REJECTED = "REJECTED"

FORBIDDEN_SOURCE_TOKENS = (
    "screenshot",
    "world_projection",
    "world-projection",
    "world projection",
    "projected_world",
    "guessed",
    "heuristic_address",
    "nearest_object",
    "nearest-object",
    "prior_point",
    "prior-point",
)

REVERSE_TRACE = [
    {
        "edge": "measurement_runner -> exact World discovery/runtime authority -> render_authority_capture launcher binding",
        "status": "PROVEN_REPOSITORY_EDGE",
    },
    {
        "edge": "render_authority_capture -> exact Worker/WASM -> wof_render_authority_capture_worker.js",
        "status": "PROVEN_REPOSITORY_EDGE",
    },
    {
        "edge": "capture worker -> Module HEAP structural 8-byte [x,y,tile,attr] candidate scan -> candidateTimeline",
        "status": "PROVEN_REPOSITORY_EDGE",
    },
    {
        "edge": "exact game RAM actor lifecycle/generation samples -> capture evidence",
        "status": "PROVEN_REPOSITORY_EDGE",
        "note": "Actor/world coordinates are diagnostic context only, never production position authority.",
    },
    {
        "edge": "displayed CPS1 frame renderer/object submission -> exact HEAP object source/pointer/window",
        "status": "UNPROVEN_REQUIRED_EDGE",
        "note": "No checked-in source/runtime causal edge currently establishes this mapping; structural similarity cannot substitute for it.",
    },
    {
        "edge": "qualified direct renderer/object source -> wof-render-object-frame-v1 canonical producer",
        "status": "GATED_ON_REQUIRED_EDGE",
    },
]


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("qualification input must be a JSON object")
    return value


def _unwrap(value: dict[str, Any]) -> dict[str, Any]:
    for key in ("capture", "captureResult", "renderAuthorityCapture"):
        candidate = value.get(key)
        if isinstance(candidate, dict) and candidate.get("schema") == CAPTURE_SCHEMA:
            return candidate
    return value


def _stable_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _contains_forbidden(value: Any) -> list[str]:
    text = _stable_json(value).lower()
    return sorted({token for token in FORBIDDEN_SOURCE_TOKENS if token in text})


def _int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _region_key(region: Any) -> str | None:
    if not isinstance(region, dict):
        return None
    offset = _int(region.get("heapOffset"))
    byte_order = region.get("byteOrder")
    if offset is None or byte_order not in {"LE16", "BE16"}:
        return None
    return f"{byte_order}:{offset}"


def _timeline_diagnostics(capture: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    timeline = capture.get("candidateTimeline")
    if not isinstance(timeline, list):
        return {
            "frames": 0,
            "uniqueCandidates": 0,
            "stableCandidates": [],
            "uniqueStableCandidate": None,
            "actorGenerationTransitions": 0,
            "epochStampedFrames": 0,
        }, [], ["candidateTimeline missing or not an array"]

    rejects: list[str] = []
    gaps: list[str] = []
    seen: Counter[str] = Counter()
    orders: dict[int, set[str]] = defaultdict(set)
    frame_times: list[int] = []
    p1_generations: list[int] = []
    epoch_stamped = 0
    expected_runtime = capture.get("runtimeEpoch")
    expected_renderer = capture.get("rendererEpoch")
    expected_authority = capture.get("authorityKey")

    for index, frame in enumerate(timeline):
        if not isinstance(frame, dict):
            rejects.append(f"timeline frame {index} is not an object")
            continue
        at = _int(frame.get("at"))
        if at is not None:
            frame_times.append(at)
        epochs_present = any(k in frame for k in ("runtimeEpoch", "rendererEpoch", "authorityKey"))
        if epochs_present:
            epoch_stamped += 1
            if frame.get("runtimeEpoch") != expected_runtime:
                rejects.append(f"timeline frame {index} runtimeEpoch mismatch")
            if frame.get("rendererEpoch") != expected_renderer:
                rejects.append(f"timeline frame {index} rendererEpoch mismatch")
            if frame.get("authorityKey") != expected_authority:
                rejects.append(f"timeline frame {index} authorityKey mismatch")
        lifecycle = frame.get("p1Lifecycle")
        if isinstance(lifecycle, dict):
            generation = _int(lifecycle.get("generation"))
            if generation is not None:
                p1_generations.append(generation)
        regions = frame.get("regions")
        if not isinstance(regions, list):
            rejects.append(f"timeline frame {index} regions missing or malformed")
            continue
        frame_keys: set[str] = set()
        for region in regions:
            key = _region_key(region)
            if key is None:
                rejects.append(f"timeline frame {index} contains malformed candidate identity")
                continue
            offset = _int(region.get("heapOffset"))
            byte_order = region.get("byteOrder")
            assert offset is not None and isinstance(byte_order, str)
            orders[offset].add(byte_order)
            entries = region.get("entries")
            if not isinstance(entries, list) or not entries:
                rejects.append(f"candidate {key} has no decoded entries in frame {index}")
                continue
            for entry_index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    rejects.append(f"candidate {key} entry {entry_index} malformed")
                    continue
                for word in ("xWord", "yWord", "tileWord", "attrWord"):
                    v = _int(entry.get(word))
                    if v is None or v < 0 or v > 0xFFFF:
                        rejects.append(f"candidate {key} entry {entry_index} impossible {word}")
            frame_keys.add(key)
        for key in frame_keys:
            seen[key] += 1

    if any(frame_times[i] >= frame_times[i + 1] for i in range(len(frame_times) - 1)):
        rejects.append("candidate timeline cadence is non-monotonic")
    if any(len(byte_orders) > 1 for byte_orders in orders.values()):
        rejects.append("same heap offset appears with inconsistent byte order")

    frames = len(timeline)
    stable = sorted(key for key, count in seen.items() if frames and count == frames)
    unique_stable = stable[0] if len(stable) == 1 else None
    transitions = sum(1 for a, b in zip(p1_generations, p1_generations[1:]) if a != b)
    if frames and epoch_stamped != frames:
        gaps.append("per-frame runtime/renderer/authority epoch stamps are incomplete")
    if not stable and frames:
        gaps.append("no candidate remains layout-stable across the full bounded timeline")
    if len(stable) > 1:
        gaps.append("multiple candidates remain equally layout-stable; uniqueness is not established")
    if unique_stable:
        gaps.append("one layout-stable candidate exists, but layout stability is not displayed-frame renderer causality")

    return {
        "frames": frames,
        "uniqueCandidates": len(seen),
        "stableCandidates": stable,
        "uniqueStableCandidate": unique_stable,
        "actorGenerationTransitions": transitions,
        "epochStampedFrames": epoch_stamped,
    }, sorted(set(rejects)), sorted(set(gaps))


def _proof_reasons(capture: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    proof = capture.get("rendererSourceProof")
    if proof is None:
        return False, [], ["rendererSourceProof is absent; displayed-frame renderer/object causality is unproven"]
    if not isinstance(proof, dict):
        return False, ["rendererSourceProof is malformed"], []

    rejects: list[str] = []
    gaps: list[str] = []
    if proof.get("schema") != PROOF_SCHEMA:
        rejects.append("rendererSourceProof schema mismatch")
    if proof.get("proofClass") != "DIRECT_DISPLAYED_FRAME_RENDER_OBJECT":
        gaps.append("proofClass is not DIRECT_DISPLAYED_FRAME_RENDER_OBJECT")
    if proof.get("displayedFrameCausalLink") is not True:
        gaps.append("displayed-frame causal link is not explicitly proven")
    if proof.get("coordinateAuthority") != "NATIVE_RENDERER_OBJECT_384X224":
        gaps.append("native 384x224 renderer/object coordinate authority is not proven")
    derivation = proof.get("addressDerivation")
    if not isinstance(derivation, dict):
        gaps.append("source address/pointer derivation evidence is missing")
    else:
        if derivation.get("kind") not in {"SOURCE_TRACED_POINTER", "DIRECT_RENDER_HOOK", "EXPORTED_RENDERER_POINTER"}:
            gaps.append("address/pointer derivation is not source-traced or directly hooked")
        if derivation.get("guessed") is not False:
            rejects.append("renderer source address/pointer derivation is guessed or unspecified")
    if proof.get("screenshotCoordinatesUsed") is not False:
        rejects.append("screenshot coordinates are used or not explicitly excluded")
    if proof.get("worldProjectionCoordinatesUsed") is not False:
        rejects.append("world projection coordinates are used or not explicitly excluded")
    association = proof.get("actorAssociation")
    if not isinstance(association, dict):
        gaps.append("explicit actor association/generation proof is missing")
    else:
        if association.get("explicit") is not True:
            gaps.append("actor association is not explicit")
        if association.get("generationBound") is not True:
            gaps.append("actor association is not bound to generation")
        if association.get("ambiguous") is not False:
            rejects.append("actor association is ambiguous or ambiguity is unspecified")
    for field in ("runtimeEpoch", "rendererEpoch", "authorityKey"):
        if proof.get(field) != capture.get(field):
            rejects.append(f"rendererSourceProof {field} mismatch")
    trace = proof.get("sourceTrace")
    if not isinstance(trace, list) or len(trace) < 2 or any(not isinstance(x, str) or not x.strip() for x in trace):
        gaps.append("sourceTrace does not contain a concrete causal chain")
    samples = _int(proof.get("directFrameSamples"))
    if samples is None or samples < 3:
        gaps.append("fewer than three direct displayed-frame renderer/object samples are proven")
    if proof.get("frameGenerationMonotonic") is not True:
        gaps.append("renderer frame generation monotonicity is not proven")
    return not rejects and not gaps, sorted(set(rejects)), sorted(set(gaps))


def analyze_capture(input_value: dict[str, Any]) -> dict[str, Any]:
    capture = _unwrap(input_value)
    reasons: list[str] = []
    gaps: list[str] = []
    rejects: list[str] = []

    if capture.get("schema") != CAPTURE_SCHEMA:
        rejects.append(f"capture schema must be {CAPTURE_SCHEMA}")

    for key, expected in (
        ("readOnly", True),
        ("ramWrites", 0),
        ("inputInjection", False),
        ("overlayEnabled", False),
    ):
        if capture.get(key) != expected:
            rejects.append(f"safety boundary mismatch: {key}={capture.get(key)!r}")

    if capture.get("worldSha256") in (None, ""):
        gaps.append("exact World identity is missing")
    for field in ("authorityKey", "runtimeEpoch", "rendererEpoch"):
        if not isinstance(capture.get(field), str) or not capture.get(field):
            gaps.append(f"{field} is missing")

    claimed_source_fields = {
        "rendererSource": capture.get("rendererSource"),
        "productionCoordinateSource": capture.get("productionCoordinateSource"),
        "canonicalNativeContract": capture.get("canonicalNativeContract"),
    }
    forbidden_claims = _contains_forbidden(claimed_source_fields)
    if forbidden_claims:
        rejects.append("capture production-source claims contain forbidden token(s): " + ", ".join(forbidden_claims))

    timeline, timeline_rejects, timeline_gaps = _timeline_diagnostics(capture)
    rejects.extend(timeline_rejects)
    gaps.extend(timeline_gaps)

    proof_ok, proof_rejects, proof_gaps = _proof_reasons(capture)
    rejects.extend(proof_rejects)
    gaps.extend(proof_gaps)

    qualification = capture.get("rendererSourceQualification")
    if qualification == "UNVERIFIED_CANDIDATE_ONLY":
        reasons.append("capture correctly labels structural regions as UNVERIFIED_CANDIDATE_ONLY")
    elif qualification not in (None, "UNVERIFIED_CANDIDATE_ONLY") and not proof_ok:
        rejects.append("capture claims renderer-source qualification without satisfying direct proof contract")

    rejects = sorted(set(rejects))
    gaps = sorted(set(gaps))
    reasons = sorted(set(reasons))

    if rejects:
        status = REJECTED
    elif proof_ok:
        status = PASS
        reasons.append("direct displayed-frame renderer/object causality satisfies rendererSourceProof v1")
    else:
        status = INCONCLUSIVE

    if status == PASS:
        owner_action = None
        blocking_edge = None
        producer = {
            "schema": "wof-render-object-frame-v1",
            "rendererSource": {"proven": True},
            "nativeWidth": 384,
            "nativeHeight": 224,
            "ready": True,
        }
    else:
        owner_action = (
            "Run one bounded exact-World normal-play capture with the one-command W3 runner; "
            "the analyzer will qualify the resulting evidence automatically. No clicking/calibration is required."
        ) if status == INCONCLUSIVE else None
        blocking_edge = (
            "displayed CPS1 frame renderer/object submission -> exact source/pointer/object rows"
            if status == INCONCLUSIVE else None
        )
        producer = {
            "schema": "wof-render-object-frame-v1",
            "rendererSource": {"proven": False},
            "nativeWidth": 384,
            "nativeHeight": 224,
            "ready": False,
            "suppressed": True,
        }

    return {
        "schema": SCHEMA,
        "status": status,
        "rendererAuthority": status,
        "repoQualificationPolicy": "DETERMINISTIC_FAIL_CLOSED",
        "captureIdentity": {
            "worldSha256": capture.get("worldSha256"),
            "authorityKey": capture.get("authorityKey"),
            "runtimeEpoch": capture.get("runtimeEpoch"),
            "rendererEpoch": capture.get("rendererEpoch"),
        },
        "timelineDiagnostics": timeline,
        "reasons": sorted(set(reasons)),
        "rejections": rejects,
        "evidenceGaps": gaps,
        "reverseTrace": REVERSE_TRACE,
        "blockingProofEdge": blocking_edge,
        "ownerAction": owner_action,
        "productionCoordinatePolicy": {
            "allowed": ["direct displayed-frame native renderer/object coordinates with explicit actor association + generation"],
            "forbidden": ["screenshot coordinates", "world projection", "guessed/heuristic address", "nearest object", "prior/stale point"],
        },
        "canonicalProducerReadiness": producer,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# W3 Renderer/Object Source Qualification",
        "",
        f"- Status: **{report.get('status')}**",
        f"- Policy: `{report.get('repoQualificationPolicy')}`",
    ]
    identity = report.get("captureIdentity") or {}
    for field in ("worldSha256", "authorityKey", "runtimeEpoch", "rendererEpoch"):
        lines.append(f"- {field}: `{identity.get(field)}`")
    lines += ["", "## Deterministic findings"]
    for reason in report.get("reasons") or []:
        lines.append(f"- {reason}")
    for gap in report.get("evidenceGaps") or []:
        lines.append(f"- GAP: {gap}")
    for rejection in report.get("rejections") or []:
        lines.append(f"- REJECT: {rejection}")
    lines += ["", "## Reverse trace"]
    for edge in report.get("reverseTrace") or []:
        lines.append(f"- `{edge.get('status')}` — {edge.get('edge')}")
        if edge.get("note"):
            lines.append(f"  - {edge.get('note')}")
    lines += ["", "## Production coordinate boundary"]
    policy = report.get("productionCoordinatePolicy") or {}
    for value in policy.get("allowed") or []:
        lines.append(f"- ALLOW: {value}")
    for value in policy.get("forbidden") or []:
        lines.append(f"- FORBID: {value}")
    if report.get("blockingProofEdge"):
        lines += ["", "## Blocking proof edge", f"- {report['blockingProofEdge']}"]
    if report.get("ownerAction"):
        lines += ["", "## Owner action", f"- {report['ownerAction']}"]
    return "\n".join(lines) + "\n"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic fail-closed W3 renderer/object source qualification")
    parser.add_argument("capture_json", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = analyze_capture(_load(args.capture_json))
    json_out = args.json_out or args.capture_json.with_name("RENDER_SOURCE_QUALIFICATION.json")
    md_out = args.md_out or args.capture_json.with_name("RENDER_SOURCE_QUALIFICATION.md")
    _write_json(json_out, report)
    md_out.write_text(render_markdown(report), encoding="utf-8")
    print(f"{report['status']}\n{json_out}\n{md_out}")
    return 2 if report["status"] == REJECTED else 0


if __name__ == "__main__":
    raise SystemExit(main())
