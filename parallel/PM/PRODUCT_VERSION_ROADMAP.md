# WOF Future Danger AI — Product Version Roadmap

Updated: 2026-09-02
Status: **AUTHORITATIVE — PRODUCT VERSION / RELEASE CADENCE / USER-VALUE ROADMAP**

This roadmap is authoritative together with `parallel/PM/PM_CORE_OPERATING_CHARTER.md`.

## 1. Product-version rule: every release must feel better to the player

A product version is earned by a clear user-visible gameplay improvement, not by internal engineering completion alone.

A release should improve at least one of:

- danger is noticed earlier;
- more common dangerous situations are covered;
- warning/target information is easier to understand;
- overlays follow the correct player/enemy more reliably;
- crowded multi-enemy situations are clearer;
- movement guidance becomes available or more useful;
- human reaction/execution becomes easier;
- measured damage / failed-evade rate decreases.

The following do **not** justify a user-facing version number by themselves:

- refactors;
- schema cleanup;
- CI/dedup/test-harness work;
- recorder/launcher infrastructure;
- synthetic QA only;
- performance work with no observable user effect;
- training infrastructure that is not yet connected to the live Assist experience.

These may be mandatory engineering stages, but remain internal until they unlock a user-visible release delta.

## 2. Release cadence

Target cadence after a usable release baseline exists:

- **Patch / experience slice:** roughly every **2–3 days** when a safe user-visible improvement is ready.
- **Minor product release:** roughly every **7 days**, combining several proven improvements into a materially better gameplay experience.
- **Major phase transition:** only when the user workflow changes qualitatively, such as warning-only -> movement guidance -> near-zero-damage guidance.

Cadence is a target, not permission to bypass safety. Do not ship while a P0/P1 defect, false-warning risk, visible overlay drift, or unproven runtime authority remains.

If a period produces only internal work, keep the product version unchanged.

## 3. Difficulty curve

The expected engineering difficulty is not flat:

1. **V1.0.0 is the first hard foundation gate.** It must prove trustworthy live state, target binding, lifecycle handling, projection/non-drift and fail-closed behavior.
2. **V1.0.x / V1.1 / V1.2 become materially easier** because they reuse the stable live state + HUD + projection + transport foundation and mainly improve user-visible warning quality/coverage.
3. **Assist Beta is the next hard transition** because the product begins recommending what the player should do, not merely what is dangerous.
4. **Near-Zero RC is another hard outcome gate** because success is measured by actual machine/human damage reduction across broad continuous gameplay.

So the expected pattern is:

`hard foundation -> faster visible iterations -> new hard capability jump -> faster iterations -> hard outcome proof`.

## 4. Current family — V1

### V1.0.0 — Trustworthy head-up warning baseline — CURRENT RELEASE TARGET

User-visible promise:

1. threatened P1/P2/P3 gets a danger reminder above the correct live player;
2. supported enemies show current `1P / 2P / 3P` target above the enemy;
3. retarget updates promptly with no stale old player/label;
4. horizontal/depth movement, jump, rapid progression, camera/stage scroll and resize/fullscreen do not cause obvious overlay drift;
5. unreliable anchoring/projection hides or falls back to fixed HUD instead of confidently drawing wrong coordinates;
6. normal gameplay remains read-only/no-input-injection.

V1.0.0 is not released from repository QA alone. The required bounded real Browser/WOF dynamic proof and current release gates must close first.

### V1.0.1 — Warning readability patch — target ~2–3 days after V1.0.0

User-visible improvement:

- warning is easier to notice and interpret during combat;
- current target/retarget state is clearer;
- visual noise is reduced without weakening fail-closed safety.

Implementation may include clearer urgency/severity presentation, better badge/text hierarchy, or cleaner redundant-warning suppression, chosen from actual play evidence.

### V1.0.2 — Multi-enemy clarity patch — target ~2–3 days after V1.0.1

User-visible improvement:

- crowded fights are easier to read;
- the player can quickly understand which enemies target which player;
- simultaneous warnings are clearer and less confusing;
- lifecycle/retarget changes remain obvious.

### V1.1 — Broader useful warning coverage — target ~1 week from V1.0 baseline

User-visible improvement:

- noticeably more common dangerous situations produce validated live warnings;
- warning timing gives more practical reaction opportunity where evidence supports it;
- supported coverage is measured and explicit.

Memory attack/action-state work is valuable here only insofar as it increases trustworthy live warning coverage or timing.

### V1.2 — Multi-enemy danger priority — next ~1-week release

User-visible improvement:

- several simultaneous threats are presented with useful urgency/priority rather than as isolated unrelated warnings;
- the player can identify what matters most right now;
- stale/ambiguous aggregation fails closed.

