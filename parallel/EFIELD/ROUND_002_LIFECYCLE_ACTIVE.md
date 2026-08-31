# EFIELD Round 002 — lifecycle active/inactive discriminator

Updated: 2026-09-01  
Lane: `EFIELD-*` only  
Namespace: WinKawaks normalized enemy object, stride `0xE0`  
Evidence class: WinKawaks-local discovery only; read-only; no game-memory writes.

## Question

> Is there a field that represents active/inactive object execution more directly than `+0x24` type-present, and that changes at lifecycle boundaries without conflating type replacement?

This round uses the retained seven-capture EFIELD corpus only. No new Collector task was queued.

Corpus:

- 23,400 frames
- 468,000 enemy-object samples
- 60,271 `+0x24 != 0` type-present samples
- 407,729 `+0x24 == 0` type-absent samples
- 74 type-enter edges
- 74 type-exit edges
- two WinKawaks process sessions

## Result

No byte in the existing corpus is supported as a more direct active/inactive discriminator than `+0x24`.

`+0x24` remains the unique perfect byte-level separator in the current evidence:

- balanced accuracy: `1.000000`
- raw accuracy: `1.000000`
- active/inactive value overlap: `0.000000`
- enter exact: `74/74`
- exit exact: `74/74`
- inactive domain in this classifier: exactly `0x00`
- active domain: nonzero enemy type codes

This does **not** rename `+0x24` as hitbox/damage ACTIVE. It confirms only the already-established current typed-enemy episode / type-present lifecycle role.

## Field 1 — `+0x42`

**Width:** `U8`  
**Observed domain:** all 256 byte values in the retained type-conditioned corpus  
**Formal classification:** `REJECTED` for the hypothesis **direct active/inactive object-execution gate**

### Evidence

`+0x42` is superficially attractive because it changes on every observed lifecycle edge:

- enter exact: `74/74`
- exit exact: `74/74`
- active/inactive classifier balanced accuracy: `0.960244`
- raw accuracy: `0.972229`
- active/inactive overlap: `0.027771`

However it is not a stable lifecycle state:

- all 256 U8 values occur;
- in the same-type transition analysis it changes on `37,162 / 58,667 = 63.344%` of transitions;
- its dominant deltas are `-1`, `-2`, `-3` and hold, with many changes while the typed enemy episode remains the same;
- total byte changes across the seven-run lifecycle pass are `46,171`, versus only 148 type enter/exit boundaries;
- active samples themselves include `0x00` frequently, so zero/nonzero is not an active gate for this byte.

### Verdict

The exact lifecycle-edge coincidence is a consequence of a high-frequency execution/counting quantity also changing on those frames, not evidence of a stable active/inactive bit or state. The broader semantic role of `+0x42` is still not formally named here.

**Status:** `REJECTED`

---

## Field 2 — `+0x2E`

**Width:** `U8`  
**Observed domain:** 7 values in the retained classifier corpus  
**Formal classification:** `REJECTED` for the hypothesis **direct active/inactive object-execution gate**

### Evidence

`+0x2E` separates type-present from type-absent samples reasonably well in aggregate:

- balanced accuracy: `0.979168`
- raw accuracy: `0.977079`
- overlap: `0.022921`
- active top values include `0x04`, `0x08`, `0x02`, `0x0A`, `0x06`, `0xFF`
- inactive mode is `0x00`, but inactive samples also contain the same nonzero state values

The decisive control is lifecycle-edge recall:

- enter exact: only `37/74 = 0.500`
- exit exact: only `32/74 = 0.432`
- total changes: `1,948`

Therefore many genuine `+0x24` lifecycle boundaries occur with no `+0x2E` change, while `+0x2E` also changes many times inside a typed episode.

### Verdict

`+0x2E` is not the direct active/inactive discriminator. This rejection does **not** reject its existing broader action/state candidate role; it only rejects the lifecycle-gate hypothesis.

**Status:** `REJECTED`

## Control notes

- `+0x34` remains `CONFIRMED` as record dwell/countdown, not lifecycle ACTIVE: it changes on `63/74` enters and `73/74` exits and has nonzero inactive overlap.
- `+0x00` remains rejected as current enemy presence: zero transitions across the corpus despite 148 `+0x24` zero/nonzero lifecycle edges.
- Numerous mostly-static profile/reference bytes classify type-present samples well only because they are usually zero in unused periods; many have `0/74` enter and `0/74` exit changes and remain latched nonzero in some `+0x24 == 0` samples. They are not direct lifecycle gates.

## Round 002 conclusion

For current WinKawaks-local EFIELD work, use `+0x24` as the best proven **type-present lifecycle discriminator**. There is no separate byte-level active/inactive execution gate supported more strongly by the existing seven-run corpus.

Do not spend another generic 60-second capture trying to beat this result. A new capture is justified only if a later concrete semantic distinction requires a scene where `+0x24` type-present and the desired execution-active concept demonstrably diverge.

## Next bounded question

Move to priority 2 (target / retarget):

> **Which field, if any, provides a selective pre-commit retarget signal before confirmed live-target `+0x6D..+0x6E` changes, without merely reflecting the long-lived C6 / `+0x3D..+0x3E` proximity association?**

Use the existing 8 confirmed live-target commits first. Rank `+0x65`, `+0x99`, association changes, script/action state and nearby transition windows. Only collect again if those 8 events cannot distinguish the leading precursor hypotheses.

## Evidence sources

- bridge `results/efield/ACTIVE_CLASSIFIER.md`
- bridge `results/efield/LIFECYCLE.md`
- bridge `results/efield/FIELD42_ROLE.md`
- `parallel/EFIELD/FIELD_FRONTIER.md` Round 001
