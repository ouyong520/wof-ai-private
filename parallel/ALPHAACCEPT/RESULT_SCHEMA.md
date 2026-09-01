# WOF Alpha RC3 — Browser Acceptance Result Schema

Schema id:

`wof-alpha-browser-acceptance-v1`

The support helper publishes the final object as:

- page UI JSON;
- `window.__WOF_ALPHA_ACCEPTANCE_RESULT`;
- one Console line prefixed `WOF_ALPHA_ACCEPTANCE_RESULT` for engineering capture if needed.

The owner should not need to inspect the Console.

## Canonical shape

```json
{
  "schema": "wof-alpha-browser-acceptance-v1",
  "result": "PASS — REAL BROWSER ACCEPTANCE",
  "release": "wof-alpha-rc3",
  "supportedBuild": "wof / Warriors of Fate (World 921031)",
  "goldenSha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62",
  "expectedIdentitySignature": "wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8",
  "startedAt": "ISO-8601",
  "finishedAt": "ISO-8601",
  "durationMs": 0,
  "qaGate": {
    "requiredExternalVerdict": "PASS — READY FOR ONE REAL BROWSER ACCEPTANCE",
    "checkedByHelper": false
  },
  "checks": {
    "bootstrap": {
      "result": "PASS",
      "workerIntercepted": true,
      "hudLoaded": true,
      "primarySession": "hex-session",
      "pageSessionMatches": true,
      "hudSessionMatches": true,
      "connected": true
    },
    "identity": {
      "result": "PASS",
      "signatureObserved": "wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8",
      "fullDigestAuthority": "product exact 1 MiB CPU-logical SHA-256 gate"
    },
    "runtimeDiagnostics": {
      "result": "PASS",
      "count": 0,
      "items": []
    },
    "webglHud": {
      "result": "PASS",
      "drawHooked": true,
      "stateSamples": 0,
      "samplesWithActualHudDraw": 0,
      "stateMismatchCount": 0,
      "stateMismatches": [],
      "hudCallbackP95Ms": 0,
      "hudCallbackMaxMs": 0,
      "hudLastError": null
    },
    "transport": {
      "result": "PASS",
      "primarySession": "P",
      "primaryChannel": "CP",
      "auxInitialSession": "A1",
      "auxInitialChannel": "CA1",
      "auxReloadSession": "A2",
      "auxReloadChannel": "CA2",
      "initialIsolation": true,
      "reloadCreatedFreshPairing": true,
      "primaryStayedConnected": true
    },
    "legacyHud": {
      "result": "PASS|NOT_APPLICABLE",
      "legacySeenBeforeAlpha": false,
      "alphaReportsResearchHudDisposed": true
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
    "performance": {
      "result": "PASS",
      "observationMs": 6000,
      "stateMessages": 0,
      "stateRateHz": 0,
      "gameDrawsDelta": 0,
      "hudCallbacksDelta": 0,
      "connectedAtEnd": true,
      "automaticLimits": {
        "minimumHudCallbackSamples": 10,
        "hudCallbackP95MsMax": 16,
        "hudCallbackSingleMaxMs": 50,
        "requiresGameDrawAdvance": true,
        "requiresDetectorContinuity": true
      }
    },
    "safetyContract": {
      "result": "EXTERNAL_QA_PRECONDITION",
      "readOnly": true,
      "ramWrites": 0,
      "inputInjection": false,
      "note": "Fresh independent QA/static source inspection is authoritative; support helper itself performs no RAM or gameplay-input access."
    }
  },
  "failures": [],
  "notes": []
}
```

## Result calculation

### `PASS — REAL BROWSER ACCEPTANCE`

Required when all of these are true:

- `bootstrap.result === 'PASS'`;
- `identity.result === 'PASS'`;
- `runtimeDiagnostics.result === 'PASS'`;
- `webglHud.result === 'PASS'`;
- `transport.result === 'PASS'`;
- `legacyHud.result` is `PASS` or `NOT_APPLICABLE`;
- `warningSanity.result` is `PASS` or `NOT_EXERCISED`;
- `performance.result === 'PASS'`;
- no required check is incomplete.

### `FAIL — REAL BROWSER ACCEPTANCE`

Use when a required invariant was actually observed to fail, including:

- bootstrap ran but did not intercept/load/pair correctly;
- wrong/missing live accepted identity signature after detector connection;
- any paired runtime diagnostic/error during the run;
- WebGL state mismatch around an actual HUD callback;
- HUD draw hook/error invariant fails;
- cross-tab sessions/channels collide or reload does not create a fresh pairing;
- naturally observed warning is outside the RC3 two-rule/current-target/current-side contract;
- catastrophic-overhead guard fails while the test environment otherwise ran normally.

### `INCOMPLETE — REAL BROWSER ACCEPTANCE`

Use only when a required Browser observation could not be obtained, for example:

- popup blocked;
- auxiliary page timeout;
- helper was run on the wrong page;
- insufficient actual HUD-draw samples because the helper was installed too late or the game never rendered.

`NOT_EXERCISED` is allowed only for naturally absent active T18 warning rows. It must never be used to hide a required infrastructure check.

## Release boundary

This JSON is Browser acceptance evidence only. No value in this schema means `Alpha released` or authorizes bypassing the fresh independent QA gate.
