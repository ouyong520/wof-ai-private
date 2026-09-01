# WOF Browser Runtime Identity Audit

Date: 2026-09-01
Decision: **STOP B — retained evidence defines the safe mechanism, but one minimal known-good Browser proof is still required**

## 1. Audit question

What is the safest positive Browser-runtime/build identity mechanism that can distinguish the supported WOF `wofr1 / Warriors of Fate (World 921002)` program from a structurally compatible unknown/lookalike before Alpha warnings are enabled?

The answer must fail closed and must not confuse shared RAM layout with build identity.

## 2. Current Alpha gate is structurally insufficient

The RC1 Alpha loader/core currently supplies/checks only:

- emulator module presence;
- CPS RAM pointer presence;
- RAM window inside heap;
- P1/P2/P3 `+0x7C` self-index values `0/4/8`.

Those facts establish that the runtime resembles the expected Browser WOF memory layout. They do **not** prove that the loaded program is the supported revision. The existing signature name containing `wofr1-world-921002` is therefore a label attached after a layout check, not positive evidence of that ROM revision.

This is exactly the ALPHAQA-001 fail-open class: a structurally compatible unknown program can satisfy the same layout predicates.

## 3. Retained Browser evidence that is stronger than layout

The repository already contains extensive read-only Browser ROM research, especially `wof_rom_focus_probe.js` and its follow-on analyzers.

The ROM-focus locator demonstrates that the Browser worker can locate a **1 MiB 68000 program region** in the emulator WASM heap. It recognizes the logical reset vector:

```text
initial SP = 0x00FF62EE
reset PC   = 0x0000754A
```

and handles either direct bytes or adjacent-byte-pair-swapped storage. It then verifies a known type-dispatch region using expected handler entries such as:

```text
0x06F4E4
0x07494C
0x071ADA
0x077B8E
0x07C6D2
```

Historical Browser work also had to tolerate a small uniform handler-address delta. That is useful evidence that these anchors identify the correct program family/region, but it is also a reason **not** to promote sparse semantic anchors into the final identity predicate.

### What this proves

- Browser runtime program ROM bytes are observable read-only.
- A complete 0x100000-byte candidate region can be located without game writes.
- Byte-pair representation can be normalized to CPU-logical byte order.
- The region is already part of established Browser reverse-engineering, so the identity solution does not require a new memory-discovery project.

### What it does not prove

- The reset vector is unique to `wofr1`.
- The first few dispatch entries are unique to `wofr1`.
- A uniform address delta is itself a revision identifier.
- The repository currently contains a captured full-region digest for the known-good Browser `wofr1` runtime.

Therefore vector/dispatch evidence should be a **locator/prefilter only**.

## 4. Canonical `wofr1` program identity

Current emulator metadata identifies:

```text
MAME machine: wofr1
Description:  Warriors of Fate (World 921002)
maincpu size: 0x100000 bytes
```

Program ROM halves:

| Offset | File | Size | CRC32 | SHA-1 |
| --- | --- | ---: | --- | --- |
| `0x000000` | `tk2e_23b.8f` | `0x80000` | `11fb2ed1` | `19e09ad6f9edc7997b030cddfe1d9c96d88135f2` |
| `0x080000` | `tk2e_22b.7f` | `0x80000` | `479b3f24` | `9fb8ae06856fe115addfb6794c28978a4f6716ec` |

Relevant comparison: the later World parent is a different program build:

```text
MAME machine: wof
Description:  Warriors of Fate (World 921031)
```

| Offset | File | Size | CRC32 | SHA-1 |
| --- | --- | ---: | --- | --- |
| `0x000000` | `tk2e_23c.8f` | `0x80000` | `0d708505` | `10b8cb53a4600e3e76f471a3eee8a600e93096fc` |
| `0x080000` | `tk2e_22c.7f` | `0x80000` | `608c17e3` | `52c2d05279623d93b27856e6b76830796a089eae` |

Thus the two World revisions do not share the same main program bytes. Other official regional revisions likewise have distinct program ROM identities in emulator databases.

External references:

- https://www.arcade-museum.com/tech-center/machine/wofr1
- https://www.gamesdatabase.org/mame-rom/wofr1
- https://mame.spludlow.co.uk/Machine.aspx?name=wof
- https://git.redump.net/mame/commit/?h=mame0142&id=f02b5d78f2c4695d78a1bef20222072a532f15ad

## 5. Candidate mechanisms evaluated

