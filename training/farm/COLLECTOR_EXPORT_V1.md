# Training Farm read-only Collector exporter v1

This is the source-owned `stable-retro-fbneo` boundary used by Unified Collector V11. It publishes evidence that an already-running Training Farm runtime has produced; it is not an emulator controller.

## Safety boundary

`training.farm.collector_export` does not own a `TrainingFarmAdapter` and does not call reset, step, step-frame, load-state, save-state, or worker orchestration APIs. It never chooses gameplay actions or injects input. It does not launch, stop, schedule, or scale real Training Farm workers. R0.2/R0.4 real-WOF proof gates and the R0.5 lock are unchanged.

The exporter is intended to be called by a Training Farm process at a point where that process already has the evidence it wants to expose. The only write side effect is local exporter evidence under the configured export directory.

## Local authority layout

The exporter writes:

- `registry.json`: an atomic discovery index. It is not the evidence authority.
- `workers/<workerId>/records/<generation>/<sequence>-<sha>.json`: immutable source record used by the Unified Collector adapter.
- `workers/<workerId>/artifacts/<generation>/<sequence>-<sha>.json`: immutable bounded evidence artifact.
- `workers/<workerId>/current.json`: atomic source convenience pointer/record for diagnostics.

Each registry row binds worker ID, worker generation, sequence, immutable record path and the exact record SHA-256. The immutable record in turn binds its immutable evidence artifact by path, byte count and SHA-256. Worker publishers are serialized with a local OS file lock; registry publication has a separate local OS lock.

For one worker ID, a generation cannot change its generation-start authority, sequence numbers must strictly increase, and an older generation cannot replace a newer generation. Runtime identity, ROM identity, Farm candidate identity, memory-layout identity, episode/generation, fork/root/branch identity and the exporter source identity are preserved explicitly. The capture-binding SHA-256 is source-aware and no Browser/WinKawaks address meaning is inferred from Stable-Retro memory-block keys.

## Evidence and bounds

The immutable artifact can contain the current RAM snapshot, address-aware RAM blocks, bounded observation samples, trajectory metadata, already-existing action/result trajectory metadata, root/fork/branch/savestate metadata, and runtime/resource/timing metadata. Missing optional facts remain `null`/absent from the evidence-kind list rather than being guessed.

One artifact is bounded to 4096 observation samples, 16 MiB of raw encoded evidence input and 1 MiB of aggregate JSON metadata. Non-finite/coercible values, overlapping/changing RAM layouts, unsafe paths, stale generation writes and hash mismatches fail closed.

## Adapter handoff

The V11 `stable-retro-fbneo` Unified Collector adapter reads only the local registry, immutable record and immutable artifact. It may select `ONE`, explicit `WORKER_IDS`, or `ALL_ACTIVE` up to 10 workers. The adapter remains the only Git queue consumer; the Training Farm exporter never reads or writes the Git task/status/result queue.

## ROM-free 10-worker isolation fixture

The stage guard forbids launching 10 real emulator workers for V11 validation. Use the deterministic fake-runtime fixture instead:

```bash
python -m training.farm.collector_export_fixture \
  --export-root /tmp/wof-v11-training-farm-export \
  --workers 10
```

The fixture constructs only the repository's `DeterministicFakeBackend` runtime identity and source-owned export evidence. It performs zero real-worker launches and does not reset, step, load state or select/inject gameplay input.

Focused exporter regression:

```bash
python -m unittest training.farm.tests.test_collector_export -v
python -m unittest training.farm.tests.test_collector_export_fixture -v
```
