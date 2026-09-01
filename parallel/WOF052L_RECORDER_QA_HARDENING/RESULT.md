# WOF-052L Recorder Discovery V2 Hardening — Fresh Independent QA Result

stageId: `WOF052L_RECORDER_HARDENING_QA_V1`

## Final stop condition

`BLOCKED — WOF052L RECORDER HARDENING QA — P0 live-live shared Worker transition can continue evidence polling before the next live-topology audit; P1 recreated Worker can inherit stale cached World identity authority`

This is an independent QA failure result. Per the start prompt, this stage does **not** modify Recorder implementation; fixes must be handled by a fresh fix stage/chat.

## Scope / implementation under review

Validated current implementation blobs:

- `parallel/WOF052L_RECORDER/hardening_v2.py` — blob `4268d39f62d62a624966e7d9fd4afda65f6e94c0`
- `parallel/WOF052L_RECORDER/discovery_v2_sync.py` — blob `ddde07ed550110058ef1cae1ed62ae873382c462`
- `parallel/WOF052L_RECORDER/recorder.py` — blob `9552d168534f3b742e7390597ff07ea5cfcaeaa2`

QA-only adversarial fixture:

- `parallel/WOF052L_RECORDER_QA_HARDENING/test_adversarial_hardening.py`
- fixture commit: `c4e3914ff848e894a03222c6ec7a024fb5b224e9`

The fixture includes the two mandatory fresh adversarial families required by the prompt:

1. shared-Worker mid-capture transition;
2. endpoint websocket drift on an explicit CDP port.

It also adds a recreated-Worker stale-identity authority adversarial case.

## P0 blocker — live/live cross-page shared Worker transition is not fail-closed before evidence polling

### Requirement

If an exact Worker becomes associated with multiple pages during capture, affected live room(s) must finalize **before later evidence polling**.

### Current path

The hardened `RecorderManager.discover()` computes all current `live_page_ids`, then performs a full audit of those live pages only when:

`now - _wof052l_last_live_topology_audit >= 10.0`

Before that 10-second audit window expires, discovery calls `discover_candidates(..., skip_page_ids=live_page_ids)`.

The normal Recorder loop is ordered as:

`discover(now)` -> `poll_rooms(now)`

Therefore, when two pages are already live and a topology transition makes page B attach to the exact Worker target already authoritative for page A during the skipped interval, neither live page is scanned in that discovery cycle. The cross-page relation graph never receives the new page-B relation, no affected room is finalized, and the immediately following `poll_rooms(now)` remains eligible to collect evidence from the still-live rooms.

### Fresh adversarial fixture

`MidCaptureSharedWorkerTransitionAdversarialTests.test_two_live_pages_shared_worker_transition_must_finalize_before_evidence_polling`

Fixture state:

- live room A: exact Worker `shared` -> page `p1`;
- live room B: Worker `other` -> page `p2`;
- topology drifts so `p2` is now also related to exact Worker `shared`;
- last live topology audit = 95.0;
- current discovery time = 100.0, so only 5 seconds have elapsed;
- the fixture exposes `shared -> p2` if and only if `p2` is actually scanned.

Required outcome: affected live rooms finalize before the next evidence poll.

Current implementation outcome by direct source-path evaluation: the live-page skip hides the transition for this cycle, no finalize occurs, and polling proceeds with the live rooms still admitted.

### Severity

**P0** — this breaks the explicit fail-closed cross-room evidence isolation invariant and permits evidence polling after a shared-Worker ambiguity has already appeared but before the delayed live-page audit sees it.

## P1 blocker — recreated Worker can inherit stale cached World identity authority

### Requirement

Reloaded/recreated Workers must not inherit stale authority. Exact World 921031 identity must remain authoritative for each current Worker runtime.

### Current path

`discovery_v2_sync._probe_session()` caches identity in `manager._wof052l_identity_cache` keyed only by `targetId`.

On a later probe for the same `targetId`, if the cached object is a dict, the identity probe is skipped and the cached result is reused. No lifecycle generation/session key is part of the cache key, and no invalidation was found on Worker recreation/reload in the reviewed path.

### Fresh adversarial fixture

`StaleIdentityAuthorityAdversarialTests.test_recreated_worker_with_reused_target_id_must_not_inherit_cached_world_authority`

Fixture sequence:

1. Worker runtime with targetId `worker-reused` returns the exact golden World SHA and is cached.
2. Runtime is recreated but the adversarial topology reuses the same targetId.
3. Replacement runtime would return the wrong SHA (`00...00`) if identity-probed.
4. Safety requirement demands a fresh identity probe and `wrong-identity` rejection.

Current implementation outcome by direct source-path evaluation: the cached golden identity is reused; the replacement session's identity probe is not called and the replacement is treated as supported.

### Severity

**P1** — stale authorization can survive a Worker lifecycle change, violating the explicit no-stale-authority requirement and weakening exact World identity admission.

## Mandatory endpoint-drift fixture

`EndpointDriftAdversarialTests.test_explicit_endpoint_that_drifts_cross_port_must_fail_closed_without_fallover`

The fixture independently models an explicit `--cdp-port 9444` endpoint whose `/json/version` initially returns port 9444 and later drifts to a websocket on another port. It asserts:

- the drifted endpoint is rejected;
- only port 9444 is probed;
- no fallback to another common CDP port occurs;
- diagnostic reason is `returned-websocket-cross-port`;
- safety diagnostics remain `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

Source inspection of the current endpoint guard is consistent with these assertions; this fixture is not a blocker.

## Existing implementation evidence reviewed, but not accepted as independent QA proof

The implementation result reports a 21/21 hardening regression plus Windows UTF-8 owner-entry checks. Those results were reviewed for context only. This QA did not treat green implementation CI as sufficient because the start prompt explicitly requires fresh adversarial construction.

In particular, the existing implementation mid-capture ambiguity test directly exercises the ambiguity helper with a live relation plus a new candidate; it does not exercise the 10-second live-page audit skip in the real hardened `discover()` path. The existing reload/replacement test uses fresh managers/target IDs and therefore does not cover stale cached identity authority across a reused targetId lifecycle.

## Write-boundary / safety audit

This QA stage changed only:

- `parallel/WOF052L_RECORDER_QA_HARDENING/**`
- `parallel/PM/STAGE_CLAIMS/WOF052L_RECORDER_HARDENING_QA_V1.json`

No Recorder implementation, Alpha, PYLAUNCH, game RAM, game input, or Worker replacement behavior was modified.

Safety contract remains the intended invariant:

- exact World SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no `window.Worker` replacement

## Owner intervention

`你现在需要操作：NO`

Both blockers are repository-side and must be handled by a fresh fix stage before long-capture QA retest.

## Final

**BLOCKED. Do not advance this Recorder hardening lane to long-capture QA retest yet.**

`BLOCKED — WOF052L RECORDER HARDENING QA — P0 live-live shared Worker transition can continue evidence polling before the next live-topology audit; P1 recreated Worker can inherit stale cached World identity authority`