### A. Existing RAM/layout signature

**Reject as identity.**

Good as a compatibility sanity check, but another WOF revision or lookalike can share it.

### B. Game/set name exposed by page, URL, asset filename, loader argument, or emulator metadata object

**Do not use as sole identity.**

No retained Browser evidence was found that the current worker exposes a trustworthy immutable `wofr1` set identifier. Even if a filename/string is later found, it is weaker than checking loaded program content and can be stale, renamed, or wrapper-controlled.

It can be logged as diagnostics, never used alone to enable warnings.

### C. Reset vector only

**Reject as final identity.**

Excellent locator anchor, insufficient uniqueness proof.

### D. Reset vector + several dispatch/code bytes

**Reject as final identity.**

Stronger family fingerprint, but the audit has no exhaustive proof that the sparse bytes differ across every compatible revision/lookalike. Existing code already permits a small uniform dispatch delta, which makes sparse semantic matching inappropriate as a revision certificate.

### E. Full 1 MiB main-program content digest

**Recommend.**

Advantages:

- covers all program/code/data bytes used by the 68000 program region;
- independent of RAM state, player count, room, enemy state, timing, and gameplay;
- independent of WASM heap address once the region is located;
- independent of the old `+0x34`-style semantic relocation/delta;
- any program modification changes the digest with overwhelming probability;
- cheap enough to compute once at startup over 1 MiB;
- directly matches the part of the build that controls the RAM semantics and AI logic Alpha relies on.

This is **program identity**, not a claim that every graphics/audio ROM is identical. For Alpha warning safety, main-program identity is the relevant boundary: a set with identical 68000 program bytes has the same program semantics the guard is meant to protect. If product policy later requires exact whole-ROM-package provenance, additional regions may be added separately without weakening this guard.

## 6. Why canonical per-file SHA-1 is useful but not the final production primitive

MAME publishes fixed SHA-1 hashes for the two `wofr1` 512 KiB program ROM files. The Browser heap, however, may store the loaded program in CPU-logical or adjacent-byte-pair-swapped order. The repository does not retain a proof of which heap orientation corresponds to the raw ROM file bytes.

The minimal Browser probe therefore hashes each half in **both** orientations. A valid known-good result must find one common orientation where both halves exactly match the two canonical `wofr1` SHA-1 values.

That establishes the chain:

```text
canonical emulator wofr1 ROM hashes
        ↓ exact two-half match
known-good Browser live program bytes
        ↓ normalize to CPU-logical 1 MiB
stable SHA-256 H
        ↓
RC2 positive identity guard == H
```

SHA-1 here is used only to bind the Browser bytes to the published canonical ROM metadata. The recommended production predicate is the full 1 MiB **SHA-256** captured from that canonically bound known-good Browser run.

## 7. Required positive evidence before warnings may be enabled

A known-good Browser worker result must satisfy all of the following:

1. `project == "WOF-AI-PRIVATE"`
2. `audit == "ALPHAID"`
3. `probe == "wofr1-maincpu-binding-v1"`
4. `readOnly == true`
5. `ramWrites == 0`
6. located region size is exactly `1048576`
7. vector/dispatch locator validation succeeds
8. either direct-heap or pair-swapped orientation matches **both** canonical `wofr1` 512 KiB SHA-1 values
9. known `wof / World 921031` pair does not match
10. full CPU-logical SHA-256 hash #1 equals the repeated hash #2 after delay
11. `stable == true`

Only then is the returned full CPU-logical SHA-256 eligible to become the production expected digest.

## 8. Negative/lookalike behavior required

The final guard must reject all of these before warnings are enabled:

- correct RAM layout but no ROM digest;
- correct RAM layout and vector/dispatch anchors but wrong full digest;
- correct digest format but wrong value;
- modified one-byte/nibble fixture;
- known other revision digest;
- ROM region cannot be uniquely located;
- unexpected program-region size;
- hashing unavailable/error;
- identity check still pending;
- any identity probe exception.

No fallback from failed ROM identity to layout-only acceptance is permitted.

## 9. Stop decision

**STOP B.**

The safe mechanism is implementation-ready in shape, but the one value that must never be guessed — the canonically bound known-good Browser full CPU-logical SHA-256 — is not present in retained GitHub evidence.

`MINIMAL_BROWSER_PROBE.md` defines exactly one read-only owner action to obtain it. No further broad reverse-engineering or WinKawaks collection is justified for this blocker.
