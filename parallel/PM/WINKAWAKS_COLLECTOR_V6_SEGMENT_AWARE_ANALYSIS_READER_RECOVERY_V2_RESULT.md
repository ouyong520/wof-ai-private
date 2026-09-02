# WinKawaks Collector V6 — Segment-Aware Analysis Reader Recovery V2 RESULT

Status: **COMPLETE**

Stage: `WINKAWAKS_COLLECTOR_V6_SEGMENT_AWARE_ANALYSIS_READER_RECOVERY_V2`

Dedup key: `winkawaks.collector.v6.segment-aware-analysis-reader.recovery-v2`

Recovery claim token: `46b6ba65b262b792046c08a1557cf8c8216e448006250856`

Final verdict:

`COMPLETE — WINKAWAKS COLLECTOR V6 SEGMENT-AWARE ANALYSIS READER — REUSABLE RAW RESEARCH TOOLKIT COMPLETE`

## Recovery authority / duplicate preflight

Recovery V2 re-read both repository mains, the original V6 START_PROMPT, original V6 canonical/stage claims, this Recovery V2 authority, durable V6 RESULT paths and successor paths before ownership.

At acquisition time:

- original V6 canonical/stage generation remained historical `ACTIVE` residue from the stopped worker;
- no Recovery V2 canonical claim existed;
- no Recovery V2 stage claim existed;
- no original or Recovery V2 durable V6 RESULT existed;
- no newer V6 Recovery V3/successor authority existed.

Recovery V2 therefore acquired a fresh canonical dedup-v2 claim and stage claim. The historical original V6 claim is intentionally preserved unchanged; this RESULT and Recovery V2 completed claims are the durable successor authority.

## Exact final bridge candidate

Repository: `ouyong520/wof-winkawaks-bridge`

Final exact bridge `main`:

```text
HEAD: c20c9dbe0684c645b4bb8760ab5110b00d12b09c
tree: 4011e46717ae6323e53d05b1b7973c1fa836536a
commit: Collector V6 recovery: remove mutable self-check receipt authority
```

The final tree is exactly the same tree as the already-successful V6 smoke-integration commit `69741873e22a4c1a93e0711281ac656b4ea89bdf`. Recovery did not rewrite the V6 reader core, schema, tests, docs, V3/V4/V5 implementation or capture/storage semantics.

Exact relevant V6 blobs at the final candidate:

| Path | Exact blob SHA |
| --- | --- |
| `bridge/analysis_reader.py` | `667a2290603d5f494947417db05eab8a6ac97b43` |
| `tests/test_analysis_reader.py` | `6d1318d8d46e2dbb0998407ce86c43fe1f5cc35b` |
| `schemas/collector_analysis_result_v1.schema.json` | `9af389f0d568d333e34e9887d23cd103dc85835c` |
| `docs/COLLECTOR_V6_SEGMENT_AWARE_ANALYSIS_READER.md` | `18d2fad49665ba3a2f6ce5cfacbe326d6ceafd9c` |
| `.github/workflows/collector-python-smoke.yml` | `e870900824151ba8e37d78f2cfb739955efca06a` |

Original landed V6 implementation lineage retained:

- `a2daed264e6a0dad59bc44472e7b9358e1bcc424` — segment-aware analysis reader core;
- `a2ff11bc285b0798eb9bd24886f3482085a9e5dc` — V6 implementation self-check matrix;
- `c377217f2e6d530d23cdc5a45c16bf00e408dc03` — versioned analysis result schema;
- `381f435b6627b18649ba0a7d97e63176fb146a6f` — analysis contract and CLI documentation;
- `69741873e22a4c1a93e0711281ac656b4ea89bdf` — V6 integration into Collector smoke.

The stopped worker's later `4c018878c0f5d929b1ca65a1bb5354dd9788d58e` one-shot receipt experiment is not retained as final authority; see Recovery-tail defect below.

## Exact upstream authority consumed

V6 consumes and preserves, rather than replaces, the completed Collector stack:

### V3 segmented capture authority

Durable upstream RESULT:

`parallel/PM/WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_RECOVERY_V2_RESULT.md`

Exact upstream implementation authority recorded there:

```text
final bridge commit: c180e303cb1caf10effde49edceec4ea70a26cc2
final tree: c6796d602f3c7aeb2046e3150b351cec31b1df30
```

