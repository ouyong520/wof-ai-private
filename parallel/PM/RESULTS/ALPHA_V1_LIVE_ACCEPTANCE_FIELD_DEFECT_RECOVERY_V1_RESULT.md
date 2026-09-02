# Alpha V1 Live Acceptance Field Defect Recovery V1 — RESULT

Status: **COMPLETE — IMPLEMENTATION RECOVERY**

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_FIELD_DEFECT_RECOVERY_V1_METADATA_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.live-acceptance.field-defect-recovery-v1`
effectiveDedupKey: `alpha.v1.live-acceptance.field-defect-recovery-v1`
dedupMode: `exclusive`
startCommit: `513a2d4fe5d62621e4069afde475c3ccbd8a5421`
finalPackageSourceCommit: `91be86ade8d4dcc7ee100458a1cedd87f5873bf7`
finalPackageManifestPublishCommit: `0cf94ab483ec3991a2a491e3ddcdecdb689ea0ef`
implementationSelfCheckWorkflowRun: `33634245686`

## Scope completed

This recovery completed the original live-acceptance field-defect implementation scope after the Metadata Recovery V2 canonical-dedup authority repair. It did not open a new QA generation and did not run or request a new Owner Browser/WOF session.

The field defects were resolved as one integrated runtime/package candidate:

1. **Periodic hitch / repeated full ROM identity scan**
   - Stable exact World 921031 authority is now retained only behind a cheap runtime-generation fingerprint.
   - The fingerprint binds page target + page isolate, Worker target + Worker isolate, module key, heap size and RAM base.
   - Stable polling uses only cheap page/Worker health checks; it does not repeat `crypto.subtle.digest` or the full ROM locator/hash scan.
   - Browser/page/Worker/runtime generation changes, including same-targetId isolate replacement and heap-generation changes, revoke cached authority and force re-attestation.

2. **`ROM locator candidate count 2` false blocker**
   - Structural locator multiplicity is no longer treated as identity multiplicity.
   - Every structural candidate is hashed as full CPU-logical ROM data.
   - Exactly one candidate matching the authoritative World 921031 SHA-256 is accepted.
   - Zero exact matches fail closed; multiple exact matches remain ambiguous and fail closed.
   - Candidate diagnostics retain heap base, swap mode, uniform delta, dispatch entries, SHA-256 and exact-match status.

3. **Menu 6 was proof-monitor-only instead of release Alpha activation**
   - The owner menu now launches `PYLAUNCH` in package-selected Alpha activation mode with the exact package root.
   - The package-local field adapter binds page bootstrap transport to the accepted native Worker and re-checks detector-local exact identity.
   - Invalid/revoked authority cannot produce a false Alpha-running state or anchored overlay authority.
   - The live-proof JSON requires Alpha package runtime running when live-acceptance activation was requested.

4. **Menu 8 depended on a non-packaged `EVIDENCE_INGESTOR`**
   - The Chinese owner surface now delegates to the self-contained local ZIP packager already in `toolkit.py`.
   - Packaging is local/offline, includes latest diagnostics/regression/live-proof categories plus optional recorder result, and writes beneath the results `packages` directory without recursive package ingestion.

5. **OneClick was not portable/offline on normal second launch**
   - First install uses a launcher-adjacent `WOF_Portable` root with releases, venv, logs and `current.txt`.
   - Normal second-and-later launch goes directly to the verified local release; no manifest fetch, bootstrap fetch, pip or update request occurs on that path.
   - Only first install or explicit `--update-only` / menu-1 repair-update uses network access.
   - Atomic staging, per-file Git blob verification, `installed.ok`, current-pointer switch and last-known-good retention are preserved.
   - Windows batch delayed expansion was fixed for the same-block `CURRENT_VERSION`/path resolution case.
   - Explicit manifest refresh is cache-safe: normal update uses a cache-busted main manifest URL; CI/diagnostic execution may exact-pin `WOF_MANIFEST_URL` only to an official full-commit raw URL.

## Successor package

Final successor package manifest:

- path: `parallel/OWNER_ONECLICK/package_manifest.json`
- packageVersion: `2026.09.02.91be86ade8d4`
- sourceCommit: `91be86ade8d4dcc7ee100458a1cedd87f5873bf7`
- selectionPolicy: `owner-oneclick-runtime-v3-field-recovery`
- selected files: **57**
- manifest publish commit: `0cf94ab483ec3991a2a491e3ddcdecdb689ea0ef`
- all ownerOneclick / Alpha / PYLAUNCH / Recorder / Browser Fleet / Live Proof component provenance points to the same immutable source commit.

Key exact selected blobs include:

- `WOF_一键工具.cmd` -> `dcafacb599960a57c17419ebf3722c76e6995143`
- `parallel/OWNER_ONECLICK/bootstrap_v2.ps1` -> `1e14ef24c2db09b6bf31f8933abcbf26274a9fda`
- `parallel/PYLAUNCH/launcher.py` -> `1dfe5a106cedc9df2ec911996b8eacc0c7c1daef`
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py` -> `bd636734ce9abb91cb0bf5afc96451f0df1810e1`
- `parallel/PYLAUNCH/wof_launcher/cdp.py` -> `7fdd318fc42df551b76af67d898e28b7ba858f8c`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` -> `210702e1be775c39381d77a3b815a10eaa34be6f`
- `parallel/PYLAUNCH/wof_launcher/monitor.py` -> `8ba44a10486180406a478c6f278e15c63fc19d81`
- `parallel/PYLAUNCH/wof_launcher/probe_v2.py` -> `a913f77568f07d199e3396a22a0528d4b734bc2b`
- `parallel/PYLAUNCH/wof_launcher/runtime_authority.py` -> `8ef859091c5fc1d20323153d5fefa6c8b77476bb`
- `product/alpha/wof_alpha_field_adapter.js` -> `9ea92451c03bd72b9d46a6cbaf9304707f5622e2`

The player/enemy projection JSON profiles remain intentionally unproved/fail-closed. This recovery did not guess projection constants, enable synthetic proof authority, change danger rules, or change target semantics.

## Implementation self-check

Authoritative implementation-owned self-check run: GitHub Actions `Owner One-Click Package` run `33634245686` at manifest publish commit `0cf94ab483ec3991a2a491e3ddcdecdb689ea0ef`.

All three jobs completed **SUCCESS**:

### `field-recovery-self-check` — SUCCESS

- **14/14** exact identity / runtime-generation cache / package-selected Alpha activation tests PASS.
  - zero structural candidates reject;
  - one exact candidate accepts;
  - two candidates with one exact match accept only the exact candidate;
  - two candidates with no exact match reject;
  - multiple exact matches reject as ambiguous;
  - strict probe is directly bound by discovery;
  - stable authority uses only cheap health checks, not full ROM hashing;
  - same-target page isolate replacement revokes;
  - same-target Worker isolate replacement revokes;
  - heap-generation change revokes;
  - package blob mutation fails closed;
  - accepted authority reaches Alpha release start;
  - invalid authority never starts Alpha / false overlay path.
- **16/16** discovery association / late-readiness tests PASS, including page-before-Worker, Worker/WASM-not-ready, nested/related Worker discovery, stale/replacement handling, ambiguous association fail-closed and read-only method restrictions.
- **5/5** live-proof Alpha gate tests PASS.
- **17/17** Operator Toolkit tests PASS, including menu-6 package Alpha activation, menu-8 local self-contained ZIP, component/safety contracts and actual local ZIP generation.
- frozen `product/alpha/regression.mjs`: **PASS** with the two existing production rules unchanged and historical rules still quarantined.
- targeted Python syntax compilation: **PASS**.

### `integrity` — SUCCESS

- **11/11** package/portable contract tests PASS after final manifest publication.
- Current selected runtime equals the immutable package snapshot.
- Every manifest blob matches its pinned commit.
- Mutated selected blobs are rejected.
- Portable atomic/LKG, cache-safe manifest refresh, direct offline second launch, UTF-8 and Chinese/space path contracts pass.

### `windows-oneclick` — SUCCESS

Windows Server 2025 executed the actual packaged flow with an exact-pinned bootstrap and manifest:

- fresh install under `...\WOF 中文 Portable Launcher\WOF_Portable`: PASS;
- package version installed: `2026.09.02.91be86ade8d4`;
- all **57/57** selected files downloaded and Git-blob verified: PASS;
- package-selected `launcher.py --activate-alpha --package-root <release>` no-Browser smoke: PASS and correctly remains `WAITING` / Alpha not running;
- no-Browser invalid authority remained fail-closed;
- Chinese proof surface present;
- explicit update repaired the current pointer while retaining synthetic prior LKG `ci.previous`: PASS;
- second explicit update was idempotent and retained LKG: PASS.

## Safety / boundaries

Preserved throughout implementation and self-check:

- `readOnly: true`
- `ramWrites: 0`
- `inputInjection: false`
- no Worker replacement
- no gameplay input injection
- no danger-rule changes
- no target-semantics changes
- no guessed player/enemy projection authority
- no Browser/WOF live acceptance session was launched by this recovery
- no independent QA/Fresh QA was opened

## Final implementation disposition

**COMPLETE — ALPHA V1 LIVE ACCEPTANCE FIELD DEFECT RECOVERY V1.**

The repository/package defects that blocked the bounded live-acceptance path are implemented, integrated, package-pinned and implementation-self-checked. The successor package is ready for **one focused Owner live retest** under the existing bounded live-acceptance procedure. This RESULT does not itself claim a live Browser/WOF acceptance PASS or a release PASS; those still require the real Owner session evidence defined by the existing acceptance authority.
