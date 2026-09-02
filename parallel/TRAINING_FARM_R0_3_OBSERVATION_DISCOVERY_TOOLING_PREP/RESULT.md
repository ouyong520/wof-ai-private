# WOF Training Farm R0.3 — Observation Discovery Tooling Prep Result

Date: 2026-09-02
Stage: `TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_V1`
Dedup key: `training.farm.r0.3.observation-discovery-tooling-prep`
Repository status: **TOOLING COMPLETE — REAL SEMANTIC MAPPING LOCKED PENDING CURRENT R0.2 REAL-WOF PROOF**

## Verdict

The complete R0.3 observation-discovery **preparation tooling** module is implemented on top of the R0.2 single-instance deterministic replay stack.

It now provides:

- source-native address-aware Stable-Retro/FBNeo RAM block sampling while preserving the R0.2 flat `read_ram()` compatibility path;
- strict controlled observation plans;
- same-savestate baseline/intervention repeated capture;
- runtime / ROM / R0.2 Farm source / R0.3 source / RAM-layout fail-closed binding;
- deterministic candidate byte/word change analysis and bounded ranking;
- a strict R0.2 real-proof consumer gate;
- explicit authority classifications;
- structured JSON schemas and CLI;
- ROM-free implementation fixture coverage;
- documentation preserving the Training Farm / Alpha / Collector authority boundary.

This result does **not** claim any real WOF semantic address. No candidate is declared to be player HP/X/Y, enemy state/slot, camera, attack ID, lifecycle, or another gameplay field.

Real R0.3 semantic observation mapping remains locked because no matching current-source real R0.2 `PASS / DETERMINISM_MATCH` proof was available in this worker environment.

## Exact implementation candidate

Current R0.3 source candidate commit before RESULT closeout:

`ad75eb6141f0468006c0d782b8cf62c0d47e3308`

The final source-head check observed this commit as current `main`; no later `training/farm/**` change was present before RESULT creation.

Exact current Farm blobs used by the R0.3 module:

- `training/farm/README.md` — `2866c642987a40c871d41efe527c3f10c7fda6fe`
- `training/farm/__init__.py` — `854ff42ff1dbf8c63607bbaeda13cfeae094a3c3`
- `training/farm/adapter.py` — `61807eba0aa05959bb48cc7bcd059c7a0d802108`
- `training/farm/fake_backend.py` — `4321a358fca4de1c535747015110fee0c74c42b3`
- `training/farm/stable_retro_backend.py` — `14ba7bf41019900d5189931f7dbb0a2819e53998`
- `training/farm/identity.py` — `9bfa117478b381ec5ac0ff21f02a1363c3271148`
- `training/farm/determinism.py` — `7cedcd78fe21835b8cc674c2ad781676146984d5`
- `training/farm/determinism.schema.json` — `22e0a25065f2d03864d759d9a3e01b187fe22462`
- `training/farm/determinism_actions.example.json` — `ff273d576c8ecb8b3ef9db1805d142b7d408a3c0`
- `training/farm/observation_discovery.py` — `349703a4a7271bcb8a5b712ee7d9a5bda326501e`
- `training/farm/observation_plan.schema.json` — `a198f2ff6b795991b4e2b6d6366f51f1db908412`
- `training/farm/observation_discovery.schema.json` — `d3ade3e901143b4e62146adea0a591f7bda7176f`
- `training/farm/observation_plan.example.json` — `577ca08cd281bd1cfce548f6bf98d69223733fbc`
- `training/farm/tests/test_contract.py` — `5349a5dea05e6e1a79b61d9d27213ce86d9a393c`
- `training/farm/tests/test_determinism.py` — `7df0d6977f0b7e6cc6d40c5e514dbdf4a3ead675`
- `training/farm/tests/test_observation_discovery.py` — `e6f638d79f025ee83d0af00a626283e22a0c4de2`

## Implemented surface

### 1. Address-aware Stable-Retro RAM blocks

R0.3 adds `RamBlockSnapshot` and `TrainingFarmAdapter.read_ram_blocks()`.

For the real backend, `StableRetroFbneoBackend.read_ram_blocks()` preserves the exact non-negative integer keys exposed by `GameData.memory.blocks`, ordered deterministically with exact bytes and block lengths. Malformed, out-of-order, duplicate/overlapping metadata fails closed where detectable.

