# WOF Future Danger AI — Release Readiness

Updated: 2026-09-01 — RC2 rejected by PM review / RC3 required

## Alpha — **RC2 REJECTED / RC3 REQUIRED**

RC2 fixed several RC1 defects and passed local Node regressions, but it is not ready for final Browser QA after two stronger evidence sources were compared against the implementation:

1. the owner's real Browser ROM probe;
2. the completed ALPHALIFE conservative lifecycle audit.

### What RC2 successfully improved

- per-session/cross-tab warning transport isolation;
- simultaneous warning aggregation in HUD;
- safe disposal of prior research HUD;
- one-step user bootstrap candidate;
- read-only/no-input constraints preserved;
- live target/side and UNKNOWN silence preserved.

### Remaining blockers

**P0 — runtime/build identity**

The owner's live Browser probe positively matched canonical `wof / World 921031` program halves, not the old assumed `wofr1 / World 921002` label. It also reproduced the historical Browser `+0x34` dispatch delta.

Current RC2 accepts sparse reset-vector + five-entry dispatch evidence with bounded uniform delta and then emits a 921002 signature. That is not a unique revision identity and can mislabel the actual 921031 runtime.

Required next gate: exact full 1 MiB CPU-logical SHA-256 equality for the cryptographically observed 921031 program. No sparse fallback.

**P1 — hidden same-type enemy replacement continuity**

ALPHALIFE established that same slot + same type does not positively prove episode continuity. Current RC2 still uses previous/current history and can resolve/arm history-derived watches across an unobserved same-type replacement in cases where no null/type-change/nonmatching-zero sample occurs.

Required next gate: follow the conservative audit policy. Without a proven Browser instance token, quarantine F1-F4 history-derived warnings and keep only F5/F6 as hold-only current-state warnings.

### Alpha gate status

| Gate | Status |
|---|---|
| Browser program version identity | **FAIL P0 — one corrected 921031 digest probe pending** |
| hidden same-type replacement safety | **FAIL P1 — RC3 correction required** |
| cross-tab/session isolation | PASS offline / Browser QA later |
| multi-threat HUD | PASS offline / visual Browser QA later |
| legacy HUD teardown | PASS offline / Browser QA later |
| user bootstrap | candidate complete / Browser QA later |
| live target/side | PASS offline |
| UNKNOWN/stale silence | PASS offline |
| no RAM writes / no input | PASS static/offline |
| RC2 implementation | COMPLETE CANDIDATE / **REJECTED BY PM REVIEW** |
| RC3 implementation | NEXT |
| fresh independent RC3 QA | WAIT |
| real Browser acceptance | WAIT |

### Current release sequence

1. owner runs one corrected read-only `World 921031` full-digest probe;
2. PM records the golden 1 MiB CPU-logical SHA-256;
3. fresh Alpha RC3 implementation fixes identity + lifecycle exactly;
4. fresh independent QA audits RC3;
5. only after no P0/P1 remains, owner runs one short real Browser acceptance;
6. if acceptance passes, release Alpha.

Do not switch ROMs to 921002 merely to satisfy the old project label.

## Alpha production breadth consequence

The safe RC3 Alpha may intentionally expose only two current-state T18 rules (F5/F6) if no positive enemy episode continuity is proven before release. This is acceptable under the Alpha freeze specification: correct silence is preferred over retaining a larger rule count with inheritance risk.

F1-F4 remain valuable frozen candidates and may return later after a Browser-proven instance/continuity contract exists.

## Beta — MID

Beta remains broader common-event coverage, ordered ambiguity resolution, multi-danger polish, player-anchored warning placement, easier install/update, extended stability and defensible breadth accounting.

## v1 — EARLY-MID

Unchanged: stable Beta, trustworthy breadth denominator, intentional silence for unsupported events, no P0 release risk, normal-user packaging and support matrix.

## Current release judgment

**Fastest safe path: one 921031 digest probe -> fresh RC3 identity+lifecycle fix -> fresh independent QA -> one Browser acceptance -> Alpha.**
