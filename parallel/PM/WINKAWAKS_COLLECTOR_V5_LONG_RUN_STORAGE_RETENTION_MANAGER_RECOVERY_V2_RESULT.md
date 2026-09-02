# WinKawaks Collector V5 — Long-Run Storage & Retention Manager Recovery V2 RESULT

Status: **COMPLETE**

Stage: `WINKAWAKS_COLLECTOR_V5_LONG_RUN_STORAGE_RETENTION_MANAGER_RECOVERY_V2`

Dedup key: `winkawaks.collector.v5.long-run-storage-retention-manager.recovery-v2`

Recovery claim token: `7ad952318995783e09d624bed7ee3828923aa13bac7e03c6`

## Outcome

Recovery V2 resumed the already-landed V5 storage/retention module from the current bridge HEAD and closed only the remaining authority / consistency / self-check tail. The existing V5 policy/schema, accounting, archive, two-phase prune, health CLI, capture-pressure guard, V3 segment-boundary integration, original implementation regressions and documentation were retained rather than rebuilt.

Final bridge authority:

```text
repo: ouyong520/wof-winkawaks-bridge
start/current bridge HEAD at recovery inspection: c66d7cd73b33fb084c5d620fd6911dacb977363b
final main: bfe8b95591f5f803d298f7cbe87a417b65e74326
compare: ahead 5 / behind 0 from c66d7cd
```

The stopped original V5 canonical claim remains historical `ACTIVE` exactly as required; Recovery V2 used its own canonical/stage generation and does not rewrite the old claim.

## Recovery-tail defects closed

Recovery inspection found a narrow shared authority gap cluster and closed it without changing V4 identity/lifecycle authority or V3 session semantics:

1. **Policy/schema exactness** — the public V5 entrypoint now checks the schema against the runtime parser contract beyond key/enums: exact numeric maxima, nullable numeric forms, booleans, storage-root/archive-root constraints and pin schema are fail-closed.
2. **Collector budget boundary** — a projected owned-byte total that reaches the configured collector budget is blocked; the guard no longer reports `allowed=true` while the projected pressure state is already `BLOCK_NEW_CAPTURE`.
3. **Authoritative owned-byte accounting for capture admission** — the default capture guard derives owned bytes from the effective V4 catalog plus V5 accounting instead of the prior narrow quick-pattern scan, so a V4-indexed local artifact with a non-orphan-pattern filename cannot be omitted from the budget decision.
4. **Receipt ↔ V4 artifact authority** — verified archive receipts must match the exact ordered V4-managed local artifact projection (`sourcePath`, deterministic archive destination, SHA-256 and kind), in addition to the pre-existing dataset/task/capture/session/record identity and archive-byte verification.
5. **Filesystem alias fail-close** — a pre-existing archive destination that is a filesystem hardlink alias of the source is rejected; receipt verification also rejects source/archive same-file aliasing while both paths exist.
6. **Incomplete operation authority** — non-complete journals now surface `kind`, `datasetId`, receipt/policy identity and state. A non-complete `ARCHIVE` operation for a dataset, or an ambiguous non-complete operation, removes that dataset from the prune candidate set even when a COMPLETE-looking receipt and exact archive bytes exist.
7. **Focused smoke assertion repair** — the final smoke source-wiring assertion was corrected to the already-current V3 import spelling `from .collector_platform import run as run_collector`; no V3 implementation was changed.

Recovery hardening is installed once by the existing `bridge.storage_retention` public entrypoint and binds the already-landed `storage_common`, `storage_inventory` and `storage_actions` runtime globals. `collector_platform` continues to consume `capture_budget_guard` from that same public V5 entrypoint, so snapshot/burst and each V3 segment boundary receive the hardened admission semantics without modifying V3 behavior.

## Exact final V5 recovery blobs

```text
bridge/storage_hardening.py
  1e1759e0c668f9f1cff433e16e679cfd86f1448c

bridge/storage_retention.py
  c779ed8a2ab37843eec93569749505e5923eec14

tests/test_storage_retention_recovery.py
  36d01c6bad309a09d9980c1226c5c465ca96a4eb

.github/workflows/collector-python-smoke.yml
  7684674a66a31f244089c0512e346f83f8697a0a
```

