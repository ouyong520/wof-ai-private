# Alpha V1 Bounded Live Acceptance Owner Flow V2

stageId: `ALPHA_V1_BOUNDED_LIVE_ACCEPTANCE_OWNER_FLOW_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.bounded-live-acceptance-owner-flow-v2`
dedupMode: `exclusive`

Priority: **V1 release usability / final owner-action simplification**

Repository: `ouyong520/wof-ai-private`

## PM decision to encode

Final Alpha V1 real Browser/WOF acceptance must NOT require the Owner to play or finish a full game.

The Owner may enter an already-active public/other-player room. The acceptance flow should be bounded to roughly 5–10 minutes of practical observation/action, provided the required evidence windows are actually exercised.

Do not loosen any proof or non-drift requirement merely to make the flow shorter.

## Goal

Produce the exact final Owner-facing bounded live acceptance procedure that will be used after current repository gates are green.

The procedure must distinguish three independent questions:

1. danger detection coverage: did a currently supported danger rule actually fire when its supported move occurred?;
2. player-head projection: when a warning exists, does `[危险]` stay attached to the correct player without visible drift?;
3. enemy-head target projection: do `1P / 2P / 3P` labels stay attached to the correct enemy and switch immediately on retarget?

A warning not appearing for an unsupported/unmapped move must not be misclassified as a projection failure. Conversely, a supported/proven danger move occurring without a warning is a detection blocker.

## Required reads

Re-read current `main` and current:

- Alpha V1 player-head / enemy-head requirements;
- `parallel/PM/ALPHA_V1_BACK_JUMP_NONDRIFT_ACCEPTANCE_ADDENDUM.md`;
- One-Session live-proof prep/contracts;
- current player warning and enemy label QA results;
- current production danger rule set;
- current Owner OneClick V4 state/result if available;
- current proof-authority hardening state, but do not interfere with its implementation.

## Required Owner flow

Design a single concise Chinese checklist for this real session:

- launch final OneClick candidate;
- join an already active room; no requirement to host or complete a game;
- confirm current World/runtime attaches normally;
- observe moving enemies with `1P/2P/3P` labels;
- exercise left/right, lane-depth movement, normal jump, explicit rear/back-jump, rapid forward movement and camera/whole-screen scroll;
- observe at least one live retarget if naturally available;
- resize/fullscreen/DPR remap once;
- if possible observe death/respawn or equivalent current-player lifecycle replacement;
- verify stale/invalid authority falls back/hides rather than drifting;
- for `[危险]`, require an actual currently-supported production warning event, not merely any enemy attack;
- if the session lacks a supported danger event, classify the player-warning live-evidence item as `NOT EXERCISED`, not PASS and not automatic FAIL;
- if a supported move is positively identifiable and warning is absent, classify as detection FAIL;
- if warning exists but head anchor drifts/falls behind/stays at old location, classify as projection FAIL.

The flow must explicitly cover the rear/back-jump addendum through takeoff, reverse horizontal travel, apex, descent and landing.

## Output

Write a durable repository artifact containing:

- preconditions;
- 5–10 minute owner checklist;
- exact PASS / FAIL / NOT EXERCISED classifications per surface;
- what screenshot/video is useful only when a failure occurs;
- what the Owner should report in one short line;
- fail-closed rule: no real live evidence means `NOT RELEASED`, never synthetic substitution.

Keep the procedure human-readable and short enough that the Owner can follow it without DevTools or manual scripts.

## Boundaries

- Preparation/documentation only.
- No Browser/WOF launch in this stage.
- No product/runtime changes.
- No danger-rule/target-semantic/Transport changes.
- Do not modify OneClick implementation.
- Do not wait for Hardening Fix V2 merely to write the procedure; record current gate dependencies accurately.

## Dedup

Strict canonical dedup v2. If an equivalent current Owner live procedure already encodes the active-room 5–10 minute flow and the PASS/FAIL/NOT EXERCISED distinctions above, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

## Success

`COMPLETE — ALPHA V1 BOUNDED LIVE ACCEPTANCE OWNER FLOW V2 — ACTIVE-ROOM 5–10 MINUTE FINAL SESSION DEFINED`

## Failure

`BLOCKED — ALPHA V1 BOUNDED LIVE ACCEPTANCE OWNER FLOW V2 — <precise blocker>`
