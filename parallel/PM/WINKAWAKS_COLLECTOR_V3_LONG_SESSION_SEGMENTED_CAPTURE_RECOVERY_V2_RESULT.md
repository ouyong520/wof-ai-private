# WinKawaks Collector V3 — Long-Session Segmented Capture Module Recovery V2 — RESULT

Status: **COMPLETE**

Final verdict:

`COMPLETE — WINKAWAKS COLLECTOR V3 LONG-SESSION SEGMENTED CAPTURE MODULE — COHERENT IMPLEMENTATION / MANIFEST / SELF-CHECK COMPLETE`

## Recovery authority

This is the PM-authorized implementation recovery generation for the stopped original stage.

- recovery stage: `WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_RECOVERY_V2`
- recovery dedup key: `winkawaks.collector.v3.long-session-segmented-capture.recovery-v2`
- recovery claim token: `3e759948bf23c19eb6568669b9b55896019c58f37d3dc675`
- original stopped stage: `WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_V1`
- original canonical claim: `parallel/PM/DEDUP_CLAIMS/winkawaks.collector.v3.long-session-segmented-capture.json`
- recovery canonical claim: `parallel/PM/DEDUP_CLAIMS/winkawaks.collector.v3.long-session-segmented-capture.recovery-v2.json`

The original V1 claim is intentionally not rewritten as though its stopped worker completed. Recovery V2 is the superseding implementation generation and is the generation closed by this RESULT.

## Exact bridge candidate

Repository: `ouyong520/wof-winkawaks-bridge`

- pre-V3 implementation base: `e3676d79a38ac23e572af69d23d560c01bd6777d`
- exact final bridge `main`: `c180e303cb1caf10effde49edceec4ea70a26cc2`
- final tree: `c6796d602f3c7aeb2046e3150b351cec31b1df30`
- V3 commits from pre-V3 base to final candidate: 9
- final recovery commit: `c180e303cb1caf10effde49edceec4ea70a26cc2` — `Collector V3 recovery: close segmented result authority gaps`

Final V3 changed/current blobs:

| Path | Exact blob SHA |
|---|---|
| `.github/workflows/collector-python-smoke.yml` | `0c27caad4d8819d33ec0672c06a3a4be5f8d146a` |
| `bridge/collector_queue_runner.py` | `8a25187b0e85cf839599a1be18376f06d63c0bd6` |
| `bridge/collector_segmented_authority.py` | `4814b6471ec1d597b304a3b68680518c375cc558` |
| `bridge/collector_segmented_session.py` | `2370791a686de75d3b7e5eca00555266a90635fc` |
| `bridge/collector_task_runner.py` | `babfa7345721dce39aea110f2f2d2da1b9c31f8f` |
| `bridge/raw_handoff.py` | `27d2f656d69efcf35b417eefa17e1caa20f82a05` |
| `docs/COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE.md` | `26d1dbd9a970dfe3bb19816b618eb11a044d3248` |
| `tests/test_collector_segmented_authority.py` | `5f58cd047a2b728ca6131d1d4889d7fd84316dc4` |
| `tests/test_collector_segmented_session.py` | `cac559c13a38f0fece854d4a077bbd9deb4d6dd1` |

## Completed module contract

The final candidate implements and retains the complete original V3 scope:

- `capture_raw_segmented_session` under `wof_collector_task_v3`;
- deterministic long-session segmentation, with each underlying capture bounded to the existing <=60 second burst implementation;
- strict finite primitive numeric parameter validation, max session 3600s, segment 5..60s, Hz <=120, max 720 segments;
- per-segment frame range, frame count, requested/achieved Hz, capture/frame timestamps, raw byte count and SHA-256;
- optional create-only per-segment gzip handoff with original/compressed bytes and SHA-256 plus remote blob/commit identity;
- authoritative local `wof_collector_segmented_session_manifest_v3` checkpoint;
- exact `taskId + taskBlobSha + captureId + sessionId + sourceIdentitySha256` binding, with the same binding embedded in each raw segment header context;
- COMPLETE rejected for missing, duplicate, reordered/non-contiguous, corrupt/hash-mismatched, unsafe, errored, or aggregate-inconsistent segment sets;
- runtime/session fail-closed identity based on WinKawaks PID, process creation FILETIME, exe name, RAM base and mapping, re-probed at segment boundaries and after capture so restarted/replaced runtimes cannot be stitched into one session;
- interruption preserves already finalized segment files and checkpoint state; same task does not silently append after restart;
- `local-only` remains default raw retention;
- structured descriptive scene metadata: `sceneLabel`, `playerConfig`, `operatorAction`, `changedVariable`, `heldStableVariables`, `researchQuestion`, `confounders`, `notes`;
- existing `capture_raw_snapshot` and `capture_raw_burst` remain backward-compatible and retain the <=60s burst contract;
- hard safety invariants remain `readOnly=true`, `writesGameMemory=false`, `inputInjection=false`, `containsAiDecisionLogic=false`, `containsFutureDangerRuleLogic=false`;
- WinKawaks Collector runtime/session identity remains separate from Browser/WASM and Stable-Retro/FBNeo Training Farm provenance. No Browser or Training Farm runtime is used as Collector capture authority.