The address authority is explicitly limited to:

`Stable-Retro GameData.memory.blocks key + byte offset`

No Browser/WASM or WinKawaks address equivalence is inferred.

The existing R0.2 `read_ram()` path remains available and is produced from the same ordered block bytes.

### 2. Canonical memory-layout identity

The observation runner records a layout identity containing:

- `sourceNamespace = stable-retro-fbneo`;
- address-kind / limitation text;
- ordered block bases and lengths;
- layout-shape SHA-256;
- current R0.2 runtime identity SHA-256;
- ROM SHA-256 / fixture marker;
- R0.2 Farm candidate identity;
- R0.3 discovery candidate identity and source-file hashes.

Runtime/ROM/R0.2 source/R0.3 source/layout drift during an experiment cannot produce a successful capture.

### 3. Strict experiment-plan contract

Schema:

`training/farm/observation_plan.schema.json`

Example:

`training/farm/observation_plan.example.json`

Plans bind:

- experiment id;
- starting-savestate id and optional expected state SHA-256;
- baseline actions;
- one or more intervention actions;
- exact frame horizon;
- repetitions;
- exact checkpoint frames;
- optional human `semanticLabel` / `hypothesis` metadata.

R0.2 all-four-player explicit frame-input semantics are reused. Player/button/frame/repetition/checkpoint values are strict; coercible booleans/strings/floats and malformed nested action contracts fail closed.

### 4. Same-savestate controlled capture

For each baseline/intervention repetition the runner restores one exact starting state, verifies state roundtrip and restored address-aware RAM, runs the exact action sequence to the exact horizon, captures requested checkpoints, and rechecks identity/layout authority.

No wall-clock timing participates in frame authority.

Compact output stores checkpoint hashes and candidate evidence rather than repository-scale raw RAM histories or savestate bytes.

### 5. Candidate change analysis

The analyzer emits candidates only, not semantic mappings. It supports byte candidates and adjacent two-byte little-endian analysis windows where available and records:

- block/base/length context;
- offset within block;
- source-native address when available from the backend;
- baseline/intervention observed values;
- changed/stable counts across repetitions;
- repetition stability;
- first/last observed changed checkpoint;
- baseline-control temporal changes;
- downgrade flag when control/baseline itself changes;
- evidence-only consistency score;
- deterministic rank/order.

The analysis is bounded to 50,000 changed-byte locations per intervention and at most 128 serialized ranked candidates; truncation is explicit.

### 6. R0.2 proof gate

The consumer gate validates a supplied R0.2 result before any real observation can be classified eligible. It requires the real R0.2 determinism schema/shape, `PASS / DETERMINISM_MATCH`, `REAL_WOF`, `realWofProof=true`, complete repetitions/checkpoints, canonical action/horizon hashes, strict real runtime identity, ROM/core/source identity and exact current Farm-source compatibility.

The documented cross-process compatibility rule permits only run-local `processId` to differ between an earlier R0.2 CLI process and the later R0.3 CLI process. Every other validated runtime/ROM/source/backend identity field must match exactly.

Because R0.3 necessarily changed adapter/backend files that participate in R0.2 Farm source identity, an older real R0.2 proof would be stale. The required Owner proof is a **new current-source R0.2 real run**.

Synthetic/fake results cannot upgrade themselves to real authority even if a proof-looking object is supplied.

### 7. Authority classifications

Structured results explicitly distinguish:

- `IMPLEMENTATION_FIXTURE`;
- `REAL_RUNTIME_OBSERVATION_UNVERIFIED`;
- `REAL_RUNTIME_OBSERVATION_ELIGIBLE`.

For this stage's executed fixture, authority remained `IMPLEMENTATION_FIXTURE` and `semanticMappingUnlocked=false`.

### 8. CLI / result schema

Primary CLI:

```bash
python -m training.farm.observation_discovery \
  --plan training/farm/observation_plan.example.json
```

ROM-free implementation fixture:

```bash
python -m training.farm.observation_discovery \
  --fake \
  --plan training/farm/observation_plan.example.json
```

Future eligible real run consumes a current R0.2 proof:

