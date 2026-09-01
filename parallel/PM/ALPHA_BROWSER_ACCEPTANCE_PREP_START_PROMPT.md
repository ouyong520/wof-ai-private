# WOF ALPHA BROWSER ACCEPTANCE PREP — START PROMPT

You own a bounded support-preparation lane for the WOF Future Danger Alpha release.

Repository:
- `ouyong520/wof-ai-private`

## Goal

Prepare the smallest, safest real-Browser acceptance procedure for the current `wof-alpha-rc3` candidate so that, if fresh independent RC3 QA passes, the owner can execute one short acceptance run with minimal manual DevTools work.

This lane prepares tooling/checklists only. It does NOT certify RC3 and does NOT modify Alpha product code.

## Read first

- `parallel/PM/RELEASE_READINESS.md`
- `parallel/PM/ACTIVE_PRIORITIES.md`
- `parallel/PM/ALPHA_RC3_QA_START_PROMPT.md`
- `product/alpha/ALPHA_RC3_REPORT.md`
- current `product/alpha/**` read-only
- existing bootstrap/user install docs
- Browser identity result for `wof / World 921031`

Authoritative Browser identity:
- `wof / Warriors of Fate (World 921031)`
- SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

## Write boundary

Write only under:
- `parallel/ALPHAACCEPT/**`

Do NOT modify:
- `product/alpha/**`
- `parallel/ALPHAQA_RC3/**`
- PM files

## Required preparation

Design one bounded owner acceptance sequence that can verify, in the real Browser runtime:

1. normal-user document-start bootstrap reaches the real game Worker;
2. exact World 921031 full-program SHA-256 is accepted;
3. fail-closed identity/runtime errors produce no warning;
4. HUD renders in the game WebGL path without corrupting GL state;
5. session/cross-tab isolation works;
6. reload creates a fresh pairing;
7. legacy WOFHUD teardown works when relevant;
8. current live target/side and stale/UNKNOWN silence remain sane;
9. runtime overhead is acceptable enough for Alpha;
10. no game RAM writes or gameplay input injection occur.

Prefer automatic diagnostics and a single summary JSON over asking the owner to inspect many console values.

If a userscript/one-line diagnostic loader can collect the acceptance state without modifying `product/alpha/**`, create it under this support lane.

Do not require the owner to provoke rare attacks merely to certify infrastructure. Use existing active RC3 rule behavior only where naturally available; separate infrastructure acceptance from attack-coverage proof.

## Required outputs

Create:
- `parallel/ALPHAACCEPT/README.md`
- `parallel/ALPHAACCEPT/ACCEPTANCE_PLAN.md`
- `parallel/ALPHAACCEPT/OPERATOR_STEPS.md`
- optional support-only diagnostic JS if it materially reduces manual work
- `parallel/ALPHAACCEPT/RESULT_SCHEMA.md`

## Stop condition

Stop when the owner acceptance is reduced to the smallest practical real-Browser operation and an unambiguous PASS/FAIL result format exists.

Do not run the final release acceptance yourself and do not declare Alpha released. Fresh independent RC3 QA remains the gate before owner acceptance.