## Recovery defect found and fixed

The stopped worker had already added local segmented manifest authority for the single-task runner, but two serialized/public result paths were still weaker than the local evidence contract:

1. `collector_queue_runner` treated a public terminal per-task result matching only `taskId + taskBlobSha + status` as completed/duplicate, and queue discovery could also trust a terminal public status record. A forged/replayed/detached terminal result could therefore suppress a valid segmented task without proving the retained local manifest/segment bytes.
2. `collector_task_runner` revalidated local evidence on a later duplicate run, but its immediate post-push `duplicateGuardVerified` still checked only public task/blob/status/capture fields rather than the same local-bound authority.

Recovery V2 fixed both paths by using one exact segmented terminal authority validator. It now requires result schema/action/safety, task/blob binding, terminal mapping, manifest schema, capture/session/source binding, failure/retention binding, exact local checkpoint equality, and—when COMPLETE—a fresh `validate_session_manifest` pass over retained local segment bytes. Queue discovery no longer treats mutable public DONE/PARTIAL/FAILED status as capture authority for a valid segmented task. Per-task and latest/status publication only proceed after the just-pushed segmented per-task result is read back and revalidated against local evidence.

A genuine current-task schema validation failure remains terminal without pretending it is capture evidence.

## Implementation-owned self-check

No Fresh QA, cross-check, second opinion, Browser session, WinKawaks live acceptance, or Training Farm run was created or performed.

Current-head GitHub Actions implementation self-check:

- workflow: `Collector Python smoke check`
- run id: `33618885915`
- exact head: `c180e303cb1caf10effde49edceec4ea70a26cc2`
- conclusion: **SUCCESS**
- Python: CPython 3.12.14 on Ubuntu 24.04
- module compile: **PASS**
- segmented implementation regressions: **15/15 PASS**
- immutable discovery + segmented authority wiring check: **PASS**

Regression coverage includes:

- strict parameter validation;
- legacy snapshot/burst compatibility and V3 schema/action compatibility;
- complete local segmented session and task/blob/capture/session/header bindings;
- per-segment gzip metadata;
- WinKawaks identity change fail-closed without cross-session stitching;
- interruption retention and no same-task append on restart;
- missing/duplicate/reordered segment rejection;
- raw hash corruption rejection;
- authoritative serialized COMPLETE binding to exact local evidence;
- public action/safety/capture/status/failure/retention tamper rejection;
- queue discovery rejection of detached result/status terminal claims;
- queue acceptance only for locally bound terminal result;
- genuine invalid-task validation failure terminal behavior;
- refusal to publish latest/status after detached post-push readback;
- detached duplicate repair path instead of `DUPLICATE_IGNORED`.

The earlier V3 queue commit had triggered the old smoke workflow and failed only because that workflow still searched for the obsolete literal `status.get("state") == "FAILED"`. Recovery V2 replaced that stale implementation-owned assertion with V3 compile, regression, immutable-discovery and segmented-authority checks; current-head run 33618885915 is green.

## Boundary / next step

This RESULT establishes coherent repository implementation plus implementation-owned deterministic self-check only. It does not claim fresh real-WinKawaks module-boundary acceptance and does not create an independent QA stage. Any later testing must be separately scheduled by PM under `TESTING_CADENCE_POLICY.md`.
