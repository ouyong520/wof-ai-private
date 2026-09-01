# WOF Future Danger AI — Product Roadmap

Updated: 2026-09-01

## Milestone 1 — ALPHA FOUNDATION / FREEZE

Goal: a real user can load Future Danger and safely see a conservative validated subset.

Research may continue in parallel, but Alpha does not wait for full attack coverage.

### Alpha minimum feature set

1. Reliable supported-game loader/bootstrap.
2. Runtime identity/version compatibility check before enabling warnings.
3. Automatic read-only state acquisition; no game RAM writes.
4. Frozen production ruleset physically/logically isolated from discovery/experimental candidates.
5. Per-enemy warning output for only validated production rules.
6. Live target reread and active-edge retarget handling.
7. Left/right warning based on validated geometry/target state.
8. Approximate lead-time display only for rules with validated timing evidence; otherwise use a qualitative imminent/early warning class.
9. UNKNOWN / unsupported attack stays silent.
10. Simple user HUD; research JSON may remain available behind debug mode but is not the primary interface.
11. Fail closed: identity/read/parser/rule errors disable the affected warning rather than guess.
12. Regression audit covering all frozen production rules and P1/P2/P3 where existing evidence supports it.

### Alpha release gate

Alpha is releasable when:

- frozen rules have prospective evidence and no known hard miss in their claimed coverage;
- loader/runtime identity guard is reliable on the declared supported build;
- read-only/no-write invariant is enforced;
- production and experimental rules cannot accidentally mix;
- target/side use current live target logic;
- failures degrade to silence, not false warnings;
- the HUD works without requiring Console JSON;
- a short real Browser acceptance run passes on the supported build.

Coverage breadth is deliberately not an Alpha gate.

## Milestone 2 — BETA COVERAGE / USABILITY

Goal: an ordinary user can keep it enabled for normal play and receive useful warnings often enough to matter.

Beta requires:

- authoritative coverage accounting refreshed with normalized type IDs;
- high coverage of the common enemy/common dangerous-attack set identified by actual census/atlas evidence;
- validated ordered-sequence rules for important ambiguous branches where single-state rules are insufficient;
- stable target/side across common P1/P2/P3 and retarget cases;
- broader multi-room/scene validation;
- simple configuration and clear supported-version messaging;
- user-facing HUD polish and warning prioritization when multiple enemies are dangerous;
- **player-anchored warning placement:** compute a stable screen-space anchor above the currently threatened P1/P2/P3 character and keep the warning following that character through movement, jumping/depth changes and camera scrolling. This must use a proven Browser camera/screen-coordinate transform (or equivalent native projection evidence), not guessed DOM/world coordinates or color/pixel tracking. Until that transform is reliable, the fixed in-game HUD remains the safe fallback;
- acceptable runtime overhead and no gameplay interference;
- automated regression checks for frozen production rules;
- release packaging/install/update instructions appropriate for non-research users.

Rare attacks and rare boss branches may remain UNKNOWN in Beta if the UI stays silent rather than wrong.

## Milestone 3 — V1

Goal: first formal supported Future Danger product release.

V1 does **not** require 100% of all attacks.

V1 requires:

1. A stable Beta-quality loader/runtime/HUD on a declared support matrix.
2. A frozen ruleset where every production rule has prospective evidence; high-value rules should have multi-room and, where applicable, cross-target evidence.
3. COVERAGE/SWEEPATLAS define the actual common gameplay set sufficiently to make a defensible breadth claim.
4. The production ruleset covers a high proportion of that common dangerous-event set, while known uncovered/ambiguous events remain silent.
5. No unresolved P0 target/retarget, namespace/version-identity, read-only, or production-rule-isolation risk.
6. Regression protection against rule drift and browser/game revision mismatch.
7. Clear release notes stating supported builds, known UNKNOWN coverage and limitations.
8. The user experience does not require research scripts, hand-read JSON, or manual rule interpretation.

The numeric coverage threshold for v1 should be set only after COVERAGE is refreshed against authoritative common-event data. PM will not invent a percentage before that denominator exists.

## Beyond v1 — Future Danger Map / Safe Path

After warning correctness and coverage are product-stable:

`enemy future intent + target + side + position + timing`

feeds:

`Future Danger Map`

then:

`Safe Path`

Safe Path is not allowed to pull research scope forward before the warning product is stable.