V6 relies on V3's authoritative manifest / ordered-segment / taskBlob / capture / session / source-runtime identity and exact retained segment bytes. It does not modify V3 acquisition or terminal semantics.

### V4 dataset/catalog authority

Durable upstream RESULT:

`parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V3_RESULT.md`

Exact upstream implementation authority recorded there:

```text
final bridge commit: c48cdd03b0136247d794078d879a868d10e1f49c
final tree: 6fac3df12311f92a2ca2aa8e51522e62faa0ed06
catalog version: wof_collector_dataset_catalog_v1
capture identity version: wof_collector_capture_identity_v1
```

V6 selects by immutable V4 dataset identity and preserves V4 lifecycle/integrity separation. Filenames, labels and paths are not promoted into dataset identity.

### V5 storage/archive authority

Durable upstream RESULT:

`parallel/PM/WINKAWAKS_COLLECTOR_V5_LONG_RUN_STORAGE_RETENTION_MANAGER_RECOVERY_V2_RESULT.md`

Exact upstream implementation authority recorded there:

```text
final bridge commit: bfe8b95591f5f803d298f7cbe87a417b65e74326
final tree: f6aba2502d03c11963cfb570b8a065a14bbcd67c
policy schemaVersion: wof_collector_storage_policy_v1
```

V6 uses the current hardened V5 receipt/hash verifier for archived-only resolution and does not create archive/prune authority of its own.

## Analysis/read schema and identity contract

Final V6 versions:

```text
toolVersion: wof-winkawaks-collector-analysis-reader-v6
result schemaVersion: wof_collector_analysis_result_v1
analysis/result identity version: wkan-v1
rank formula version: wof_collector_candidate_rank_v1
sourceNamespace: winkawaks
```

Every successful analysis result is research-only and carries:

```text
researchOnly=true
semanticAuthority=false
readOnly=true
writesGameMemory=false
inputInjection=false
```

The deterministic `analysisId` binds the versioned operation, immutable input identity projection and canonical analysis parameters. The immutable input projection includes the V4 dataset ID/source namespace/capture mode/source task binding, task blob where available, capture/session/source-runtime identity where available, V4 content bindings and exact hashes of artifacts actually used.

Display labels, filenames and resolved local/archive paths are excluded from the deterministic identity. Moving an identical artifact without changing immutable evidence therefore does not create a false new analysis identity.

`resultSha256` additionally binds the exact analyzed ranges and computed research payload. Generated timestamps/build provenance are descriptive and do not alter deterministic result identity.

The result envelope is versioned by `schemas/collector_analysis_result_v1.schema.json`; operation-specific parameters are normalized/validated by the runtime with strict native numeric/integer checks and canonical JSON hashing. Coercible strings, booleans where strict integers are required, non-finite values and out-of-range values fail closed.

## V4 dataset selection and source isolation

Primary selection is exact immutable V4 `datasetId`. Practical catalog filters remain bounded to V4-recorded fields.

Default analysis requires lifecycle `VALID`. `INVALID`, `SUPERSEDED` and `UNREVIEWED` evidence require explicit inactive opt-in. Integrity `PARTIAL` / `FAILED` requires explicit partial-evidence opt-in where analysis remains possible.

The reader accepts only:

```text
sourceNamespace=winkawaks
```

It does not silently reinterpret `browser-wasm`, `stable-retro-fbneo` or unknown evidence as WinKawaks. No cross-runtime offset inheritance or semantic equivalence is created.

## V3 segmented logical stream behavior

For `captureMode=segmented_v3`, V6 exposes one ordered logical frame stream without concatenating or rewriting the source artifacts.

Before a COMPLETE logical stream is accepted, the reader verifies current V4/V3 authority including manifest identity, task/blob/capture/session/source identity, ordered segments, segment indexes, exact retained artifact hashes, global frame continuity and frame-record integrity. Segment-local identity is retained while global frame sequence is exposed to analysis operations.

Each JSONL segment is read incrementally. Header `bytesPerFrame`, raw record width, per-frame hash and sequence are checked. Missing, duplicate, reordered, corrupt or discontinuous evidence fails closed instead of being skipped while retaining COMPLETE status.

## PARTIAL / FAILED behavior

