# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC2 rejected by PM review / RC3 preparation

## Current owner action required: YES — one read-only World 921031 Browser identity probe

The first ALPHAID probe did not fail due to user error. It positively identified the current Browser program as:

```text
MAME set: wof
Warriors of Fate (World 921031)
main-program SHA-1 halves:
10b8cb53a4600e3e76f471a3eee8a600e93096fc
52c2d05279623d93b27856e6b76830796a089eae
```

It also reported the historical live dispatch delta `+52 / +0x34`, matching prior Browser ROM work (`4e6f32865302d2ed390f129b5c66123fdf5f04d0`).

PM therefore treats the old `wofr1 / World 921002` label as a stale/unverified project label for this Browser lineage. Do not switch ROMs to satisfy it.

## Action O1 — Run the corrected 921031 probe

In the same live `gstyphoon.js` Worker Console, paste this one line:

```js
fetch("https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/PM/wof_runtime_identity_921031_probe.js?"+Date.now()).then(r=>r.text()).then(s=>(0,eval)(s))
```

This is read-only. It does not write game RAM and does not control the player.

Return the single JSON object printed at the end.

Success requires:
- `accepted == true`
- `readOnly == true`
- `ramWrites == 0`
- `canonical.world921031Match == true`
- `fullCpuLogicalSha256 == repeatCpuLogicalSha256`
- `stable == true`

That full SHA-256 becomes the golden Browser program identity for the next Alpha candidate.

## RC2 stage decision

The RC2 implementation thread produced a candidate, but PM review rejected it before final Browser QA for two reasons documented in `parallel/PM/RC2_REVIEW_BLOCKERS.md`:

1. P0 identity guard still uses sparse vector/dispatch evidence and can mislabel the actual 921031 runtime as 921002.
2. P1 lifecycle handling still permits history-derived previous/current logic without positive same-enemy continuity and therefore does not fully implement the ALPHALIFE conservative policy.

A fresh implementation stage is already prepared at:

`parallel/PM/ALPHA_RC3_FIX_START_PROMPT.md`

Do not revive the completed RC2 implementation chat.

## Work-thread cleanup

The following current-stage work threads have reached their stop points and may be closed:
- Alpha RC2 implementation — candidate produced, then rejected by PM review.
- Runtime Identity audit — method/probe defined; PM now owns the corrected one-shot binding.
- Enemy Lifecycle audit — implementation-ready conservative policy complete.
- Normal-user Bootstrap audit — implementation recommendation complete.

After the 921031 probe succeeds, open one fresh **Alpha RC3 Fix** thread using `ALPHA_RC3_FIX_START_PROMPT.md`.

## Do not do yet

- Do not run final Alpha Browser acceptance.
- Do not resume WOF-052 as a release blocker.
- Do not perform broad Browser/WinKawaks collection.
- Do not switch the game ROM to 921002 merely to fit the old label.

## Next PM trigger

Paste the corrected 921031 probe JSON here. PM will record the golden digest, route it into RC3, then start the fresh repair stage.
