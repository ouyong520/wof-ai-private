# PYLAUNCH Startup Attestation Fix Result

- Stage: `PYLAUNCH_STARTUP_ATTESTATION_FIX_V1`
- Production status: **FIX COMPLETE**
- QA status: **FRESH QA REQUIRED / NOT SELF-APPROVED**
- Write boundary used for product changes: `parallel/PYLAUNCH/**`

## Failure → fix mapping

| Observed failure | Production fix |
| --- | --- |
| `/json/version` without `Browser` was accepted by synthesizing `"Chromium"` | Removed the fallback. `Browser` is now mandatory and must be a non-empty, structurally valid supported Chrome/Chromium/Edge-family product string. |
| Unsupported/spoofed/malformed `Browser` metadata could pass the startup boundary | Added an explicit supported-product allowlist and structural validation. Missing, non-string, empty, unsupported, control-character, empty-version, extra-slash, and whitespace-containing version shapes fail closed. |
| `webSocketDebuggerUrl` only needed loopback + matching port, so `/devtools/page/...` could masquerade as the browser endpoint | Startup now requires a browser-level path exactly shaped as `/devtools/browser/<id>`. Page/worker paths, empty IDs, extra path components, query/fragment, or userinfo fail closed. |
| Endpoint confinement needed to remain local | Existing loopback confinement and exact configured-port matching remain. A remote configured host or remote returned websocket host fails closed; loopback aliases remain compatible. |
| A reconnect/new browser generation must not reuse stale accepted startup authority | `LauncherMonitor` performs fresh `/json/version` attestation on every monitor pass; reconnect invalidates the prior CDP/endpoint/identity authority; a failed fresh attestation invalidates any previous authority immediately. Even a stable websocket URL retains only metadata from the current fresh attestation. |
| Owner-facing rejection needed to be actionable | Attestation rejection diagnostics are Chinese-first and identify malformed JSON/object, missing/unsupported Browser metadata, or invalid browser-level websocket shape. |

## Changed files

- `parallel/PYLAUNCH/wof_launcher/browser.py`
  - fail-closed Browser metadata validation
  - strict browser-level websocket endpoint validation
  - diagnostic probe/wait helpers while preserving existing `probe_endpoint()` / `wait_for_endpoint()` callers
- `parallel/PYLAUNCH/wof_launcher/monitor.py`
  - fresh startup attestation handling
  - explicit stale authority invalidation on rejection/reconnect/replacement
  - Chinese-first startup rejection surfaced through runtime status
- `parallel/PYLAUNCH/tests/test_startup_attestation.py`
  - dedicated startup-attestation regression matrix
- `parallel/PYLAUNCH/STARTUP_ATTESTATION_FIX_RESULT.md`
  - this result and fresh-QA handoff

## Regression evidence

### Executed targeted regression

**22 / 22 passed** in an isolated executable harness using the committed startup-attestation production logic:

- 15 / 15 `test_startup_attestation.py` test methods passed.
- 5 / 5 existing endpoint-hardening cases passed.
- 2 / 2 adversarial startup-attestation repro cases from `parallel/PYLAUNCH_QA_IDENTITY_GENERATION/test_startup_attestation_regression.py` passed.
- Python compile checks for the modified startup-attestation modules/tests passed.

Covered cases include valid Chrome/Chromium/Edge, missing/unsupported/malformed Browser metadata, malformed/non-object `/json/version`, page-level and worker-level websocket masquerades, wrong port, remote host, websocket userinfo/query/extra path, Chinese-first rejection, and reconnect forcing a fresh attestation.

### Full PYLAUNCH suite boundary

The current `parallel/PYLAUNCH/tests/**` source inventory contains 53 test methods after adding the 15 startup-attestation tests. A full 53/53 run is **not claimed here**: the available GitHub connector exposes no safe dispatch path for the repository's `regression-orchestrator` at the current commit, its push trigger is outside this stage's allowed write boundary, and the execution container cannot clone GitHub directly. Fresh QA must run the complete PYLAUNCH suite independently.

### Automatic repository workflow observation

For current-stage push commit `dec33b6597e36466529ef36e3f756f2d8695936d`, Owner One-Click workflow run `33528154149` reported:

- `windows-oneclick`: **success** (all listed install/smoke/update/rollback steps passed).
- `integrity`: 13 tests executed, 11 passed and 2 errored because `parallel/OWNER_ONECLICK/package_manifest.json` still pins the pre-fix `browser.py` blob (`expected=e883030...`, current startup-fix blob `d6f7fa9...`).

That package-manifest freshness update is deliberately **not** performed here because `parallel/OWNER_ONECLICK/**` is explicitly outside this stage's write boundary. The failure is a downstream package-pin refresh signal, not a relaxation of the PYLAUNCH startup-attestation fix.

## Safety / read-only confirmation

- `parallel/PYLAUNCH/wof_launcher/cdp.py` remains at blob `def308bed2a5609be1da26505a15d621395b66aa`; the explicit read-only CDP allowlist was not changed.
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` remains at blob `ec9d27bfe26557a11187a23853893b898a3366d1`.
- `parallel/PYLAUNCH/wof_launcher/probe.py` remains at blob `789a6849b826b35542b22d56a4d2ca3628d285a1`.
- No RAM-write path was added.
- No input-injection path was added.
- No Worker replacement, URL rewrite, target substitution, or identity-policy relaxation was added.
- Existing identity-cache generation invalidation remains in force; startup rejection additionally invalidates the monitor's current authority.

## Fresh QA handoff

This implementation is intentionally held for independent QA. A fresh QA lane should, at minimum:

1. Re-run `parallel/PYLAUNCH_QA_IDENTITY_GENERATION/test_startup_attestation_regression.py` against the current production `parallel/PYLAUNCH/wof_launcher/browser.py`.
2. Run the complete `parallel/PYLAUNCH/tests/**` suite on a real repository checkout.
3. Reconfirm missing/unsupported/malformed Browser metadata and page/worker websocket masquerades fail closed.
4. Reconfirm valid Chrome/Chromium/Edge startup and reconnect/new-browser generations succeed only after a fresh attestation.
5. Reconfirm CDP remains read-only and existing discovery/identity-generation protections remain green.

**QA decision remains owned by the fresh QA lane. This FIX stage does not self-approve readiness.**
