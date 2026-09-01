# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC3 candidate complete / fresh QA next

## P0 — Fresh independent Alpha RC3 QA

RC3 implementation is complete and has reached its stop condition.

Candidate evidence:
- `product/alpha/ALPHA_RC3_REPORT.md`
- product regression: PASS
- supported Browser lineage: `wof / Warriors of Fate (World 921031)`
- exact full 1 MiB CPU-logical SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- user-facing production rules intentionally reduced to two stateless current-level T18 rules
- F1-F4 history-derived candidates quarantined

Fresh QA bootstrap:
- `parallel/PM/ALPHA_RC3_QA_START_PROMPT.md`

RC3 implementation thread should now be closed and must not self-certify release readiness.
QA may write only under `parallel/ALPHAQA_RC3/**` and must not modify `product/alpha/**`.

## P1 — Local WinKawaks ROM identity

Support lane: `parallel/LOCALROM/**`.

Current retained evidence strongly indicates local WinKawaks is `wofr1 / World 921002` from the live emulator title, while Browser is proven `wof / World 921031`.
Cryptographic local proof is not yet complete.

The lane has reduced this to one read-only local ROM hash probe. No gameplay/recollection is needed.

This does not block RC3 QA or Alpha Browser release, because local WinKawaks remains discovery-only and Browser production proof is authoritative.

## P1 — Runtime speed / timing consistency audit

Support lane: `parallel/RUNTIMESPEED/**`.

Goal: determine whether WinKawaks is actually simulating faster, Browser is slower, or the perceived difference is frame pacing/input/render latency.

This does not block RC3 QA unless the audit discovers that Browser lead-time labels themselves were measured incorrectly.
Do not numerically equate local Collector wall-clock sampling with Browser warning milliseconds without proof.

## BETA SUPPORT — Player-anchored warning HUD

Bootstrap exists:
- `parallel/PM/PLAYER_ANCHORED_HUD_START_PROMPT.md`

No `parallel/HUDANCHOR/**` execution result is currently present on GitHub, so this lane has not yet produced a handoff.
It may run in parallel because it writes only `parallel/HUDANCHOR/**` and must not modify Alpha.

## P2 — One real Browser acceptance after fresh QA

Only if RC3 fresh independent QA returns:

`PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`

Then perform one bounded real Browser acceptance for bootstrap/worker interception, exact 921031 hash acceptance, HUD/WebGL behavior, session isolation/reload pairing, and runtime overhead.

## P2 — MAINLINE WOF-052 after Alpha release gate

Ordered T18 discrimination remains valuable but is not an Alpha blocker because BODY4728-specific attack promotion remains excluded.

## PARK / COMPLETE

- Alpha RC3 implementation — COMPLETE CANDIDATE; close thread.
- Alpha RC2 — completed/rejected; do not revive.
- Runtime Identity audit — Browser identity fully bound to World 921031.
- Enemy Lifecycle audit — conservative policy consumed by RC3.
- Normal-user Bootstrap audit — recommendation consumed by RC2/RC3.
- COVERAGE — complete.
- SEQMINER — retained corpus exhausted; no recap requested.
- BASECAP/GEO/EFIELD/RAWMINE/SWEEPATLAS — closed or on-demand only.

## Explicit stops

- STOP modifying RC3 from the completed RC3 implementation thread.
- STOP final Alpha Browser acceptance before fresh RC3 QA.
- STOP treating local WinKawaks title alone as cryptographic ROM proof.
- STOP assuming WinKawaks wall-clock Collector Hz equals game simulation speed.
- STOP broad collection / speculative production-rule promotion.

## Current fastest path

**fresh RC3 independent QA -> one bounded Browser acceptance -> Alpha release**

Parallel support that need not delay this path:
**Local ROM identity + Runtime Speed audit + Beta HUD Anchor research**.
