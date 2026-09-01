# WOF Future Danger AI — Release Readiness

Updated: 2026-09-01 — RC5 room-entry P0 repaired; Alpha now blocked on safe live-Worker transport

## Alpha — **BLOCKED / SAFE TRANSPORT REQUIRED**

Owner real-Browser RC5 retest:
- current RC5 Safe Bootstrap enabled;
- Browser Acceptance Helper disabled;
- game **enters a room normally**;
- no HUD/warnings appear because RC5 intentionally waits for a safe external live-Worker transport.

Therefore the former P0 `Alpha prevents room entry` is closed by owner evidence, pending fresh independent RC5 QA confirmation.

This does **not** make Alpha release-ready. A usable Alpha still needs a proven non-replacing live-Worker transport and a final bounded Browser acceptance exercising real detector/HUD behavior.

## Gate status

| Gate | Status |
|---|---|
| RC4 product regression | PASS |
| Fresh RC4 independent QA | PASS |
| RC5 product regression | PASS |
| Real host can enter room with RC5 enabled | **PASS** |
| Fresh RC5 room-entry QA | PENDING |
| Python Launcher foundation implementation | DONE |
| Real Windows CDP live-Worker proof | **PENDING / P0** |
| Alpha transport integration | BLOCKED ON PROOF |
| Full Browser acceptance | PAUSED |
| Alpha release | BLOCKED |

## Current transport route

Primary candidate:
`Python/EXE Launcher -> localhost Chrome/Edge CDP -> already-native gstyphoon Worker -> WASM/heap -> exact World 921031 identity`.

The launcher foundation is implemented under `parallel/PYLAUNCH/**` and has one real Windows/Browser proof remaining. It does not replace `window.Worker` and is read-only in the current stage.

## Required sequence

1. fresh RC5 independent QA confirms the room-entry repair;
2. Python Launcher live Windows proof passes;
3. fresh Alpha transport-integration stage connects the detector through the proven non-replacing path;
4. bounded real Browser acceptance verifies actual HUD/warnings and preserved safety behavior;
5. PM release decision.

## Retained safety requirements

Must remain true through transport integration:
- exact `wof / World 921031` full-program SHA-256 authority;
- only two current-level T18 production rules;
- F1-F4 quarantined;
- same-type replacement safety;
- session isolation;
- multi-warning HUD;
- runtime diag immediate warning invalidation;
- target/side/UNKNOWN safety;
- read-only / no gameplay input injection for Alpha;
- WebGL restoration;
- base game continues even when the transport cannot attach.

## Current release judgment

**Alpha is not releasable yet. The startup-blocking defect is repaired, but the real Browser detector/HUD path is intentionally silent until a safe live-Worker transport is proven and integrated.**
