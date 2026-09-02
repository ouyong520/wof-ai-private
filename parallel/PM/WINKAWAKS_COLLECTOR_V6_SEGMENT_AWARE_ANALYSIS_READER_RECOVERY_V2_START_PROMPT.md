# WinKawaks Collector V6 — Segment-Aware Analysis Reader Recovery V2

stageId: `WINKAWAKS_COLLECTOR_V6_SEGMENT_AWARE_ANALYSIS_READER_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v6.segment-aware-analysis-reader.recovery-v2`
dedupMode: `exclusive`

Priority: **P2 segment-aware analysis tooling / implementation recovery**

## Mandatory duplicate-forward / successor preflight

Read `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md` first.

This Recovery V2 itself may be forwarded more than once. Before claim acquisition or implementation, verify current:

- `ouyong520/wof-ai-private/main`;
- `ouyong520/wof-winkawaks-bridge/main`;
- original V6 START_PROMPT and original V6 canonical/stage claim;
- this Recovery V2 START_PROMPT and any Recovery V2 claim/stage;
- any durable V6 RESULT;
- any newer V6 recovery/successor authority.

If this same/equivalent Recovery V2 is already ACTIVE under another legitimate current owner, already COMPLETE, or superseded by a newer legitimate successor, do not execute or create a parallel equivalent claim. Stop:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

Historical original V6 `ACTIVE` residue is not a reason to rerun the original START_PROMPT. This file is PM-authorized recovery authority for that stopped generation.

## Read first

- `parallel/PM/WINKAWAKS_COLLECTOR_V6_SEGMENT_AWARE_ANALYSIS_READER_START_PROMPT.md`
- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- V3 Recovery V2 RESULT
- V4 Recovery V3 RESULT
- V5 Recovery V2 RESULT
- current original V6 canonical/stage claims
- current bridge V3/V4/V5/V6 contracts, tests and workflow
- current both repository mains

## Recovery facts at staging time

The original V6 worker has already landed substantial implementation in `ouyong520/wof-winkawaks-bridge`; do not restart from zero.

Observed V6 bridge commits include:

- `a2daed264e6a0dad59bc44472e7b9358e1bcc424` — segment-aware analysis reader core;
- `a2ff11bc285b0798eb9bd24886f3482085a9e5dc` — analysis reader self-check matrix;
- `c377217f2e6d530d23cdc5a45c16bf00e408dc03` — versioned analysis result schema;
- `381f435b6627b18649ba0a7d97e63176fb146a6f` — analysis contract and CLI docs;
- `69741873e22a4c1a93e0711281ac656b4ea89bdf` — Collector smoke integration;
- `4c018878c0f5d929b1ca65a1bb5354dd9788d58e` — one-shot integrated self-check receipt support.

At staging time the last observed tree for `4c018878...` is `ec4e04fc827b6a4ec3df893c6ad2de7859e3f319`.

The original canonical claim `winkawaks.collector.v6.segment-aware-analysis-reader` remained `ACTIVE`, and the expected durable original V6 RESULT was not present. Treat those facts only as recovery context: re-read current HEAD because the repositories may have advanced after this prompt was created.

## Objective

Finish the original V6 module end-to-end from current HEAD, preserving all correct existing implementation and repairing only concrete remaining gaps.

This is implementation recovery, not Fresh QA, not a second implementation, and not permission to move to V7.

The completed V6 must satisfy the full original V6 START_PROMPT, including:

- strict V4 dataset-ID/source authority resolution;
- V3 segment-aware logical frame streaming without destructive concatenation;
- honest explicit handling of COMPLETE/PARTIAL/FAILED evidence;
- legacy snapshot/burst read compatibility where repository authority permits;
- V5 verified archived-only read resolution without weakening receipt/hash authority;
- bounded-memory streaming whose deterministic result is independent of chunk boundaries;
- deterministic raw delta summaries;
- cross-capture controlled-scene diff;
- caller-specified transition/temporal precursor research analysis;
- deterministic candidate offset ranking with visible formula/components/tie ordering;
- explicit repeated-trial/experiment grouping only from V4 metadata;
- structured operator/scene metadata preservation without semantic inference;
- versioned machine-readable analysis result identity/provenance;
- deterministic CLI and bounded JSON output;
- derived analysis artifact isolation from V3/V4/V5 capture/storage authority;
- strict source namespace separation;
- `researchOnly=true` and no semantic promotion.

## Recovery-tail verification priorities

Do not rewrite the reader merely because this is a recovery. First inspect the landed V6 candidate and close only real gaps, especially:

