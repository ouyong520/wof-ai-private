# Alpha V1 Named Danger Move Mapping Live-Proof Prep — RESULT

stageId: `ALPHA_V1_NAMED_DANGER_MOVE_MAPPING_LIVE_PROOF_PREP`
dedupKey: `alpha.v1.named-danger-move-mapping-live-proof-prep`
stageStatus: **COMPLETE**
nextAction: **future bounded Browser/WOF mapping session may consume the prepared contract; do not change rules from this prep alone**

Start/source commit: `8880351fe58aeeded404da7c025aaeb87111ce01`
Preparation finalization source HEAD: `fe6f845a1b6a8d7f8a08e70cf8e30415fa5cb6ac`
Canonical claim token: `9e95de2fa1621b5ed3f9995005dd7ec83ec2eebcd6268289`

## Result

The repository now has a minimal fail-closed evidence contract for a future bounded live session to answer the missing Chinese-name ↔ numeric-type ↔ visible-move ↔ ACTIVE-attack-ID questions without guessing and without changing current danger rules.

Created:

1. `parallel/alpha/live-proof/ALPHA_V1_NAMED_DANGER_MOVE_MAPPING_LIVE_PROOF_PLAN.md`
   - commit `616dfa2c7e46e60a8ecdac44762447516c9b58a3`;
2. `parallel/alpha/live-proof/alpha_v1_named_danger_move_mapping_observation.template.json`
   - commit `fe6f845a1b6a8d7f8a08e70cf8e30415fa5cb6ac`.

No executable extractor was added. The missing authority is a live identity/visual correlation, not a repository-side attack-ID computation problem. Introducing another extractor/authority path in this preparation stage would add unnecessary proof surface.

## Current authority preserved

This stage does not alter the incoming authority verdict:

- `type 18 -> A5440` numeric precursor rule: production-enabled;
- `type 18 -> A5424` numeric precursor rule: production-enabled;
- `夏侯惇 -> type`: **UNMAPPED**;
- `曹仁 -> type`: **UNMAPPED**;
- `飞身 -> attack ID`: **UNMAPPED**;
- `扑击 -> attack ID`: **UNMAPPED**;
- `冲撞 -> attack ID`: **UNMAPPED**;
- `A5440/A5424 -> named Chinese move`: **UNMAPPED**.

Nothing in this prep claims otherwise.

## Evidence contract prepared

For one exact live enemy lifecycle, the future packet records:

- `runId`;
- `slot`;
- `lifecycleGeneration`;
- exact numeric enemy `type`;
- first/last timestamps and raw source refs;
- accepted Chinese identity anchor when one exists;
- live visual move label only when unambiguous, with frame/video interval;
- zero-cycle precursor tuple copied verbatim from live/Collector evidence;
- eventual directly observed ACTIVE `attackId`;
- exact `target7E` plus target label only if current runtime authority derives it;
- stable `cycleId`, source order, row refs, and `deltaMs`;
- transition-integrity assertions proving zero and ACTIVE belong to the same lifecycle/cycle;
- repeat counts and explicit contradictions.

Immutable join authority:

`lifecycleKey = <runId>/<slot>/<lifecycleGeneration>/<numericType>`

Slot reuse, generation/type/source-generation changes, or an unresolvable lifecycle gap terminate the packet; old/new lifecycle evidence cannot be spliced.

## Identity authority rule

Chinese enemy identity is not allowed to come from operator familiarity or sprite resemblance.

`MAPPED` requires an explicit reviewable identity anchor tied to the exact lifecycle, such as:

- `IN_GAME_EXPLICIT_TEXT`; or
- a future `REPOSITORY_APPROVED_EXPLICIT_LABEL` for the same Browser/WOF identity namespace.

In addition, at least **2 distinct live numeric samples** inside that lifecycle must agree on `slot + lifecycleGeneration + type`.

If the session never exposes an accepted Chinese identity anchor, `夏侯惇 -> type` or `曹仁 -> type` remains `UNMAPPED` even when the numeric type itself is known perfectly.

## Move authority rule

For `飞身`, `扑击`, or `冲撞`, an operator may supply the move label only as `OPERATOR_LIVE_VISUAL_UNAMBIGUOUS` and only with a reviewable video/frame interval.

`MAPPED` requires at least **2 distinct complete move cycles in the same lifecycle** where all of the following agree:

