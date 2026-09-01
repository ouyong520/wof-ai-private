# HUDANCHOR One-Click Browser Proof Automation

Status: repository-side harness ready; real Browser proof is intentionally fail-closed.

## Goal

Replace the old Worker Console + Top Console + pasted-JS flow with one CDP process. The harness:

- discovers the live WOF page and its native Worker through current `parallel/PYLAUNCH` Discovery V2;
- requires the exact World 921031 SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
- attaches to page and Worker directly over localhost CDP;
- installs read-only sampling helpers without replacing `window.Worker`;
- samples live P1 `x/y/z`, bounded camera candidates, canvas/content rect and drawing-buffer size;
- synchronizes Worker/page epochs and fails closed on stale pairs;
- scores camera candidates and Y-depth/Z-jump model evidence;
- runs the strict `hudanchor_proof_safe.py` policy and writes `results/HUDANCHOR_PROOF.json` plus `HUDANCHOR_PROOF_中文摘要.txt`;
- records `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`.

## Owner UX

Preferred path:

1. Open WOF using the existing PYLAUNCH / Browser Fleet localhost-CDP browser.
2. Double-click `RUN_HUDANCHOR_PROOF_CN.cmd`.
3. Play normally for the bounded capture: move far enough to make the background scroll, move in floor depth, and jump once.
4. If an absolute visual anchor is still needed, click **once** at the desired P1 above-head warning center.
5. Read only `results/HUDANCHOR_PROOF.json`.

No DevTools, Worker Console, Top Console, or pasted JavaScript is required.

## Important proof rule

A single calibration click is enough to set an absolute bias **only after** the vertical projection model is independently proven. It cannot by itself distinguish `Y-Z`, `Y+Z`, and `Y` after those models are all forced through the same one point.

Therefore the supported strict entry point never turns one click into a fake proof. It returns `BLOCKED` when the live trace has no independent visual/projection oracle, when camera confidence is weak, when page/Worker epochs are stale, or when the World identity/safety invariants fail.

It can consume a projection-reference JSON with:

```json
{
  "worldSha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62",
  "visuallyProven": true,
  "verticalModel": "Y-Z",
  "absoluteAnchorProven": false
}
```

via `--projection-model PATH`. When `absoluteAnchorProven` is not true, one calibration click is still required. If the reference itself proves the absolute above-head anchor, the click is eliminated.

The concurrent player-projection reverse lane may provide that evidence; this harness does not assume its outcome.

## Offline verification

Run:

```text
python -m unittest discover -s tests -v
```

Coverage includes two-context sync, camera-scroll scoring/confidence, depth/jump excitation, wrong identity, stale epochs, resize/fullscreen mapping, missing page/Worker, ambiguous-model fail-closed behavior, exact good traces, calibration gating, and all safety invariants.

The raw `hudanchor_proof.py` file is the sampling engine. The supported entry point is `RUN_HUDANCHOR_PROOF_CN.cmd` / `hudanchor_proof_safe.py`, which installs the strict fail-closed policy before collection.
