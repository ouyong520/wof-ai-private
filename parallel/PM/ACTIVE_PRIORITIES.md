# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC3 candidate complete; support audits at bounded stop points

## P0 — Fresh independent Alpha RC3 QA

RC3 implementation is complete and must remain closed.

Candidate evidence:
- `product/alpha/ALPHA_RC3_REPORT.md`
- product regression: PASS
- supported Browser lineage: `wof / Warriors of Fate (World 921031)`
- exact full 1 MiB CPU-logical SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- active user-facing production rules: exactly two stateless current-level T18 rules
- F1-F4 history-derived rules quarantined

Fresh QA bootstrap:
- `parallel/PM/ALPHA_RC3_QA_START_PROMPT.md`

QA writes only under `parallel/ALPHAQA_RC3/**` and must not modify `product/alpha/**`.

Current GitHub status: no RC3-QA verdict commit is present yet.

## P1 — One bounded Browser acceptance after QA PASS

Only if RC3 QA returns:

`PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`

Then run one short real Browser acceptance covering:
- document-start bootstrap / real Worker interception;
- exact World 921031 SHA-256 positive identity;
- fail-closed behavior on identity/runtime failure;
- WebGL HUD rendering/state restoration;
- session/cross-tab isolation and clean reload pairing;
- legacy HUD teardown;
- live target/side and stale/UNKNOWN silence;
- acceptable runtime overhead.

## SUPPORT COMPLETE / HUMAN-GATED

### Local WinKawaks ROM Identity — STOP B

`parallel/LOCALROM/**` exhausted retained evidence.
Strong evidence indicates local WinKawaks is `wofr1 / World 921002`, while Browser is proven `wof / World 921031`.
Exactly one read-only PowerShell ROM hash command remains before cryptographic classification.

This is not an Alpha Browser blocker.

### Runtime Speed / Timing — STOP B

`parallel/RUNTIMESPEED/**` verdict:
- existing Collector ~60 Hz is external sampling cadence, not proof of emulated game speed;
- Browser production lead milliseconds remain valid and require no Alpha change;
- local timing must not be directly compared numerically with Browser milliseconds;
- retained evidence does not prove Browser is globally slow;
- exactly one paired 15 s no-input timing measurement per runtime remains to distinguish actual simulation speed from feel/latency.

This is not an Alpha blocker.

### Player-Anchored HUD — STOP B / Beta handoff ready pending one proof

`parallel/HUDANCHOR/**` has produced the Beta anchor model and implementation handoff.
Classification: `NEEDS ONE MINIMAL BROWSER PROOF`.

The later Beta implementation should use authoritative Browser player/camera/native projection state and direct game WebGL, with fixed in-game HUD fallback whenever the anchor is uncertain.

This is not an Alpha blocker.

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

- STOP modifying RC3 from the completed implementation thread.
- STOP final Alpha Browser acceptance before fresh RC3 QA.
- STOP treating Local ROM title alone as cryptographic proof.
- STOP equating Collector Hz with game simulation speed.
- STOP doing HUD Anchor implementation before its one Browser projection proof.
- STOP broad collection / speculative production-rule promotion.

## Current fastest path

**fresh RC3 independent QA -> one bounded Browser acceptance -> Alpha release**

Non-blocking human-gated follow-ups can be completed in parallel later:
**Local ROM hash -> Runtime Speed paired timing test -> HUD Anchor Browser projection proof**.
