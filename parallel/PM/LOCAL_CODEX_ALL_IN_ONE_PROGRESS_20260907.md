# Local Codex all-in-one checkpoint — 2026-09-07

This is the durable checkpoint for the single local execution thread. It is
not a new product/PM/Worker stage and does not replace any Alpha claim.

## Git

- Main repository: `ouyong520/wof-ai-private`
- Branch: `codex/local-all-in-one`
- Fresh remote base read: `origin/main=4533627f2`
- Collector worktree: `F:/三国/wof-winkawaks-bridge-codex-local`, fresh `origin/main=d693b0f`
- Original user worktrees remain untouched and dirty; no local user changes were reconciled or deleted.

## Current durable truth

- Alpha P49 is terminal COMPLETE; one Owner live-run budget remains unused. P48 was BLOCKED_PRE_RUN because no Owner Windows/browser-debugger channel was connected. Renderer authority remains blocked by `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`.
- Unified Collector V12 is already the maintained read-only product. Its existing Stable-Retro/FBNeo adapter accepts source-owned exporter records and does not start/schedule workers.
- Training Farm previously had only single-instance R0.2/R0.4, R0.4.5 policy contracts, and a ROM-free V11 exporter fixture. Real multi-worker orchestration was absent.

## Implemented coherent slice

`training/farm/fleet.py` now provides a source-owned Stable-Retro/FBNeo fleet
supervisor with:

- staged `1 -> 2 -> 4 -> 8 -> 10` scale;
- per-worker process identity and generation identity;
- clean start/stop, bounded automatic restart, and sibling failure isolation;
- R0.4 in-memory savestate fork and explicit action-result experiment;
- heartbeat, best-effort CPU/RSS telemetry, and durable fleet status/events;
- parent-serialized publication through the existing V11 read-only exporter;
- no Collector queue duplication and no host/global input injection.

The `--fake` path is explicitly fixture-only and never produces real-WOF
authority. Real mode returns `WAITING_PREREQUISITE` until the existing legal
external ROM + pinned Stable-Retro/FBNeo gate is satisfied.

## Verification

- Focused fleet tests: PASS (3/3).
- Fake supervisor ladder: PASS through 10 workers, no failures, exporter records verified for all 10 workers.
- Existing Training Farm suite under the dedicated WOF Python 3.13.6 venv: 91/92 PASS; the sole failure is the pre-existing Windows path-separator assertion in `test_windows_oneclick_bootstrap.py`.
- Collector V12 cross-repo ingestion contract: PASS against a fleet-produced exporter record (`READY`, `capture_export_stream=PASS`); result remained `sourceNamespace=stable-retro-fbneo`, `readOnly=true`, `writesGameMemory=false`, `inputInjection=false`.
- Real WOF fleet proof: NOT RUN. No legal ROM was selected and no one-shot live budget was consumed.

## Next action

Run the focused implementation/repository checks after any remote drift, commit
and push this coherent fleet slice. Then continue Alpha safe diagnosis and
prepare the real Training Farm run only when a legal external ROM/runtime is
available; do not relabel the fixture proof as real 10训.
