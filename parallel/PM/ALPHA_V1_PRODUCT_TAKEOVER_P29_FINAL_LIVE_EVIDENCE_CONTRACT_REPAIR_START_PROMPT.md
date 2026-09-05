# Alpha V1 P29 — Final Live Evidence Contract Repair — START PROMPT

## Mission

Repair the concrete repository-side contract defects exposed by the first real Owner final-staging run, so the next Owner run is meaningful rather than another blind retry.

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P29_FINAL_LIVE_EVIDENCE_CONTRACT_REPAIR`

DedupKey:
`alpha.v1.product-takeover.final-live-evidence-contract-repair-v1`

Canonical claim path:
`parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.final-live-evidence-contract-repair-v1.json`

Stage claim path:
`parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P29_FINAL_LIVE_EVIDENCE_CONTRACT_REPAIR.json`

Progress path:
`parallel/PM/PROGRESS/ALPHA_V1_PRODUCT_TAKEOVER_P29_FINAL_LIVE_EVIDENCE_CONTRACT_REPAIR_PROGRESS.json`

Result paths:
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P29_FINAL_LIVE_EVIDENCE_CONTRACT_REPAIR_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P29_FINAL_LIVE_EVIDENCE_CONTRACT_REPAIR_RESULT.md`

## Mandatory bootstrap / dedup preflight

Read latest `main`, root `AGENTS.md`, full `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`, `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`, the current final live gate, terminal P25/P27/P28 results, and the W3 authority documents/code listed below.

Check canonical + stage claims before creating anything. If an equivalent task is already ACTIVE/CLAIMED, return exactly:
`ALREADY ACTIVE / CLAIMED — NO EXECUTION`

If an equivalent task is already COMPLETE/PASS, return exactly:
`ALREADY COMPLETE — NO EXECUTION`

Otherwise create the canonical dedup-v2 claim first, then the stage claim, both with one fresh exact claimToken, read both back, and only then begin implementation. Immediately create the P29 PROGRESS checkpoint after both claims are verified.

## Live evidence that triggered P29

The first real Owner Windows final-staging run reached the actual browser/game runtime and produced bounded evidence, but ended:
- P17: `FAILED_EVIDENCE_MISMATCH`
- W3: `REJECTED`
- `rendererSource.proven=false`, `suppressed=true`
- no Owner visual acceptance, no promotion, alpha-live unchanged.

Observed W3 rejection/gaps:
- `same heap offset appears with inconsistent byte order`
- no candidate remains layout-stable across the full bounded timeline
- per-frame runtime/renderer/authority epoch stamps are incomplete
- `rendererSourceProof` is absent.

Observed timeline diagnostics:
- 61 frames
- 17 unique candidates
- 0 epoch-stamped frames
- no stable candidate.

Observed P16/P17 seam:
- P16 was captured with `world.accepted=false`, canonical `VERIFYING_WORLD`, null runtime authority/epoch/renderer fields;
- independent W3 measurement subsequently locked the exact World identity;
- staged runtime surfaced a maintained P1/HUD binding failure during this run.

Do not require the Owner to rerun the game during P29 implementation. Use committed code + focused deterministic fixtures to repair the contract first.

## Truth boundary — must not weaken

Read and preserve `parallel/RENDER_AUTHORITY_V2/RENDER_OBJECT_SOURCE_LONG_QUALIFICATION.md`.

The repository does not currently prove the causal edge from displayed CPS1 renderer/object submission to an exact HEAP object source. P29 MUST NOT manufacture that proof, infer it from structural stability, use screenshot/world projection as production coordinates, guess addresses, or convert `UNVERIFIED_CANDIDATE_ONLY` into authority.

A valid safe capture with no legitimate `wof-renderer-source-proof-v1` must remain `INCONCLUSIVE`. `PASS` still requires the existing direct displayed-frame renderer/object proof contract.

## Required implementation

### A. W3 capture/analyzer contract consistency

Inspect at minimum:
- `parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js`
- `parallel/RENDER_AUTHORITY_V2/qualification_analyzer.py`
- `parallel/RENDER_AUTHORITY_V2/test_qualification_analyzer.py`
- `parallel/RENDER_AUTHORITY_V2/test_long_qualification_runner.py`
- `parallel/PYLAUNCH/wof_launcher/render_authority_capture.py`
- `parallel/RENDER_AUTHORITY_V2/measurement_runner.py`

Repair so that:
1. every `candidateTimeline` frame carries the exact bound `runtimeEpoch`, `rendererEpoch`, and `authorityKey`;
2. scanner/analyzer byte-order semantics are internally consistent: diagnostic exploration of BE16 and LE16 at the same offset must not create a false `REJECTED` merely because both candidate identities were observed;
3. malformed/stale/epoch-mixed evidence remains truly `REJECTED`;
4. safe structural-only evidence with no direct renderer proof is deterministically `INCONCLUSIVE`;
5. `PASS` criteria remain unchanged and strict.

Do not solve this by deleting safety rejection checks wholesale or treating stability/score as proof.

### B. P16 staged evidence readiness

Inspect at minimum:
- `parallel/OWNER_STAGING/p21_acceptance.py`
- `parallel/OWNER_STAGING/exact_candidate_staging_acceptance.py`
- relevant focused staging tests
- only the minimal maintained runtime/HUD binding code necessary to explain the observed P1 binding failure.

Repair so that staging does not accept a fresh-but-still-`VERIFYING_WORLD` P16 record as final P16 evidence. A usable staged P16 must be bound to the exact candidate and have:
- exact World accepted;
- expected world identity;
- nonempty runtime epoch;
- nonempty authorityKey;
- nonempty rendererEpoch / renderer authority as required by downstream P18/P17.

Diagnose the maintained P1/HUD binding failure. If it is a deterministic repository defect that prevents P16 readiness, repair only that concrete boundary. Do not broaden into unrelated HUD redesign.

### C. Outcome semantics

After focused deterministic repair:
- if the contract is internally coherent and ready for a new Owner run, terminal RESULT may be `COMPLETE`, `integrationReady=true`;
- this COMPLETE means “repo-side live-evidence contract repaired and ready for one new Owner bounded run”, NOT that real WOF or visual correctness has passed;
- preserve `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, `visibleProof=NOT_PROVEN`, `alphaLiveMoved=false`.

If a legitimate direct renderer proof still cannot be produced by checked-in code, do not fake it. Record that the subsequent Owner run may truthfully end `INCONCLUSIVE`; P29 itself can still COMPLETE if the false rejection/timing defects are repaired.

## Focused self-check only

Do not run broad QA. Add/run only focused deterministic checks needed to prove:
- structural-only valid capture => `INCONCLUSIVE`;
- same-offset BE/LE diagnostic exploration no longer causes false rejection;
- stale/mismatched epochs still reject;
- timeline frames are fully epoch stamped;
- P16 wait ignores `VERIFYING_WORLD` / incomplete runtime identity and accepts only ready exact-world evidence;
- any concrete P1 binding fix has a focused regression.

Before terminal-significant self-check, create a durable implementation candidate commit/tree containing the exact tested bytes and record it in PROGRESS. Any implementation-byte change after that test requires a new candidate and rerun of affected focused checks.

## Forbidden

- no real Owner/game run during P29 implementation;
- no alpha-live movement;
- no promotion;
- no P20 YES/NO question;
- no reopening P25/P26/P27/P28;
- no W3 guessed coordinates / screenshot production authority / world-projection production authority;
- no global/system Python changes, PATH changes, browser reinstall, or environment reset;
- no unnecessary dependency redownload.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.
