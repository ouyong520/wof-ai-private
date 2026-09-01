# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC1 QA blocked

## Current owner action required: YES — two new non-gameplay work threads

Alpha QA has completed its RC1 audit and returned **QA BLOCKED** with four open release blockers:

- P0: runtime/build identity is layout-only and can fail open on a lookalike revision;
- P1: same-type same-slot enemy replacement can inherit an old warning;
- P1: HUD silently drops simultaneous warnings after the first row;
- P1: current user load path still requires researcher-level Worker-console selection.

Do **not** run real Browser Alpha acceptance yet.

## Close these completed work threads

- COVERAGE: complete / PARK; human recap = NO.
- SEQMINER: current retained corpus exhausted / PARK; no recapture requested.
- Alpha QA RC1 audit: stage complete at QA BLOCKED. Preserve the thread/result, but do not keep extending the same QA stage.
- Original Alpha RC1 implementation thread: stage complete; use a new RC2 fix thread rather than reviving the old implementation chat.

## Action O1 — Open new Alpha Fix / RC2 thread

Send:

```text
你负责 WOF Alpha RC2 修复。请连接 GitHub，读取 ouyong520/wof-ai-private/parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md，然后严格按里面要求修复 Alpha QA 找出的 P0/P1 问题，直到 RC2 可以交给新的独立 QA 复测，或者只剩一个必须真人 Browser 操作才能解决的精确阻断点。
```

This thread owns `product/alpha/**` fixes for this stage.

## Action O2 — Open parallel Runtime Identity audit thread

Send:

```text
你负责 WOF Alpha 的 Browser 运行时/版本识别审计。请连接 GitHub，读取 ouyong520/wof-ai-private/parallel/PM/ALPHA_RUNTIME_IDENTITY_AUDIT_START_PROMPT.md，然后只读检查现有 GitHub 证据，找出怎样真正确认是支持的 wofr1 / World 921002 Browser 版本。不要改 Alpha 产品代码，结果写回 GitHub，直到找到安全的版本识别办法，或者确认只差一个最小真人 Browser 探针。
```

This thread is read-only against `product/alpha/**` and writes only `parallel/ALPHAID/**`, so it can run in parallel with RC2 fixes without code conflicts.

## Human gameplay action — NOT YET

Do not spend owner Browser time on Alpha acceptance until:

1. RC2 exists;
2. a fresh independent QA retest clears all P0/P1;
3. PM explicitly moves the project to Browser acceptance.

WOF-052 remains useful post-Alpha research but is not the current release bottleneck.

## Next PM trigger

After the RC2 fix and/or identity audit writes new GitHub results, return to PM and say `继续`. PM will read GitHub directly and decide whether to open fresh QA retest or request one minimal Browser probe.