# Alpha V1 P35 — Accepted Repair Integration Lineage — RESULT

State: **COMPLETE**

## Verdict

P35 produced one durable deterministic integration source whose real Git ancestry contains the exact PM-accepted P29/P30/P31 tested commits. All 13 accepted repair-owned files fresh-read at the integration source to the exact terminal tested blob identities. The P31 ancestry merge required no semantic hand-edit. No real WOF run, promotion, or alpha-live move occurred.

## Durable integration source

- Branch: `worker/p35-accepted-repair-integration-lineage`
- P35 latest-main base: `cc0da35480b7b89c40525254d52601b18b001a92`
- Base tree: `12a836a618c87206cf95a9dc19b021c4059bba8e`
- Source / tested commit: `82b0b09ecd902f502ae5509bcb3ee5a713f43fee`
- Source / tested tree: `e5dba33a2cd579826704d3f78ec2587ee2305a5a`
- Merge parents:
  1. `cc0da35480b7b89c40525254d52601b18b001a92`
  2. `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731`

The second parent is the exact P31 tested commit. P29 and P30 were already true ancestors of the latest-main parent.

## Exact tested-commit ancestry proof

| Repair | Exact tested commit | Candidate relation | Merge base | Verdict |
|---|---|---|---|---|
| P29 | `c02f7e108e73665f22eb950573622acb6f452732` | candidate ahead, behind=0 | exact P29 commit | PASS exact ancestor |
| P30 | `90094a656ab311f18b0a758716dc97c3f8df092d` | candidate ahead, behind=0 | exact P30 commit | PASS exact ancestor |
| P31 | `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731` | candidate ahead, behind=0 | exact P31 commit | PASS exact ancestor |

This is not cherry-pick equivalence. The original exact tested commits are real ancestors of the source commit.

## Accepted repair blob readback

Fresh candidate readback matched **13/13** terminal tested blob identities.

### P29

- `parallel/RENDER_AUTHORITY_V2/qualification_analyzer.py` → `a412faa31ac8d946e25f72868a57ae234d92b4b2`
- `parallel/RENDER_AUTHORITY_V2/test_qualification_analyzer.py` → `d243efbc092dac9fe80c0cfa8c517d9685d5272e`
- `parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js` → `fa3642388d7bf89d77334a86f8091858ff8ad2c2`
- `parallel/RENDER_AUTHORITY_V2/selftest.mjs` → `588a3781a37a9cc9e390e545328b4812c47cfa7f`

### P30

- `parallel/OWNER_STAGING/p21_acceptance.py` → `b14f0e8967093b8a35512321965e4b646573bef1`
- `parallel/OWNER_STAGING/p21_runtime.py` → `28a8f19f1b4bb27719c1e09f70fc91bf2ebdcce5`
- `parallel/OWNER_STAGING/exact_candidate_staging_acceptance.py` → `613caade29ab6cb7f35192f90a6a57aa53f2289c`
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py` → `c90c5aeb631a3f4109d1132389a612379d17782d`
- `parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py` → `32312651c983d23714b71018505e3e43fb1990ae`
- `parallel/OWNER_STAGING/test_p30_p16_p9_binding_staging_readiness.py` → `b0639a9dd602c57b63147a3ef28bd08d18f2d858`
- `parallel/PYLAUNCH/tests/test_alpha_p30_p9_p1_binding.py` → `288d77b0714f975638fd6071dd35bae13e201991`

### P31

- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` → `518c290aed5f1a06a4b981a11160ee1d95693a56`
- `parallel/PYLAUNCH/tests/test_p31_page_association_authority.py` → `6e898ae26e8eaff96c95de00b8e02b7634085d47`

## Merge-conflict / precedence proof

P31 branched from `433bb26b3804f927901a4f898a4d403e29694276`. At that branch base, `discovery_v2.py` had blob `210702e1be775c39381d77a3b815a10eaa34be6f`. The P35 latest-main base had the same exact blob, and the new P31 test path was absent there. Therefore P31's exact tested bytes could be integrated without guessing or semantic conflict resolution.

The latest-main-base → P35 source delta contains only:

- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py`
- `parallel/PYLAUNCH/tests/test_p31_page_association_authority.py`

P33 OWNER_ONECLICK rebuild, P34 readiness gate, and P36 renderer-source-trace ownership surfaces were not modified.

## P32 remains BLOCKED

P32 terminal authority remains:

- tested commit `bd75c3b5f7fd20fe004fae21142a0fa19942e076`
- terminal state `BLOCKED`
- `integrationReady=false`
- blocker `NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN`

That commit is already inherited through the selected latest-main base. P35 does **not** count it as an accepted repair, does not use it to satisfy the required P29/P30/P31 containment set, and does not rewrite the BLOCKED authority to PASS.

## Focused integration self-check

- P31 semantic-conflict precheck: **PASS**
- accepted-repair exact blob readback: **PASS**, 13/13
- exact tested-commit ancestry regression: **PASS**, P29/P30/P31 exact ancestors
- candidate branch/tree exact readback: **PASS**
- focused latest-main-base → source delta regression: **PASS**, only the two P31-owned paths
- real WOF acceptance: **NOT RUN** by scope
- promotion / alpha-live movement: **NOT RUN** by scope

P29/P30/P31 had already passed their terminal focused functional tests on these exact accepted file bytes. P35 changed no accepted implementation byte beyond conflict-free integration of the exact P31 tested bytes, so the P35 focused regression is intentionally limited to integration lineage, exact-byte coexistence, ancestry, tree and scope invariants rather than broad QA reruns.

## Proof boundary

P35 proves the repository/Git accepted-repair integration lineage only. It does **not** prove P32 resolved, final retry readiness, a rebuilt final candidate/package, real-WOF correctness, or Owner-visible acceptance. It authorizes no Owner retry.

## Safety / scope

- real game/browser run: no
- RAM writes: 0
- input injection: no
- promotion: no
- alpha-live moved: no
- P33 rebuild code modified: no
- P34 readiness gate modified: no
- P36 renderer source trace modified: no

## Next action

PM/P33 may consume exact source commit `82b0b09ecd902f502ae5509bcb3ee5a713f43fee` for a separately authorized deterministic final-candidate rebuild/readiness flow. P32/P36 remains a separate renderer-proof stream.
