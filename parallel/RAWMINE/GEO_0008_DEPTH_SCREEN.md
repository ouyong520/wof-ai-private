# RAWMINE — GEO-0008 P1 depth-control screen

Date: 2026-09-01
Lane: `RAWMINE-*` evidence only
Owner: `GEO`
Evidence class: `WinKawaks-local-discovery-only`

## Source

- raw: `captures/GEO-0008-p1-depth-only-5s60-20260831-2115Z.jsonl.gz`
- 300 frames / 299 transitions
- collector result: mechanically `PASS`, read-only, zero game-memory writes
- automated candidate report: bridge `results/rawmine/candidate_screen_summary.json`

## RAWMINE control verdict

`CONTROLLED_RAW_NO_P1_DEPTH_MANIPULATION_EVIDENCE`

The capture is mechanically healthy and its owner-specified orthogonal controls are clean:

- reconstructed X (`+0x04/+0x0B`) changes: **0**
- reconstructed Z (`+0x0C/+0x11`) changes: **0**
- allowed control-change threshold: 6

However the intended P1 depth manipulation is not visible in the player object evidence:

- `+0x08` changes in this controlled run: **0**
- the only strongly dynamic P1 byte surfaced by the first neutral pass was `+0x7F`, with 154 P1 changes, but untouched P2/P3 show essentially the same behavior (`untouchedP2P3ChangeRate ~0.4883`, P1 specificity ~0.5133)
- no byte satisfies the manipulation guardrail of >=5 P1 changes, >=0.80 P1 specificity, and <=0.05 untouched-P2/P3 change rate

Therefore GEO-0008 cannot discriminate the P1 floor/depth coordinate. This is **not negative evidence against `+0x08`** and not evidence for `+0x7F`; it is an ineffective manipulation capture.

## Follow-up already routed

RAWMINE queued one targeted retry because the owner question remains unresolved and no owner capture is currently active:

`RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z`

The retry explicitly requires visibly repeated P1 UP/DOWN traversal in an open walkable area, P2/P3 untouched, no LEFT/RIGHT/jump/attack, and retains X/Z contamination guards.

RAWMINE will consume that raw automatically. Final P1 Y/depth naming and promotion remain GEO-owned.
