# Alpha V1 Current Production Danger Coverage Authority Audit — RESULT

stageId: `ALPHA_V1_CURRENT_DANGER_COVERAGE_AUTHORITY_AUDIT`
dedupKey: `alpha.v1.current-production-danger-coverage-authority-audit`
stageStatus: **COMPLETE**
nextAction: **stop**

Audit finalization source HEAD: `956ab8e7edc3a255076ff245daf3ea86be35d538`
Current Alpha core blob: `product/alpha/wof_alpha_core.js` = `267a44190744b6848b0685712c3d5572627d3a8a`

## Executive authority verdict

Current Alpha V1 has exactly **two** user-facing production danger rules. Both are numeric `type=18` current-level predicates:

- `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` -> attack `A5440`;
- `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` -> attack `A5424`.

Current core also carries exactly **four** frozen candidates marked `production:false` and `releaseStatus:'quarantined-rc3-lifecycle'`; these are absent from the evaluation/publication loop and therefore cannot emit user-facing `[危险]` warnings.

The repository evidence audited here does **not** provide an authoritative Chinese enemy-name or move-name mapping for `T18`, `T16`, `T20`, `T9`, `T11`, `T33`, `T34`, `A5440`, `A5424`, `A5136`, `A3232`, etc. Therefore:

- 夏侯惇 coverage: **NOT PROVEN**;
- 曹仁 coverage: **NOT PROVEN**;
- whether A5440/A5424 (or any frozen candidate) should be called 飞身 / 扑击 / 冲撞 / jumping/flying-body: **NOT PROVEN**.

This is an authority limitation, not permission to guess from gameplay familiarity.

## 1. Production-enabled rule matrix

| ruleId | enemy type | enemy Chinese name | attack ID | human move label | Alpha V1 state | trigger | validated lead | target/side evidence | exact authority | confidence / caveat |
|---|---:|---|---:|---|---|---|---|---|---|---|
| `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` | `18` | **NOT PROVEN** | `5440` | **NOT PROVEN** | `PRODUCTION_ENABLED` | stateless `current-level`; exact current `type=18`, `attack=0`, `BODY7512`, `TM4` + descriptor tuple | core label `~62–71 ms`; WOF-046 33/33 at 59.1–78.5 ms; WOF-051 4/4 at 62.3–70.9 ms | WOF-051 target/side 4/4; current warning publication also requires live target 0/4/8 and finite geometry | `product/alpha/wof_alpha_core.js`; `reports/WOF-046_ANALYSIS.md`; `reports/WOF-051_ANALYSIS.md` | **Strong numeric rule authority. No repository authority for Chinese enemy/move name.** |
| `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` | `18` | **NOT PROVEN** | `5424` | **NOT PROVEN** | `PRODUCTION_ENABLED` | stateless `current-level`; exact current `type=18`, `attack=0`, `BODY7520`, `TM4` + descriptor tuple | core label `~69–70 ms`; WOF-046 33/33 at 58.2–71.3 ms; WOF-051 4/4 at 69.1–70.0 ms | WOF-051 target/side 4/4; current warning publication also requires live target 0/4/8 and finite geometry | same | **Strong numeric rule authority. No repository authority for Chinese enemy/move name.** |

Current core mechanically derives `RULES = FROZEN_RULES.filter(r => r.production)`, so these two and only these two enter matching/statistics/warning publication.

## 2. Quarantined frozen-rule matrix

