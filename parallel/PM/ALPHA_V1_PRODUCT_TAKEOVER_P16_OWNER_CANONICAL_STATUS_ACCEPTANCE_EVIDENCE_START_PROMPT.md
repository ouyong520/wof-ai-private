stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.owner-canonical-status-acceptance-evidence-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE`

# Alpha V1 Product Takeover P16 — Owner Canonical Status + Acceptance Evidence

Repository: `ouyong520/wof-ai-private`

This is intentionally a larger Owner-facing productization task. Do not split it into micro-stages unless a genuine external blocker prevents a coherent implementation.

Read latest `main` first, then at minimum:
- `AGENTS.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- current dispatch authority
- completed P10/P11/P12/P13 RESULTs
- P15 start prompt only to understand its canonical runtime status contract and write boundaries
- `parallel/PYLAUNCH/wof_launcher/monitor.py`
- `parallel/PYLAUNCH/wof_launcher/state.py`
- `parallel/PYLAUNCH/wof_launcher/tray.py`
- existing Owner feedback/status artifact paths used by the permanent Alpha test channel.

Perform normal dedup-v2 create-only canonical claim + exact-token re-read + create-only stage claim + exact-token re-read before implementation. Fail closed on any ownership failure. Do not invent recovery.

## Goal

Make the Owner-facing Alpha product tell the truth about the new canonical runtime without exposing implementation noise, and automatically retain enough compact evidence for the final real-WOF acceptance gate.

P16 must not create position authority. It consumes launcher/runtime status only. It must not touch W3 source qualification, P15 canonical runtime implementation, or package pinning.

Target Owner experience:
- one permanent launcher/tray path;
- concise human status that answers what is happening now;
- no DevTools, JSON hunting, file/version hunting, coordinate calibration, or internal module terminology required from Owner;
- final acceptance evidence is automatically retained for PM after the Owner simply plays normally.

## Workstream A — canonical Owner state model

Add a narrow normalization layer, preferably a new module such as:
`parallel/PYLAUNCH/wof_launcher/canonical_owner_status.py`

It should map `LauncherStatus` + `alpha_status` into one explicit Owner-facing canonical state without mutating runtime authority.

Required states/meanings should cover at least:
- `WAITING_WOF` — browser/game authority not ready;
- `VERIFYING_WORLD` — exact World/runtime authority not yet accepted;
- `CANONICAL_STACK_READY` — package/runtime stack loaded but no canonical authority/frame yet;
- `WAITING_RENDERER_SOURCE` — W3 source/qualification not ready or rendererSource unproven;
- `IDENTITY_SUPPRESSED` — actor/generation registry/current identity suppressed;
- `ANCHORS_SUPPRESSED` — canonical resolver returned suppression/stale authority/epoch mismatch;
- `ANCHORS_READY` — current canonical anchors are READY;
- `HUD_INGEST_ACCEPTED` — HUD accepted the canonical envelope/plan;
- `CANONICAL_RUNTIME_ERROR` — fatal canonical lifecycle/CDP/runtime error.

You may refine names, but the semantics must remain distinct and deterministic.

Never display `VISIBLE`, `DRAWN`, `PASS`, `WORKING`, or equivalent solely because modules loaded, anchors were READY, or HUD ingest returned accepted. Real-WOF visible proof remains a later Owner gate.

## Workstream B — StatusStore canonical transition evidence

Extend `StatusStore` so canonical state transitions become first-class significant events rather than being buried inside raw `alpha_status` JSON.

Requirements:
- retain the current accepted authority and safety fields;
- capture canonical state/reason, package version, runtime epoch, renderer epoch/authority identity when present;
- deduplicate repeated identical states;
- record meaningful transitions such as stack-ready -> waiting-source -> anchors-ready -> HUD-ingest-accepted -> revoked/suppressed;
- on authority replacement/disconnect/error, record the end/revoke transition;
- do not persist unbounded per-frame noise; keep the existing bounded event philosophy;
- do not treat legacy calibration/projection progress as canonical success.

Preserve compatibility with existing status snapshots and diagnostics.

## Workstream C — tray / diagnostics Owner UX

Update `tray.py` so the human hint and diagnostics surface the canonical state in simple Chinese.

