# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — Alpha RC1 reached

## P0 — Independent Alpha QA

Alpha RC1 now exists under `product/alpha/**`.

Start/continue the independent QA workstream defined by:
- `parallel/PM/ALPHA_QA_START_PROMPT.md`

QA must treat `product/alpha/**` as read-only and write only to `parallel/ALPHAQA/**`.

Highest-value checks:
1. frozen-rule fidelity versus audited Browser evidence;
2. fail-closed runtime identity;
3. no RAM writes / no input injection;
4. live target/retarget/side and UNKNOWN silence;
5. warning lifecycle, stale cleanup, slot/type reuse and reload behavior;
6. independent regression quality;
7. ordinary-user packaging path.

Stop at either QA PASS or a precise P0/P1 defect list for the Alpha developer.

## P0 — Real Browser Alpha acceptance, **after QA clears P0/P1**

The Product Alpha implementation owner has already reached its engineering stop condition and published `wof-alpha-rc1`.

Do not spend owner Browser time before independent QA returns no open P0/P1. After QA clears, perform one short real-game acceptance using the exact RC1 instructions in `product/alpha/**`.

Acceptance must confirm:
- loader works in live Worker + top Window;
- runtime says release `wof-alpha-rc1`, running/readOnly true, ramWrites 0, inputInjection false;
- HUD connects/draws without persistent error;
- warning target/side looks correct in real play;
- stale/SAFE/UNKNOWN clears;
- reload does not break the game or HUD hook.

If this passes, Alpha can be released without waiting for WOF-052.

## P1 — MAINLINE WOF-052 ordered T18 discrimination

WOF-052 remains the highest-value research Browser task, but it is no longer an Alpha release blocker because BODY4728 is intentionally excluded from RC1.

When owner Browser time is available after/alongside Alpha acceptance, run the already-defined T18-focused WOF-052 protocol. Do not promote the ambiguous anchor itself.

## P2 — SEQMINER finish current materialization, then park

Latest SEQMINER work strengthens cross-state timer/feature contracts. No Collector recapture is justified. Stop when the current retained corpus is exhausted; wait for new Browser/labeled material.

## PARK — COVERAGE refresh complete

COVERAGE normalized type IDs and ingested current atlases. Current decision: **human recap required: NO**.

Do not ask for broad WinKawaks replay. Reopen only if later Beta/v1 work identifies one concrete residual coverage question that existing raw cannot answer.

## Explicit stops

- STOP broad BASECAP collection.
- STOP generic EFIELD mapping.
- STOP generic RAWMINE discovery.
- STOP broad unlabeled sweep collection.
- STOP speculative production-rule promotion.
- STOP treating WinKawaks numeric offsets as Browser/WASM production evidence.
- STOP opening more discovery AI lanes before Alpha QA/acceptance is resolved.

## Current fastest path

**Alpha QA -> fix only real blockers -> one Browser acceptance -> Alpha release.**