V4 `PARTIAL` / `FAILED` integrity or non-COMPLETE V3 terminal evidence never masquerades as COMPLETE.

Analysis requires explicit partial-evidence authorization and emits:

```text
status=PARTIAL_EVIDENCE
```

with exact limitations carried in each input projection. Only finalized/available authoritative ranges are analyzed; gaps are not synthesized or interpolated.

## Legacy snapshot / burst behavior

Legacy Collector `snapshot` and `burst` JSONL/gzip evidence remains readable where V4 authority provides usable immutable artifact bindings.

V6 preserves the historical authority that actually exists and does not fabricate V3 manifest/session/segment fields. Frame width comes from the authoritative raw stream header rather than a hard-coded future WOF layout. Local/gzip hashes are verified and malformed/truncated/sequence-invalid/frame-hash-invalid evidence fails closed.

## V5 archived-only resolution

If an authoritative V4 source artifact is absent locally, V6 may use an archived copy only after the current hardened V5 receipt validator proves the receipt and archived bytes/hashes match the exact V4-managed artifact projection.

A missing receipt, changed receipt, conflicting artifact mapping, missing archive bytes or hash mismatch fails closed. The archived path is a resolution location only; dataset identity remains the original V4 immutable dataset identity.

## Bounded-memory / chunk and segment determinism

The reader is streaming/raw-first rather than whole-session materializing:

- JSONL/gzip frame records are iterated incrementally;
- V3 segments are traversed in authoritative order as one logical stream;
- analysis ranges are bounded;
- offset span/result sizes, transition windows/event values/dataset counts/trial counts and transition-state tables have explicit hard caps;
- cross-frame state is carried explicitly rather than resetting at segment boundaries.

Because the algorithms operate on the same ordered logical frame sequence and carry transition/change state across source-segment boundaries, deterministic outputs do not depend on where V3 segment/file boundaries occur. No destructive concatenation or temporary authoritative raw stream is created.

## Research operations

### Delta

`delta` reports deterministic raw-byte facts including per-offset change count/frequency, first/last observed change, distinct-value count within the bounded representation and stable ratio. Caller-specified ranges are explicit.

### Compare

`compare` reports bounded deterministic cross-dataset raw differences such as stable/varying behavior, distinct-value-set differences and transition-distribution differences. It does not infer temporal alignment from filenames or scene labels; aligned windows exist only when supplied explicitly by the caller.

### Transitions

`transitions` accepts caller-defined raw events/predicates and reports bounded lead/lag association/support candidates. Output is explicitly candidate/association language; it carries no causal claim and cannot create production danger/target authority.

### Rank

`rank` records formula version, visible component metrics and deterministic ordering. The formula uses documented raw research components such as controlled-change selectivity, held-stable stability, repeated-trial consistency, optional transition support and noise penalty. Ties are deterministically ordered by ascending raw offset.

Ranking is research triage only and never semantic authority.

### Repeated trials

`trials`/repeated-trial helpers use only explicit V4 grouping metadata such as `repeatGroupId`, `trialId`, `trialOrdinal` and related fields. Missing group/trial authority fails closed; membership is never synthesized from filenames or display labels.

## Structured metadata / no semantic promotion

Operator-provided V3/V4 metadata such as `sceneLabel`, `playerConfig`, `operatorAction`, `changedVariable`, `heldStableVariables`, `researchQuestion`, `confounders` and `notes` is preserved as descriptive provenance.

V6 does not backfill missing gameplay semantics from raw values. Candidate results do not become player position, enemy type, attack ID, danger, target, reward or action authority merely because a raw offset ranks highly.

## CLI and derived artifact contract

Final deterministic CLI surface:

```text
inspect
stream-info
verify
delta
compare
transitions
rank
trials
```

CLI output is structured JSON with deterministic ordering and bounded result sizes. Invalid source/dataset/range/parameter/integrity states return fail-closed errors rather than a false COMPLETE result.

Optional result-file output is restricted to:

```text
derived/analysis/**
```

Finalization uses the V6 result validator and guarded derived namespace. Derived analysis files are disposable/recomputable research artifacts and are not V3 capture evidence, V4 catalog identity authority or V5 archive/prune authority.

## Recovery-tail defect closed

The stopped V6 worker's final commit `4c018878c0f5d929b1ca65a1bb5354dd9788d58e` changed the otherwise-green Collector smoke workflow into a repository-writing one-shot receipt publisher:

