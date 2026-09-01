# WOF Alpha QA Audit Status

Updated: 2026-09-01
QA status: **BLOCKED**
Artifact: `wof-alpha-rc1`

## Release decision

Do **not** mark Alpha QA PASS yet.

Open blockers:

| ID | Severity | Summary |
|---|---|---|
| ALPHAQA-001 | P0 | Runtime/build guard assigns the supported `wofr1` signature from layout-only evidence and can fail open on an unsupported lookalike revision. |
| ALPHAQA-002 | P1 | Same-type same-slot replacement can inherit a warning from the prior enemy episode. |
| ALPHAQA-003 | P1 | Core can publish multiple simultaneous warnings but HUD silently renders only `warnings[0]`. |
| ALPHAQA-004 | P1 | Supported load path still requires manual selection of the live `gstyphoon.js` Worker console plus a second top-page console load. |

Detailed reproduction and fix requirements are in `FINDINGS.md`.

## Mandatory audit summary

### 1. Frozen-rule fidelity — PASS

Direct source comparison was performed against the WOF-051 production audit and its inherited Browser validators.

- T16 exact predicate matches WOF-038 lineage and remains danger-only.
- T20 B0->B255 exact transition predicate matches the WOF-038/WOF-043R lineage.
- D867BA and D8811E exact descriptor predicates match audited Browser source and remain non-type-constrained where appropriate.
- T18 BODY7512/TM4 and BODY7520/TM4 level predicates match WOF-045R/046R production-shadow lineage.
- T18 BODY4728/A4/B2/TM1 is excluded from attack-specific production logic.
- No T23, T24 or local/discovery candidate was found in the release rule engine.

### 2. Runtime identity / fail-closed — FAIL (P0)

The current positive guard checks memory/layout compatibility but not actual game/build/revision identity. `validateIdentityProbe()` can return `ok:true` and the declared `wofr1-world-921002-browser-layout-v1` signature with no build identifier in its input.

### 3. Read-only / interference — STATIC PASS; REAL-BROWSER GL CHECK PENDING

Static/manual audit found:

- no game RAM write path;
- no keyboard/gameplay input injection;
- worker exception path stops timer and clears engine warnings;
- HUD GL work is wrapped in snapshot/restore/finally paths.

Still pending after blockers are fixed:

- real Browser rendering/performance acceptance;
- visible verification that WebGL state restoration does not disturb gameplay.

### 4. Target / retarget / side — CORE PASS; LIFECYCLE BLOCKED

Pass:

- `enemy+0x7E` is reread every poll;
- P1/P2/P3 mapping uses 0/4/8;
- target and threat side are recomputed from current snapshot;
- unknown selector/geometry stays silent;
- slot disappearance and type change clear watches.

Blocked:

- same-type slot replacement is not distinguishable from continuity, so a watch can transfer to a new enemy episode.

### 5. Warning lifecycle — FAIL (P1)

Pass:

- horizon expiration;
- slot-gone cleanup;
- type-change cleanup;
- active-edge resolution;
- level-rule cycle deduplication;
- worker reload calls prior runtime stop/clear.

Fail:

- same-type slot reuse/replacement can retain a prior watch;
- simultaneous warnings are silently reduced to one row by the HUD.

### 6. Regression independence — QA HARNESS ADDED; CURRENT ARTIFACT EXPECTED BLOCKED

`parallel/ALPHAQA/independent_qa.mjs` is separate from product regression and adds adversarial cases for:

- layout-lookalike identity;
- same-type replacement;
- multiple simultaneous warnings;
- normal-user load-path assumptions;
- stronger heap-alias write scan;
- frozen-rule inventory / BODY4728 exclusion;
- retarget + unknown silence;
- slot-gone/type-change cleanup.

The existing product regression's 143-count replay is a synthetic reconstruction from WOF-051 aggregate counts, not a replay of retained raw per-poll Browser evidence; it is therefore not treated as independent proof by QA.

### 7. Packaging / user path — FAIL (P1)

The repository is public, so GitHub private-auth loading is not the issue. The blocker is operational: a normal user still has to identify the live emulator Worker execution context and eval the loader in two DevTools consoles.

## Retest conditions

QA should re-run after product owner fixes all open P0/P1 items. Retest must include the independent QA harness and a short real-Browser acceptance focused on:

- supported build recognized;
- unsupported/unknown lookalike rejected;
- same-type replacement / scene transition cleanup;
- simultaneous warning presentation;
- P1/P2/P3 retarget and side update;
- HUD rendering/performance and reload safety;
- normal user load path.

Until then, status remains **QA BLOCKED**.