```bash
python -m training.farm.observation_discovery \
  --plan /path/to/real-observation-plan.json \
  --r0-2-proof /path/to/current-r0.2-real-proof.json \
  --output /path/to/local-r0.3-result.json
```

Result schema:

`training/farm/observation_discovery.schema.json`

Real prerequisite absence is represented as structured `SKIP / RUNTIME_PREREQUISITE_UNAVAILABLE`, not a fake PASS.

## Compact implementation self-check

Commands actually executed against the authored coherent R0.3 candidate content:

```bash
python -m compileall -q training
python -m unittest discover -s training/farm/tests -v
python -m training.farm.determinism --fake --actions training/farm/determinism_actions.example.json --horizon 8 --repetitions 3
python -m training.farm.observation_discovery --fake --plan training/farm/observation_plan.example.json
```

Observed outcome:

- `compileall`: PASS;
- module-owned unittest discovery: **19/19 PASS** after the single concrete candidate-ranking tie-break defect was fixed;
- existing R0.1/R0.2 contract/determinism regressions remained green;
- R0.2 fake replay: `PASS / DETERMINISM_MATCH`, still non-real proof;
- R0.3 fake controlled capture: `PASS / IMPLEMENTATION_FIXTURE_PASS`;
- R0.3 fixture authority: `IMPLEMENTATION_FIXTURE`;
- R0.3 fixture `semanticMappingUnlocked=false`;
- synthetic fixture candidate analysis returned six bounded candidates;
- deterministic top fixture candidate was the known synthetic byte at block `0x1000`, offset `8` (`0x1008`), proving ranking control flow only — **not a WOF address**;
- strict-plan coverage includes coercible horizon/checkpoint/player rejection;
- fail-closed coverage includes overlapping layout, layout drift and identity/source binding;
- R0.2 proof-gate coverage accepts the documented process-id-only cross-process change, rejects ROM mismatch / fixture proof, and prevents fixture authority escalation.

After durable source write, the final nested-action contract normalization was re-read at blob `349703a4a7271bcb8a5b712ee7d9a5bda326501e`; malformed R0.2/R0.3 nested action contracts are converted to the module's structured fail-closed contract path rather than escaping as an unstructured parser exception.

## Real runtime / R0.2 proof availability

Execution environment observed during closeout:

- Python: `3.13.5`;
- `stable_retro` importable: **no**;
- `WOF_ROM_PATH` configured: **no**.

No legal local WOF ROM bytes were available to this worker and none were copied/uploaded.

No matching current-source real R0.2 proof was available. Therefore:

```text
real R0.3 semantic observation mapping unlocked = false
```

This is an expected external Owner prerequisite, not an unfinished repository implementation item.

## Exact remaining Owner action

1. Install/use the pinned `stable-retro==0.9.8` environment on a machine with a legally obtained external WOF `.zip`.
2. Set `WOF_ROM_PATH` outside the repository.
3. Run current-source R0.2 determinism:

```bash
python -m training.farm.determinism \
  --actions training/farm/determinism_actions.example.json \
  --horizon 8 \
  --repetitions 3 \
  --output /path/to/current-r0.2-real-proof.json
```

4. Require that result to be real `PASS / DETERMINISM_MATCH` with `realWofProof=true`.
5. Then run the R0.3 observation CLI with a controlled real experiment plan and that proof JSON.
6. Only after that gate may a later R0.3 semantic-mapping stage begin proving actual WOF field meanings.

## Scope boundary preserved

This stage did not modify `product/alpha/**`, Alpha proof/release logic, Transport, Recorder, PYLAUNCH, OneClick, or WinKawaks Collector code/contracts/results.

It did not import Browser/WinKawaks offsets, create authoritative WOF player/enemy addresses, add multi-worker orchestration, PPO/SB3/RL, route search, search-teacher, or safe-path logic.

## Precise next legitimate Farm gate

The next legitimate gate is:

**Owner current-source R0.2 real-WOF determinism PASS -> one controlled real R0.3 observation-discovery run -> later semantic mapping proof.**

Do not advance from fixture candidate ranking directly to semantic address claims or multi-worker training.

## Stop condition

**COMPLETE — TRAINING FARM R0.3 OBSERVATION DISCOVERY TOOLING PREP — REAL SEMANTIC MAPPING LOCKED PENDING R0.2 REAL-WOF PROOF**
