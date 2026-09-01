# WOF Alpha RC5 — Independent QA / Retest Status

Updated: 2026-09-01

## Verdict

**PASS — RC5 ROOM-ENTRY REPAIR QA**

## Specific former P0

`Alpha prevents room entry` — **CLOSED**.

Accepted evidence chain:

1. owner real-Browser retest: RC5 Safe Bootstrap enabled, Browser Acceptance Helper disabled, room entry succeeds;
2. current RC5 source: native `window.Worker` is not replaced/wrapped and no Blob/ObjectURL Worker rewrite remains;
3. independent VM bootstrap retest: PASS for Worker identity, original URL/options, no pre-pair HUD fetch, no Blob/ObjectURL, session filtering, BroadcastChannel failure fail-open, and secure-random failure fail-open;
4. current product regression source/result: PASS;
5. critical RC4 core/loader/HUD/HUD-model blobs remain identical to the prior independent RC4 QA snapshot.

## RC4 gates

**PASS / preserved**:

- World 921031 exact full 1 MiB SHA-256 gate;
- exactly two T18 current-level production rules;
- F1-F4 quarantine;
- same-type slot replacement safety;
- session/cross-tab isolation;
- runtime diag immediate warning invalidation;
- foreign-session diag isolation;
- ordinary 1500 ms stale behavior;
- multi-warning HUD;
- legacy HUD teardown;
- target/side/UNKNOWN safety;
- read-only / `ramWrites=0` / no input injection;
- WebGL state restoration.

## Release boundary

**Alpha release-ready: NO.**

The remaining Browser-product blocker is a proven safe non-replacing live-Worker transport. Until that exists, RC5 correctly remains `WAITING_EXTERNAL_TRANSPORT` / warning-silent and the full live detector/HUD/warning Browser acceptance has not run.

## QA mutation boundary

- `product/alpha/**`: unchanged by QA
- Python Launcher / `parallel/PYLAUNCH/**`: unchanged by QA
- WOF-052L: unchanged by QA
- QA writes: `parallel/ALPHAQA_RC5/**` only