1. the same unambiguous Chinese move label;
2. same lifecycleKey;
3. complete zero-cycle precursor evidence;
4. same-cycle eventual ACTIVE row;
5. directly observed, nonzero ACTIVE attack ID;
6. transition integrity passes;
7. repeated ACTIVE attack ID is identical.

A conflicting ACTIVE ID is not majority-voted away; it produces `AMBIGUOUS` until a stronger discriminator exists.

## Exact classifications

### `MAPPED`

All mandatory identity/visual/raw/lifecycle/cycle anchors exist, repeat threshold is met, direct ACTIVE IDs agree, and there is no contradiction.

### `AMBIGUOUS`

Evidence exists but has a non-unique interpretation, including unclear move visuals, conflicting ACTIVE IDs, multiple possible enemy owners, uncertain lifecycle/cycle join, or disagreeing accepted anchors.

Fail closed; no mapping claim.

### `UNMAPPED`

Required authority is absent, including no accepted Chinese identity anchor, no direct type sample, no zero precursor, no eventual ACTIVE row, fewer than two complete matching move cycles, or an unresolvable lifecycle/cycle join.

Means "not proven by this session", not "false".

### Future session `PASS`

A requested mapping target may be called `PASS` only when that target is `MAPPED`. A single packet may legitimately leave other targets `UNMAPPED`/`AMBIGUOUS`.

## How the prepared packet answers the requested questions

### 夏侯惇到底对应哪个 type？

Only from an accepted explicit `夏侯惇` identity anchor tied to one lifecycle plus at least two agreeing live numeric type samples. No identity anchor -> `UNMAPPED`; conflicting owner/join -> `AMBIGUOUS`.

### 曹仁到底对应哪个 type？

Same independent rule. Never infer by exclusion from 夏侯惇.

### 飞身 / 扑击 / 冲撞分别对应什么 attack ID？

Each move requires two complete same-lifecycle visual + zero-precursor + ACTIVE cycles with one stable directly observed attack ID. No ID is inferred from rule names or from the remaining candidate IDs.

### A5440/A5424 是否是其中某一招？

For each requested move:

- `YES`: the move is `MAPPED` and the repeated direct ACTIVE ID is exactly `5440` or `5424`;
- `NO_OBSERVED_MAPPING`: the move is `MAPPED` to a stable different ACTIVE ID within the bounded captured scope;
- `AMBIGUOUS`: conflicting IDs or visual/cycle authority;
- `UNMAPPED`: missing anchors/repeats.

Observing the current T18 precursor alone never assigns a Chinese move name to A5440/A5424.

## Future operator steps

1. Pin repository/runtime/Collector authority and confirm `readOnly=true / ramWrites=0 / inputInjection=false`.
2. Start one bounded evidence run and assign `runId`.
3. Select one live enemy lifecycle and freeze `slot + lifecycleGeneration + type` into lifecycleKey.
4. Capture an accepted explicit Chinese identity anchor if one appears; otherwise leave the Chinese identity `UNMAPPED`.
5. Mark a requested move only when visually unambiguous; retain frame/video refs and timestamps.
6. Copy the same cycle's zero precursor tuple and eventual ACTIVE row from existing live/Collector evidence, including raw row refs and exact `target7E`.
7. Verify same lifecycleKey, same cycleId, source order, and no lifecycle/source-generation discontinuity.
8. Repeat the same move for a second complete cycle in the same lifecycle; preserve any conflict.
9. Fill the template and derive only `MAPPED`, `AMBIGUOUS`, or `UNMAPPED`.
10. Explicitly record A5440/A5424 decisions without manual attack-ID inference.

## Expected future evidence artifacts

Minimum bounded-session packet:

- one filled `alpha_v1_named_danger_move_mapping_observation.template.json`;
- raw Collector/live trace references for every zero -> ACTIVE cycle;
- reviewable frame/video evidence for every accepted identity/move visual anchor;
- terminal mapping summary derived from the packet.

## Scope / non-change attestation

- Browser/WOF launched during this prep: **NO**;
- `product/alpha/**` modified: **NO**;
- danger rule promoted/demoted: **NO**;
- target semantics changed: **NO**;
- RAM writes added: **NO**;
- input injection added: **NO**;
- production/runtime executable tooling changed: **NO**;
- repository preparation docs/template added: **YES**.

## Final

**COMPLETE — ALPHA V1 NAMED DANGER MOVE MAPPING LIVE-PROOF PREP — MINIMAL AUTHORITATIVE NAME↔TYPE↔ATTACK EVIDENCE CONTRACT READY**
