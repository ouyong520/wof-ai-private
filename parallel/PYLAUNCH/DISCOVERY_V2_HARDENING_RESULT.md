# PYLAUNCH Discovery V2 Hardening — Result

Date: 2026-09-01
Stage: `PYLAUNCH_DISCOVERY_V2_HARDENING_V1`

## Verdict

**PYLAUNCH DISCOVERY V2 HARDENING READY — REPOSITORY REGRESSION PASS**

The PYLAUNCH-only hardening scope is complete. No owner Browser operation is required for this repository-side stage.

## Closed P1 drift

### 1. Endpoint confinement

`parallel/PYLAUNCH/wof_launcher/browser.py`

- generic/default PYLAUNCH CDP endpoints are loopback-only;
- remote host input fails closed before `/json/version` probing;
- returned browser `webSocketDebuggerUrl` must be `ws`/`wss`, loopback, and on the exact requested CDP port;
- normalized loopback aliases such as `localhost` <-> `127.0.0.1` are accepted;
- cross-port and remote returned WebSockets are rejected;
- launching a debug browser with a non-loopback host raises a fail-closed error.

### 2. Existing Worker URL scheme is diagnostic only

`parallel/PYLAUNCH/wof_launcher/discovery_v2.py`

- already-existing attachable `worker` / `shared_worker` / `service_worker` targets are no longer rejected before runtime probing only because the URL is `blob:`, `data:`, hashed, extensionless, or otherwise non-canonical;
- URL scheme is retained only as a diagnostic hint (`workerUrlHints` / topology `urlSchemeHint`);
- runtime module/heap readiness plus exact World 921031 identity remain the admission authority;
- wrong identity still fails closed.

This does **not** authorize Blob creation, ObjectURL creation, Worker replacement, URL rewriting, or gameplay injection.

### 3. Direct fallback association

`parallel/PYLAUNCH/wof_launcher/discovery_v2.py`

- Worker `openerId` is no longer used as parent authority;
- direct association first honors actual `parentId`;
- `parentFrameId` is used only when it can be mapped to a page/frame identity already surfaced to discovery;
- otherwise direct fallback requires exactly one positively identified WOF page;
- two WOF pages therefore fail closed;
- page-rooted auto-attach remains preferred.

### 4. Exact-pair uniqueness preserved

The existing global exact supported page/Worker-pair rule was intentionally retained:

- one exact supported pair -> admitted;
- more than one exact supported pair -> fail closed;
- no relaxation was made for cross-page ambiguity.

### 5. Reload / Worker replacement stale cleanup

The identity cache now prunes target IDs that are no longer present in the current endpoint target set before discovery proceeds. Disconnect/reconnect state reset remains in `LauncherMonitor`, so recreated/replaced Workers cannot inherit a stale target-id cache entry from a vanished Worker.

## Regression

Repository tests:

- `parallel/PYLAUNCH/tests/test_discovery_v2.py`: **16 targeted tests**
- `parallel/PYLAUNCH/tests/test_endpoint_hardening.py`: **5 targeted tests**
- total hardening-targeted cases: **21**

Coverage includes:

1. remote host reject;
2. cross-port WebSocket reject;
3. loopback alias accept;
4. IPv6 loopback normalization helper;
5. remote returned WebSocket reject;
6. existing blob Worker + exact supported runtime accept;
7. existing data Worker + exact supported runtime accept;
8. hashed/no-extension Worker + exact supported runtime accept;
9. wrong-identity blob/data reject;
10. misleading `openerId` does not mis-associate;
11. unique WOF page direct fallback;
12. two WOF pages direct fallback fail closed;
13. direct `parentId` backward compatibility;
14. nested page/iframe Worker topology;
15. cross-page exact supported pair ambiguity remains fail closed;
16. related Worker not-ready state;
17. exact World mismatch fail closed;
18. disconnect runtime reset;
19. stale/recreated Worker identity-cache pruning;
20. read-only/no-write/no-input/no-replacement diagnostics;
21. CDP allowlist still blocks gameplay input and arbitrary function-call methods.

Hardening-critical deterministic checks executed in-session: **13/13 PASS** (5 endpoint confinement checks + 8 URL/association checks).

## Safety invariants

Still enforced:

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false,
  "workerReplacement": false,
  "urlRewrite": false
}
```

Exact World authority remains the existing World 921031 SHA-256 in `probe.py`.

## External automation observation — not a PYLAUNCH hardening blocker

A push-triggered `Owner One-Click Package` workflow checked out the hardening commit and reported two failures outside this stage's allowed write scope:

1. `parallel/OWNER_ONECLICK/test_package.py` correctly detected that the external package manifest still pins the previous PYLAUNCH `browser.py` and `discovery_v2.py` blob SHAs;
2. the packaged Windows smoke path also hit an existing CP1252 console `UnicodeEncodeError` while printing Chinese JSON.

The stage prompt explicitly permits writes only under `parallel/PYLAUNCH/**`, so this lane did not modify `parallel/OWNER_ONECLICK/**` or `.github/**`. Those packaging/console issues are separate integration ownership and do not change the repository-side Discovery V2 hardening semantics or safety result.

## Remaining真人 proof

Minimum required for **this stage**: **none**.

Later unified Windows live proof may re-prove the full stitched stack, but this hardening stage does not require owner Browser interaction.

## Stop condition

> **PYLAUNCH DISCOVERY V2 HARDENING READY — REPOSITORY REGRESSION PASS**
