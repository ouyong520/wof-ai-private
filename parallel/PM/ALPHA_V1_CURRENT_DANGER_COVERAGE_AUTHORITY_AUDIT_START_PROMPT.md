# Alpha V1 Current Production Danger Coverage Authority Audit

stageId: `ALPHA_V1_CURRENT_DANGER_COVERAGE_AUTHORITY_AUDIT`
dedupProtocol: `v2`
dedupKey: `alpha.v1.current-production-danger-coverage-authority-audit`
dedupMode: `exclusive`

Priority: **V1 release truth / capability coverage audit**

Repository: `ouyong520/wof-ai-private`

## Goal

Produce one authoritative current-HEAD repository audit of what Alpha V1 danger detection actually recognizes today, versus what remains research-only / quarantined / unmapped.

This is not an implementation task and must not modify production danger rules.

The Owner specifically needs a factual answer for named gameplay cases such as:

- 夏侯惇 dangerous attacks;
- 曹仁 dangerous attacks;
- 飞身 / 扑击 / 冲撞 / jumping or flying body attacks;
- other visually obvious boss/enemy attacks that a normal player would reasonably expect `[危险]` to warn about.

## Required reads

Re-read current `main` and at minimum:

- `product/alpha/wof_alpha_core.js`;
- current Alpha real worker / HUD only as needed to distinguish detection from rendering;
- `WOF_AI_HANDOFF.md`;
- `WOF_AI_CURRENT_FRONTIER.md` / `WOF_AI_MASTER_PROGRESS.md` when relevant;
- WOF-038 through latest relevant WOF-0xx reports/results;
- production-shadow / quarantined rule evidence;
- any enemy type/name mapping evidence already present in repository;
- relevant Collector / EFIELD / RAWMINE / BASECAP results only if they provide authoritative name/type/attack mapping.

Do not infer a Chinese boss/enemy name from an attack ID or type unless repository evidence explicitly proves the mapping.

## Required output

Create a compact table classifying every current/frozen danger rule with at least:

- ruleId;
- enemy type / name if proven;
- attack ID if attack-specific;
- human-readable move label if proven;
- current Alpha V1 state: `PRODUCTION_ENABLED / QUARANTINED / RESEARCH_ONLY / RETIRED`;
- trigger style;
- validated lead range;
- target/side evidence;
- exact evidence source;
- confidence / mapping caveat.

Then explicitly answer:

1. Which dangerous moves are definitely covered by the current Alpha V1 runtime?
2. Which previously validated production-shadow rules are currently quarantined and therefore will NOT show `[危险]`?
3. Can current repository evidence prove whether 夏侯惇 is covered? If yes, which move(s); if no, say `NOT PROVEN`.
4. Same for 曹仁.
5. Can any current rule be authoritatively called 飞身/扑击/冲撞? If not, do not guess.
6. What is the smallest missing evidence needed to map those named moves without changing V1 code?
7. Separate `coverage gap` from `HUD/projection failure`: an unsupported move producing no warning is not a projection bug.

## Boundaries

- Repository-only audit.
- No Browser/WOF.
- No production changes.
- No danger-rule promotion/demotion.
- No target semantic changes.
- No Collector task unless the audit proves a specific mapping fact is absent; even then only record the proposed future evidence need, do not start owner-gated collection in this stage.
- `readOnly=true / ramWrites=0 / inputInjection=false` remains invariant.

## Dedup

Strict canonical dedup v2. If an equivalent current-HEAD coverage audit already exists and answers the named-move questions, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

## Success

`COMPLETE — ALPHA V1 CURRENT DANGER COVERAGE AUTHORITY AUDIT — ENABLED / QUARANTINED / UNMAPPED MOVE COVERAGE MADE EXPLICIT`

## Failure

`BLOCKED — ALPHA V1 CURRENT DANGER COVERAGE AUTHORITY AUDIT — <precise missing repository authority>`
