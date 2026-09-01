# Runtime Speed Probe Result JSON

Schema version: `wof-runtime-speed-result-v1`

The owner-facing output is one compact JSON object. The preferred producer is `run_probe.py`; `analyze.py` can also produce the same core schema when invoked directly on paired captures.

## Core fields

```json
{
  "schemaVersion": "wof-runtime-speed-result-v1",
  "analyzerVersion": "wof-runtime-speed-analyzer-v1",
  "orchestratorVersion": "wof-runtime-speed-one-shot-v1",
  "verdict": "SAME_SIMULATION_SPEED_DIFFERENT_FEEL",
  "confidence": "HIGH",
  "measurementMode": "monotonic-counter",
  "primaryHeartbeat": {
    "cpsAddress": "0xFF1234",
    "width": 1,
    "direction": "+",
    "winkawaksRateHz": 59.63,
    "browserRateHz": 59.64,
    "primaryPairRatio": 0.9998
  },
  "speedRatio": 0.9998,
  "ratioDeltaPct": -0.02,
  "ratioConsensus": {
    "commonCandidateCount": 4,
    "agreeingCandidateCount": 4,
    "medianRelativeSpreadPct": 0.1
  },
  "winkawaks": {
    "sampleCount": 1800,
    "captureHz": 120.0,
    "spanMs": 14991.0,
    "primaryRateHz": 59.63,
    "nearNominal59_6374": true
  },
  "browser": {
    "sampleCount": 1875,
    "captureHz": 125.0,
    "spanMs": 14992.0,
    "primaryRateHz": 59.64,
    "nearNominal59_6374": true
  },
  "nominalCps1Hz": 59.637405,
  "nominalReferenceApplicable": true,
  "planDirectionConflict": false,
  "evidence": [],
  "captures": {
    "winkawaks": "parallel/RUNTIMESPEED_PROBE/out/local_speed_capture.wofsp.gz",
    "browser": "parallel/RUNTIMESPEED_PROBE/out/browser_speed_capture.wofsp.gz"
  },
  "readOnly": true,
  "writesGameMemory": false,
  "inputInjection": false
}
```

Numeric values above are illustrative only; they are not a runtime measurement.

## Definitions

### `measurementMode`

- `monotonic-counter` — preferred: same logical CPS U8/U16 counter was stable in both captures.
- `periodic-heartbeat` — fallback: no literal common monotonic counter survived, but a regular autonomous same-address heartbeat was found in the already-recorded paired full-RAM data.
- `none` — no defensible common heartbeat.

### `primaryHeartbeat`

The highest-quality representative member of the agreeing common-candidate cluster.

- `cpsAddress` is a logical CPS address in `0xFF0000..0xFFFFFF`.
- `width` is 1 for U8 or 2 for big-endian U16.
- `direction` is `+` or `-` for monotonic counters; it may be null/absent for periodic fallback.
- rates are autonomous game progression events per measured host second, **not capture samples per second**.

### `speedRatio`

Always defined as:

```text
WinKawaks game-progression rate / Browser game-progression rate
```

Therefore:

- `1.00` means equal average simulation progression;
- `>1.00` means WinKawaks game state progressed faster;
- `<1.00` means Browser game state progressed faster.

### `ratioConsensus`

Diagnostics for common candidate agreement:

- `commonCandidateCount` — all qualifying same-address candidates shared by both runtimes;
- `agreeingCandidateCount` — candidates inside the selected ratio cluster;
- `medianRelativeSpreadPct` — median relative distance from the cluster's consensus ratio.

### Runtime blocks

`winkawaks` and `browser` deliberately expose both:

- `captureHz` — external observation/read cadence;
- `primaryRateHz` — selected in-game heartbeat progression rate.

These are different clocks and must not be conflated.

## Verdict values

Possible principal values:

- `SAME_SIMULATION_SPEED_DIFFERENT_FEEL`
- `WINKAWAKS_FASTER`
- `BROWSER_SLOWER`
- `WINKAWAKS_FASTER_THAN_BROWSER_NOMINAL_ATTRIBUTION_UNPROVEN`
- `WINKAWAKS_SLOWER`
- `BROWSER_FASTER`
- `BROWSER_FASTER_THAN_WINKAWAKS_NOMINAL_ATTRIBUTION_UNPROVEN`
- `INCONCLUSIVE_1_5_TO_3_PERCENT`
- `INCONCLUSIVE_MEASUREMENT_QUALITY`
- `INCONCLUSIVE_NO_COMMON_HEARTBEAT`
- `INCONCLUSIVE_TOOL_ERROR`

The completed measurement plan defines `speedRatio = WinKawaks / Browser` but also contains one directionally inconsistent prose rule for `speedRatio <= 0.97`. The analyzer does not silently reverse the ratio definition. When it enters that below-0.97 branch it reports the mathematically measured direction and sets:

```json
"planDirectionConflict": true
```

## Confidence

- `HIGH` — strong capture spans/cadence and multiple agreeing common monotonic counters with tight ratio spread.
- `MEDIUM` — usable stable common heartbeat but fewer corroborating candidates or weaker capture diagnostics.
- `LOW` — not sufficient for a directional speed conclusion; verdict remains inconclusive.

## Safety invariants

Successful and error results both carry:

```json
{
  "readOnly": true,
  "writesGameMemory": false,
  "inputInjection": false
}
```

No result field represents emulator speed tuning, because this tooling does not alter emulator or Browser timing settings.