# EFIELD Collector Discovery Status

Research line: `EFIELD-` only. WinKawaks-local, read-only discovery. No Browser/WASM rule promotion and no game-memory writes.

## Current blocker

`EFIELD-007-passive-proximity-association-60s60` and the follow-up one-frame `EFIELD-008-discovery-probe-snapshot` both failed before raw capture with:

`RuntimeError: Fresh immutable CPS RAM discovery is not uniquely qualified`

Neither task produced EFIELD raw evidence. Their failure must not be interpreted as a field-semantic negative result.

Both exact failed task blobs were removed from the active queue and preserved under `tasks/archive/` so the older running queue service cannot retry them forever.

## Root cause / queue hardening

The running local Collector was loaded before the latest bridge changes. Its original queue runner treated only PASS as terminal, so a FAILED task could remain first in the queue and starve later tasks.

Bridge main now contains:

- FAILED same-blob terminal queue handling (`collector_queue_runner` v2)
- richer fresh-discovery diagnostics on capture failure
- no relaxation of `candidateUnique`
- no cached RAM base as discovery input
- no transient player state gate
- no enemy state gate

## Stronger immutable discovery fingerprint

Seven EFIELD captures first identified additional stable P1/P2/P3 structural triplets. A cross-corpus validation then tested all compatible retained raw captures.

Cross-corpus coverage:

- compatible captures: **13**
- compatible frames: **26,402**
- mismatches: **0** for every checked triplet

Validated player triplets:

- `0x20`: `00/01/02`
- `0x21`: `1A/1B/1C`
- `0x26`: `00/01/02`
- `0x62`: `00/02/04`
- `0x7C`: `00/04/08`
- `0x92`: `00/04/08`

`bridge/session_discovery.py` now uses these immutable structural checks as `immutable-player-structure-v3` while preserving the strict one-candidate requirement.

## Verification

GitHub Actions smoke checks passed:

- collector Python modules compile successfully
- strengthened immutable v3 fingerprint source checks pass
- FAILED terminal queue guard is present
- cross-corpus fingerprint validation passes with zero mismatches

## Local reload required

`START_WOF_COLLECTOR.bat` runs the local Python checkout directly and does not pull GitHub changes or hot-reload modules. Therefore the currently running Collector cannot use the new v3 discovery logic until the local `wof-winkawaks-bridge` checkout is updated and the Collector service is restarted.

After that reload, the next EFIELD action should be a new one-frame discovery probe. Only after it returns unique discovery PASS should a new 60-second proximity-association burst be queued.
