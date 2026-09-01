# Local WinKawaks ROM Identity — Verdict

Updated: 2026-09-01
Status: **NOT YET PROVEN — STOP CONDITION B**

## Strict verdict

Current required classification:

```text
Local WinKawaks vs Browser World 921031:
NOT YET PROVEN
```

Reason: the repository retains decisive Browser program hashes, but does not yet retain a cryptographic hash of the local WinKawaks WOF program ROM bytes.

## Strong retained indication

The strongest direct local evidence is the saved live WinKawaks title:

```text
Kawaks 1.59 - 暂停 - Warriors of Fate (World 921002)
```

It came from the exact `WinKawaks.exe` PID used by the read-only local runtime probe.

Therefore the expected final classification is:

```text
local:   wofr1 / Warriors of Fate (World 921002)
browser: wof   / Warriors of Fate (World 921031)
relation: DIFFERENT PROGRAM REVISION
```

This expected classification becomes **positively proven** as soon as the local read-only probe matches the canonical `wofr1` program pair:

```text
tk2e_23b.8f  SHA-1 19e09ad6f9edc7997b030cddfe1d9c96d88135f2
tk2e_22b.7f  SHA-1 9fb8ae06856fe115addfb6794c28978a4f6716ec
```

The Browser comparison target is already proven as:

```text
tk2e_23c.8f  SHA-1 10b8cb53a4600e3e76f471a3eee8a600e93096fc
tk2e_22c.7f  SHA-1 52c2d05279623d93b27856e6b76830796a089eae
full CPU-logical SHA-256 5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
```

## Decision table for the minimal probe

| Probe result | Final classification |
| --- | --- |
| live title `World 921002` + exact 23b/22b SHA-1 pair | **DIFFERENT PROGRAM REVISION** |
| exact 23c/22c SHA-1 pair | **EXACT SAME PROGRAM REVISION** |
| title/hash contradiction, missing pair, or unknown program files | **NOT YET PROVEN** |

## Consequence if local is confirmed World 921002

Existing local work is **not discarded**. Its correct role remains discovery rather than Browser production proof.

### BASECAP

Still useful:

- scene/wave coverage;
- player/enemy raw-state diversity;
- lifecycle episodes;
- operator-labelled movement/attack/camera phases;
- comparative local field discovery.

Do not transfer automatically:

- numeric local RAM offsets to Browser;
- ROM/code addresses;
- revision-specific pointer values;
- assumptions that identical raw numeric states imply identical Browser behavior.

### EFIELD

Still useful:

- candidate field semantics;
- local correlations and transition structure;
- retarget/lifecycle hypotheses;
- which fields deserve Browser validation.

Mandatory Browser proof remains necessary for any production semantic or rule because the existing I1 compatibility result already showed that Browser reference offsets were not directly reusable in local WinKawaks (`FIELD_REMAP_REQUIRED`).

### RAWMINE

Still useful:

- change-frequency ranking;
- transition/event-window mining;
- local field clusters;
- candidate state-machine structure.

Not revision-portable by default:

- exact byte offsets;
- exact pointer/code constants;
- any inference tied to 921002 implementation details.

### SEQMINER

Still useful:

- ordered local event/attack sequence discovery;
- candidate temporal/state motifs;
- identifying repeated precursor patterns worth testing in Browser.

Must not be promoted directly:

- exact state numbers or program transitions without Browser confirmation;
- revision-specific sequences assumed to be identical in 921031.

## Browser validation boundary

If local proves to be World 921002, all local findings intended for production still require real Browser World 921031 validation before promotion.

That is already consistent with the project's established local-discovery -> Browser-proof architecture and does not invalidate the existing local corpus.

## Stop condition

GitHub evidence is exhausted for exact local program identity.

Exactly one remaining read-only operator command is specified in `MINIMAL_PROBE.md`. No gameplay, replay, new BASECAP, or broad recollection is requested.
