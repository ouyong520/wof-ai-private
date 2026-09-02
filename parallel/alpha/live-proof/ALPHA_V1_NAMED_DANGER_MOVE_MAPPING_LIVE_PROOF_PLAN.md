# Alpha V1 Named Danger Move Mapping — Future Bounded Live-Proof Plan

Status: **REPOSITORY PREPARATION ONLY**

Stage: `ALPHA_V1_NAMED_DANGER_MOVE_MAPPING_LIVE_PROOF_PREP`

## 1. Purpose and authority boundary

This plan exists only to close the current name-authority gap during a future bounded Browser/WOF session. It does **not** change Alpha production rules and it does not treat gameplay familiarity as authority.

Current repository authority entering this plan is deliberately narrow:

- production-enabled numeric rule: `type=18 -> A5440` precursor;
- production-enabled numeric rule: `type=18 -> A5424` precursor;
- `夏侯惇 -> type`: **UNMAPPED**;
- `曹仁 -> type`: **UNMAPPED**;
- `飞身 -> attack ID`: **UNMAPPED**;
- `扑击 -> attack ID`: **UNMAPPED**;
- `冲撞 -> attack ID`: **UNMAPPED**;
- `A5440/A5424 -> Chinese move name`: **UNMAPPED**.

The future session may resolve those mappings. Until the evidence contract below passes, none of them may be promoted from `UNMAPPED`/`AMBIGUOUS` to fact.

Safety boundary for the future evidence run: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

## 2. One exact live-enemy lifecycle is the join authority

Every evidence packet MUST choose one exact enemy lifecycle and use this immutable join key for every row in that packet:

`lifecycleKey = <runId>/<slot>/<lifecycleGeneration>/<numericType>`

Required lifecycle fields:

- `runId`;
- numeric `slot`;
- numeric/string `lifecycleGeneration` exactly as emitted by the live authority source;
- numeric enemy `type` exactly as emitted by the live authority source;
- first/last timestamp for the packet;
- raw source row/frame references.

A slot reuse, lifecycle-generation change, type change, source-generation change, or unresolvable gap ends the lifecycle packet. Evidence from the old and new lifecycle MUST NOT be spliced together.

Time proximity alone never proves lifecycle continuity.

## 3. Chinese enemy identity anchor

A Chinese identity such as `夏侯惇` or `曹仁` is `MAPPED` only when the same lifecycle packet contains an **explicit, reviewable identity anchor** that names that enemy and can be tied to the selected live instance.

Accepted identity-anchor classes:

1. `IN_GAME_EXPLICIT_TEXT`: captured game/UI text visibly names the enemy and the capture proves which live enemy instance it denotes; or
2. `REPOSITORY_APPROVED_EXPLICIT_LABEL`: a future repository authority explicitly approved for this exact Browser/WOF identity namespace, with its authority reference recorded in the packet.

Not accepted as identity authority:

- operator familiarity with the sprite;
- visual resemblance;
- WinKawaks-local interpretation without a separately proven Browser equivalence;
- an old screenshot not tied to the current lifecycle;
- type-number folklore or an unlabeled roster image.

For an identity mapping, record at least **two distinct live numeric samples** inside the same lifecycle packet that agree on `slot + lifecycleGeneration + type`. If no accepted Chinese identity anchor exists, the Chinese-name mapping is `UNMAPPED` even if the numeric type is perfectly observed.

## 4. Visible move anchor

A move label such as `飞身`, `扑击`, or `冲撞` may be supplied by the operator **only when the move is visually unambiguous in the live capture**.

Each move annotation MUST record:

- exact Chinese move label entered by the operator;
- `labelAuthority = OPERATOR_LIVE_VISUAL_UNAMBIGUOUS`;
- video/frame evidence reference;
- visible interval start/end timestamps;
- the lifecycleKey active throughout that interval;
- any ambiguity note.

If the visual action cannot be named unambiguously, use `AMBIGUOUS`; do not choose the closest move name.

## 5. Zero-cycle precursor -> eventual ACTIVE attack evidence

Each candidate move cycle MUST preserve the raw causal sequence rather than only the final attack ID.

