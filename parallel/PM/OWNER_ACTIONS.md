# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC3 candidate complete / fresh QA next

## Current owner action required: YES — stage/thread management only

The Browser identity probe is complete and accepted.
No additional Browser ROM probe is required now.

Authoritative supported Browser program:
- `wof / Warriors of Fate (World 921031)`
- full 1 MiB CPU-logical SHA-256:
  `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

RC3 has produced a candidate and its own product regression passes.

## Action O1 — close the RC3 implementation thread

The RC3 implementation thread has reached its stop condition.
Do not ask it to continue testing or certifying its own release.

## Action O2 — open a fresh independent RC3 QA thread

Use:

`parallel/PM/ALPHA_RC3_QA_START_PROMPT.md`

The fresh QA thread must:
- read current RC3 artifacts;
- write only under `parallel/ALPHAQA_RC3/**`;
- not modify `product/alpha/**`;
- independently audit exact 921031 SHA-256 gating, two-rule stateless lifecycle policy, session isolation, multi-threat HUD, bootstrap, legacy teardown, target/side, UNKNOWN silence, read-only/no-input and discovery-rule exclusion;
- stop at PASS-for-one-Browser-acceptance or a concrete P0/P1 blocker.

## Parallel support threads

### Local WinKawaks ROM Identity

Current status: one minimal read-only local hash probe remains.
Strong retained evidence points to local `World 921002`, but cryptographic proof is still pending.

Run only the exact one-command probe supplied by that support thread when requested. No gameplay or recollection is needed.

### Runtime Speed / Timing

Continue independently. No owner action yet unless that lane reduces the question to one minimal timing test.

### Player-Anchored HUD

Beta-support lane may be opened/continued independently using:

`parallel/PM/PLAYER_ANCHORED_HUD_START_PROMPT.md`

It must not modify Alpha product code.

## Do not do yet

- Do not run final Alpha Browser acceptance before fresh RC3 QA passes.
- Do not restart WOF-052 as an Alpha blocker.
- Do not perform broad Browser or WinKawaks recollection.
- Do not revive RC2 or RC3 implementation threads after their stages are complete.

## Next PM trigger

After the fresh RC3 QA writes its verdict to GitHub, PM will either:
- open a fresh next fix stage for any P0/P1 blocker; or
- issue one exact bounded Browser acceptance procedure and then decide Alpha release.
