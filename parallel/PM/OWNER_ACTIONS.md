# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC1 QA blocked / RC2 parallel repair

## Current owner action required: YES — four new non-gameplay work threads

Alpha QA completed RC1 audit and returned **QA BLOCKED** with four open blockers:

- P0 runtime/build identity can fail open on a layout-compatible lookalike;
- P1 same-type same-slot replacement can inherit an old warning;
- P1 HUD silently drops simultaneous warnings after the first row;
- P1 user load path still requires researcher-level manual Worker-console selection.

Do **not** run real Browser Alpha acceptance yet.

## Close these completed work threads

- COVERAGE: complete / PARK; human recap = NO.
- SEQMINER: current retained corpus exhausted / PARK; no recapture requested.
- Alpha QA RC1: stage complete at QA BLOCKED.
- Original Alpha RC1 implementation: stage complete; do not revive it for RC2.

## Action O1 — Open Alpha Fix / RC2 thread

```text
你负责 WOF Alpha RC2 修复。请连接 GitHub，读取 ouyong520/wof-ai-private/parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md，然后严格按里面要求修复 Alpha QA 找出的 P0/P1 问题，直到 RC2 可以交给新的独立 QA 复测，或者只剩一个必须真人 Browser 操作才能解决的精确阻断点。
```

Owns `product/alpha/**` fixes for this stage.

## Action O2 — Open Runtime Identity audit thread

```text
你负责 WOF Alpha 的 Browser 运行时/版本识别审计。请连接 GitHub，读取 ouyong520/wof-ai-private/parallel/PM/ALPHA_RUNTIME_IDENTITY_AUDIT_START_PROMPT.md，然后只读检查现有 GitHub 证据，找出怎样真正确认是支持的 wofr1 / World 921002 Browser 版本。不要改 Alpha 产品代码，结果写回 GitHub，直到找到安全的版本识别办法，或者确认只差一个最小真人 Browser 探针。
```

Writes only `parallel/ALPHAID/**`.

## Action O3 — Open Enemy Lifecycle audit thread

```text
你负责 WOF Alpha 的敌人生命周期/槽位复用审计。请连接 GitHub，读取 ouyong520/wof-ai-private/parallel/PM/ALPHA_LIFECYCLE_AUDIT_START_PROMPT.md，然后只读检查现有 Browser 证据，解决“同类型敌人复用同一槽位时旧警告可能继承”的问题。不要改 Alpha 产品代码，把可实施的安全清理方案和测试要求写回 GitHub。
```

Writes only `parallel/ALPHALIFE/**`.

## Action O4 — Open User Bootstrap audit thread

```text
你负责 WOF Alpha 的普通用户加载方式审计。请连接 GitHub，读取 ouyong520/wof-ai-private/parallel/PM/ALPHA_BOOTSTRAP_AUDIT_START_PROMPT.md，然后只读研究怎样让普通用户不用手动寻找 gstyphoon.js Worker 控制台，也能用一个简单入口启动 Alpha。不要改 Alpha 产品代码，把推荐方案写回 GitHub。
```

Writes only `parallel/ALPHABOOT/**`.

## Why four threads are safe

Only O1 edits `product/alpha/**`. O2/O3/O4 are read-only support investigations with separate output directories, so they can run simultaneously without code-write conflicts.

## Human gameplay action — NOT YET

Do not spend owner Browser time on Alpha acceptance until RC2 exists and fresh independent QA clears all P0/P1.

If any support audit proves that exactly one minimal Browser probe is unavoidable, PM will give the precise operation later.

## Next PM trigger

After these threads produce GitHub results, return here and say `继续`. PM will read GitHub directly and decide when to open a fresh RC2 QA-retest thread.