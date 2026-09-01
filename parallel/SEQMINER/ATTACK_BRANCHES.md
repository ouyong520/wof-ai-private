# SEQMINER Attack Branches

This file tracks known attack ambiguity and the ordered context required to split it. Browser-labelled evidence is used only to prioritize prospective validation; WinKawaks-local evidence remains namespace-local.

## Branch A — T18 shared BODY4728 state

Shared Browser state:

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

Prospective WOF-051 outcomes:

| eventual attack | count | lead | target/side |
|---|---:|---:|---|
| A4704 | 1 | 19.9 ms | stable |
| A4712 | 1 | 100.4 ms | stable |

Verdict: **single-state ambiguity proven prospectively**.

### Required branch search

For every candidate-containing zero cycle, compare in order:

1. first distinct state after shared BODY4728;
2. post-state pair;
3. post-state triple;
4. preceding tail2/tail3 + shared state;
5. exact TM progression;
6. timer-normalized progression;
7. descriptor/`next` progression;
8. target/reference stability.

The first split that remains stable across independent cycles is the preferred validation candidate. Do not promote the BODY4728 state itself.

## Branch B — T23 A4792 / A4920 / A5888

WOF-047 same-cycle labelled sample:

| eventual attack | resolved cycles |
|---|---:|
| A4792 | 3 |
| A4920 | 3 |
| A5888 | 2 |

### A5888 ordered branch

One observed A5888 tail3:

```text
S0/A8/B2 BODY4936
-> S0/A2/B0 BODY4936
-> S0/A6/B4 BODY4936
-> A5888
```

Important ambiguity: the first `S0/A8/B2 BODY4936` state also appears in an A4792 cycle. This is direct same-cycle evidence that the transition path is more informative than single-state membership.

A second A5888 final state differs only in `S2` versus `S0` at the same `A6/B4 BODY4936` family, so final-state equality is not assumed universal even inside one attack class.

### A4792 is itself multi-branch

The three A4792 cycles ended through different immediate tails:

1. `... A6/B0 -> A6/B4 -> S0/A2/B0 BODY4952 ... -> A4792`
2. `S0/A8/B2 BODY4936 ... -> A4792`
3. `S2/A4/B10 BODY4952 -> S2/A2/B0 BODY4952 -> S2/A8/B2 BODY4936 -> A4792`

Therefore a useful T23 model may be a **set of attack-specific branches**, not one universal signature per attack.

### A4920 observed final/tail families

Observed examples include:

```text
S0/A4/B0|BODY4976|FE84868|NX83c56|V1|TM8|P6C0
S0/A6/B4|BODY4976|FE84868|NX83f20|V0|TM11|P6C0
S0/A4/B10|BODY4952|FE84102|NX83c7e|V0|TM1|P6C4960
```

These are discovery examples, not a universal A4920 rule.

## Branch C — WinKawaks structural executor branches

The retained EFIELD corpus does not supply a separately proven exact WinKawaks attack descriptor, so these branches are **structural proxy branches**, not attack labels.

### Core/bridge branch

```text
40,00,E8,1B,00
-> E0,A0,D8,0A,0C
-> 40,00,E8,1B,00
```

Observed compressed count: 41.

### Core/bridge/terminal branch

```text
40,00,E8,1B,00
-> E0,A0,D8,0A,0C
-> 40,00,E8,1B,00
-> 48,00,00,1B,00
```

Observed compressed count: 24.

### Alternate-entry branch

```text
E0,00,38,0A,00
-> E0,A0,D8,0A,0C
```

Observed compressed count: 38.

### Boundary-only families

```text
78,78,78,1E,0B
70,70,70,1E,0B
```

Both had zero interior samples in the retained boundary analysis. They are high-value termination/context markers for future exact attack-labelled mining.

## Branch dimensions to retain

Every branch comparison should preserve:

- `type`;
- action/state `+0x2D/+0x2E`;
- logical cursor + raw flag bits;
- exact `+0x34` timer;
- normalized `+0x34` timer family;
- `+0x35` mode progression;
- `+0x37` gate progression;
- full `(6C,70,72,73,77)` phase tuple;
- live target `+0x6D..0x6E`;
- association/reference `+0x3D..0x3E/+0xC6`;
- profile `+0xB0/+0xB4/+0xB6`;
- capture, scene and object slot/episode identity.

## Promotion boundary

A branch becomes `potentially_prospectively_testable_candidate` only after repeated same-cycle support and stability beyond a single capture/scene. It still requires an explicit prospective Browser validator before any production consideration.
