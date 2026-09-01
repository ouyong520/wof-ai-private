# Alpha Safe Transport Reference Implementation — Fresh Independent QA Result

Stage: `ALPHA_TRANSPORT_REFERENCE_QA_V1`  
Status: **BLOCKED**

## Stop condition

**BLOCKER — stale in-flight detector completion can be relabeled as the new pair after rebind**

Required fresh-fix ownership: **new `ALPHA_TRANSPORT_IMPL` fix stage**. This QA lane must not modify the implementation under its write-scope contract.

## Independent adversarial finding

The frozen 67-vector baseline contains Worker replacement/reconnect coverage, but the reference worker runtime models detector work with a single mutable `inFlight` boolean and a mutable current `pair`.

Adversarial sequence:

1. Install pair generation 1 and start a detector tick; leave its asynchronous work unresolved.
2. Reinstall/rebind to pair generation 2. `install()` calls `stop()`, clears `inFlight`, then mutates `this.pair` to generation 2.
3. Start a legitimate generation-2 tick, setting the same shared `inFlight` boolean.
4. Let the unresolved generation-1 callback complete and call `finishTick()`.
5. `finishTick()` has no immutable tick token / epoch / pair argument. It consumes the generation-2 `inFlight` flag and creates a state envelope from the *current* mutable pair, so the stale generation-1 warning is stamped with generation 2 + the new nonce.
6. `PageTransportAuthority` accepts that envelope as current-pair authority. The real generation-2 completion then finds `inFlight=false` and throws `no detector tick in flight`.

Observed result from the repository-code reproduction:

```text
leakedPairGeneration=2
leakedPairNonce=22222222222222222222222222222222
acceptedByNewPair=true
visibleWarningsOnPair2=1
workerInFlightAfterStaleCompletion=false
freshCompletionError="no detector tick in flight"
readOnly=true
ramWrites=0
inputInjection=false
```

This is fail-safe with respect to writes/input, but it is **not** fail-closed for warning authority: stale old-generation detector evidence can become authoritative on the freshly rebound pair.

## Contract conflict

This violates the required independent-QA boundaries:

- Worker replacement/reload must reset old authority immediately;
- reconnect/rebind must not revive an old generation;
- one detector tick may be in flight without stale completion stealing the new slot;
- stale warning/retarget evidence must not survive onto a newly authoritative pair/session.

It also exposes a gap in the frozen catalog's V44/V55 lifecycle coverage: those vectors revoke the runtime while no unresolved pre-rebind completion races the first new-generation tick.

## Reproduction artifact

`parallel/ALPHA_TRANSPORT_IMPL_QA/adversarial_reference_qa.mjs`

The test imports the actual reference implementation and deterministically models the race without Owner Browser/WOF involvement.

## Required fix

A fresh implementation fix stage must make detector completions generation-safe. Acceptable semantics are:

- every started tick captures an immutable token containing at least runtime epoch + session + pair generation + pair nonce, or an equivalent unique tick identity;
- completion is ignored unless that captured token still matches the currently authoritative runtime/pair;
- an old/stale completion must never consume or clear the new generation's in-flight slot;
- add a regression where generation-1 work remains unresolved across reinstall/rebind, generation-2 starts a tick, then generation-1 returns first;
- after the fix, rerun this independent adversarial case and then rerun the frozen 67-vector catalog.

## Baseline status

The existing reference result remains `67/67 PASS`, but this fresh QA did **not** count that as sufficient evidence. Per the start prompt, the fresh 67-vector rerun is after adversarial validation; this stage reached its permitted precise-blocker stop condition first.

## Owner action

`NO`