| ruleId | enemy type authority | enemy Chinese name | attack authority | human move label | Alpha V1 state | trigger/history dependency | historical validation | target/side evidence | why no `[危险]` now |
|---|---|---|---|---|---|---|---|---|---|
| `T16_B4_DANGER_40` | exact predicate `type=16` | **NOT PROVEN** | **not attack-specific** (`attack:null`); WOF-051 future ACTIVE outcomes A6432=97/A4840=1 | **NOT PROVEN** | `QUARANTINED` | entry/history-style precursor | WOF-051 98/98 strict, ~8.9–21.0 ms; WOF-046 225 resolved, 224 strict + 1 jitter | WOF-051 98/98 | `production:false`; lifecycle continuity across previous/current samples is not proven |
| `T20_5136_B0_TO_B255_1250` | exact predicate `type=20` | **NOT PROVEN** | `A5136` | **NOT PROVEN** | `QUARANTINED` | transition `B0 -> B255` | WOF-051 5/5 strict A5136, ~380.9–639.7 ms; WOF-046 14/14 | WOF-051 5/5 | `production:false`; transition requires unproven same-instance continuity |
| `D867BA_3232_TM6_220` | **rule is not type-bound**; WOF-051 observed T33=8/T9=2 | **NOT PROVEN** | `A3232` | **NOT PROVEN** | `QUARANTINED` | entry/history-style precursor | WOF-051 10/10 strict A3232, ~99.1–109.4 ms; WOF-046 16/16 | WOF-051 10/10; P1/P2/P3 target coverage noted | `production:false`; entry detection needs previous/current continuity not proven by Browser lifecycle authority |
| `D8811E_3232_TM6_135` | **rule is not type-bound**; WOF-051 observed T34=15/T11=7 | **NOT PROVEN** | `A3232` | **NOT PROVEN** | `QUARANTINED` | entry/history-style precursor | WOF-051 22/22 strict A3232, ~98.6–119.2 ms; WOF-046 21/21 eventual A3232 (one clean long-tail sample) | WOF-051 22/22 | `production:false`; entry detection needs previous/current continuity not proven by Browser lifecycle authority |

Current Alpha RC3/RC5 documentation gives the same reason for all F1–F4 quarantine: `same slot + same type` is not a proven enemy-instance continuity token, so history/watch/previous-current dependent warning authority is removed from the user-facing engine.

## 3. Research-only / retired evidence that must not be confused with current V1 coverage

| item | numeric evidence | current classification | authority consequence |
|---|---|---|---|
| T24 BODY7512/TM3 -> A5440 | WOF-046 28/28 strict | `RESEARCH_ONLY / excluded from current Alpha` | Historical production-shadow evidence exists, but current Alpha README explicitly excludes T24 and current `FROZEN_RULES` does not contain it. No `[危险]` authority. |
| T24 BODY7520/TM4 -> A5424 | WOF-046 34/34 strict | `RESEARCH_ONLY / excluded from current Alpha` | Same. |
| T18 BODY4728/A4/B2/TM1 candidate -> A4704 | WOF-051 direct prospective produced A4704 once and A4712 once | `RETIRED AS A4704-SPECIFIC PREDICTOR / RESEARCH_ONLY` | Attack-ambiguous; WOF-052 had zero target T18 candidate coverage and explicitly promoted no rule. |
| T23 sequence candidates | WOF-047 had 8 resolved cycles across A4792/A4920/A5888; common states are attack-ambiguous | `RESEARCH_ONLY` | Ordered discovery only; no current production rule. |
| old T23 BODY4920/B0 rule | historical | `RETIRED` | Must not be revived. |

`WOF_AI_HANDOFF.md`, `WOF_AI_CURRENT_FRONTIER.md`, and `WOF_AI_MASTER_PROGRESS.md` use the research-mainline term `production-shadow` for several historically validated rules. That term is **not** current Alpha V1 user-facing authority. For current V1, `product/alpha/wof_alpha_core.js` and Alpha RC3/RC5 release contract control publication status.

## 4. Enemy/name authority matrix

| requested identity | repository numeric authority | name -> type authority | current V1 danger coverage verdict |
|---|---|---|---|
| 夏侯惇 | none in audited current Alpha/future-danger evidence that binds the Chinese name to a current enemy `type` and attack ID | **NO AUTHORITATIVE MAPPING FOUND** | **NOT PROVEN**. Do not claim A5440/A5424 or any quarantined rule belongs to 夏侯惇. |
| 曹仁 | none in audited current Alpha/future-danger evidence that binds the Chinese name to a current enemy `type` and attack ID | **NO AUTHORITATIVE MAPPING FOUND** | **NOT PROVEN**. Do not claim A5440/A5424 or any quarantined rule belongs to 曹仁. |
| T18 | exact numeric type in both enabled predicates | Chinese enemy name absent | Two enabled numeric attack rules: A5440, A5424. |
| T16 | exact numeric type in quarantined predicate | Chinese enemy name absent | No current user-facing rule. |
| T20 | exact numeric type in quarantined predicate | Chinese enemy name absent | No current user-facing rule. |
| D867 historical observed types | T33/T9 in WOF-051 | Chinese names absent | Quarantined; no current user-facing rule. |
| D881 historical observed types | T34/T11 in WOF-051 | Chinese names absent | Quarantined; no current user-facing rule. |