For every cycle record:

### 5.1 Cycle identity

- `cycleId`: a session-local stable identifier;
- `cycleOrdinal`;
- `lifecycleKey`;
- raw source row indices/IDs covering the cycle;
- `cycleStartedAt` / `cycleEndedAt`.

A cycle is not joined by timestamp alone. The zero precursor and eventual ACTIVE row must both belong to the same recorded cycle and lifecycleKey.

### 5.2 Zero-cycle precursor tuple

Record the Collector/live-source tuple **verbatim** at the zero precursor:

- timestamp;
- `attack=0`;
- `target7E` as observed at that row;
- `BODY`/body field if supplied;
- `TM`/timing-mode field if supplied;
- every descriptor/state field used by the source/rule, as a raw key/value object;
- raw row reference;
- optional current numeric rule candidate (`T18_5440_CYCLE_BODY7512_TM4_LEVEL_90`, `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`, or `null`) only when exact tuple matching says so.

Do not fill unknown descriptor values from documentation or memory. Missing raw fields remain missing and weaken classification.

### 5.3 Eventual ACTIVE row

Record the first/authoritative eventual ACTIVE row for the same cycle:

- timestamp;
- exact numeric `attackId` directly observed from Collector/live trace, with `attackId != 0`;
- canonical display string `A<attackId>` derived from that numeric value;
- exact primitive numeric `target7E`;
- target label only if the current runtime authority can derive it; otherwise leave the label null and retain raw `target7E`;
- same `slot`;
- same `lifecycleGeneration`;
- same numeric `type`;
- same `cycleId`;
- raw row reference.

The operator MUST NOT type the ACTIVE attack ID from memory or infer it from the precursor rule name.

### 5.4 Transition integrity

The cycle is valid only if:

- zero precursor precedes ACTIVE in source order;
- lifecycleKey remains identical;
- no lifecycle/reset/source-generation discontinuity occurs between them;
- the source identifies both rows as the same cycle;
- ACTIVE attack ID is directly observed rather than predicted.

Record `deltaMs = activeAt - precursorAt`, but do not invent a timing cutoff solely for this mapping prep. Existing live-source cycle authority controls the join.

## 6. Repeat threshold

A single visually labeled attack cycle never creates a named move mapping.

Minimum for `MAPPED`:

- identity mapping: one accepted explicit Chinese identity anchor plus at least **2** distinct agreeing numeric samples in the same lifecycle;
- move mapping: at least **2 distinct complete move cycles** in the same lifecycle, each with the same unambiguous visible move label and the same directly observed ACTIVE attack ID;
- every repeated cycle must independently contain its own zero precursor and ACTIVE row and satisfy transition integrity.

A third or later repeat is encouraged when naturally available. Conflicting attack IDs do not get majority-voted away; they make that move mapping `AMBIGUOUS` until separately explained by stronger evidence.

Evidence from another lifecycle may be retained as supportive replication, but it must remain a separate packet and MUST NOT be used to repair a missing anchor in this lifecycle.

## 7. Classification rules

### `MAPPED`

Use only when all mandatory anchors, lifecycle joins, direct ACTIVE observations, and repeat thresholds pass with no contradiction.

### `AMBIGUOUS`

Use when evidence exists but at least one interpretation is non-unique, including:

- visually unclear move label;
- two different ACTIVE attack IDs observed for the same move label without a stronger discriminator;
- multiple enemies could own the visible move interval;
- cycle join is non-unique;
- lifecycle continuity is questionable;
- accepted anchors disagree.

`AMBIGUOUS` is fail-closed and must not be treated as a mapping.

### `UNMAPPED`

Use when the required authority is absent, including:

- no accepted explicit Chinese enemy identity anchor;
- no direct numeric type sample;
- no zero precursor;
- no eventual ACTIVE row;
- fewer than two complete matching move cycles;
- missing lifecycle/cycle authority prevents a join.

`UNMAPPED` means "not proven by this session", not "the mapping is false".

### Session `PASS`

A future session may return `PASS` for a requested mapping target only when that target is `MAPPED`. A mixed packet can therefore contain some `MAPPED` answers and some `UNMAPPED`/`AMBIGUOUS` answers without silently filling gaps.

