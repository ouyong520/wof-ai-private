# Recommended Alpha RC2 Runtime Identity Guard

Date: 2026-09-01
Audience: Alpha RC2 implementation owner
This document is advisory only. This ALPHAID audit does **not** modify `product/alpha/**`.

## 1. Required principle

Warnings must remain disabled until the Browser runtime positively proves the supported **68000 program identity**.

Do not treat any of these as sufficient identity:

- expected RAM addresses;
- expected player self indexes;
- emulator module object name;
- RAM pointer/heap bounds;
- reset vector alone;
- a few dispatch/code addresses;
- page title, ROM filename, URL, query parameter, or wrapper label.

Those may be compatibility checks or locator hints only.

## 2. Positive identity primitive

After the one-time canonical Browser binding in `MINIMAL_BROWSER_PROBE.md`, persist exactly one expected value in the Alpha implementation:

```text
expectedMainCpuLogicalSha256 = <64 lowercase hex chars from accepted ALPHAID probe>
```

Runtime procedure:

1. find the emulator module/heap as today;
2. perform the existing layout sanity checks;
3. locate exactly one valid 1 MiB 68000 ROM candidate using the existing vector/dispatch locator semantics;
4. normalize adjacent-byte-pair storage to CPU-logical byte order;
5. SHA-256 all `0x100000` logical program bytes;
6. compare exact lowercase digest equality with `expectedMainCpuLogicalSha256`;
7. enable warning evaluation only if **all** layout checks and the ROM digest check pass.

The content digest is authoritative. Vector/dispatch checks are only used to find the bytes efficiently and reject obviously invalid candidates earlier.

## 3. Suggested identity result shape

The product owner may adapt naming, but the semantic contract should be equivalent to:

```js
{
  ok: true,
  identity: {
    game: 'wof',
    set: 'wofr1',
    description: 'Warriors of Fate (World 921002)',
    kind: 'maincpu-logical-sha256-v1',
    logicalBytes: 0x100000,
    sha256: '<golden 64-hex digest>',
    canonicalBinding: 'tk2e_23b.8f + tk2e_22b.7f'
  },
  layout: {
    moduleOk: true,
    ramBaseOk: true,
    ramWithinHeap: true,
    selfIndexes: [0, 4, 8]
  }
}
```

A safe emitted signature would be derived **after** digest equality, for example:

```text
wofr1-world-921002-maincpu-sha256-v1:<first-16-hex>
```

The human-readable string is diagnostic. The digest comparison is the proof.

## 4. Fail-closed state machine

Recommended states:

```text
IDENTITY_PENDING
  -> IDENTITY_ACCEPTED
  -> warnings may initialize

IDENTITY_PENDING
  -> IDENTITY_REJECTED
  -> warnings permanently disabled for this loader instance
```

Rules:

- no warnings while hashing is pending;
- timeout is rejection, not layout fallback;
- exception is rejection;
- missing Web Crypto/hash implementation is rejection;
- zero or multiple valid ROM candidates is rejection unless the locator is explicitly made deterministic and the selected candidate's full digest matches;
- digest mismatch is rejection;
- no retry loop that starts warnings before identity succeeds;
- a later RAM-layout check cannot override a ROM mismatch.

If the product supports hot-loading a new ROM without reloading the worker, identity must be invalidated and recomputed before warnings resume. If the emulator lifecycle guarantees a worker reload for each ROM, once-per-worker startup hashing is sufficient.

## 5. Byte normalization

Prior Browser ROM tooling already supports direct and adjacent-pair-swapped heap representations.

For a located heap base `B` and a locator result `pairSwap`:

```js
logical[i] = HEAPU8[B + (pairSwap ? (i ^ 1) : i)]
```

for `0 <= i < 0x100000`.

Hash **logical** bytes, not the raw heap slice, so the expected SHA-256 is independent of emulator storage representation.

Do not bake the heap base, RAM pointer, or historical small handler-address delta into the digest contract.

## 6. Performance

One SHA-256 over 1 MiB at startup is small relative to emulator load and should not be repeated on every polling tick.