### V1.3 — Reaction-oriented warning experience — next ~1-week release

User-visible improvement:

- warnings are steadier, less flickery and better timed for human reaction;
- movement/camera-scroll readability improves;
- real-play reaction usability is measured.

V1.3 is still a warning product; it does not claim safe-route guidance.

## 5. Assist Beta family — first movement guidance

Assist Beta is the qualitative transition from "what is dangerous" to "where should I move".

### Assist Beta 2.0 — First safe-direction guidance

User-visible promise:

- for a bounded supported set of current states, show a simple movement suggestion such as `↑ / ↓ / ↙ / → / HOLD`;
- guidance comes from current game state and validated search/policy output, not guessed geometry;
- uncertain states suppress the suggestion.

### Assist Beta 2.1 — Multi-enemy safe direction

User-visible improvement:

- guidance accounts for several simultaneous enemies/threats;
- wall/corner/conflicting-threat cases are considered;
- suggested direction seeks safer reachable space, not just distance from one enemy.

### Assist Beta 2.2 — Human-executable guidance

User-visible improvement:

- fewer rapid direction reversals;
- earlier usable prompts;
- less frame-tight behavior;
- when two routes are similarly safe, prefer the simpler route a human can actually perform.

Important metrics: lead time, direction stability, direction changes per second, and human follow-success rate.

## 6. Near-Zero RC family — prove outcome quality

Near-Zero RC is defined by measured damage reduction, not by adding UI widgets.

### Near-Zero RC 3.0 — Machine near-zero benchmark

- high no-damage success rate on a large held-out corpus of representative supported states;
- failures are bucketed, replayed and retrained;
- per-scene failure rates remain visible.

### Near-Zero RC 3.1 — Human-follow near-zero benchmark

User-visible promise:

- real players following the guidance show a major damage reduction versus baseline play;
- policy compensates for human reaction delay and execution variability;
- evaluation uses human-executable safety, not TAS/frame-perfect theoretical safety.

### Near-Zero RC 3.2 — Continuous-flow near-zero benchmark

User-visible promise:

- strong performance persists through long continuous gameplay, not only isolated savestate scenes;
- repeated encounters, stage/camera progression, mixed enemy groups and cumulative error are included;
- whole-stage / whole-run damage becomes a primary metric.

## 7. Production Assist — stable low/near-zero-damage product

Production Assist is reached only when the supported scope has durable outcome evidence.

The live user experience should remain simple:

- current danger;
- current safest human-executable direction / HOLD;
- clear urgency;
- low visual noise;
- confidence-aware suppression/fallback;
- measured damage reduction.

Do not promise universal literal zero damage until continuous real evidence proves it. Distinguish:

- supported-scope machine no-damage rate;
- human-follow no-damage / damage-reduction rate;
- uncovered/unknown situations.

## 8. Memory attack/action state stays in the product strategy

The future system should retain verified or raw-stable memory action/attack state as a strong observation feature.

It is useful for:

- earlier warning;
- training-state classification;
- policy disambiguation;
- failure diagnosis;
- faster learning.

However, future progress does not require manually converting every enemy attack into a hand-authored `T18`-style production rule before safe-route training can begin.

The intended future combination is:

`live RAM state + target + action/attack state + player/enemy geometry + outcome search/training -> safe movement policy`.

## 9. Training Farm is an R&D lane, not a user product version

The planned local headless multi-instance emulator/training farm exists to improve future Assist quality. It is not itself a user-facing release.

Expected internal milestones after V1.0.0 release:

- **Farm R0.1:** deterministic one-instance headless host with frame-step, independent input, RAM observation and save/load state;
- **Farm R0.2:** 2 -> 4 -> 8 -> 10 isolated workers benchmarked on the target local PC class;
- **Farm R0.3:** same-state savestate fork + automatic outcome scoring;
- **Farm R0.4:** automatic scene/corpus generation and `state -> action -> result` dataset;
- **Farm R0.5:** safe trajectory search / teacher policy;
- **Farm R0.6:** distilled real-time policy suitable for Assist Beta.

Hard sequencing rule:

**Do not start Training Farm implementation merely because an AI worker slot is empty while V1.0.0 release gates remain open.**

Before V1.0.0 ships, Training Farm work should remain parked unless it is explicitly required to unblock V1, which is not the normal case.

## 10. PM release-planning rule

Before assigning work, PM should ask:

1. Which current product version is being delivered?
2. What will the player visibly experience that is better when it ships?
3. Is the task necessary for that user-visible delta or a release safety gate?
4. Can the work fit into the next 2–3 day patch or ~7 day minor release without weakening safety?
5. If it is infrastructure-only, should it remain an internal stage rather than become a product-version milestone?

The default is to finish the current product version before starting implementation for the next major family.
