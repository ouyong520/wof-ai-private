# RAWMINE — New Chat Handoff — 2026-09-01

Scope: WinKawaks-local discovery only. Read-only. RAWMINE writes only `parallel/RAWMINE/**` in `wof-ai-private`.

## Start here

The new RAWMINE chat must first read:

1. `WOF_AI_HANDOFF.md`
2. `PARALLEL_RESEARCH.md`
3. `COLLECTOR_ROUTING.md`
4. `ouyong520/wof-winkawaks-bridge/docs/COLLECTOR_V1_CONTRACT.md`
5. `parallel/RAWMINE/START_HERE.md`
6. latest files under `parallel/GEO/**` read-only
7. latest files under `parallel/EFIELD/**` read-only
8. latest `results/rawmine/**` and RAWMINE analysis code in `ouyong520/wof-winkawaks-bridge`

`parallel/RAWMINE/START_HERE.md` is the authoritative RAWMINE role definition after the 2026-09-01 reset.

## Redefined responsibility

RAWMINE is no longer an autonomous semantic reverse-engineering lane.

RAWMINE is now the automatic candidate screener / evidence analyzer for concrete questions owned by GEO and EFIELD.

It may consume identifiable `GEO-*`, `EFIELD-*`, and `RAWMINE-*` raw captures, but it must return ranked evidence rather than directly naming high-correlation offsets as X/Y/target/attack/ACTIVE/timer/etc.

Semantic interpretation belongs to the owning GEO/EFIELD lane. Browser/Web remains authoritative for production validation.

## Required generic evidence primitives

For existing raw, RAWMINE should automatically expose:

1. per-object offset change frequency;
2. zero->nonzero and nonzero->zero edges;
3. value domain / unique count / concentration / entropy;
4. U8/U16/U32 minimum reasonable width evidence;
5. same-frame and neighboring-frame linkage;
6. transition/event windows;
7. pair / cluster correlation and conditional co-change;
8. Top 10 candidate offsets for each concrete owner-lane question.

High change rate alone is never semantic proof.

## Current GEO questions to support

Current GEO frontier is deliberately narrow: P1 X/Y discriminators.

### GEO-Q-X
Which P1 offsets best discriminate horizontal-only motion from vertical/idle controls?

Owner-lane hypotheses currently include `+0x04`, `+0x0B`, the composite `256*U8(+0x0B)+U8(+0x04)`, and cache/control candidates. RAWMINE must rank all offsets and show whether these survive controls; it must not independently declare the coordinate semantics confirmed.

### GEO-Q-Y
Which P1 offsets best discriminate vertical/floor-depth motion from horizontal/idle controls?

Owner-lane hypotheses currently include `+0x08` and rejected/cache families. Again, RAWMINE supplies rankings/evidence only.

## Current EFIELD question families to support

Use EFIELD artifacts only as owner-supplied event labels / hypotheses:

- `EFIELD-Q-RETARGET-PRE`: offsets/events enriched before known retarget commits;
- `EFIELD-Q-RETARGET-COMMIT`: offsets/events selective on known retarget commit frames;
- `EFIELD-Q-LIFECYCLE`: offsets selective at type-present enter/exit or replacement boundaries;
- `EFIELD-Q-ATTACK`: offsets selective at owner-labeled attack/phase transitions versus controls;
- `EFIELD-Q-INSTANCE`: offsets stable inside an object episode but changing across replacement;
- `EFIELD-Q-EXECUTOR`: offsets/pairs predictive of owner-labeled cursor/record transition windows.

Do not re-interpret EFIELD semantics inside RAWMINE. Treat EFIELD labels as event definitions supplied by the owner lane.

## Existing RAWMINE bridge assets

At the reset, the RAWMINE bridge already had a mixed GEO/EFIELD corpus and report families including:

- `results/rawmine/targeted.json`
- `results/rawmine/stability.json`
- `results/rawmine/pairmap.json`
- `results/rawmine/pairmap_digest.json`
- `results/rawmine/conditioned_pairs.json`
- `results/rawmine/conditioned_digest.json`
- `results/rawmine/retarget_context.json`
- `results/rawmine/scalar_families.json`

Reuse these as evidence primitives. Do not treat their old labels as autonomous semantic conclusions.

## Required question-conditioned output

For every active question, emit Top 10 candidates in an auditable format, for example:

```text
Question: P1 X candidate

Top1 +0xXX
Evidence:
- event recall: ...
- background/control rate: ...
- precision/lift: ...
- horizontal specificity: ...
- vertical/idle control behavior: ...
- value continuity/domain: ...
- minimum reasonable width: ...
- best lag: ...
- zero edges: ...
- strongest pair/cluster partners: ...
Verdict: STRONG_CANDIDATE
```

Allowed verdicts are evidence labels such as:

- `STRONG_CANDIDATE`
- `CANDIDATE`
- `WEAK_CANDIDATE`
- `REJECTED_BY_CONTROL`
- `INSUFFICIENT_COVERAGE`

Do not use `CONFIRMED` for semantics.

## Immediate next work

1. Inspect latest GEO/EFIELD owner-lane frontier and latest bridge RAWMINE results.
2. Determine which active question has enough labeled/control raw for a defensible ranking.
3. Build or update one compact question-conditioned RAWMINE report under `parallel/RAWMINE/**`.
4. Prefer reusing existing raw instead of blindly requesting another capture.
5. If collection is genuinely needed, use `RAWMINE-*` task IDs only and preserve Collector task/result identity.
6. Never modify `parallel/GEO/**`, `parallel/EFIELD/**`, Browser mainline files, or production-shadow rules.

## Continue behavior

When the operator says only `继续`, autonomously:

- read latest owner-lane questions;
- inspect new raw/results;
- choose the highest-value concrete question;
- regenerate candidate evidence;
- publish Top 10 rankings under RAWMINE ownership;
- continue without asking the operator to manually transfer logs/JSON/raw.
