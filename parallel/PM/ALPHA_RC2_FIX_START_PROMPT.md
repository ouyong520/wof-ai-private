# WOF PRODUCT / ALPHA RC2 FIX — START PROMPT

You own the next bounded WOF Alpha repair stage after independent QA blocked `wof-alpha-rc1`.

Repositories:
- `ouyong520/wof-ai-private`
- `ouyong520/wof-winkawaks-bridge` only for read-only provenance/evidence when needed.

Before changing anything, reread current GitHub state, especially:
- `parallel/ALPHAQA/AUDIT_STATUS.md`
- `parallel/ALPHAQA/FINDINGS.md`
- `parallel/ALPHAQA/ACCEPTANCE_CHECKLIST.md`
- `parallel/ALPHAQA/independent_qa.mjs`
- `parallel/PM/ALPHA_FREEZE_SPEC.md`
- `parallel/PM/RELEASE_READINESS.md`
- current support-audit outputs under `parallel/ALPHAID/**`, `parallel/ALPHALIFE/**`, `parallel/ALPHABOOT/**` when they appear
- all current `product/alpha/**`
- exact Browser evidence cited by the six frozen rules.

## Role

This is a PRODUCT FIX stage, not a research lane.

Your only goal is to turn RC1 into an RC2 candidate that closes **every currently open Alpha QA P0/P1 blocker** without widening the frozen rule set or weakening fail-closed behavior.

The blocker list is live: always reread `parallel/ALPHAQA/FINDINGS.md` and `AUDIT_STATUS.md`. Do not assume an older four-item snapshot is complete.

You may modify `product/alpha/**` as the implementation owner for this stage. Treat `parallel/ALPHAQA/**` and support-audit lanes as read-only evidence; do not rewrite QA findings to make them pass.

## Mandatory blocker families currently known

### F1 — ALPHAQA-001 P0 — positive runtime/build identity

RC1 recognizes only a compatible memory/layout shape and then labels it as the supported `wofr1` build. That is not enough.

Required outcome:
- warnings remain disabled unless the runtime positively distinguishes the declared supported Browser game/build/revision from structurally compatible unknown/lookalike layouts;
- do not synthesize a supported-build signature from layout-only checks;
- first exhaust existing GitHub Browser evidence/history and consume `parallel/ALPHAID/**` recommendations when available;
- if no retained evidence can positively distinguish the build, fail closed and document the exact minimal real-Browser evidence needed rather than guessing;
- add a negative regression for a layout-compatible unknown/unsupported revision.

Do not copy WinKawaks numeric addresses into Browser/WASM as identity proof.

### F2 — ALPHAQA-002 P1 — same-type slot replacement watch inheritance

Required outcome:
- a warning from enemy episode A cannot transfer to replacement enemy episode B merely because the same physical slot and type are reused;
- consume `parallel/ALPHALIFE/**` recommendations when available;
- use only Browser-proven continuity/reset evidence or a conservative invalidation policy that cannot create a false inherited warning;
- do not import unproven WinKawaks-local instance/profile offsets;
- add adversarial regression reproducing same-type same-slot replacement without an observed null/type-change sample.

Prefer silence/reset over preserving a warning across uncertain continuity.

### F3 — ALPHAQA-003 P1 — simultaneous warning presentation

Required outcome:
- HUD must not silently drop valid active warnings after `warnings[0]`;
- use a compact user-facing aggregation or another conservative presentation that indicates all currently relevant threats/targets/sides;
- preserve game readability and avoid turning this into Beta-level UI redesign;
- add regression or deterministic rendering-state coverage for multiple simultaneous warnings.

### F4 — ALPHAQA-004 P1 — normal-user bootstrap

Required outcome:
- supported Alpha load path must no longer require the user to manually find/select the live `gstyphoon.js` Worker console and then separately load the top-page console;
- consume `parallel/ALPHABOOT/**` recommendations when available;
- provide one bounded user bootstrap/install path suitable for an Alpha user;
- researcher-only DevTools execution-context knowledge is not an acceptable final Alpha path;
- if Browser architecture imposes a hard limitation, prove it from current code/runtime and produce the smallest safe user operation possible; do not simply relabel the two-console workflow as user-friendly.

### F5 — ALPHAQA-005 P0 — cross-session / cross-tab warning provenance

RC1 uses a fixed origin-global `BroadcastChannel`, so another same-origin Alpha game/runtime can feed the wrong HUD.

Required outcome:
- each HUD must accept state/diagnostics only from its intended paired runtime/page session;
- two same-origin game tabs must remain isolated;
- reinstall/restart must establish a clean pairing and cannot inherit another session;
- use a per-session channel, unpredictable pairing nonce/session id, or equivalent robust binding;
- add deterministic foreign-session/two-producer regression proving unrelated messages are ignored;
- preserve stale fail-closed behavior.

### F6 — ALPHAQA-006 P1 — legacy research HUD residue

RC1 hides a prior research `WOFHUD` but may leave its keyboard listener, BroadcastChannel and owned resources alive.

Required outcome:
- Alpha takeover must safely dispose/tear down a recognized legacy project HUD rather than only hiding it;
- preserve the persistent native WebGL bridge needed by Alpha;
- remove legacy keyboard handlers/channel consumers/owned overlay resources;
- add regression or fixture proving legacy teardown occurs and does not destroy the safe native GL hook.

## Preserve RC1 safety and scope

Must remain true:
- exactly the six PM-frozen production rules unless a rule is removed for safety;
- T16 B4 stays danger-only, never A6432-exclusive;
- T18 BODY4728/A4/B2/TM1 stays excluded as A4704-specific;
- no T23/T24/discovery/local candidates enter production;
- UNKNOWN/invalid target stays silent;
- target is reread live and side recomputed;
- no game RAM writes;
- no gameplay input injection/autoplay;
- release runtime remains isolated from WOF-0xx research coordinators;
- unsupported/uncertain runtime fails closed.

## Required outputs

Update/create under `product/alpha/**` as appropriate:
- implementation fixes;
- machine-readable manifest/version if behavior or identity contract changes;
- release regression covering every current QA P0/P1 blocker;
- `ALPHA_RC2_REPORT.md` with exact status of every blocker;
- minimal user load/install instructions.

Do not mark RC2 ready for human Browser acceptance merely because the original four findings are fixed. It must address the **latest complete open P0/P1 set** in QA.

## Stop condition

Stop only when one of these is true:

A. `wof-alpha-rc2` candidate exists and all currently known RC1 QA P0/P1 blockers are addressed with concrete code/tests, ready for a **fresh independent QA retest**; or

B. one blocker cannot be closed from retained GitHub evidence without a precise real-Browser operation, in which case document exactly the smallest required operator step and why no safe offline implementation can replace it.

Do not ask the owner to choose technical solutions. Do not start new attack discovery, broad Collector capture, GEO/EFIELD/RAWMINE work, or expand the production rule set. Use GitHub as the coordination bus and continue until RC2 is ready for QA retest or a single precise human-gated blocker remains.
