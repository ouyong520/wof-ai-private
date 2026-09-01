# SEQMINER — WinKawaks enemy attack ordered-sequence mining

Status: **active discovery lane / WinKawaks-local only**

Write boundary: `parallel/SEQMINER/**` only.

## Mission

SEQMINER exists because a single pre-attack state is not necessarily enough to determine the eventual attack.

The Browser mainline already contains two direct examples:

- T18: the same `BODY4728/A4/B2/TM1` state was prospectively followed by both `A4704` and `A4712`.
- T23: WOF-047 resolved eight zero-cycle traces across three eventual attacks (`A4792=3`, `A4920=3`, `A5888=2`), so the next useful unit is ordered context rather than another isolated state predicate.

SEQMINER therefore mines:

`zero attack/zero proxy -> ordered distinct states -> pair -> triple -> timer/descriptor progression -> future ACTIVE/nonzero event`

and asks which ordered contexts remain stable across captures, scenes, targets, and object instances.

## Hard namespace rule

WinKawaks normalized offsets are **not** Browser/WASM offsets. Nothing in this lane promotes a Browser production rule.

Current confirmed/high-value WinKawaks-local enemy fields reused by SEQMINER:

| local offset | role used by SEQMINER |
|---|---|
| `+0x24` | verified type/type-present lifecycle anchor |
| `+0x2D` | action/reset/control candidate |
| `+0x2E` | broad action/state candidate |
| `+0x2F..0x32` | flagged U32 BE script/animation record cursor |
| `+0x34` | record dwell/countdown |
| `+0x35` | independent dwell/control mode |
| `+0x37` | attack-associated gate/substate candidate |
| `+0x6C` | fine executor/attack-associated phase |
| `+0x6D..0x6E` | materialized live player-target pointer |
| `+0x70` | second fine body/attack-associated phase |
| `+0x72` | joint-phase payload/companion |
| `+0x73` | deterministic coarse projection/family anchor |
| `+0x77` | second coarse projection |
| `+0x3D..0x3E` | stored player-association pointer |
| `+0xC6` | stored player-association index |
| `+0xB0/+0xB4/+0xB6` | profile/instance context |
| `+0xB9/+0xBB` | locomotion phase/countdown context |

`+0x73 != 0` is **not** treated as a proven semantic attack ACTIVE condition. It is only a structural proxy that lets us exhaust ordered-sequence information already present in the retained EFIELD corpus.

## Current corpus state

The connector-visible GitHub `main` currently contains the established BASECAP/EFIELD/GEO/RAWMINE retained captures, including the seven valid EFIELD runs, but no pushed all-game `SWEEP*` capture and no `parallel/SWEEPATLAS` directory. Therefore this first SEQMINER pass does two things:

1. exhausts the already-computed raw-derived ordered-sequence evidence in `results/efield/**`;
2. installs `seqminer.py`, which automatically consumes `captures/*.jsonl.gz` from a local/CI checkout as soon as retained sweep raw is present, without asking a human to move files or enumerate filenames.

This is a **reuse-before-recapture** result. No Collector task is created by this lane.

## Evidence classes

SEQMINER uses three explicit evidence labels:

1. `discovery_correlation` — association in retained local data; useful for ranking only.
2. `same_cycle_evidence` — an ordered context is observed before the same object's later nonzero event in the same cycle.
3. `potentially_prospectively_testable_candidate` — enough same-cycle support/stability exists to justify a separate prospective Browser experiment. This still is **not** a production rule.

When the miner runs in `phase73` proxy mode, candidates remain local structural evidence. Only a future run with a separately proven WinKawaks attack-value field may group cycles by an exact local `activeAttack` value.

## Automatic miner

`seqminer.py` is standard-library Python and discovers raw files itself.

Example from a checkout containing both repositories:

```bash
python wof-ai-private/parallel/SEQMINER/seqminer.py \
  --captures wof-winkawaks-bridge/captures \
  --output wof-ai-private/parallel/SEQMINER/generated
```

Default mode is conservative structural proxy mode:

```text
attack-zero proxy: enemy+0x73 == 0
future event:       same object enemy+0x73 becomes nonzero
label:              first nonzero PH73 family
```

Once a true WinKawaks-local attack-value field is independently proven, use explicit attack mode instead of silently reinterpreting an existing offset:

```bash
python .../seqminer.py \
  --captures .../captures \
  --output .../parallel/SEQMINER/generated \
  --attack-offset 0xNN --attack-width 2 --attack-endian be
```

The miner never assumes a Browser offset equivalence.

## State representation

A distinct state retains at least:

- `type`
- local action/state candidates `+0x2D/+0x2E`
- raw/logical cursor and cursor flags `+0x2F..0x32`
- timer `+0x34`
- mode/value `+0x35`
- gate `+0x37`
- fine/body/payload/coarse phase tuple `(+0x6C,+0x70,+0x72,+0x73,+0x77)`
- live target `+0x6D..0x6E`
- player-association/reference layer `+0x3D..0x3E/+0xC6`
- instance/profile context `+0xB0/+0xB4/+0xB6`
- locomotion context `+0xB9/+0xBB`
- local coordinates `+0x07..0x0A/+0x0B..0x0E`
- frame start/end and dwell length

The base distinct-state key deliberately excludes the rapidly decrementing `+0x34` timer. Exact-timer and timer-normalized variants are computed separately.

## Timer normalization

The retained EFIELD corpus strongly favors record-relative timer normalization over literal timer equality. Across 4,323 logical `+0x0A` destination arrivals, the arrival timer is at the observed record ceiling 73.84%, within one below it 92.53%, and within two below it 94.61%. Leave-one-run-out behavior is similarly stable.

SEQMINER therefore records both:

- exact `timer34` progression;
- `ceilingMinusTimer34` relative to the logical cursor's observed record ceiling, with buckets `0`, `1`, `2`, `3-5`, `6-10`, `11+`.

This preserves exact timing while allowing the same record to match despite sampling one or two countdown ticks apart.

## Outputs

Human-maintained current frontier:

- `SEQUENCE_ATLAS.md`
- `ATTACK_BRANCHES.md`
- `CANDIDATES.json`
- `BROWSER_VALIDATION_QUEUE.md`
- `FRONTIER.md`

A local/CI run of `seqminer.py` additionally writes machine-generated artifacts under the requested output directory.

## Guardrails

- No game-memory writes.
- No Browser production-rule promotion.
- No bulk Collector task creation.
- No offset equivalence assumption between WinKawaks and Browser/WASM.
- Do not call a `+0x73` transition an actual attack unless independently proven.
- Do not call `+0x24` attack ACTIVE; it is type/type-present lifecycle.
- Prefer cross-capture and cross-target support over single-run purity.
- A perfect in-sample pair/triple with one cycle is not a validation candidate.
