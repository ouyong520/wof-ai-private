# WOF PM Owner Intervention Gate

Updated: 2026-09-01

Status: **MANDATORY PROJECT-WIDE PM POLICY**

## Principle

Owner time is the scarcest resource.

Do not ask the Owner to run WOF, open Browser, start WinKawaks, collect data, click through Windows tools, or perform manual proof while any meaningful repository-side work can still reduce uncertainty.

Use, in order:

1. source/code inspection;
2. reverse-engineering of existing artifacts and runtime contracts;
3. historical GitHub evidence/corpus reuse;
4. static analysis;
5. unit/integration tests;
6. fixtures and synthetic CDP target topologies;
7. mock Worker/WASM/runtime surfaces;
8. recorded/frozen corpus replay;
9. cross-component audit;
10. full repository regression;
11. one-click package/preflight self-test;
12. only then, if the remaining fact intrinsically requires a real Windows/Browser/game runtime, request one bounded Owner action.

## Forbidden PM pattern

Do not use Owner as an exploratory debugger:

`先试一下 -> 失败 -> 修一点 -> 再试一下 -> 再失败`

This is considered PM failure unless the previous real run exposed a fact that could not reasonably have been derived or simulated repository-side.

## Owner action admission gate

PM may request a real Owner run only when all of the following are true:

- all known P0/P1 repository blockers in the relevant path are closed;
- fresh independent QA for the one-click/live-proof path is PASS;
- cross-component contracts are aligned;
- relevant component regressions are PASS;
- global regression coverage includes the current component blobs/tests;
- direct-download / fresh-install / stale-cache / Chinese path / spaces / rerun paths are preflighted;
- failure preserves one compact JSON/screenshot with an actionable exact blocker;
- the requested run proves multiple remaining gates at once where possible;
- no DevTools, Worker Console, pasted JS, long commands, repo navigation, or manual evidence transcription is required;
- no equivalent answer can be obtained from existing data or synthetic/runtime mocks.

If any item above is false, open a fresh engineering/QA stage instead of asking Owner.

## Real-run bundling

Prefer one Owner run to prove multiple components:

`Browser Fleet + PYLAUNCH + Recorder admission + exact World 921031 + read-only safety + gameplay still works`

Do not ask for separate runs when one unified proof can cover them.

Long capture is a separate unavoidable runtime action and should start only after the short unified proof passes. Once started, analysis/handoff/prospective follow-up should be automatic.

## Long capture rule

Do not ask Owner to spend 1h/2h/overnight capture time until:

- short unified live proof PASS;
- 10-room orchestration fresh QA PASS;
- recorder/fleet discovery and failure isolation regressions PASS;
- owner-facing UX Chinese PASS;
- automatic analysis PASS;
- automatic discovery->prospective handoff QA PASS;
- output/failure recovery paths tested.

## Fresh-thread rule

Every failure produces a **new fix stage in a fresh chat**. Every fix completion produces a **new QA/retest stage in a fresh chat**.

Never tell Owner to continue debugging in the old work thread.

## Owner UX

Owner should normally only receive one of:

- `你现在需要操作：NO`
- `你现在需要操作：YES — 下载/双击这个文件，进入一次 WOF；结束后只发最终 JSON 或截图。`

No intermediate technical decision should be delegated to Owner.