Recommended behavior:

- allocate/normalize once;
- hash once;
- discard temporary 1 MiB buffer after comparison;
- cache only the accepted identity result and digest string.

If the implementation uses `crypto.subtle.digest`, identity validation becomes asynchronous. The loader must explicitly await acceptance before installing/enabling warnings.

## 7. Canonical binding provenance

The golden Browser SHA-256 must come only from a probe result that first proves the live Browser halves match the canonical `wofr1` program ROM metadata:

```text
tk2e_23b.8f
SHA-1 19e09ad6f9edc7997b030cddfe1d9c96d88135f2
CRC32 11fb2ed1
size   0x80000

tk2e_22b.7f
SHA-1 9fb8ae06856fe115addfb6794c28978a4f6716ec
CRC32 479b3f24
size   0x80000
```

Do not populate the golden SHA-256 from:

- a guessed concatenation of published SHA-1 strings;
- an offline WinKawaks address/value assumption;
- another WOF revision;
- a Browser run whose canonical half-hash match was not verified.

## 8. Required regression fixtures

At minimum, add deterministic unit/regression fixtures equivalent to the following.

### Positive fixture P1 — exact supported digest

Input:

```text
layout = valid
rom logical size = 0x100000
sha256 = EXPECTED_WOFR1_SHA256
```

Expected:

```text
identity accepted
warnings eligible
```

### Negative fixture N1 — old ALPHAQA-001 layout-only lookalike

Input:

```text
moduleOk = true
ramBase = valid
ramWithinHeap = true
selfIndexes = [0,4,8]
ROM evidence = missing
```

Expected:

```text
identity rejected/pending-never-accepted
warnings disabled
```

This is the direct regression for the current P0.

### Negative fixture N2 — sparse anchors match, full program does not

Input:

```text
layout = valid
reset vector = expected
dispatch anchors = expected
sha256 != EXPECTED_WOFR1_SHA256
```

Expected:

```text
identity rejected
warnings disabled
```

This prevents the proposed locator from accidentally becoming the certificate.

### Negative fixture N3 — one-bit/one-byte mutation

Take the positive test byte fixture/digest fixture and mutate one byte (or simply supply a digest differing by one hex digit).

Expected:

```text
identity rejected
```

### Negative fixture N4 — known other World revision

When/if the implementation keeps a fixture digest for `wof / World 921031`, it must reject it even though the general WOF layout is compatible.

Canonical program files for reference:

```text
tk2e_23c.8f SHA-1 10b8cb53a4600e3e76f471a3eee8a600e93096fc CRC32 0d708505
tk2e_22c.7f SHA-1 52c2d05279623d93b27856e6b76830796a089eae CRC32 608c17e3
```

A real other-revision ROM blob is **not** necessary in the product regression suite; a deterministic wrong digest fixture is enough to enforce fail-closed logic.

### Negative fixture N5 — malformed ROM evidence

Reject each:

- wrong logical length;
- non-hex hash;
- hash wrong length;
- no unique ROM candidate;
- hash operation rejected/throws.

### Negative fixture N6 — asynchronous race

Delay the hash promise while otherwise valid live state is available.

Expected:

```text
zero warnings before identity promise resolves accepted
```

Then resolve mismatch.

Expected:

```text
zero warnings after mismatch
```

## 9. Optional diagnostics that must not weaken the gate

It is useful to log:

- ROM heap base;
- pair-swap mode;
- vector values;
- dispatch locator offset/delta;
- page/asset/set label if exposed;
- SHA-256 prefix after acceptance.

None of those diagnostics may create an alternate acceptance path.

## 10. Product-owner handoff condition

Do not implement an expected SHA-256 value until `MINIMAL_BROWSER_PROBE.md` has produced an accepted known-good result.

After that result is committed under `parallel/ALPHAID/**`, the Alpha RC2 owner has an unambiguous implementation task:

```text
layout sanity
AND full 1 MiB CPU-logical SHA-256 == accepted golden wofr1 digest
=> identity accepted
else
=> warnings disabled
```
