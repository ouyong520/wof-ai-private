# WOF Alpha A1 — Reuse Matrix

Updated: 2026-09-01

| Asset | Decision | Alpha use |
|---|---|---|
| `wof_canvas_hud.js` | ADAPT | Reuse persistent WebGL `drawArrays` bridge, GL state snapshot/restore, reload-safe disposal, stale hiding and in-game load confirmation. Product copy uses a new `wof-alpha-v1` state schema and no research action routing. |
| `wof_hud_worker.js` | RESEARCH-ONLY | Useful proof of BroadcastChannel and threat-side presentation, but it depends on `WOFV4` research runtime and therefore cannot be in the Alpha production path. |
| `wof_future_danger_map_production_shadow_v22.js` | RESEARCH-ONLY / REFERENCE | Confirms Browser RAM reader, module discovery, target geometry and live-state publishing patterns. Its V22 provisional rules and empirical danger-map envelopes are not shipped. |
| WOF-038 → WOF-052R validators/coordinators | READ-ONLY REFERENCE | Exact predicates, target selector and retarget semantics are copied only for frozen rules. Mining, traces, JSON reports and experimental arms are excluded. |
| `wof_v4_install_once.js` | RESEARCH-ONLY | Rich danger/safe-path runtime is outside Alpha freeze and contains experimental/generalized product logic. Not loaded by Alpha. |
| Existing research resume/coordinator loaders | RETIRE FOR USER ALPHA PATH | Alpha gets one dedicated dual-context loader under `product/alpha/`. Research resume flow remains unchanged for research. |

## A1 conclusion

The proven direct WebGL HUD mechanism is reusable. The old HUD data producer and V4 danger runtime are not reusable as production execution because they mix research/generalized logic with user output. Alpha therefore keeps the HUD rendering mechanism but replaces the producer with a small fail-closed reader + frozen rule engine.
