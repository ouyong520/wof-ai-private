# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC4 candidate PASS / open fresh RC4 QA

## Current owner action required: YES — thread management only

RC4 product fix has reached its stop condition.

Product regression now records:
- artifact `wof-alpha-rc4`;
- tests `PASS`;
- exact World 921031 golden SHA-256 preserved;
- `runtimeDiagImmediateWarningInvalidation: true`;
- ordinary 1500 ms no-diag stale behavior unchanged;
- exactly two T18 current-level production rules;
- F1-F4 quarantined;
- read-only/no-input and session safety preserved.

## Action O1 — close the RC4 implementation thread

Do not ask RC4 engineering to certify itself further.

## Action O2 — open a fresh independent RC4 QA thread

Use:

`parallel/PM/ALPHA_RC4_QA_START_PROMPT.md`

QA must not modify `product/alpha/**`.
It must independently prove the old RC3 blocker is closed and recheck the preserved release gates.

Required final verdict:
- `PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`, or
- a concrete `BLOCKED — P0/P1`.

## After QA PASS

The Browser Acceptance Prep stage is already complete under `parallel/ALPHAACCEPT/**`.
Do not create another acceptance-prep thread.
Once QA passes, use the prepared one-refresh + one-button flow and return the single acceptance JSON.

## Non-blocking support

### Runtime Speed

Probe tooling is ready. The remaining owner work is one paired local/Browser measurement; this does not block Alpha.

### Local ROM identity

One read-only local hash command remains; this does not block Browser Alpha.

### HUD Anchor

One Browser projection proof remains for Beta; not an Alpha prerequisite.

## Do not do yet

- Do not run final Browser acceptance before RC4 QA PASS.
- Do not revive RC3/RC4 implementation threads after their stage stop.
- Do not restart WOF-052 as an Alpha blocker.
- Do not perform broad recollection.

## Next PM trigger

After fresh RC4 QA writes its verdict, PM will either open a new fix stage for a concrete P0/P1 or authorize the already-prepared one-click Browser acceptance.
