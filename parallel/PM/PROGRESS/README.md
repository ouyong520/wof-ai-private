# Worker Progress Checkpoints

Per-stage durable non-terminal status lives here.

Authority: `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`.

Path:

`parallel/PM/PROGRESS/<stageId>_PROGRESS.json`

Rules:

- one file per stage;
- exact claimToken binding;
- no shared worker-owned dashboard/index;
- checkpoint at mandatory milestones, blockers, self-check completion, before terminal publication, and before any non-terminal stop when possible;
- `ACTIVE` claim does not prove a chat is currently running;
- RESULT + closed claim remains terminal authority;
- PM reconstruction is permitted only with `writerRole=PM_RECONSTRUCTION` and must not fabricate unpublished facts.

Machine schema: `parallel/PM/PROGRESS/worker-progress.schema.json`.
