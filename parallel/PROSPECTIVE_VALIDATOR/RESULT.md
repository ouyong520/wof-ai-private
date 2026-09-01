# WOF Prospective Validator Framework — Result

## Verdict

**READY — repository-side stop condition reached.**

未来分析线产出候选 manifest 后，不需要再开发新的 prospective validator。候选文件可以直接交给：

`RUN_PROSPECTIVE_VALIDATOR.cmd candidate.json`

框架会复用现有 Browser Fleet / localhost CDP，独立附加真实 gstyphoon Worker，并按同一规则引擎完成前瞻统计。

## Delivered

- `validator.py`
  - manifest validation；
  - ordered `tail2 / pair / tail3 / triple`；
  - exact signature / `TM*` family / state predicates；
  - current-level predicates；
  - signal / strict / jitter / late / hardMiss / censored；
  - target / side / retarget evidence；
  - multi-room aggregation；
  - compact `wof-prospective-result-v1`；
  - WOF-052L recorder adapter；
  - discovery/prospective hard separation；
  - production promotion permanently disabled。

- `live_validator.py`
  - Browser Fleet manifest reuse；
  - localhost CDP fallback；
  - endpoint re-probe；
  - real `gstyphoon*.js` Worker discovery；
  - strict World 921031 full CPU-logical SHA-256 identity gate；
  - read-only live state matcher；
  - wrong attack hard miss；
  - no-ACTIVE timeout hard miss；
  - Worker/reload/stop pending signal censored；
  - independent room/session lifecycle；
  - rolling corpus/result output。

- `start_session.py`
  - freezes candidate SHA-256 + timestamp；
  - prevents pre-freeze discovery corpus from being relabelled as prospective；
  - detects manifest mutation after freeze。

- `prospective_run.py`
  - compatibility path that can freeze a candidate, reuse the existing WOF-052L Recorder unchanged, then validate fresh per-room files。

- `RUN_PROSPECTIVE_VALIDATOR.cmd`
  - candidate manifest is the only required argument for the generic live path；
  - owner-facing output is Simplified Chinese。

- schemas/examples/fixtures/tests
  - manifest schema；
  - unified corpus schema；
  - T18 BODY4728 ordered-tail expression example；
  - T23 A5888 BODY4936 tail3 example；
  - simple current-level predicate example；
  - prospective/discovery mock corpus。

## Evidence boundary preserved

WOF-051 remains authoritative that:

`S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736`

is forward-relevant but attack-ambiguous because it prospectively produced both A4704 and A4712.

Therefore the T18 example manifest in this framework is explicitly an **expression/test vector only**. It does not claim that the sample post-state is a discovered A4704-specific rule.

WOF-047's observed T23 A5888 BODY4936 ordered tail3 is represented as a research-only example and is not auto-promoted.

## Validation performed

Local repository-independent checks completed before write-back:

- Python compile: PASS
  - `validator.py`
  - `start_session.py`
  - `prospective_run.py`
  - `live_validator.py`

- Unit regression: **12/12 PASS**
  - T18 tail2 + prospective gate；
  - T23 tail3 + timer normalization；
  - current-level predicate；
  - discovery isolation；
  - wrong attack -> hard miss；
  - no ACTIVE timeout -> hard miss；
  - censored signal；
  - Recorder default discovery；
  - post-freeze Recorder room -> prospective；
  - pre-freeze Recorder room -> discovery；
  - frozen manifest mutation rejected；
  - production promotion rejected。

- Generated live Worker probe: `node --check` PASS。

- Mock CLI run: PASS；produced compact result with:
  - signal=2；
  - strict=1；
  - jitter=1；
  - hardMiss=0；
  - two prospective rooms；
  - verdict=`PROSPECTIVE_PASS_RESEARCH_ONLY`；
  - `productionPromotionAllowed=false`。

## Safety audit

No files outside `parallel/PROSPECTIVE_VALIDATOR/**` are changed by this lane.

Runtime policy remains:

- `readOnly=true`；
- `ramWrites=0`；
- `inputInjection=false`；
- `windowWorkerReplacement=false`；
- no gameplay input；
- no game RAM write；
- no Alpha modification；
- no PYLAUNCH modification；
- no Recorder modification；
- no Browser Fleet modification。

## Stop condition

Satisfied:

> future analysis line emits a candidate manifest -> fresh prospective validation needs only that candidate file, not a new validator implementation.

A real Windows/browser run is now evidence collection, not repository-side framework development.
