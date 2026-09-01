# WOF ALPHA ENEMY LIFECYCLE AUDIT — START PROMPT

You own one bounded read-only product-support investigation for Alpha QA blocker ALPHAQA-002.

Repositories:
- `ouyong520/wof-ai-private`
- `ouyong520/wof-winkawaks-bridge` read-only only for provenance/negative-assumption evidence.

Read first:
- `parallel/ALPHAQA/FINDINGS.md` — ALPHAQA-002
- `parallel/ALPHAQA/independent_qa.mjs`
- `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`
- current `product/alpha/**`
- retained Browser production-shadow/coordinator code and evidence relevant to enemy slot/object lifetime, zero->ACTIVE cycles, disappearance, type changes, scene transitions and retargeting.

## Role and boundary

This is NOT an implementation owner and NOT a new generic field-research lane.

Question:

**How can Alpha conservatively prevent a warning armed by enemy episode A from being inherited by a different same-type enemy episode B reusing the same Browser slot?**

Treat `product/alpha/**` as READ-ONLY.
Write only under `parallel/ALPHALIFE/**`.
Do not modify QA, PM or product implementation.

## Work

1. Audit Browser evidence/code for object lifetime/reset markers already used or observed in the project.
2. Determine whether the current Browser reader/protocol guarantees an observable gap/reset/type change between same-type slot episodes. Do not assume it does.
3. Search for Browser-proven continuity signals that are stable enough for release use.
4. Use WinKawaks same-type replacement evidence only to invalidate unsafe assumptions; do not copy local offsets into Browser code.
5. If no positive instance identifier exists, design the most conservative implementation policy that prevents inherited false warnings, even if this increases silence/missed warnings.
6. Analyze the six frozen rules separately if necessary: transition watches, descriptor/timer watches and level/cycle rules may need different conservative invalidation conditions.
7. Define exact adversarial regression fixtures RC2 must pass, including same-type same-slot replacement without an observed null/type-change sample.
8. State clearly which recommendation is Browser-proven versus conservative fail-closed policy.

## Outputs

Write under `parallel/ALPHALIFE/**`:
- `README.md`
- `LIFECYCLE_AUDIT.md`
- `RECOMMENDED_INVALIDATION_POLICY.md`
- `RC2_REGRESSION_CASES.md`

## Stop condition

Stop when either:

A. an implementation-ready Browser-proven continuity/replacement guard is identified; or

B. no such identity is proven, but a conservative per-rule invalidation policy is defined that prevents old-watch inheritance and is ready for RC2 implementation/regression.

Do not request broad collection. If one real-Browser probe is genuinely required, define only the smallest precise probe and why retained evidence cannot answer it.