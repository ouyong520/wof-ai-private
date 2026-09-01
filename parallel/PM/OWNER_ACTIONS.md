# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — Alpha RC1 gate

## Current owner action required: YES — one immediate non-gameplay action

Alpha RC1 exists. COVERAGE refresh is complete and says no human recap. SEQMINER requests no recapture. WOF-052 remains useful research but is not required for Alpha release.

### Action O1 — Start / continue one ALPHA QA thread

If you have not already opened it, open one new ChatGPT thread and send:

```text
你负责 WOF Alpha 的独立 QA / 测试验收。请连接 GitHub，读取 ouyong520/wof-ai-private/parallel/PM/ALPHA_QA_START_PROMPT.md，然后严格按照里面的要求持续检查。你的主要任务是找 Alpha 的 Bug、错误规则、加载问题、目标切换问题和安全问题。不要和 Alpha 开发帖抢着修改产品代码，把发现的问题写回 GitHub，直到 QA 通过或者明确找出必须修复的问题。
```

No `parallel/ALPHAQA/**` result exists yet at this snapshot, so PM cannot treat QA as started/completed from GitHub alone.

### Action O2 — Real Browser Alpha acceptance — WAIT FOR QA

Do **not** run the Alpha RC1 Browser acceptance yet if QA has not cleared P0/P1.

Once QA reports PASS / no open P0/P1, the next owner action becomes one short real Browser acceptance using the exact instructions under `product/alpha/**`.

That run will be the final Alpha release gate.

### Action O3 — MAINLINE WOF-052 — optional research after current Alpha gate

WOF-052 still needs owner Browser gameplay to add ordered T18 evidence. It can resume after Alpha QA/acceptance or whenever owner time is available, but it does not block RC1 because the ambiguous BODY4728 rule is excluded from Alpha.

## No other owner work now

- COVERAGE: no recap requested.
- SEQMINER: no Collector recapture requested.
- BASECAP/GEO/EFIELD/RAWMINE: no generic work requested.
- Do not open more discovery threads until Alpha QA returns.

## Next PM trigger

When QA writes results to `parallel/ALPHAQA/**`, simply return to the PM thread and say `继续`. PM will read GitHub directly and decide whether Alpha needs fixes or can proceed to the final Browser acceptance.