from __future__ import annotations

import math
import statistics
from typing import Any

import hudanchor_proof as base

WORLD_SHA256 = base.WORLD_SHA256
SAFETY = base.SAFETY
_num = base._num
fit_bias = base.fit_bias
model_native_y = base.model_native_y


def evaluate_trace(trace: list[dict[str, Any]], *, projection_reference: dict[str, Any] | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    if not trace:
        return {"result": "BLOCKED", "reasons": ["missing Worker/page samples"], "modelScores": {}, **SAFETY}

    if not all(all(s.get(k) == v for k, v in SAFETY.items()) for s in trace):
        reasons.append("safety invariant mismatch")
    if not all(s.get("identitySha256") == WORLD_SHA256 for s in trace):
        reasons.append("wrong World identity")

    try:
        skews = [abs(float(s["pageEpochMs"]) - float(s["workerEpochMs"])) for s in trace]
        max_skew = max(skews)
    except (KeyError, TypeError, ValueError):
        max_skew = math.inf
    if max_skew > 250:
        reasons.append("stale/two-context epoch skew")
    if not all(bool(s.get("pageFound")) for s in trace):
        reasons.append("missing page")
    if not all(bool(s.get("workerFound")) for s in trace):
        reasons.append("missing Worker")

    mapping_keys: list[tuple[float, float, int, int]] = []
    mapping_valid = True
    for s in trace:
        c, d = s.get("canvas") or {}, s.get("drawingBuffer") or {}
        try:
            key = (round(float(c["width"]), 3), round(float(c["height"]), 3), int(d["width"]), int(d["height"]))
            mapping_keys.append(key)
            mapping_valid &= all(v > 0 for v in key)
        except (KeyError, TypeError, ValueError):
            mapping_valid = False
    if not mapping_valid:
        reasons.append("invalid resize/fullscreen mapping")

    cameras = [s["camera"] for s in trace if isinstance(s.get("camera"), dict)]
    addresses = [str(c.get("address")) for c in cameras if c.get("address")]
    camera_stable = bool(addresses) and len(set(addresses)) == 1
    scores = [float(c["proofScore"]) for c in cameras if _num(c.get("proofScore")) is not None]
    camera_score_median = statistics.median(scores) if scores else 0.0
    camera_confident = camera_stable and len(scores) >= 5 and camera_score_median >= 6.5
    if not camera_stable:
        reasons.append("ambiguous/unstable camera model")
    elif not camera_confident:
        reasons.append("camera model confidence too low")

    players = [s["player"] for s in trace if isinstance(s.get("player"), dict)]
    def span(k: str) -> float:
        vals = [float(p[k]) for p in players]
        return max(vals) - min(vals) if vals else 0.0
    x_span, depth_span, jump_span = span("x"), span("y"), span("z")
    excitation = {"xSpan": round(x_span, 3), "depthSpan": round(depth_span, 3), "jumpSpan": round(jump_span, 3)}
    if x_span < 8:
        reasons.append("insufficient horizontal movement")
    if depth_span < 4:
        reasons.append("insufficient depth movement")
    if jump_span < 4:
        reasons.append("insufficient jump movement")

    visual = [(s, s["visualReference"]) for s in trace if isinstance(s.get("visualReference"), dict)]
    model_scores: dict[str, Any] = {}
    for name in ("Y-Z", "Y+Z", "Y"):
        predicted, observed = [], []
        for s, ref in visual:
            p = s.get("player")
            y = _num(ref.get("nativeY"))
            if isinstance(p, dict) and y is not None:
                predicted.append(model_native_y(p, name))
                observed.append(y)
        if len(predicted) >= 2:
            bias, err = fit_bias(predicted, observed)
            model_scores[name] = {"visualSamples": len(predicted), "bias": round(bias, 4), "rmsNativePx": round(err, 4)}
        elif len(predicted) == 1:
            model_scores[name] = {"visualSamples": 1, "bias": round(observed[0] - predicted[0], 4), "rmsNativePx": None}
        else:
            model_scores[name] = {"visualSamples": 0, "bias": None, "rmsNativePx": None}

    chosen = None
    if projection_reference:
        ref_ok = projection_reference.get("worldSha256") == WORLD_SHA256 and projection_reference.get("visuallyProven") is True
        ref_model = projection_reference.get("verticalModel")
        if ref_ok and ref_model in model_scores:
            chosen = str(ref_model)
            ref_camera = projection_reference.get("cameraAddress")
            if ref_camera and camera_stable and str(ref_camera).upper() != str(addresses[0]).upper():
                reasons.append("live camera address differs from projection reference")
            if projection_reference.get("absoluteAnchorProven") is not True and len(visual) < 1:
                reasons.append("absolute above-head anchor not calibrated/proven")
        else:
            reasons.append("projection reference is absent/unproven/wrong identity")
    else:
        ranked = [(m, q["rmsNativePx"]) for m, q in model_scores.items() if q["rmsNativePx"] is not None]
        ranked.sort(key=lambda row: float(row[1]))
        if len(ranked) >= 2 and ranked[0][1] <= 2.5 and ranked[1][1] - ranked[0][1] >= 2.0:
            chosen = ranked[0][0]
        else:
            reasons.append("vertical model ambiguous without an independent visual/projection oracle")
        if len(visual) == 1:
            chosen = None

    calibration = None
    if visual:
        s0, ref0 = visual[0]
        p0, c0 = s0.get("player"), s0.get("camera")
        nx, ny = _num(ref0.get("nativeX")), _num(ref0.get("nativeY"))
        cv = _num(c0.get("value")) if isinstance(c0, dict) else None
        if isinstance(p0, dict) and nx is not None and ny is not None and cv is not None:
            calibration = {
                "nativeX": round(nx, 4), "nativeY": round(ny, 4),
                "xBias": round(nx - (float(p0["x"]) - cv), 4),
                "verticalBias": model_scores.get(chosen or "", {}).get("bias"),
                "source": ref0.get("kind") or "visual-reference",
            }

    return {
        "result": "PASS" if not reasons and chosen else "BLOCKED",
        "reasons": reasons,
        "verticalModel": chosen,
        "modelScores": model_scores,
        "calibration": calibration,
        "maxContextSkewMs": round(max_skew, 3),
        "cameraStable": camera_stable,
        "cameraConfident": camera_confident,
        "cameraScoreMedian": round(camera_score_median, 4),
        "cameraAddress": addresses[0] if camera_stable else None,
        "mappingChanged": len(set(mapping_keys)) > 1,
        "mappingValid": mapping_valid,
        "excitation": excitation,
        **SAFETY,
    }