Existing landed core remained in place, including:

```text
bridge/storage_common.py       3c8f372bbdbd5095670f9272670f5fd17148c3a3
bridge/storage_inventory.py    2910445a97d247160ce1292a77198d6ac7cbc36e
bridge/storage_actions.py      603b189626cb68955d00ef32d13f414fc9de30c6
bridge/collector_segmented_session.py
                               2370791a686de75d3b7e5eca00555266a90635fc
config/collector_storage_policy_v1.json
                               bbc9faf6a4f94ba7fb9623088b224c151e7c4d8a
schemas/collector_storage_policy_v1.schema.json
                               61e9d9a5b02bd8b4b14351e188923240ba9cc803
```

## Implementation self-check

Testing followed the implementation cadence: one coherent recovery-tail candidate was completed, then the integrated smoke was run. The first run exposed only a stale smoke literal; implementation regressions and current repository health had already passed. That single assertion was corrected and one focused full smoke rerun was used as the final candidate proof.

Final exact-candidate GitHub Actions run:

```text
run id: 33634733195
head sha: bfe8b95591f5f803d298f7cbe87a417b65e74326
workflow: Collector Python smoke check
conclusion: SUCCESS
```

Successful final steps:

```text
Compile collector modules                                  PASS
Collector V3 segmented implementation regressions          PASS — 15/15
Collector V4 dataset catalog Golden self-check             PASS — 20/20
Collector V5 storage retention self-check                  PASS — 28/28
Current retained Collector evidence index                  PASS — 33 records / 8 default active
V5 current-repository policy/schema + storage health       PASS
Immutable discovery / segmented authority / V5 wiring      PASS
```

The V5 28-case total includes the original landed V5 suite plus Recovery V2 regressions for:

```text
schema numeric-contract drift
exact collector-budget boundary
V4-cataloged non-pattern owned bytes
changed V4 artifact authority against an old receipt
valid receipt + RUNNING archive journal prune denial
pre-existing hardlink source/archive alias
```

The previous integrated run `33634585060` is intentionally not the final verdict: V3 15/15, V4 20/20, V5 28/28, catalog/index and V5 health/schema all passed there; only the final source-wiring text assertion used the obsolete local alias `collector_run` instead of current `run_collector`. Recovery V2 fixed that self-check defect and the exact successor run above is fully green.

## Safety / authority invariants

Still true after Recovery V2:

```text
Collector source namespace: winkawaks
readOnly=true
writesGameMemory=false
inputInjection=false
containsAiDecisionLogic=false
```

V5 still does not mutate V4 dataset identity or lifecycle state. Prune remains explicit/destructive-only, requires exact verified archive authority, and does not treat unknown/orphan evidence as an automatic prune candidate. PARTIAL/FAILED protection and BASECAP/pin protection remain policy-driven and fail-closed.

No Browser/Alpha production code, danger rules, target semantics, Transport, Recorder, PYLAUNCH, OneClick or `product/alpha/**` were modified. No Training Farm / Stable-Retro / FBNeo / 10-worker scheduling or action-injection semantics were modified. Collector remains an independent read-only observation/data-retention side lane.

No real WinKawaks gameplay session was started for this repository implementation recovery. Runtime free-space values on an Owner machine remain runtime facts; implementation self-check validates deterministic classification/guard behavior and current repository integration without inventing machine-specific disk state.

## Closeout

Recovery V2 has a complete V5 local long-run storage/retention module, exact candidate self-check evidence, and a durable RESULT. The Recovery V2 canonical claim and stage claim may now be closed `COMPLETE` while preserving the stopped original V5 historical claim.

Final status:

`COMPLETE — WINKAWAKS COLLECTOR V5 LONG-RUN STORAGE & RETENTION MANAGER — SAFE LARGE-SCALE LOCAL RETENTION MODULE COMPLETE`
