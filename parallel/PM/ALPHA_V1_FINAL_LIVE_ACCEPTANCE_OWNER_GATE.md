# Alpha V1 Final Live Acceptance — Owner Gate

Status: ACTIVE OWNER GATE
Scope ceiling: P24. P25/P26 are cancelled historical dispatch artifacts and are not executable authority.

## Current authoritative state

- Development scope ends at P24.
- P19 final candidate is READY at source commit `0752796369f1687435a1b1647e66ea0b5ab07688`, package `2026.09.05.0752796369f1`.
- P21 exact-candidate staging harness is COMPLETE/integration-ready.
- W3 repository work is SUBCOMPLETE with live qualification `INCONCLUSIVE`; this is the current hard gate.
- P20 Owner visual confirmation/promotion gate is COMPLETE as implementation only; real Owner visual verdict is NOT_RUN and alpha-live has not moved.
- P23 close harness is COMPLETE as implementation only; current close state is `WAITING_FOR_W3_LIVE_PASS`.
- P22 and P24 passive analyzers are COMPLETE as repository modules; any live coverage must remain same-session and truthful. Missing rare states stay NOT_OBSERVED/UNPROVEN and must never be guessed.

## Step 1 — exact-candidate live acceptance

On the Owner Windows machine, from the repository root, run exactly:

```cmd
parallel\OWNER_STAGING\WOF_ALPHA_STAGE_FINAL_ACCEPTANCE.cmd
```

Then play World 921031 normally for the bounded interval requested by the harness. Do not edit coordinates, hashes, actor identities, generations, runtime/renderer epochs, or evidence JSON.

P21 must stage the immutable P19 candidate without moving `alpha-live`, invoke the existing bounded W3 qualification/P16/P18/P17 path, preserve read-only safety, and stop at most at `READY_FOR_OWNER_VISUAL_CONFIRMATION`.

## Gate A — W3 result

After the staged run, PM must inspect the produced W3 qualification evidence.

- If W3 is `PASS` with a proven exact displayed-frame renderer/object causal source, continue.
- If W3 is `INCONCLUSIVE`, `FAIL`, missing, stale, ambiguous, or identity-mismatched: STOP. Keep canonical output suppressed and do not guess an address or coordinate source.

No later Owner visual confirmation, promotion, or project close is allowed while W3 is not PASS.

## Step 2 — Owner visual gate

Only when P17 for the same staged candidate reaches exactly `READY_FOR_OWNER_VISUAL_CONFIRMATION`, run:

```cmd
parallel\OWNER_RELEASE\WOF_ALPHA_FINAL_RELEASE_GATE.cmd
```

Answer only the real observation question:

`游戏里的提示是否稳定跟随正确的人物/怪物？`

- `NO` blocks promotion for that receipt/bundle.
- `YES` creates the real bound visual receipt and promotion plan, but does not itself move `alpha-live`.

Do not treat P18 draw acknowledgement, screenshots, fixtures, module load, or repository tests as visual PASS.

## Step 3 — PM promotion

Promotion is a separate PM action after a real Owner YES receipt and a READY exact P20 promotion plan exist.

Requirements remain:
- exact candidate/bundle/receipt/plan hashes unchanged;
- immediate compare-and-swap re-read of current `alpha-live`;
- target is fast-forward descendant;
- no force push / force-with-lease / `+refspec`;
- W1 permanent required files present;
- promotion result recorded only after confirmed ref movement.

Until this gate is explicitly applied, `alpha-live` must remain unchanged.

## Step 4 — post-promotion close

After confirmed promotion:

1. Run the existing permanent `Desktop\WOF_ALPHA_TEST.cmd` once so W1 converges to the promoted commit.
2. Preserve truthful P22 dynamic-state coverage from the real acceptance session; unsupported HIT/DOWN/RECOVERY/JUMP/DEATH remain UNPROVEN/NOT_OBSERVED.
3. Consume P24 temporal evidence only from time-ordered exact canonical observations from the relevant live session; never repair gaps with interpolation or old coordinates.
4. Run:

```cmd
parallel\OWNER_RELEASE_POSTVERIFY\WOF_ALPHA_POST_PROMOTION_VERIFY.cmd
```

P23 may emit `ALPHA_V1_FINAL_COMPLETE` only when its existing real-evidence close contract is fully satisfied.

## Safety / non-goals

- No new P25/P26/P27 stage.
- No change to permanent W1 updater during this gate.
- No screenshot/world-projection production coordinates.
- No guessed addresses.
- `readOnly=true`, `ramWrites=0`, `inputInjection=false`.
- Missing evidence means WAITING/SUPPRESSED, never synthetic PASS.