- workflow permission changed from `contents: read` to `contents: write`;
- the workflow attempted to commit/push mutable `results/v6_analysis_reader_selfcheck_latest.json`;
- PASS authority therefore depended on a public mutable latest receipt and expanded workflow write permission;
- exact-head workflow run `33638830094` for `4c018878...` ended `failure` before any job was created.

This was inconsistent with Recovery V2 priorities requiring exact tested-commit/run binding, no stale/public-mutable PASS authority, no recursive workflow write loop and narrowly justified permissions.

Recovery V2 removed the one-shot repository-writing receipt path and restored the prior read-only workflow (`contents: read`). The authoritative implementation self-check evidence is now the immutable GitHub Actions run bound directly to the exact tested commit/head, not a mutable PASS file written back by the workflow.

No reader/core/schema semantics were changed for this fix.

## Implementation-owned self-check

Testing followed `TESTING_CADENCE_POLICY.md`: one coherent Recovery-tail fix, then one integrated implementation-owned smoke run. No Fresh QA, cross-check, second opinion, Browser/WOF session, real WinKawaks capture or Training Farm run was created.

Final exact-candidate run:

```text
workflow: Collector Python smoke check
run id: 33642019001
head sha: c20c9dbe0684c645b4bb8760ab5110b00d12b09c
tree: 4011e46717ae6323e53d05b1b7973c1fa836536a
conclusion: SUCCESS
```

Successful current-head steps:

```text
Compile collector modules                                      PASS
Collector V3 segmented implementation regressions              PASS
Collector V4 dataset catalog Golden self-check                 PASS
Collector V5 storage retention self-check                      PASS
Collector V6 segment-aware analysis reader self-check          PASS
V6 CLI/help + schema/tool/research-only envelope check          PASS
Current retained Collector evidence index                      PASS
V5 current repository health + schema                          PASS
Immutable discovery / segmented authority / V5/V6 wiring       PASS
```

Upstream durable counts remain the completed module counts recorded by their own authorities: V3 segmented regressions 15/15, V4 catalog 20/20, V5 storage 28/28. The final current-head workflow re-ran those owned suites successfully together with the V6 suite.

For comparison, V6 smoke integration commit `69741873e22a4c1a93e0711281ac656b4ea89bdf` had already passed run `33638573168`. Recovery final tree is exactly that same green tree after removing the stopped worker's receipt-only drift.

## Safety / lane isolation

Still true at final candidate:

```text
sourceNamespace=winkawaks
readOnly=true
writesGameMemory=false
inputInjection=false
containsAiDecisionLogic=false
```

Recovery V2 did not modify:

- `product/alpha/**`;
- Alpha V1 release/live acceptance/proof, danger rules or target semantics;
- Transport / Recorder / PYLAUNCH / OneClick;
- Training Farm / Stable-Retro / FBNeo / PPO/RL / savestate/action injection / 10-worker scheduling;
- V3 acquisition/terminal semantics;
- V4 immutable dataset/lifecycle semantics;
- V5 archive/prune/storage semantic authority.

## Remaining runtime/data limitations

No unresolved repository implementation blocker remains inside V6 Recovery V2.

Intentional/runtime facts remain:

- V6 is offline/read-side research tooling and does not establish Browser production semantics;
- actual archived-only use requires the relevant V5 receipt and exact archived bytes to exist and verify on the machine/repository state where analysis runs;
- PARTIAL/FAILED evidence remains explicitly limited and cannot be upgraded by V6;
- no real WinKawaks gameplay session was started for this implementation recovery, so this RESULT does not invent machine-specific runtime/disk/capture facts.

## Closeout

V6 Recovery V2 has completed the only concrete current-tail defect, preserved the landed V6 body, passed one coherent exact-current-candidate integrated self-check, and now has durable implementation authority.

The original stopped V6 canonical/stage claim remains historical `ACTIVE` residue exactly as required. Recovery V2 canonical/stage claims are the successor generation to close `COMPLETE` against this RESULT.

Final status:

`COMPLETE — WINKAWAKS COLLECTOR V6 SEGMENT-AWARE ANALYSIS READER — REUSABLE RAW RESEARCH TOOLKIT COMPLETE`
