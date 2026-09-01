# RAWMINE Post-Completion BASECAP Incremental Audit

Date: 2026-09-01  
Scope: bounded post-completion audit only  
Evidence class: `WinKawaks-local-discovery-only`  
Final bounded verdict: **A — MATERIAL_INCREMENT**

RAWMINE remains sealed. This audit does not restart generic RAWMINE research, does not request new acquisition, does not modify GEO/EFIELD conclusions, and does not promote any WinKawaks offset to Browser/WASM production truth.

## Inputs

New canonical BASECAP v1 raws:

```text
BASECAP-B13-attack-12s60-20260901-0558Z
BASECAP-B20-camera-scroll-16s60-20260901-0559Z
BASECAP-B40-P2-xy-16s60-20260901-0600Z
BASECAP-B40-P3-xy-16s60-20260901-0601Z
```

Controls/reference reused without new capture:

```text
BASECAP-B00-idle-8s60-20260901-0510Z
RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z
```

Bridge evidence outputs:

```text
results/rawmine/basecap_incremental_audit.json
results/rawmine/basecap_incremental_audit.md
results/rawmine/basecap_incremental_audit_detail.md
results/rawmine/basecap_p2_depth_pair_focus.json
```

## 1. B40-P2 — material neutral increment

### GEO-known offsets

| Offset | change count | frequency | P2 specificity among players | bidirectional | observed domain | all-offset rank |
|---|---:|---:|---:|---:|---|---:|
| `+0x04` | 0 | 0.000000 | 0.000000 | 0.000000 | 234..234 / 1 | 27 |
| `+0x0B` | 0 | 0.000000 | 0.000000 | 0.000000 | 0..0 / 1 | 33 |
| `+0x08` | 10 | 0.010428 | 1.000000 | 0.000000 | 99..112 / 11 | 6 |
| `+0xA2` | 11 | 0.011470 | 1.000000 | 0.000000 | 99..113 / 12 | 4 |

`+0x08` and `+0xA2` therefore add new P2-only dynamic evidence. The controlled run does **not** provide bidirectional coverage at these offsets: all observed changes are one signed direction, so RAWMINE does not treat this as promotion-grade same-offset proof.

### +0x08 / +0xA2 coupling

Whole-run event relation:

- `+0x08` events: 10
- `+0xA2` events: 11
- intersection: 8
- union: 13
- same-frame event Jaccard: **0.615385**

The best exact value-copy relation over comparable frames is source `+0x08` at lag `-1` relative to `+0xA2`, i.e. the same orientation as the existing P1 relationship:

```text
A2[t] ~= 08[t-1]
```

Whole-run exact match is 950 / 959 = 0.990615, but this number is static-frame dominated and is not used alone.

Dynamic-frame conditioned check removes that inflation:

| Condition | P2 lag -1 exact ratio | P1 reference lag -1 exact ratio |
|---|---:|---:|
| union of `+08/+A2` dynamic frames | 10 / 13 = **0.769231** | 509 / 648 = **0.785494** |
| `+0xA2` change frames only | 8 / 11 = **0.727273** | 397 / 536 = **0.740672** |
| same-frame event Jaccard | **0.615385** | **0.654321** |

This is the material increment: the new canonical P2 controlled raw reproduces, at similar dynamic-frame ratios, the previously observed P1 `+0x08/+0xA2` temporal family pattern. RAWMINE records this only as **P2 same-family / same-offset candidate evidence**; GEO owns final structure/offset semantics and promotion.

### P2 neutral all-offset ranking

The shared `+0x7F` activity remains non-specific across players and is not treated as geometry evidence. Excluding that shared row, the leading P2-specific dynamic candidates from this controlled run are:

1. `+0x34` — 13 changes, specificity 1.0, bidirectional 0.769231, small-step ratio 1.0
2. `+0xB0` — 7 changes, specificity 1.0
3. `+0xA2` — 11 changes, specificity 1.0, small-step ratio 1.0
4. `+0xC9` — 11 changes, specificity 1.0
5. `+0x08` — 10 changes, specificity 1.0, small-step ratio 1.0

