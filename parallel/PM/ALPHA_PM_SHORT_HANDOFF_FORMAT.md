# Alpha PM Short Handoff Format

Effective immediately for Alpha PM -> Worker chat handoffs.

## Chat presentation rule

The PM chat message should stay minimal:

1. Opening: approximately 100 Chinese characters summarizing the worker's mission, current product context, and the one outcome that matters.
2. Middle: provide only the authoritative Git references the worker must read, preferably as repository paths/links rather than reproducing the full task body in chat.
3. Ending: one short execution instruction, e.g. `按 Git authority 执行，完成后回报 COMPLETE / SUBCOMPLETE / 精确 BLOCKED。`

Do not paste full dedup metadata, file-boundary tables, acceptance matrices, implementation notes, or long background into chat when those details already exist in Git.

## Git remains authoritative

All detailed execution requirements must live in repository authority files, including where applicable:

- stageId / dedupProtocol / dedupKey / dedupMode
- parent authority and supersession rules
- scope isolation
- file ownership boundaries
- implementation requirements
- fail-closed rules
- focused test requirements
- Owner-intervention policy
- exit criteria and durable RESULT/SUBRESULT requirements

Workers must treat the referenced Git start prompt / dispatch as authoritative, not the shortened chat summary.

## PM behavior

For future `1`, `1 2`, `1 3` dispatches, PM should first update or create the detailed Git authority, verify the relevant paths exist, then send only the short handoff message to the Owner for copy/paste into worker chats.

This presentation rule changes only chat verbosity. It does not weaken dedup-v2, governance, testing, safety, product truth, or fail-closed requirements.