Examples of the level of abstraction expected:
- “等待 WOF”
- “已确认 World 921031，正在建立 Alpha 运行时”
- “Alpha 已就绪，等待游戏渲染坐标来源确认”
- “角色身份暂时无法唯一确认，提示已安全隐藏”
- “已取得当前角色坐标，正在送入 HUD”
- “HUD 已接收当前提示数据；等待最终实机可见性确认”
- “运行时已撤销旧坐标，正在重新绑定”
- precise error text when fatal.

Do not expose P8/P9/P10/P12 stage names to normal Owner-facing text. Technical diagnostics may include them in JSON/details if useful.

Remove or demote stale language that tells Owner to perform legacy head calibration when canonical mode is active or waiting for W3 renderer qualification. Legacy calibration text may remain only for an explicitly legacy path.

## Workstream D — automatic acceptance evidence snapshot

Add a narrow evidence helper, preferably beside launcher status modules, that can produce one compact machine-readable acceptance snapshot from existing status/events without touching runtime position authority.

Expected content:
- schema/version;
- generated timestamp;
- package version;
- exact World SHA / accepted page+worker identity when available;
- runtime epoch / authority key / renderer epoch when available;
- normalized canonical current state + reason;
- recent canonical transition timeline only (bounded);
- safety `readOnly`, `ramWrites`, `inputInjection`;
- latest HUD canonical status if already exposed through `alpha_status`;
- explicit `visibleProof: NOT_PROVEN` unless a later gate records dedicated visual evidence.

Expose this through the existing diagnostics/status flow or one deterministic feedback-file writer used by the launcher. Do not require the Owner to locate internal JSON manually during normal use.

If an existing feedback bundle path already exists, integrate narrowly rather than creating competing directories/protocols.

## Workstream E — final Owner gate readiness

Prepare the UI/status semantics so the eventual PM test can be a single simple question after the candidate is promoted, such as whether the expected `1P/2P/3P`/danger提示 visibly follows the correct actors during normal play.

P16 itself must not run or claim that test. It must only make the state/evidence route ready.

## Write boundaries

Allowed primarily:
- `parallel/PYLAUNCH/wof_launcher/monitor.py`
- `parallel/PYLAUNCH/wof_launcher/state.py`
- `parallel/PYLAUNCH/wof_launcher/tray.py`
- new narrow Owner-status/evidence helper modules in the same launcher package
- focused self-check fixtures for these modules
- existing feedback-output integration file only if needed and not owned by P15.

Forbidden:
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`
- P15 canonical coordinator/field adapter/package manifest/refresh files
- P10/P12 bridge/registry implementation
- W3 capture/producer/qualification files
- maintained HUD JS
- `alpha-live` movement/promotion
- Collector / Unified Collector / Training Farm / 10训.

If a desired change requires a P15-owned file, do not edit it. Implement the consumer/normalizer side against the documented status contract and record a narrow integration note.

## Acceptance invariants

1. Owner-facing canonical states are truthful and fail-closed.
2. No legacy calibration instruction appears as the primary instruction while canonical runtime is active/waiting.
3. Canonical transition events are bounded/deduplicated and survive long enough for final acceptance evidence.
4. No state implies real visible PASS without dedicated later evidence.
5. Existing browser/World discovery diagnostics and safety reporting remain intact.
6. P16 never becomes a spatial authority and never injects input or writes game RAM.
7. Final evidence can be obtained automatically from launcher state without asking Owner for DevTools/internal JSON.

## Cadence

Implementation first. Run only focused checks:
- Python parse/compile for touched modules;
- state normalization fixtures across waiting/source-unproven/identity-suppressed/anchors-ready/HUD-ingest/error/revoke states;
- event dedup/bounded-timeline fixture;
- tray human-hint fixture ensuring canonical text beats legacy calibration text in canonical mode;
- acceptance snapshot fixture proving `visibleProof` remains NOT_PROVEN without real evidence;
- narrow preservation check for existing browser/World/safety fields.

No broad Fresh QA, real-WOF run, package rebuild, or unrelated regression.

## Terminal

Write exactly:
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE_RESULT.md`

Record implementation commits, changed files, focused checks, integrationReady, productProof boundary, remaining Owner gate, safety, and nextAction.

Expected successful terminal state is Owner-status/evidence **integration-ready**, not visible PASS.

Final commit begins:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P16_OWNER_CANONICAL_STATUS_ACCEPTANCE_EVIDENCE <STATE>`

Chat terminal only: `COMPLETE`, `SUBCOMPLETE`, or precise `BLOCKED`.