The WinKawaks EFIELD atlas can provide local numeric type/lifecycle/field observations, but it explicitly forbids promoting those local interpretations into Browser production authority without separate proof. It also does not provide the missing Chinese boss/move identity mapping used by this audit.

## 5. Named-move answers

### 夏侯惇
**NOT PROVEN.** The current repository does not provide an authoritative `夏侯惇 -> enemy type -> attack ID` binding. Therefore this audit cannot truthfully list any current V1 rule as a confirmed 夏侯惇 attack.

### 曹仁
**NOT PROVEN.** Same authority gap.

### 飞身 / 扑击 / 冲撞 / jumping / flying body
**NOT PROVEN as move labels.** Current Alpha rules and reports identify numeric enemy types, attack IDs, state/body/descriptor tuples, trigger styles, and timing. They do not authoritatively name A5440, A5424, A5136, A3232, etc. as 飞身、扑击、冲撞 or another Chinese move. No semantic promotion is allowed by this audit.

The only definite production statement is: **current V1 detects the two exact T18 numeric precursor tuples for eventual A5440 and A5424.**

## 6. Coverage gap vs HUD/projection failure vs research/quarantine

| classification | authority test | current examples |
|---|---|---|
| `DETECTION COVERAGE GAP` | gameplay attack has no matching `production:true` rule in current core | Any named/numeric attack outside the two enabled T18 predicates, unless a future repository mapping proves otherwise. Lack of `[危险]` is expected detector behavior, not a projection bug. |
| `HUD / PROJECTION FAILURE` | an enabled rule matches and core emits an authoritative warning row, but the user-facing HUD fails to display/anchor it | **Not diagnosed by this repository-only audit.** No Browser/WOF was run. Existing HUD/projection QA must be used for that layer. |
| `RESEARCH_ONLY` | evidence exists in WOF/Collector research but rule is absent from current Alpha production set | T24 rules, T23 sequences, BODY4728/A4704 discrimination work. |
| `QUARANTINED` | rule remains in current `FROZEN_RULES` metadata but `production:false` | T16, T20, D867, D881 listed above. They cannot publish `[危险]`. |
| `RETIRED` | prior candidate explicitly withdrawn/superseded | T18 BODY4728 single-state as A4704-specific predictor; old T23 BODY4920/B0. |

## 7. Smallest missing evidence to map named moves without changing V1 code

No production modification is needed. The missing artifact is a **read-only identity/move mapping proof** that ties all three layers together:

1. a scene/capture with an authoritative human label for the enemy (e.g. `夏侯惇` or `曹仁`) and the exact live enemy instance/slot;
2. the same instance's numeric enemy `type` observed under the supported World 921031 authority (or another source with an explicit proven equivalence to that Browser type namespace);
3. for each visually labeled move, synchronized evidence of the visible move and the exact eventual ACTIVE attack ID (`Axxxx`) plus relevant zero-cycle state/descriptor tuple;
4. repeat enough cycles to rule out an attack-ambiguous state (the BODY4728 A4704/A4712 history demonstrates why one observation is insufficient).

A compact future artifact like `Chinese enemy name -> type -> visible move name -> ACTIVE attack ID -> evidence timestamps/cycle IDs` would close the name authority gap. This audit intentionally starts no Collector/Browser task.

## 8. Invariants / scope

- repository-only audit;
- no Browser/WOF launch;
- no `product/alpha/**` modification;
- no danger-rule promotion or demotion;
- no target-semantic change;
- no Collector task created;
- `readOnly=true / ramWrites=0 / inputInjection=false` boundary preserved.

## Final

**COMPLETE — ALPHA V1 CURRENT DANGER COVERAGE AUTHORITY AUDIT — ENABLED / QUARANTINED / UNMAPPED MOVE COVERAGE MADE EXPLICIT**
