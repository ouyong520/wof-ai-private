# WinKawaks Collector V5 — Long-Run Storage & Retention Manager Recovery V2 RESULT

Status: **COMPLETE**

Stage: `WINKAWAKS_COLLECTOR_V5_LONG_RUN_STORAGE_RETENTION_MANAGER_RECOVERY_V2`

Dedup key: `winkawaks.collector.v5.long-run-storage-retention-manager.recovery-v2`

Recovery claim token: `7ad952318995783e09d624bed7ee3828923aa13bac7e03c6`

## Outcome

Recovery V2 resumed the already-landed V5 storage/retention module from current bridge HEAD and closed only the remaining authority / consistency / self-check tail. Existing V5 policy/schema, accounting, archive, two-phase prune, health CLI, capture-pressure guard, V3 segment-boundary integration, implementation regressions and documentation were retained rather than rebuilt.

Final bridge authority:

```text
repo: ouyong520/wof-winkawaks-bridge
recovery start/current HEAD inspected: c66d7cd73b33fb084c5d620fd6911dacb977363b
final main / exact tested candidate: bfe8b95591f5f803d298f7cbe87a417b65e74326
final tree: f6aba2502d03c11963cfb570b8a065a14bbcd67c
compare from c66d7cd: ahead 5 / behind 0
```

The stopped original V5 canonical claim remains historical `ACTIVE` exactly as required. Recovery V2 used its own canonical/stage generation and supersedes the stopped implementation generation only through this durable result and its own completed claims.

## Recovery-tail defects closed

1. **Policy/schema exactness** — public V5 validation now checks the schema against runtime parser semantics beyond keys/enums: exact numeric maxima, nullable numeric forms, booleans, storage-root/archive-root constraints and pin schema are fail-closed.
2. **Collector budget exact boundary** — projected Collector-owned bytes that reach the configured budget are blocked; the guard no longer reports `allowed=true` while projected pressure is already `BLOCK_NEW_CAPTURE`.
3. **Authoritative owned-byte admission accounting** — default capture admission derives Collector-owned bytes from effective V4 catalog + V5 inventory instead of the prior narrow quick-pattern scan, so a V4-indexed local artifact with a non-orphan-pattern filename cannot be omitted from the budget decision.
4. **Receipt ↔ V4 artifact authority** — a valid archive receipt must match the exact ordered V4-managed local artifact projection (`sourcePath`, deterministic archive destination, SHA-256 and kind) in addition to dataset/task/capture/session/record identity and archive-byte verification.
5. **Filesystem alias fail-close** — a pre-existing archive destination that is a filesystem hardlink alias of the source is rejected; receipt verification also rejects source/archive same-file aliasing while both paths exist.
6. **Incomplete operation authority** — non-complete journals expose operation kind, dataset ID, receipt/policy identity and state. A non-complete `ARCHIVE` operation for a dataset, or an ambiguous non-complete storage operation, removes that dataset from the prune candidate set even if a COMPLETE-looking receipt and exact archive bytes exist.
7. **Focused smoke assertion repair** — the final smoke source-wiring assertion was corrected to current V3 spelling `from .collector_platform import run as run_collector`; V3 implementation semantics were not changed.

Recovery hardening is installed once through the existing `bridge.storage_retention` public entrypoint and binds the already-landed `storage_common`, `storage_inventory` and `storage_actions` authority paths. `collector_platform` continues to consume `capture_budget_guard` from that public V5 entrypoint, so snapshot/burst and each V3 segment boundary receive the hardened admission semantics without changing V3 terminal/session behavior.

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

Existing landed core remained in place:

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

## Final storage authority contract

Policy/runtime identity:

```text
policy schemaVersion: wof_collector_storage_policy_v1
default normalized policy SHA-256: 46017615b37d1ce739d3090eaedd130fcd54cf82122c1cfd0624164cf2a73703
status schemaVersion: wof_collector_storage_status_v1
pressure states: HEALTHY / WARNING / BLOCK_NEW_CAPTURE / CRITICAL
```

