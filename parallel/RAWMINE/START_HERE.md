# RAWMINE — START HERE / Candidate Evidence Screener

Updated: 2026-09-01

Scope: **WinKawaks-local discovery only**. Read-only evidence analysis. No Browser/WASM offset equivalence. No production promotion. No RAM writes.

## 1. Redefined responsibility

RAWMINE is no longer responsible for independently assigning semantics to every offset.

Its role is now:

> **automatic candidate screener / evidence analyzer for concrete GEO and EFIELD questions**

RAWMINE consumes existing raw captures produced by `GEO-*`, `EFIELD-*`, and `RAWMINE-*` when task/result identity is clear, and returns ranked candidate offsets plus reproducible evidence.

RAWMINE must NOT conclude that a high-correlation field *is* X, Y, target, attack, ACTIVE, timer, etc. Semantic interpretation and promotion remain with the owning GEO/EFIELD lane; Browser/Web remains authoritative for production validation.

## 2. Governing documents re-read for this reset

- `WOF_AI_HANDOFF.md`
- `PARALLEL_RESEARCH.md`
- `COLLECTOR_ROUTING.md`
- bridge `docs/COLLECTOR_V1_CONTRACT.md`

Hard boundaries:

- do not modify/advance Browser mainline coordinator or validator;
- do not change production-shadow rules;
- do not map WinKawaks numeric offsets directly to Browser/WASM;
- read-only only, `ramWrites=0`;
- in `wof-ai-private`, RAWMINE writes only `parallel/RAWMINE/**`;
- GEO/EFIELD artifacts are read-only inputs to this lane.

## 3. Required automatic outputs for existing raw

For every object/offset and every concrete question, RAWMINE should be able to emit:

1. per-object offset change frequency;
2. zero -> nonzero and nonzero -> zero transition counts/rates;
3. value domain / unique count / concentration / entropy where useful;
4. U8/U16/U32 **minimum reasonable width evidence**;
5. same-frame and neighboring-frame linkage (`lag -N..+N`);
6. transition/event windows around labeled events;
7. pair / cluster correlation and conditional co-change;
8. **Top 10 candidate offsets for each concrete GEO/EFIELD question**.

Generic statistics are infrastructure. The primary deliverable is now **question-conditioned candidate ranking**.

## 4. Required candidate report format

Example shape:

```text
Question: P1 X candidate

Top1 +0xXX
Evidence:
- horizontal-event change recall: 0.98
- vertical-control correlation: 0.03
- idle/background change rate: low
- value path: continuous / monotonic within observed segment
- zero-edge behavior: ...
- value domain: ...
- minimum reasonable width: U8 / U16 / U32 + reason
- best lag: 0 / -1 / +1 ...
- strongest pair/cluster partners: ...
Verdict: STRONG_CANDIDATE

Top2 ...
...
Top10 ...
```

Allowed ranking labels are evidence labels only, for example:

- `STRONG_CANDIDATE`
- `CANDIDATE`
- `WEAK_CANDIDATE`
- `REJECTED_BY_CONTROL`
- `INSUFFICIENT_COVERAGE`

RAWMINE should not use `CONFIRMED` for field semantics.

## 5. Ranking principles

A candidate should rank highly because it separates the requested event from controls, not merely because it changes often.

Preferred evidence dimensions:

- event recall / coverage;
- background false-positive rate;
- event precision / lift versus baseline;
- directional specificity when relevant;
- stability during control periods;
- continuity / monotonicity for scalar questions;
- value-domain plausibility;
- minimum-width coherence;
- exact-frame vs lagged association;
- repeatability across runs / slots / object instances;
- pair/cluster stability across runs.

High global change rate by itself is not evidence of semantics.

## 6. Current owning-lane questions to support

### GEO current frontier — read-only input

GEO currently narrows its scope to P1 X/Y discriminators.

Questions RAWMINE should support when suitable labeled/control raw exists:

- **GEO-Q-X:** Which P1 offsets best discriminate horizontal-only movement from vertical/idle controls?
- **GEO-Q-Y:** Which P1 offsets best discriminate vertical/floor-depth movement from horizontal/idle controls?

Current GEO hypotheses such as `+0x04`, `+0x0B`, `+0x08`, cache families, etc. are *labels supplied by GEO*, not RAWMINE conclusions. RAWMINE should rank all offsets and report whether those known hypotheses survive controls.

### EFIELD current frontier — read-only input

EFIELD has accumulated target/executor/lifecycle hypotheses from seven+ captures. RAWMINE should support them as concrete ranking questions rather than independently naming fields.

Priority question families:

- **EFIELD-Q-RETARGET-PRE:** offsets/events enriched before known enemy retarget commits;
- **EFIELD-Q-RETARGET-COMMIT:** offsets/events most selective on known retarget commit frames;
- **EFIELD-Q-LIFECYCLE:** offsets most selective at type-present enter/exit or replacement boundaries;
- **EFIELD-Q-ATTACK:** offsets most selective at owner-labeled attack/phase transitions versus movement/idle controls;
- **EFIELD-Q-INSTANCE:** offsets stable within an object episode but changing across instance replacement;
- **EFIELD-Q-EXECUTOR:** offsets/pairs most predictive of owner-labeled record/cursor transition windows.

RAWMINE outputs candidates only; EFIELD owns interpretation.

## 7. Existing bridge RAWMINE assets at reset time

Latest bridge RAWMINE reports are already operating on a growing mixed GEO/EFIELD corpus. The latest targeted refresh observed **11 input runs**.

Existing result families include:

- `results/rawmine/targeted.json`
- `results/rawmine/stability.json`
- `results/rawmine/pairmap.json`
- `results/rawmine/pairmap_digest.json`
- `results/rawmine/conditioned_pairs.json`
- `results/rawmine/conditioned_digest.json`
- `results/rawmine/retarget_context.json`
- `results/rawmine/scalar_families.json`

Existing infrastructure already covers generic diff/ranking, cross-run stability, pair mapping, zero-conditioned pairs, retarget context, scalar-family alignment, and minimum-width comparison. These should be reused as evidence primitives rather than treated as autonomous semantic conclusions.

## 8. Next implementation target

Create/maintain one compact RAWMINE question-conditioned report under this lane that can be regenerated from existing raw and that emits Top 10 candidates for the active GEO/EFIELD questions.

Recommended logical output schema per question:

```json
{
  "questionId": "GEO-Q-X",
  "sourceRuns": [],
  "eventDefinition": "owner-supplied label/control definition",
  "candidates": [
    {
      "rank": 1,
      "offset": "0xXX",
      "minReasonableWidth": "U8",
      "eventRecall": 0.0,
      "backgroundRate": 0.0,
      "precision": 0.0,
      "bestLag": 0,
      "zeroToNonzero": 0,
      "nonzeroToZero": 0,
      "domainSize": 0,
      "pairPartners": [],
      "verdict": "STRONG_CANDIDATE",
      "notes": []
    }
  ]
}
```

The exact metrics can differ by question, but every ranking must expose enough evidence for GEO/EFIELD to audit why an offset is above or below another.

## 9. Continue behavior

On `继续`:

1. read latest GEO and EFIELD owned frontier artifacts without modifying them;
2. inspect new raw/report availability;
3. select the highest-value concrete owner-lane question;
4. regenerate/update RAWMINE candidate evidence;
5. output Top 10 ranked offsets with controls and uncertainty;
6. write only RAWMINE-owned artifacts;
7. do not ask the operator to transfer raw/log/JSON manually.

If no new raw exists, improve ranking quality using the existing corpus instead of inventing semantic conclusions or blindly collecting more data.
