# Alpha V1 Named Danger Move Mapping Live-Proof Prep

stageId: `ALPHA_V1_NAMED_DANGER_MOVE_MAPPING_LIVE_PROOF_PREP`
dedupProtocol: `v2`
dedupKey: `alpha.v1.named-danger-move-mapping-live-proof-prep`
dedupMode: `exclusive`

Priority: **P1 observability / coverage-authority preparation**

Repository: `ouyong520/wof-ai-private`

## Trigger

Current danger coverage authority audit is COMPLETE and proves exactly two production-enabled numeric rules:

- type 18 -> A5440 precursor;
- type 18 -> A5424 precursor.

The same audit found no authoritative repository mapping for:

- 夏侯惇 -> enemy type -> attack ID;
- 曹仁 -> enemy type -> attack ID;
- 飞身 / 扑击 / 冲撞 -> attack ID.

Do not guess these mappings.

## Goal

Prepare the smallest read-only live-evidence procedure that can close the missing `Chinese enemy name -> numeric type -> visible move -> ACTIVE attack ID` authority gap during a future bounded Browser/WOF session, without changing current production rules.

This is preparation only; do not launch Browser/WOF.

## Required output

Define an evidence contract that records, for one exact live enemy lifecycle:

- authoritative human-visible enemy identity label when possible;
- slot + lifecycle/generation authority;
- numeric enemy type;
- visible move label supplied by the operator only when visually unambiguous;
- zero-cycle precursor tuple;
- eventual ACTIVE attack ID;
- exact target7E / P1-P3 target;
- timestamps and cycle identity;
- enough repeated cycles to reject attack-ambiguous single-state mappings;
- mapping confidence and explicit `UNMAPPED` fallback.

Specifically describe how future evidence could prove or fail to prove:

- 夏侯惇 coverage;
- 曹仁 coverage;
- 飞身 / 扑击 / 冲撞 move identity;
- whether A5440/A5424 correspond to any of those names.

## Constraints

- repository-only preparation;
- no Browser/WOF launch;
- no production rule promotion/demotion;
- no `product/alpha/**` modification;
- no claim that visual familiarity is authority;
- no WinKawaks-local interpretation promoted directly into Browser production authority;
- reuse existing one-session/live-proof/Collector evidence mechanisms where safe rather than inventing a second authority system;
- readOnly=true, ramWrites=0, inputInjection=false.

## Deliverable

A concise future-session mapping proof plan plus exact PASS / UNMAPPED / AMBIGUOUS classifications, so the Owner does not have to manually infer attack IDs.

## Success

`COMPLETE — ALPHA V1 NAMED DANGER MOVE MAPPING LIVE-PROOF PREP — MINIMAL AUTHORITATIVE NAME↔TYPE↔ATTACK EVIDENCE CONTRACT READY`

## Failure

`BLOCKED — ALPHA V1 NAMED DANGER MOVE MAPPING LIVE-PROOF PREP — <precise missing repository capability>`

Strict canonical dedup v2. Stop duplicate-safe if equivalent work already exists.