These are candidate-ordering data only. Existing owner semantics for any of these fields are not changed by RAWMINE.

### P2 X coverage

`+0x04` and `+0x0B` are static in B40-P2. Therefore this new raw adds **no controlled P2 X same-offset evidence** and is not negative evidence against the existing GEO hypothesis. Existing natural-corpus P2 X evidence remains separate and unchanged.

## 2. B40-P3 — no usable geometry increment

In B40-P3, the known GEO offsets are static:

```text
+0x04: 0 changes
+0x0B: 0 changes
+0x08: 0 changes
+0xA2: 0 changes
```

Across the P3 object, the only prominent dynamic byte is shared `+0x7F`, with roughly one-third player specificity. No P3-specific geometry candidate is exposed by this raw under the retained 23-object interpretation.

The BASECAP operator label remains canonical; RAWMINE only states that this raw does not provide a discriminative P3 geometry signal. It is not used as negative proof that P3 differs structurally from P1/P2.

## 3. B13 ordinary attack vs B00 idle — no material increment

The attack-vs-idle differential does not improve the sealed action/animation ranking materially.

Top row:

- `+0x7F`: 354 attack-run changes vs 238 idle-run changes;
- normalized attack/idle rate ratio: **0.990907**;
- P1 specificity inside the attack run: **0.332707**.

This is shared/background-like activity rather than attack-specific enrichment. Other P1 offsets do not acquire useful controlled dynamic support in this comparison.

Result: `NO_MATERIAL_INCREMENT_B13`.

## 4. B20 camera-scroll vs B00 idle — no material increment

The object-record screen finds no new broad synchronous offset enriched by the visually confirmed scroll episode.

The only high-activity broad row is `+0x7F`:

- B20 broad-sync frequency: **0.464025**
- B00 broad-sync frequency: **0.469729**
- mean majority slots: 3

It is not scroll-enriched. Known GEO offsets do not produce broad synchronous object movement in this screen.

Important visibility limit: the retained raw contains only the 23 object records. A standalone global camera variable located outside those object records cannot be observed by this BASECAP stream, so absence of an object-record candidate is not evidence that no global camera state exists.

Result: `NO_MATERIAL_INCREMENT_B20`.

## Final A/B decision

**A — MATERIAL_INCREMENT**

Reason is narrow and specific:

```text
B40-P2 adds new controlled P2-only +0x08/+0xA2 dynamics,
and its dynamic-frame lag relationship closely matches the existing P1 pattern.
```

B13, B20, and B40-P3 do not add material candidate evidence under this audit.

An initial strict automatic gate emitted `NO_MATERIAL_INCREMENT` because it required bidirectional motion for the known geometry offsets. That threshold is appropriate for stronger promotion-grade coverage, but it is too strict for this task's question of whether *any new candidate evidence* exists. The dynamic-frame conditioned check is therefore the final materiality discriminator for this bounded audit.

## GEO handoff

Handoff status:

`READY_FOR_GEO_P2_SAME_STRUCTURE_CANDIDATE_REVIEW`

Give GEO the following neutral evidence only:

1. P2 `+0x08`: 10 changes, specificity 1.0, domain 99..112 / 11 values, one-direction small-step trajectory.
2. P2 `+0xA2`: 11 changes, specificity 1.0, domain 99..113 / 12 values, one-direction small-step trajectory.
3. `+0x08/+0xA2` event Jaccard 0.615385.
4. Dynamic-frame lag `A2[t] ~= 08[t-1]`: P2 0.769231 on union-dynamic frames vs P1 0.785494; on A2-change frames P2 0.727273 vs P1 0.740672.
5. No new controlled P2 `+0x04/+0x0B` evidence from this run.
6. No usable P3 geometry increment from B40-P3.
7. RAWMINE makes no same-structure/same-offset semantic declaration; GEO owns the decision.

## Stop rule after audit

RAWMINE returns to sealed state immediately after this handoff.

- no new operator task;
- no generic candidate mining restart;
- no B13/B20 follow-up acquisition;
- no P2/P3 re-capture requested by RAWMINE;
- future work only if an owner lane presents a new bounded ambiguity that retained data can discriminate.
