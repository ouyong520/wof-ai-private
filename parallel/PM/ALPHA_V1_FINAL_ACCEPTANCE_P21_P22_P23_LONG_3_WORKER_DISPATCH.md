# Alpha V1 Final Acceptance — P21 / P22 / P23 Long 3-Worker Dispatch

Repository: `ouyong520/wof-ai-private`

## PM state at dispatch

- P19 Final Canonical Candidate Rebuild + Attestation: COMPLETE / integration-ready.
- P20 Owner Visual Confirmation + Alpha-Live Promotion Gate: COMPLETE / integration-ready; no real Owner PASS and no real alpha-live movement.
- P21 Pre-Promotion Exact Candidate Staging + Acceptance Harness: existing ACTIVE ownership; continue exactly the existing claim, no duplicate/recovery.
- W3 repository-side qualification remains exhausted and requires one bounded Owner normal-play live sample for the final renderer-source causal proof.

## Parallel topology

### Slot 1 — existing ACTIVE P21

Continue:
`ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS`

Authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P21_PREPROMOTION_EXACT_CANDIDATE_STAGING_ACCEPTANCE_HARNESS_START_PROMPT.md`

Do not create another P21 claim. Existing exact ownership remains authoritative.

### Slot 2 — new P22

`ALPHA_V1_PRODUCT_TAKEOVER_P22_DYNAMIC_ACTOR_STATE_COVERAGE_ACCEPTANCE`

Authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P22_DYNAMIC_ACTOR_STATE_COVERAGE_ACCEPTANCE_START_PROMPT.md`

Purpose: implement passive evidence-backed coverage for actor movement/lifecycle/body-state/visibility/generation/enemy-target transitions so final acceptance is not limited to a static standing frame. Missing/unproven states remain explicit gaps; no guessed state classifier or coordinate authority.

### Slot 3 — new P23

`ALPHA_V1_PRODUCT_TAKEOVER_P23_POST_PROMOTION_VERIFICATION_PROJECT_CLOSE_HARNESS`

Authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P23_POST_PROMOTION_VERIFICATION_PROJECT_CLOSE_HARNESS_START_PROMPT.md`

Purpose: implement final post-promotion verification and project-close evidence state machine. It waits for real P20 promotion/Owner evidence and never moves alpha-live itself.

## Concurrency boundaries

P21 owns only its isolated staging area and must not be duplicated.
P22 owns new `parallel/OWNER_ACCEPTANCE_STATE/` implementation/evidence tooling.
P23 owns new `parallel/OWNER_RELEASE_POSTVERIFY/` implementation/evidence tooling.

P22/P23 must not modify P21 staging files, P20 release-gate files, P19 final candidate builder/candidate/attestation, P18 HUD/draw evidence, P17 orchestrator, W3 producer/qualification, P15 runtime semantics, W1 permanent updater, or `alpha-live`.

## Cadence

Implementation first. These are long bounded modules, not micro-patches. Each worker finishes its complete module before terminal RESULT. Only focused parse/fixture/self-checks are allowed; no broad QA and no real WOF run in repository implementation stages.

## Product truth boundary

No repository worker may claim real-WOF visibility, complete dynamic-state live coverage, Owner visual PASS, remote promotion, permanent-channel convergence, or Alpha V1 FINAL COMPLETE until the later real evidence exists.

Safety remains:
- readOnly=true
- ramWrites=0
- inputInjection=false
- no screenshot/world-projection production coordinates
- no guessed addresses
- no force-push