1. current analysis result schema exactly matches runtime output/parameter strictness;
2. analysis/result identity binds immutable dataset/source evidence plus canonical parameters, not labels/paths;
3. V3 COMPLETE stream cannot stay COMPLETE after missing/reordered/duplicate/corrupt segments or frame continuity failure;
4. V3 PARTIAL/FAILED analysis requires explicit opt-in and preserves exact limitations;
5. legacy evidence does not fabricate V3-only authority;
6. V5 archived-only resolution requires current verified receipt/hash authority and fails closed on mismatch;
7. chunk/window boundaries do not alter delta/compare/transition/rank results;
8. transition operations make association/support claims only, never causal or production-danger claims;
9. candidate ranking records formula version, components and deterministic tie break;
10. group membership is never synthesized from filenames/labels;
11. output cannot silently backfill missing gameplay semantics from raw values;
12. result/derived artifact path cannot be mistaken by V3/V4/V5 as capture/catalog/archive authority;
13. current V3/V4/V5 contracts remain unchanged and compatible;
14. CLI/help/docs/schema/tests are mutually current;
15. integrated self-check receipt, if retained, must bind the exact tested commit/run and must not create a recursive workflow write loop, stale PASS, or public mutable PASS authority;
16. workflow write permission, if required only for the one-shot receipt, must remain narrowly justified and not become general Collector correctness authority; if a safer current-repo mechanism already exists, use it without broadening scope.

Any concrete current defect found in this boundary is part of V6 Recovery V2. Fix the coherent defect cluster, then rerun only implementation-owned affected/integrated checks.

## Testing cadence

This is implementation-owned recovery only.

Do not create:

- Fresh QA;
- second opinion;
- cross-check;
- QA V2/V3/V4/V5/V6;
- readiness audit;
- Browser/WOF session;
- real WinKawaks capture;
- Training Farm run.

Complete the module first, then run one coherent implementation self-check boundary. Appropriate checks include:

- compile/parse;
- V6 owned tests;
- schema/runtime contract validation;
- deterministic fixtures for COMPLETE/PARTIAL/legacy/archive paths;
- chunk-boundary equivalence;
- delta/compare/transition/rank correctness;
- strict malformed/coercible/non-finite parameter rejection;
- source namespace/no-semantic-inference checks;
- V3/V4/V5 regressions needed for integration safety;
- current Collector smoke workflow where appropriate.

Do not multiply test generations. If the first integrated run finds a concrete V6 or stale-wiring defect, fix it and perform one focused successor run.

## Hard boundaries

Do not modify or block:

- `product/alpha/**`;
- Alpha V1 release/live acceptance/proof;
- danger rules or target semantics;
- Transport / Recorder / PYLAUNCH / OneClick;
- Training Farm runtime, savestate, PPO/RL, input/action injection, or 10-worker scheduling;
- V3 acquisition authority;
- V4 immutable dataset/lifecycle authority;
- V5 storage/archive/prune semantic authority.

Collector remains:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
containsAiDecisionLogic=false
```

V6 is offline/read-side research tooling only.

## Durable completion

Before COMPLETE, write:

`parallel/PM/WINKAWAKS_COLLECTOR_V6_SEGMENT_AWARE_ANALYSIS_READER_RECOVERY_V2_RESULT.md`

Record at minimum:

- exact final bridge HEAD/tree;
- exact relevant V6 blobs;
- exact upstream V3/V4/V5 authority consumed;
- final analysis/read schema/version;
- dataset/input authority and result identity contract;
- V3 segmented logical stream behavior;
- PARTIAL/FAILED behavior;
- legacy behavior;
- V5 archived-only read behavior;
- bounded-memory/chunk determinism;
- delta/compare/transition/rank operations;
- repeated-trial behavior;
- research-only/no-semantic-promotion contract;
- CLI/result/derived-artifact contract;
- integrated self-check commands/results and exact workflow run/head if used;
- any real remaining data/runtime limitation.

Then close the Recovery V2 canonical claim and stage `COMPLETE` under canonical dedup v2. Preserve the stopped original V6 claim as historical truth; do not rewrite it to pretend the original worker closed normally. Recovery V2 becomes the durable successor authority.

## Stop

Claim acquisition is not progress completion. Do not stop at repository inspection, one patch, one test, one workflow edit, receipt creation, or documentation.

Continue through the complete remaining V6 functional boundary, implementation integration, coherent self-check, durable RESULT and Recovery V2 claim/stage closeout.

Do not begin V7 from this worker.

Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V6 SEGMENT-AWARE ANALYSIS READER — REUSABLE RAW RESEARCH TOOLKIT COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V6 SEGMENT-AWARE ANALYSIS READER — <precise unavoidable blocker>`
