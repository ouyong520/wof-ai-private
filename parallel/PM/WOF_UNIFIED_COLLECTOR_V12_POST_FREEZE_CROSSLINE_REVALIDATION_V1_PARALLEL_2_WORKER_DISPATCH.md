# WOF Unified Collector V12 — Post-Freeze Crossline Revalidation V1 — Parallel 2-Worker Dispatch

Parent authority:
`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_POST_FREEZE_CROSSLINE_REVALIDATION_V1_START_PROMPT.md`

This is a post-freeze audit, not V13 and not permission to create another Collector.

## W1 — Bridge/SUT Contamination Audit + Coordinator

Subkey:
`wof.unified-collector.v12.post-freeze-crossline-revalidation-v1.bridge-sut-coordinator`

W1 is the only terminal revalidation coordinator. Acquire the parent audit claim/stage plus W1 subclaim after dedup.

Read current bridge main and independently compare:
- V11 terminal `e80257d9486cd3129b115d4e1007bf24335b8852`
- earlier V12 terminal `9b7c6897149cc7de615dd372e072d7b21e9de8f7`
- current candidate `65831cb0cf3ec3fcfdfe0f20bade5ee24deafc95`
- latest main at execution time

Audit every post-terminal changed file/commit. Prove or refute:
- changes are V12 lifecycle/acceptance only;
- no Alpha/Training Farm/unrelated product code entered bridge V12 scope;
- no second Collector/daemon/queue/data plane appeared;
- canonical BAT/lifecycle/Agent/three-adapter structure remains singular;
- stale-stop, lifecycle identity, health/readiness instance binding and mutex authority remain correct;
- final V12 focused CI/machine bundle binds the exact latest candidate.

Do not modify production during audit. Run only directly affected V12 checks if necessary. If W2 reports an authority mismatch or this audit finds a concrete product defect, W1 may make the smallest V12-only correction and then rerun the directly affected boundary once.

After W2 SUBCOMPLETE, integrate both audits and write terminal revalidation RESULT:
`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_POST_FREEZE_CROSSLINE_REVALIDATION_V1_RESULT.md`

Close parent/W1 claims/stage. PASS keeps FEATURE FROZEN.

## W2 — PM Authority / Evidence Crossline Audit

Subkey:
`wof.unified-collector.v12.post-freeze-crossline-revalidation-v1.authority-evidence-audit`

W2 acquires only its subworkstream claim; never parent/umbrella terminal authority.

Audit `ouyong520/wof-ai-private` only. Do not modify bridge production/tests.

Verify:
- V12 W1 claim, umbrella canonical, stage, terminal recovery, RESULT and acceptance bundle are mutually consistent;
- all final candidate bindings point to the same current bridge HEAD/tree;
- no stale ACTIVE V12 claim exists;
- recent Alpha/Training Farm/other-product commits around the V12 reconciliation did not overwrite V12 files/claims/evidence;
- V12 reconciliation did not overwrite unrelated product authority;
- real Windows/WOF and live 10-worker facts remain BLOCKED/DEFERRED rather than fabricated PASS;
- one Collector / three adapters / one Git-data plane remains the durable authority statement.

This is an audit. Do not rewrite existing V12 RESULT/claims during W2. If inconsistency exists, record exact paths/commits and hand it to W1.

Write durable subresult:
`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_POST_FREEZE_CROSSLINE_REVALIDATION_V1_W2_AUTHORITY_EVIDENCE_SUBRESULT.md`

Then mark W2 SUBCOMPLETE. Terminal V12/revalidation authority not claimed.

## Merge / testing rule

- two independent domains: bridge/SUT vs PM authority/evidence;
- no production edits by W2;
- no historical broad regression unless material shared-SUT drift is actually found;
- no real Windows/WOF or live 10-worker claims without real evidence;
- no V13/V14;
- exactly one Unified Collector product.
