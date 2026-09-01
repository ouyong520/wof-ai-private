# WOF ALPHA USER BOOTSTRAP AUDIT — START PROMPT

You own one bounded read-only product-support investigation for Alpha QA blocker ALPHAQA-004.

Repository:
- `ouyong520/wof-ai-private`

Read first:
- `parallel/ALPHAQA/FINDINGS.md` — ALPHAQA-004
- `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`
- current `product/alpha/**`
- prior Browser loaders, HUD bridge, Worker hooks and other user/bootstrap experiments in repository history.

## Role and boundary

You are NOT the RC2 implementation owner.

Question:

**What is the smallest reliable Alpha-user bootstrap/install path that activates both the Browser game Worker runtime and top-page HUD without asking the user to manually identify/switch to the live `gstyphoon.js` Worker DevTools console?**

Treat `product/alpha/**` as READ-ONLY.
Write only under `parallel/ALPHABOOT/**`.
Do not change PM/QA/research/product files.

## Work

1. Audit current Browser architecture and previous project loader/hook approaches.
2. Determine what can be initiated from the top page, before or after the game Worker exists.
3. Consider bounded Alpha-suitable mechanisms such as a single paste/bootstrap, page hook around Worker creation, userscript/bookmarklet/extension-style install only if current architecture requires it, while minimizing setup burden.
4. Do not claim a method works unless the repository evidence/code path supports it.
5. Preserve read-only/no gameplay-input constraints.
6. Define failure behavior: if the Worker cannot be reached/identified, the system must fail closed and clearly tell the user it is not active.
7. Prefer one supported path over many alternatives.
8. Provide exact implementation requirements to the RC2 owner, but do not modify product code yourself.

## Outputs

Write under `parallel/ALPHABOOT/**`:
- `README.md`
- `BOOTSTRAP_AUDIT.md`
- `RECOMMENDED_USER_PATH.md`
- `RC2_ACCEPTANCE_REQUIREMENTS.md`

## Stop condition

Stop when either:

A. one implementation-ready normal-user Alpha bootstrap path is selected and justified from current Browser architecture; or

B. a hard Browser limitation is proven and the smallest safe user operation is precisely defined, together with what RC2 can automate and what must remain manual.

Do not start attack research or broad collection. Do not ask the owner to choose among technical alternatives unless two options remain genuinely equivalent in safety and effort.