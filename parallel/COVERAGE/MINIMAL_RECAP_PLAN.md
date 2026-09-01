# MINIMAL RECAP PLAN

Snapshot: `2026-09-01`

## Decision

**Human recap required: NO**

- selected scenes: **none**
- selected waves: **none**
- new Collector tasks created by COVERAGE: **0**
- current minimum physical recap set: **∅**

This is an intentional result, not a failure to plan.

## Why the optimum is currently the empty set

The largest unresolved cells in COVERAGE are not proven physical-data shortages. They are:

1. authoritative stage / scene / wave labels — `LABEL_UNKNOWN`;
2. boss / ordinary classification — `LABEL_UNKNOWN`;
3. semantic ACTIVE-cycle definition/count — `LABEL_UNKNOWN`;
4. per-Txx lifecycle / attack / target / scene cross-tabs — `LABEL_UNKNOWN`;
5. ordered sequence-family output — `LABEL_UNKNOWN` because SEQMINER is absent;
6. low-density Txx and one rare structural family, whose useful scene incidence is not yet known.

Without an authoritative scene-to-gap incidence matrix, choosing “three scenes” would be guesswork and would violate the rule against assigning scenes from raw numerics.

The existing corpus already contains 28 mechanically successful gameplay raws with complete task/status/result/raw provenance, while GEO and RAWMINE owner lanes do not call for a generic resweep.

## Set-cover formulation to use once labels exist

Candidate unit: a specific authoritative `(stage, scene, wave, player-config)` capture opportunity.

A candidate's coverage set may include:
- one or more LOW/MISSING Txx;
- P1/P2/P3 target evidence;
- rare structural attack/executor families;
- boss or ordinary enemy class;
- left/right/depth/camera geometry diversity;
- ordered sequence families;
- any still-missing semantic label that can be directly observed.

Optimization order:

1. minimize number of human-entered scenes;
2. then minimize total capture seconds;
3. maximize number of independent gaps closed by each selected scene;
4. prefer candidates that simultaneously add Txx + target + attack/sequence + boss/ordinary + geometry diversity;
5. penalize weak labels, uncontrolled geometry, or known confounds;
6. never choose a broad game resweep when a smaller equivalent cover exists.

## Recompute gates

Re-run the set-cover decision when at least one of these becomes available:

- `parallel/SWEEPATLAS/**`;
- `parallel/SEQMINER/**`;
- an authoritative stage/scene/wave/boss label table;
- new EFIELD/RAWMINE results that materialize per-Txx cross-tabs;
- new bridge task/status/result/raw artifacts.

## What does *not* trigger recap by itself

- a Txx having fewer than 500 samples;
- T23 having zero samples in the current EFIELD corpus;
- a flat/confounded historical geometry run;
- a rare `+0x73` value without a semantic scene/attack label;
- absence of a Browser production-shadow proof.

When a future recomputation produces a nonempty minimal scene set, COVERAGE should report exactly: stage, wave, reason, duration, and the gaps closed by that one acquisition. At this snapshot there is no defensible nonempty set to report.
