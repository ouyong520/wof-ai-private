# Alpha V1 Live Acceptance — Projection Transform + Owner UX Recovery V1

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_PROJECTION_TRANSFORM_OWNER_UX_RECOVERY_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.live-acceptance.projection-transform-owner-ux-recovery-v1`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

This is a focused **implementation recovery**, not QA and not a restart of prior live-acceptance work.

## 0. Mandatory preflight / ownership

Before any task work:

1. re-read current `main`;
2. re-read `parallel/PM/STAGE_DEDUP_GUARD.md` and `parallel/PM/TESTING_CADENCE_POLICY.md`;
3. re-read the latest completed Camera READY recovery result and claims;
4. inspect recent equivalent commits/results/claims;
5. create-only acquire and verify the canonical v2 claim for this exact dedupKey;
6. only after canonical ownership is verified, create and verify the stage claim.

If equivalent current work is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`. If already claimed, stop `ALREADY CLAIMED — SAFE TO CLOSE`.

Do not reuse, overwrite, delete or mutate historical claim tokens.

## 1. Superseding live evidence / starting authority

The immediately preceding accepted repository candidate is:

- packageVersion: `2026.09.02.52c942085c99`
- sourceCommit: `52c942085c99f6814d4389c43d8e5fe626bdea10`
- Camera READY recovery result: `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_CAMERA_AUTHORITY_READY_STABILITY_RECOVERY_V1_RESULT.md`

That recovery is COMPLETE and its successful contracts are frozen inputs to this task, not defects to reopen.

Latest real Owner/WOF evidence on the above package advanced farther than all earlier runs:

- Browser/Page/Worker/WASM exact World 921031 accepted;
- readOnly remained enabled, RAM writes remained 0, input injection remained off;
- Camera reached stable `READY_LATCHED` authority and no longer exhibited the prior READY -> CANDIDATE_AMBIGUOUS conflict;
- examples observed included Camera authority generations `#1` and `#3`, with the latched Camera address shown as `0xFF81B8` in the Owner UI;
- Owner clicked the actual P1 character head region once as instructed and entered post-click projection calibration;
- post-click checklist progressed through camera, horizontal/scroll, depth, jump, WebGL, resize/fullscreen and observed enemy types (including live types 9 and 10 during one run);
- however the simultaneous `Y-Z / Y+Z / Y` candidate markers did not provide a reliable head projection in real play: markers visibly occupied chest/leg/below-feet positions during jump states and large numbers of labels floated away from P1/enemy heads during normal play;
- Owner additionally reported depth/up-down motion where candidate markers moved in the opposite visual direction from the character for at least part of the candidate set;
- no candidate may be promoted merely because it is "closest"; the real acceptance requirement is stable head alignment across P1 + observed enemies + depth/jump/scroll/resize;
- the current UI becomes visually chaotic because all three candidate families are drawn for P1 and multiple enemies simultaneously, making manual model selection impractical for a novice Owner.

The Owner also uploaded `WOF_RESULTS_20260903_085513.zip`. That archive is a generic menu-7/8 diagnostics package, not the authoritative menu-6 live-session ZIP: it contains package `2026.09.02.52c942085c99`, diagnostics, and stale/ordinary `WAITING_WOF` proof material, but does not contain the current `READY_LATCHED -> click -> projection candidate` authority timeline. Do not misinterpret that generic diagnostics ZIP as live proof success or failure.

## 2. Primary defect cluster

Treat the field evidence as one coherent projection-calibration failure cluster:

### A. Projection transform authority is incomplete

The current post-click proof path only compares hard-coded candidate forms equivalent to `Y-Z`, `Y+Z`, and `Y` using a single click-derived bias. Real WOF evidence shows that this model family / transform authority is not sufficient to produce stable head coordinates across depth and jump.

Determine the actual missing transform semantics from authoritative runtime/render evidence or from a bounded live-derived fitting/validation procedure. Likely dimensions may include sign, scale, depth-to-screen convention, native/drawing-buffer transform, character-height reference, or other projection terms, but **do not guess which one** and do not hard-code unproven constants just to make screenshots look closer.

Required behavior:

- model/transform candidates must be generated or selected from evidence, not guessed constants;
- any fitted sign/scale/bias/offset must carry the exact live authority/proof window that established it;
- residual/error/stability acceptance must be bounded and fail closed;
- player and enemy projection authority must remain lifecycle/runtime-generation bound;
- no current serialized/synthetic/repository-only state may fabricate `IMPLEMENTATION_READY`;
- runtime/session replacement must revoke stale transform authority exactly as Camera authority is revoked.

### B. Owner visual confirmation UX is unacceptable

Do not continue showing every `Y-Z / Y+Z / Y` marker for P1 plus all enemies at the same time.

Redesign the bounded visual confirmation so a novice Owner is never asked to interpret a screen full of overlapping black labels. Prefer automatic quantitative fitting/elimination and automatic confidence/residual checks. If one human confirmation is intrinsically required, show only one candidate at a time and ask one plain-language yes/no question.

Owner-facing requirements:

- explicit current step and **exactly one next action**;
- visually distinguish P1 vs enemy evidence without clutter;
- never require the Owner to understand coordinate math, `Y-Z`, `Y+Z`, `Y`, sign, scale, bias, offsets or model names;
- never ask the Owner to choose among multiple mathematical models;
- do not enable a success action until the candidate is actually eligible;
- if no candidate is authoritative, surface one clear failure result and stop instead of inviting guesswork;
- no repeated P1 clicks unless the current authority was explicitly revoked and the UI clearly says a new click is required.

### B1. Mandatory simplicity budget — this is a product requirement

The current live-acceptance flow is rejected as too complicated. The successor normal path must target:

**`菜单 6 -> 正常进入 WOF -> Camera 自动准备 -> 最多点击一次 P1 头顶 -> 正常玩 -> 自动完成或给出一个明确结果`**

For the normal successful path:

- after menu 6, do not require the Owner to run another menu item;
- at most **one deliberate calibration click** per valid runtime/Camera authority generation;
- no manual selection among projection models;
- no manual interpretation of multiple debug labels;
- no simultaneous multi-model marker flood;
- no checklist that asks the Owner to remember a sequence of left/right, depth, jump, resize, fullscreen and enemy appearance;
- collect horizontal/depth/jump/enemy/layout evidence opportunistically from normal gameplay wherever technically possible;
- if a specific additional motion is genuinely required because evidence is still insufficient, request **one action at a time**, in plain Chinese, only when needed, and automatically advance once observed;
- do not require resize/fullscreen merely because the historical proof script did so; keep it only if it is still technically necessary for current transform authority, and justify that necessity in the durable RESULT;
- do not require the Owner to click a "success model" button. The tool must decide eligibility from evidence. If a final human visual confirmation is unavoidable, it must be a single plain-language `位置正确 / 位置不正确` decision for one already-selected candidate, not a mathematical choice;
- after success, automatically activate the production head overlay; after failure, automatically preserve evidence and show one clear failure reason;
- authoritative menu-6 live ZIP must be created automatically and its exact path shown prominently;
- menu 7/8 remain fallback diagnostics only and must not be part of the ordinary Owner instructions.

Target Owner-facing steady-state text should be conceptually as simple as:

- `正在自动校准，请正常玩。`
- `请点击一次 P1 头顶上方希望提示出现的位置。`
- `正在自动验证头顶位置，请继续正常玩。`
- `校准完成，头顶提示已启用。`

or, on fail-closed inability:

- `本次无法可靠确定头顶位置，已自动保存结果；请结束本次验证。`

Do not expose internal candidate names or engineering diagnostics in the primary game overlay. Detailed diagnostics may remain in evidence/tray advanced detail.

### C. Production activation boundary

Do not enable production head overlays until the projection result is genuinely `IMPLEMENTATION_READY` under current authority.

Preserve:

- enemy target raw semantics `0 -> 1P`, `4 -> 2P`, `8 -> 3P`;
- player `[危险]` detection semantics and existing production danger rules;
- no claim that `[危险]` failed simply because no supported danger rule was exercised;
- fail-closed behavior when projection authority is absent/ambiguous/stale.

