# WOF-052 Evening Multiplayer Capture — Start Prompt

You own a fresh, independent WOF-052 ordered-sequence collection stage. This is an opportunistic research/data lane running in parallel with Alpha RC5 because evening multiplayer rooms are currently available.

Repository:
- `ouyong520/wof-ai-private`

Read first:
- `WOF_AI_CURRENT_FRONTIER.md`
- `reports/WOF-051_ANALYSIS.md`
- `wof_future_danger_multiroom_coordinator_v52.js`
- the current WOF-052 embedded validator / tracer dependencies reachable from the coordinator
- `parallel/PM/ACTIVE_PRIORITIES.md`

## Why this lane is temporarily resumed

The owner reports that evening multiplayer rooms are now available. WOF-052 needs natural Browser room coverage, especially T18, to discriminate the exact BODY4728/A4/B2/TM1 candidate that prospectively led to both A4704 and A4712.

This is a time-window opportunity, not an Alpha release dependency.

## Hard separation from Alpha RC5

- Do NOT modify `product/alpha/**`.
- Do NOT enable or depend on the broken Alpha normal-user bootstrap.
- Keep the Alpha product userscript disabled during WOF-052 collection unless a later dedicated retest explicitly says otherwise.
- WOF-052 must remain read-only / `ramWrites=0` / no gameplay input injection.
- Do not interfere with room entry or normal play.

## WOF-052 objective

Use the existing WOF-052 ordered T18 tracer to collect candidate-containing zero->ACTIVE cycles and identify a post-candidate ordered-state discriminator between eventual A4704 and A4712.

Retain the existing protocol:
- Worker = collect
- top page = finalize + one JSON
- up to 5 rooms
- 1P/2P/3P rooms accepted
- prioritize rooms with T18
- preserve ordered distinct states
- summarize candidate-containing cycles by eventual activeAttack
- compare exact/TM* final, tail2, tail3, transition pair/triple
- discovery only; do not promote a production rule from WOF-052 alone

T23 tracing may continue opportunistically, but do not distract from the T18 BODY4728 split.

## Operator burden

Minimize owner actions. First inspect whether the current coordinator can be run safely on already-entered live rooms without touching startup. If yes, give the owner the shortest possible procedure, preferably one short loader command per live Worker and one top-page finalize command. Do not make the owner copy large JS bodies or perform broad manual inspection.

If the current WOF-052 coordinator itself has a concrete compatibility/runtime problem, diagnose and repair only the WOF-052 research tooling; do not touch Alpha product code.

## Collection target for tonight

Prefer up to 5 simultaneously or sequentially available live Browser rooms, especially T18-heavy rooms. Do not require the owner to hunt rare attacks manually. Let the collector observe natural play for its designed bounded window and then merge exactly one final JSON.

## Stop condition

Stop when either:

A. one valid merged WOF-052 JSON is produced from the available evening rooms and analyzed for the A4704 vs A4712 ordered discriminator; or

B. the existing tooling is reduced to one precise owner action / Browser observation needed to proceed.

If evidence is still insufficient after the available rooms, report exactly what sequence coverage is missing. Do not invent a rule or reopen broad research.
