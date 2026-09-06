# P45 — P42 / P39 Live Diagnostic Staging Integration — COMPLETE

## Verdict

Maintained Alpha now has a default-off staging diagnostic wrapper that deterministically installs exact P39 first and exact P42 second, then exposes one zero-click diagnostic readout bound by `runtimeEpoch`, a diagnostic-only `rendererEpoch`, and `authorityKey`. Production authority semantics are not modified.

Tested candidate: `3dac7a9e2cbe4a23c3de44eb15cf45f19b136149`.

## Integrated sources

- P39 terminal COMPLETE: `ac5387f00d8c2382dcf3ed435ffcfa0acc1a2f05`.
- P39 classification remains exactly `UNVERIFIED_AUTO_BASELINE`.
- P39 staging bridge blob remains `05a1a6e8632f62dac6ff9bedf8897b3f2df6e685`.
- P42 terminal COMPLETE: `7b523187a955179b04155b758847c82aaf569a0d`.
- P42 staging classification is explicitly retained as `BOUNDED_LIVE_DIAGNOSTIC_MAPPING_ONLY`.
- P42 probe blob remains `32b9c50e8a72de1a097b8ce5dc91b69bdcef0219`.

P45 pins the exact accepted P39/P42 source blobs and fails closed before injection if those checkout bytes drift.

## Staging runtime contract

Owned runtime: `parallel/PYLAUNCH/wof_launcher/live_diagnostic_staging.py`.

The gate is explicit and default-off: `WOF_ALPHA_P45_LIVE_DIAGNOSTIC_STAGING=1` enables the integration. With the gate off, the wrapper delegates directly to the maintained `AlphaRuntimeManager`; it does not construct P39, read diagnostic source bytes, attach an extra CDP session, or inject P42.

With the gate on, injection order is contract-significant and deterministic:

1. `P39_AUTO_BASELINE_HUD`
2. `P42_RAW_CORRELATION_PROBE`

P39 is deliberately installed first because P42's correlation provider consumes the current P39 diagnostic status. No click, manual portrait/player selection, or manual seed is introduced.

## Same-run readout

The P45 readout preserves the complete P39 status and derives a compact lifecycle view containing:

- automatic P1/P2/P3 state;
- visible players;
- hidden players;
- lost players;
- stale state;
- ambiguous state;
- per-player reacquire count.

The P42 section contains:

- current probe state;
- the complete `result()` object as `rawBundle`;
- seal reason;
- teardown state.

P45 does not rank, select, sort, slice, filter, or delete P42 submissions/uploads/groups before handing the result to the bounded diagnostic consumer.

## Identity binding

Every diagnostic session carries:

- maintained Alpha `runtimeEpoch`;
- P45 diagnostic-session `rendererEpoch`;
- maintained runtime `authorityKey`.

P42's `bindingProvider` re-reads the same binding at hook time. A stale/mixed identity tears the diagnostic session down fail-closed. The P45 renderer epoch is explicitly labeled `P45_DIAGNOSTIC_SESSION_ONLY` and `productionRendererAuthority=false`; it is not written into canonical production renderer authority.

## Authority boundary

P45 does **not** create or upgrade any product authority. Specifically:

- no renderer source proof is minted;
- no P29 PASS is minted;
- no P32 QUALIFIED state is minted;
- no P36 direct renderer source is minted;
- no retry eligibility is minted;
- no promotion eligibility is minted.

The unchanged P39 payload may still contain its existing `rendererSourceProof: null` safety field; P45 does not turn that field into proof.

## Gate-off / teardown

Gate-off restores the maintained Alpha behavior by exact delegation. On bounded seal/revoke/rebind, P42 is stopped and its raw terminal result is preserved before P42 globals/hooks are removed; P39 is then disabled/disposed so its maintained HUD callback restoration path runs.

## Tests

Successful exact-candidate GitHub Actions run: `34005760019`, head `3dac7a9e2cbe4a23c3de44eb15cf45f19b136149`.

- Python syntax: PASS.
- P45 focused staging integration: 6/6 PASS.
- unchanged P39 regression: 4/4 PASS.
- unchanged P42 renderer correlation probe regression: 6/6 PASS.

The first CI attempt (`34005701323`) stopped before assertions because the clean Actions image lacked the launcher's existing `websocket-client` dependency. The workflow installed that dependency, the replacement exact candidate was materialized, and all focused/regression checks passed.

No real WOF game was run. Therefore Owner-visible correlation/mapping remains intentionally unproven here; that bounded live run remains P43 ownership.

## Scope isolation

P45 did not modify P43 harness assets, P29/P32/P36 criteria, maintained production Alpha source tuples, promotion flow, or alpha-live. No promotion was performed and alpha-live was not moved.

## Next action

P43 should instantiate the P45 staging wrapper with the explicit gate enabled for the next single bounded live diagnostic and persist the returned unfiltered P39/P42 readout.