### D. Evidence / ZIP handoff clarity

Normal menu 6 already automatically collects/packages live evidence. Preserve that behavior and make the authoritative live-session ZIP unmistakable to the Owner.

The field run demonstrates that a generic menu-7/8 `WOF_RESULTS_*.zip` can be confused with the actual menu-6 `WOF_LIVE_ACCEPTANCE_<session>.zip`. Within this recovery, ensure the Owner-facing terminal/final status clearly identifies the authoritative live-session ZIP and that projection authority/candidate/failure timeline is retained there. Do not require manual menu 7 then menu 8 for the normal live flow.

Do not add credential/token setup or claim repository auto-upload exists when it does not.

## 3. Frozen contracts / non-goals

Do **not** regress or reopen these completed contracts:

- exact World 921031 SHA identity;
- lifecycle-aware active/inactive player identity;
- Camera `READY_LATCHED` stable authority / exact click binding / TOCTOU fix;
- room re-entry Worker rediscovery and runtime-generation revocation;
- cached low-overhead steady-state runtime health;
- one Tk owner thread and clean Tk shutdown semantics;
- readOnly=true;
- ramWrites=0;
- inputInjection=false;
- existing danger rules / target semantics;
- historical repository Fresh QA.

Do not start a new broad QA chain. This is implementation + implementation-owned self-check + immutable successor packaging. The remaining visual truth must be checked by one later focused Owner live retest after this recovery is COMPLETE.

Do not run Browser/WOF and do not fabricate a real-game PASS if the worker environment does not possess the Owner's real session.

## 4. Implementation expectations

Complete the coherent module end-to-end before stopping:

1. identify the precise transform/projection authority deficiency from current source and available durable/live evidence;
2. implement the minimal authoritative transform discovery/fitting/validation path without guessed constants;
3. replace the simultaneous multi-model clutter with the mandatory simplified Owner flow above;
4. preserve exact Camera authority binding from READY through click through transform proof;
5. ensure transform authority is versioned, lifecycle/session bound, revocable and evidence-visible;
6. preserve production fail-closed activation;
7. preserve / improve automatic live evidence and final ZIP clarity;
8. add deterministic implementation-owned tests for the actual defect class, including depth-direction/sign mistakes, jump/Z model separation, stale-authority rejection, model ambiguity/failure, and novice UI state progression;
9. add self-checks enforcing the simplicity budget: no model-choice buttons in normal path, no simultaneous multi-model flood, at most one calibration click per valid authority generation, one-next-action guidance, and menu-6 automatic ZIP;
10. run only the needed implementation-source self-check/regression/safety gates;
11. freeze a new immutable successor source/package; do not reuse `2026.09.02.52c942085c99` for the next Owner retest;
12. validate Windows portable / Chinese+spaces path / last-known-good behavior as applicable;
13. write a durable RESULT with exact sourceCommit, packageVersion, manifestPublicationCommit and workflow run IDs, and explicitly state the final Owner interaction count/sequence;
14. close both canonical and stage claims COMPLETE with the matching claimToken.

If authoritative transform semantics cannot be established without another bounded real Owner measurement, do not guess and do not spin indefinitely. Implement the minimal safe measurement/UX/evidence path needed for that one measurement, package it as an immutable successor, and state exactly what one Owner action remains. Even in that case, the measurement flow must honor the simplicity budget: one instruction at a time, no math/model choice, no full checklist memorization, automatic evidence packaging.

Do not stop at a partial code patch, a workflow draft, or an unpublished candidate.

## 5. Exit condition

Only stop on one of:

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE PROJECTION TRANSFORM + OWNER UX RECOVERY V1 — SUCCESSOR PACKAGE READY — READY FOR ONE FOCUSED OWNER LIVE RETEST`

or

`BLOCKED — ALPHA V1 LIVE ACCEPTANCE PROJECTION TRANSFORM + OWNER UX RECOVERY V1 — <precise external/authority blocker>`

or canonical duplicate stop per dedup v2.

Do not stop at claim acquisition, single patch, self-check PASS, workflow in progress, package publication, or RESULT-with-claims-still-ACTIVE.