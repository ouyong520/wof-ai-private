# Alpha V1 P31 — WOF Page Association Ambiguity Repair — RESULT

## Verdict

COMPLETE for the repo-side P31 repair. The tested candidate at `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731` deterministically associates Page/Worker/WASM only from explicit/runtime authority, rejects stale or duplicate targets, and remains fail-closed when multiple live pages cannot be authoritatively disambiguated.

This does **not** claim real-WOF or Owner-visible acceptance. Real WOF was not run, no promotion was performed, and alpha-live was not moved.

## Implementation

Candidate branch: `worker/p31-wof-page-association-ambiguity-repair`

Tested commit: `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731`

Changed files:

- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py`
- `parallel/PYLAUNCH/tests/test_p31_page_association_authority.py`

The repair:

- collapses identical duplicate `targetId` rows and fail-closes conflicting duplicate identities;
- rejects stale/unattachable Page and Worker targets before association;
- preserves the established deterministic authority hierarchy: valid `parentId`, then unique `parentFrameId`, then browser-context/runtime `gameSurface` evidence;
- keeps `openerId` non-authoritative for Worker parent selection;
- makes URL/title/alpha-bootstrap signals diagnostic only when more than one page is live;
- keeps unresolved two-page association fail-closed instead of using first/last/list order/timing guesses;
- retains exact Worker/WASM World identity requirements already present in discovery.

## Exact Candidate Evidence

Fresh blob readback for the terminal-tested bytes:

- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` → `518c290aed5f1a06a4b981a11160ee1d95693a56`
- `parallel/PYLAUNCH/tests/test_p31_page_association_authority.py` → `6e898ae26e8eaff96c95de00b8e02b7634085d47`
- existing `parallel/PYLAUNCH/tests/test_parentframe_authority.py` → `1ed144a003bc54246ff12f75db5f5f886028029a`

Candidate diff readback from branch base `433bb26b3804f927901a4f898a4d403e29694276` touches only the two P31-owned files above.

## Focused Self-Check

PASS — 13/13 deterministic checks against the exact durable candidate:

- 8 P31 fixtures: parentId association and order invariance, parentFrame association, parentId precedence, unique runtime `gameSurface` disambiguation, URL-only fail-closed behavior, identical duplicate collapse, conflicting duplicate rejection, stale page rejection, and unresolved two-live-page fail-closed behavior;
- 5 existing parentFrame authority regressions, including child-frame ownership, duplicate frame mapping fail-closed behavior, parentId precedence, and read-only CDP introspection surface.

The test process returned code 0. A Python environment spreadsheet-runtime warmup warning was emitted before unittest output; it was unrelated to the discovery tests and did not affect the 13/13 PASS result.

## Scope and Safety

P31 did not modify P29/P30/P32 ownership, W3 analyzer semantics, or P9/P16 staging readiness code. No real game was launched. No promotion or alpha-live move occurred. Runtime probing remains read-only with `ramWrites=0` and `inputInjection=false`.

## Next Action

PM may integrate the exact tested P31 candidate and retry the separately authorized live acceptance flow. P31 itself is complete only for the repo-side ambiguity repair; live proof remains `NOT_RUN` / `NOT_PROVEN`.
