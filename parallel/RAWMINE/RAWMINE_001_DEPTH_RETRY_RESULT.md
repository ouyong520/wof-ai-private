# RAWMINE-001 P1 Depth Retry Result

Date: 2026-09-01
Lane: `RAWMINE-*` only
Evidence class: `WinKawaks-local-discovery-only`

## Scope

This note records the completed evidence-only retry for the GEO-owned P1 floor/depth question. RAWMINE remains a neutral candidate screener and does not assign final geometry semantics or promote WinKawaks offsets to Browser production truth.

## Collector result

Task: `RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z`

The Collector completed successfully and remained read-only:

- result: `PASS`
- requested duration: `8.0 s`
- samples: `481`
- achieved rate: `60.011 Hz`
- bytes/frame: `5152`
- read errors: `0`
- frame-size errors: `0`
- distinct raw frames: `433`
- `writesGameMemory: false`
- raw: `captures/RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z.jsonl.gz`
- raw blob SHA: `2a33e6543e91e4ca0d041805e0ee792c9fb47f4c`
- raw commit: `f73a465ddcc558cd247e8baa2ad0a6d9eb139dc9`

The raw is therefore mechanically healthy; the game was not frozen.

## Controlled depth screen

The v8 candidate workflow completed successfully and selected RAWMINE-001 as controlled attempt 2.

Retry-only controls/evidence:

- frames / transitions: `481 / 480`
- reconstructed X (`+0x04/+0x0B`) changes: `0`
- reconstructed Z (`+0x0C/+0x11`) changes: `0`
- X/Z control validity: `PASS`
- `+0x08` changes: `0`
- manipulation-validity: `FAIL`
- manipulation evidence offsets: none

Automated verdict:

`CONTROLLED_RAW_NO_P1_DEPTH_MANIPULATION_EVIDENCE`

This is an ineffective manipulation capture, not negative evidence against `+0x08` or any other Y/depth candidate. The highly dynamic `+0x7F` remains insufficient because its activity is not P1-specific against untouched P2/P3 controls.

## Attempt history

| Attempt | Source | Control | Manipulation | +0x08 | X | Z |
|---:|---|---|---|---:|---:|---:|
| 1 | `GEO-0008-p1-depth-only-5s60-20260831-2115Z` | PASS | FAIL | 0 | 0 | 0 |
| 2 | `RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z` | PASS | FAIL | 0 | 0 | 0 |

Both attempts are mechanically clean and both fail only the manipulation-evidence gate.

## P1/P2/P3 slot identity control

Cross-corpus player fingerprint validation after RAWMINE-001 covers 15 compatible captures / 27183 frames. Expected player-slot fingerprints at offsets `+0x20`, `+0x21`, `+0x26`, `+0x62`, `+0x7C`, and `+0x92` show zero mismatches. RAWMINE-001 itself has zero mismatches across all 481 frames.

Therefore wrong P1/P2/P3 slot indexing is not a plausible explanation for the missing depth-coordinate dynamics.

## Remaining acquisition ambiguity

`READY_WOF_TASK.bat` invokes `bridge.operator_ready` and pauses in the console after writing the ready token. The Collector can begin the burst immediately when that token appears. Because the READY console can own foreground keyboard focus, the prior operator procedure did not independently prove that the subsequent UP/DOWN keys reached WinKawaks during the capture.

This is an acquisition/focus ambiguity, not a field-semantic result.

## Final bounded retry

One final narrow retry is justified to isolate that remaining ambiguity:

`RAWMINE-002-p1-depth-focus-retry-20s60`

The analyzer is already configured to consume this task as controlled attempt 3. The task explicitly requires immediate WinKawaks refocus after READY plus visible confirmation that UP/DOWN moves P1 between distinct floor/depth positions. It remains P1-only, no LEFT/RIGHT/jump/attack, P2/P3 untouched, read-only, and discovery-only.

Stop rule: if RAWMINE-002 is mechanically valid but again contains no P1-specific manipulated byte dynamics, RAWMINE will not request another equivalent retry. The acquisition limitation will be recorded explicitly and the unresolved semantic question returned to GEO without treating the failed manipulation as negative evidence against `+0x08`.
