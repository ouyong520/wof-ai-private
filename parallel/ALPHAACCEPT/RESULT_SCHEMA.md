# WOF Alpha — Browser Acceptance V2 Result Schema

Schema id:

`wof-alpha-browser-acceptance-v2`

The final result is a compact machine-readable object produced by the integrated driver + page collector. Owner-facing UI may show Chinese labels, but JSON keys and enum values remain stable English machine contracts.

## Canonical shape

```json
{
  "schema": "wof-alpha-browser-acceptance-v2",
  "result": "PASS — REAL BROWSER ACCEPTANCE V2",
  "release": "wof-alpha-rc3",
  "transportVersion": "wof-alpha-safe-transport-v1",
  "supportedBuild": "wof / Warriors of Fate (World 921031)",
  "goldenSha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62",
  "expectedIdentitySignature": "wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8",
  "startedAt": "ISO-8601",
  "finishedAt": "ISO-8601",
  "durationMs": 0,
  "integrationGate": {
    "status": "PASS",
    "productRegression": "PASS",
    "transportIntegrationTests": "PASS",
    "pylaunchTests": "PASS",
    "rc5NoWorkerReplacementRegression": "PASS",
    "rc4DiagSessionStaleRegression": "PASS",
    "exactStaleBoundary1500_1501": "PASS"
  },
  "launcher": {
    "browser": true,
    "wofPage": true,
    "worker": true,
    "wasmHeap": true,
    "world921031": true,
    "launcherIdentityGate": true
  },
  "pair": {
    "session": "32-lowercase-hex",
    "initialGeneration": 1,
    "initialNonce": "32-lowercase-hex",
    "reboundGeneration": 2,
    "reboundNonce": "32-lowercase-hex",
    "generationIncreased": true,
    "nonceChanged": true
  },
  "detectorIdentity": {
    "result": "PASS",
    "accepted": true,
    "signature": "wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8"
  },
  "firstCurrentPairState": {
    "result": "PASS",
    "observed": true,
    "seq": 1,
    "hudAuthorityOnlyAfterState": true
  },
  "noWarningState": {
    "result": "PASS",
    "observed": true
  },
  "stale1500": {
    "result": "PASS|OFFLINE_GATE_ONLY|FAIL|INCOMPLETE",
    "exactBoundaryAuthority": "offline integration regression",
    "exact1500_1501Gate": "PASS",
    "browserObservedSilentAfter1500": true
  },
  "diagImmediateClear": {
    "result": "PASS|NO_ACTIVE_WARNING|FAIL|INCOMPLETE",
    "currentPairDiagObserved": true,
    "warningCountBefore": 1,
    "warningCountNextTask": 0,
    "waitedForStaleTimeout": false
  },
  "rebind": {
    "result": "PASS",
    "freshPair": true,
    "freshStateObserved": true,
    "oldAuthorityInherited": false
  },
  "negativePairRejection": {
    "result": "PASS|NO_ACTIVE_WARNING|FAIL|INCOMPLETE",
    "oldGenerationStateRejected": true,
    "oldGenerationDiagRejected": true,
    "wrongNonceStateRejected": true,
    "wrongNonceDiagRejected": true
  },
  "warningSanity": {
    "result": "PASS|NOT_EXERCISED|FAIL",
    "observedWarningRows": 0,
    "allowedRuleIds": [
      "T18_5440_CYCLE_BODY7512_TM4_LEVEL_90",
      "T18_5424_CYCLE_BODY7520_TM4_LEVEL_90"
    ],
    "invalidRows": []
  },
  "gameplay": {
    "result": "PASS",
    "ownerConfirmedPlayableAtStart": true,
    "renderAliveAcrossStopRebind": true,
    "roomRemainedPlayable": true,
    "navigationInjected": false
  },
  "safety": {
    "result": "PASS",
    "readOnly": true,
    "ramWrites": 0,
    "inputInjection": false,
    "windowWorkerReplacement": false
  },
  "failures": [],
  "incomplete": [],
  "notes": []
}
```

## PASS calculation

`PASS — REAL BROWSER ACCEPTANCE V2` requires:

- every `integrationGate` item is `PASS`;
- every launcher Browser/page/Worker/WASM/World gate is true;
- exact current pair is valid;
- detector-local identity is accepted with the exact signature;
- first current-pair state is observed and is the first HUD authority;
- a fresh empty-warning state is observed;
- `stale1500.result` is `PASS` or `OFFLINE_GATE_ONLY`, but `exact1500_1501Gate` must still be `PASS`;
- current-pair diagnostic is observed and does not wait for stale timeout;
- rebind creates strictly greater generation + new nonce and fresh state;
- all four negative old/wrong-pair vectors are rejected;
- warning sanity is `PASS` or `NOT_EXERCISED`;
- gameplay result is `PASS`;
- safety is exactly `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `windowWorkerReplacement=false`;
- no mandatory field is incomplete.

`NO_ACTIVE_WARNING` is allowed only for the real-Browser visual-clear subcheck when no warning happens to be active. The offline warning->diag and old-pair rejection regressions remain mandatory PASS.

## FAIL

Use `FAIL — REAL BROWSER ACCEPTANCE V2` when a required invariant is actually observed to fail, including:

- wrong/ambiguous Worker or identity;
- current-pair metadata mismatch;
- detector-local identity missing/wrong;
- HUD accepts warning authority before first valid current-pair state;
- stale warning remains authoritative beyond the contract;
- current valid diag waits for stale timeout;
- rebind reuses generation/nonce or inherits old authority;
- old generation/wrong nonce can create or clear current authority;
- game render stops because Alpha transport fails;
- safety fields differ from the required values;
- invalid warning row is observed.

## INCOMPLETE

Use `INCOMPLETE — REAL BROWSER ACCEPTANCE V2` only for missing required real-Browser evidence where no invariant failure was observed.

Do not use INCOMPLETE to hide an offline integration failure.

## BLOCKED

Use `BLOCKED — TRANSPORT INTEGRATION NOT READY` before the integration authorization gate opens.

## Release boundary

No result in this schema declares Alpha released. PM/release ownership consumes this evidence separately.
