# SWEEPATLAS — WinKawaks retained-capture atlas

Updated: 2026-09-01

Status: **retained corpus audited to the current GitHub limit**

Evidence class: `WinKawaks-local-discovery-only`

## Scope

SWEEPATLAS consumes already-retained Collector tasks/results/raw and turns them into a capture/type/attack atlas. It does not change Browser/WASM production state, does not assign Future Danger predictor semantics, and does not write game memory.

This lane writes only `parallel/SWEEPATLAS/**`.

## Critical result of the repository audit

The repository currently contains **no `BASECAP-SWEEP-*` task/result/raw series** and therefore no authoritative full-game `stage/scene/wave` labels from the sweep protocol described in `WINKAWAKS_SINGLE_OPERATOR_SWEEP_GUIDE.md`.

The retained corpus is instead composed of:

- canonical BASECAP laboratory/control captures;
- seven natural-gameplay EFIELD captures;
- GEO captures;
- RAWMINE captures;
- two tiny Collector smoke/delivery artifacts.

Consequently:

- capture-level enemy-type coverage can be recovered from retained EFIELD analyses;
- target and lifecycle evidence can be indexed;
- attack-associated executor phase values can be indexed structurally;
- **stage/scene/wave -> enemy/type/attack cannot be populated without inventing labels**, so those fields remain explicitly `null` / `UNKNOWN`;
- boss-name -> internal-type mapping is not asserted;
- scene-specific attack claims are not asserted.

This is a data-provenance limitation, not evidence that the missing enemies/attacks do not exist.

## Admission rule

A raw-backed capture is admitted as trusted corpus evidence only when all of the following are consistent:

1. task file `taskId` matches the result;
2. result `taskBlobSha` matches the actual task blob SHA;
3. result status is `PASS`;
4. `readOnly=true` and `writesGameMemory=false`;
5. `readErrors=0` and `frameSizeErrors=0` for the primary corpus;
6. result names a retained `rawArtifact.remotePath`;
7. the current `captures/` manifest contains that path and its Git blob SHA matches `rawArtifact.remoteContentSha`.

Canonical BASECAP identity is additionally checked against `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`.

## Raw/statistics provenance

The GitHub connector exposes the retained gzip objects and their blob identity, but does not expose the complete binary gzip body as a decompressed local stream in this run. Therefore SWEEPATLAS does **not** pretend to have reparsed the gzip bytes locally.

Raw-derived counters in this atlas are consumed from the bridge's already-generated retained analysis products, especially:

- `results/efield/RUN_FOCUS.md`
- `results/efield/ALL_RUN_CORE.md`
- `results/efield/TYPE_FINGERPRINT.md`
- `results/efield/EPISODE_STABILITY_ATLAS.md`
- `results/efield/ATTACK_CYCLE.md`
- `results/efield/summary.json`

Those reports are themselves generated from the retained EFIELD gzip corpus. SWEEPATLAS separately validates the task/result/raw identity chain before admitting the associated run.

## Local field anchors used for indexing

These are **WinKawaks discovery-namespace anchors only**:

- enemy internal type / type-present episode anchor: enemy `+0x24` U8;
- live target reference: enemy `+0x6D..0x6E` U16 big-endian;
- coarse attack-associated executor family: enemy `+0x73` U8;
- finer executor subphase feeding `+0x73`: enemy `+0x6C` U8;
- second fine family: enemy `+0x77` U8 with upstream `+0x70` U8.

`+0x73/+0x6C/+0x77/+0x70` are recorded only as **attack-associated structural executor phases**. SWEEPATLAS does not rename them as exact move IDs, hit frames, startup/recovery, or Browser ACTIVE.

## Files

- `CAPTURE_INDEX.json` — machine-readable audit/admission index.
- `ATLAS.json` — machine-readable enemy/type/target/attack atlas currently derivable from retained evidence.
- `SWEEP_ATLAS.md` — human-readable capture and coverage table.
- `ENEMY_TYPE_ATLAS.md` — type-centric atlas and priority T23/T18/T16/T20 findings.
- `ATTACK_ATLAS.md` — attack-associated structural phase atlas.
- `FRONTIER.md` — explicit solved/unsolved boundary and the single consolidated provenance gap.

## Naming convention

`Txx` means the **decimal** representation of the WinKawaks-local U8 value at enemy `+0x24`.

Examples:

- `T23 = 0x17`
- `T18 = 0x12`
- `T16 = 0x10`
- `T20 = 0x14`

No equality with a Browser/WASM offset or production type namespace is implied.