## 8. Exact questions the future packet must answer

### 8.1 夏侯惇 -> type

`MAPPED` only if an accepted explicit `夏侯惇` identity anchor is tied to one lifecycleKey and at least two live numeric samples in that lifecycle agree on the same `type`.

Otherwise: `UNMAPPED` or `AMBIGUOUS`.

### 8.2 曹仁 -> type

Same rule as above, independently. Never infer it by exclusion from 夏侯惇.

### 8.3 飞身 / 扑击 / 冲撞 -> ACTIVE attack ID

Each named move is independent. For each one, require at least two complete, visually unambiguous cycles with the same direct ACTIVE attack ID in the same lifecycle.

Do not infer one move's ID from the remaining IDs.

### 8.4 Does A5440 or A5424 equal one of those named moves?

For each named move and each candidate ID:

- `YES` only when that move is `MAPPED` and its repeated direct ACTIVE ID is exactly `5440` or `5424`;
- `NO_OBSERVED_MAPPING` only when the move is `MAPPED` to a stable different ACTIVE ID in the captured scope; this does not prove the game can never use another ID outside scope;
- `AMBIGUOUS` when the same move label yields conflicting ACTIVE IDs or the visual/cycle join is uncertain;
- `UNMAPPED` when repeat/anchor requirements are missing.

Seeing the current T18 precursor alone is never enough to assign a Chinese move name to A5440/A5424.

## 9. Relationship to current production coverage

The mapping proof and the danger-rule decision remain separate:

- if a Chinese enemy is mapped to `type=18`, that proves the identity-to-type relation for the captured authority scope;
- if a named move is mapped to A5440/A5424, that proves the name-to-ACTIVE-ID relation for the captured authority scope;
- only exact observation of the corresponding zero precursor tuple can correlate the named move with the currently enabled numeric precursor rule;
- no result from this mapping session automatically promotes, demotes, broadens, or rewrites any danger rule.

## 10. Operator procedure for the future bounded session

1. Record source commit/runtime manifest and confirm `readOnly=true`, `ramWrites=0`, `inputInjection=false`.
2. Start one bounded evidence run and assign `runId`.
3. Select exactly one live enemy lifecycle; freeze its `slot + lifecycleGeneration + type` into the packet lifecycleKey.
4. Capture an accepted explicit Chinese identity anchor if one becomes available. If none appears, keep Chinese identity `UNMAPPED`; do not substitute familiarity.
5. When one of the requested moves is visually unambiguous, mark its exact video/frame interval and label it live.
6. Export/copy the same cycle's zero precursor tuple and eventual ACTIVE row from the existing Collector/live source, preserving raw row references and timestamps.
7. Confirm lifecycleKey and cycleId match across visual interval, precursor, and ACTIVE row.
8. Repeat the same named move for a second complete independent cycle in the same lifecycle. Preserve conflicts; do not overwrite them.
9. Repeat for other requested moves as the bounded session naturally permits. Do not prolong the session just to force a label.
10. Complete the mapping table and derive only `MAPPED`, `AMBIGUOUS`, or `UNMAPPED` using this plan.
11. Explicitly answer whether A5440/A5424 were mapped to 飞身/扑击/冲撞; if not proven, say so.

## 11. Expected future artifacts

Minimum artifact set for one bounded run:

- one filled copy of `parallel/alpha/live-proof/alpha_v1_named_danger_move_mapping_observation.template.json`;
- referenced raw Collector/live-trace rows or source artifact IDs for every precursor/ACTIVE pair;
- referenced video/frame evidence for every accepted identity or move visual anchor;
- a small terminal summary table derived from the filled JSON, without manual ID inference.

No new production/runtime code is required by this prep.

## 12. Preparation invariants

This repository-preparation stage itself:

- does not launch Browser/WOF;
- does not modify `product/alpha/**`;
- does not promote/demote any danger rule;
- does not alter target semantics;
- does not create a synthetic mapping;
- does not claim 夏侯惇, 曹仁, 飞身, 扑击, 冲撞, A5440, or A5424 have a named relation that current authority has not proven.