Capture pressure/budget remains conservative and pre-capture. It blocks current `BLOCK_NEW_CAPTURE`/`CRITICAL`, projected free space at or below the configured capture floor, and projected Collector-owned bytes at or above an explicit budget. V3 continues to cross the same guarded Collector platform at each segment capture boundary, so already-finalized segments remain durable if a later segment is stopped by pressure and V3's existing PARTIAL/FAILED authority is preserved.

Archive remains copy-first and exact-byte/hash preserving. A COMPLETE receipt binds dataset ID, V4 record identity, source task ID, capture/session identity, policy identity and the exact V4-managed artifact source/destination/hash/kind set. Destination collisions, path escape, symlink/reparse ambiguity, source/destination aliases and different existing bytes fail closed; source data is not deleted by archive.

Prune remains two-phase: deterministic plan/dry-run by default, then explicit destructive apply only. A source can be removed only after the surviving archive copy re-verifies immediately at the destructive boundary and the dataset still satisfies lifecycle/integrity, grace/retention-age, not-active and protection rules. Incomplete/ambiguous archive authority never authorizes prune. Unknown/orphan evidence is detected/reported but is not silently promoted into a delete candidate.

Protection remains V4/V3-authority preserving: immutable-ID pins and configured BASECAP VALID data are protected; PARTIAL/FAILED evidence follows conservative preserve/recent-protection policy; storage actions do not rewrite V4 dataset identity/lifecycle or V3 COMPLETE/PARTIAL/FAILED semantics.

CLI/status surface remains structured JSON through the existing V5 entrypoint and includes `status`, `plan`, `archive`, `prune`, `verify` and `show` repository conventions. Status exposes free space by configured root, Collector-owned/local/archive/metadata/protected/partial/orphan byte accounting, pressure state, archive/prune backlog, storage conflicts, incomplete operations, catalog source and the read-only safety invariants.

Crash/concurrency/path safety remains fail-closed: mutation uses the storage-manager lock, archive/prune operation journals and atomic JSON finalization; non-complete operations remain visible and cannot masquerade as completed archive authority. Collector-owned relative roots are enforced and archive/storage roots cannot overlap; unrelated ROM/BIOS/emulator/game files are outside the managed storage authority.

## Implementation self-check

Testing followed the implementation cadence: one coherent recovery-tail candidate was completed, then integrated smoke was run. The first run exposed only a stale smoke source literal; implementation regressions and current-repository health had already passed. That assertion was corrected and one focused full smoke rerun was the final candidate proof.

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

The V5 28-case total includes original landed V5 tests plus Recovery V2 regressions for schema numeric-contract drift, exact collector-budget boundary, V4-cataloged non-pattern owned bytes, changed V4 artifact authority against an old receipt, valid receipt + RUNNING archive-journal prune denial, and pre-existing hardlink source/archive alias.

The previous integrated run `33634585060` is not the final verdict: V3 15/15, V4 20/20, V5 28/28, catalog/index and V5 health/schema passed there; only the final source-wiring text assertion used obsolete local alias `collector_run` rather than current `run_collector`. The exact successor run above is fully green.

## Safety / isolation and remaining runtime limitation

Still true after Recovery V2:

```text
Collector source namespace: winkawaks
readOnly=true
writesGameMemory=false
inputInjection=false
containsAiDecisionLogic=false
```

No Browser/Alpha production code, danger rules, target semantics, Transport, Recorder, PYLAUNCH, OneClick or `product/alpha/**` were modified. No Training Farm / Stable-Retro / FBNeo / 10-worker scheduling or action-injection semantics were modified.

No real WinKawaks gameplay session was started for this repository implementation recovery. Actual free-space totals and filesystem capacity on the Owner machine remain runtime facts; implementation self-check proves deterministic classification/admission behavior and current repository integration but does not invent machine-specific disk state.

## Closeout

Recovery V2 now has a complete V5 local long-run storage/retention module, exact tested bridge HEAD/tree, exact authority blobs, implementation-owned self-check evidence and this durable RESULT. Recovery V2 canonical/stage claims may be closed `COMPLETE` while preserving the stopped original V5 historical claim.

Final status:

`COMPLETE — WINKAWAKS COLLECTOR V5 LONG-RUN STORAGE & RETENTION MANAGER — SAFE LARGE-SCALE LOCAL RETENTION MODULE COMPLETE`
