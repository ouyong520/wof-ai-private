# WOF Project — Proactive Parallel Execution Board

Updated: 2026-09-01

## PM operating policy

This project should not wait for the owner to invent the next task.

PM must maintain a continuously populated parallel execution pool:
- when one stage reaches PASS / READY / BLOCKED / CLOSED, close that stage;
- immediately re-read GitHub and dispatch the next highest-value non-overlapping fresh stage;
- do not keep finished chats alive;
- do not create duplicate write ownership;
- do not make the owner manually carry technical findings between lanes;
- reserve owner actions for true Windows/Browser/WinKawaks human gates only;
- owner-facing tools are Simplified Chinese by default.

## Current active execution pool

### Slot 1 — P0 product path
`PYLAUNCH Worker Discovery Fresh Fix`
- owns `parallel/PYLAUNCH/**`
- closes real Chrome `no gstyphoon worker target` blocker.

### Slot 2 — independent P0 diagnosis
`Chrome Worker Surface Audit`
- owns `parallel/WORKER_SURFACE/**`
- independent root-cause investigation; no PYLAUNCH modifications.

### Slot 3 — long capture operations
`WOF-052L Multi-Room Long Live Capture`
- combines existing Fleet + Recorder;
- prepares 10-room indefinite/1h+ capture;
- must not ask owner to waste an hour while Worker discovery is known-broken.

### Slot 4 — capture analysis
`WOF-052L Automatic Analysis`
- owns `parallel/WOF052L_ANALYSIS/**`
- ensures long capture turns into T18 conclusions immediately.

### Slot 5 — owner UX localization
`Owner Tools Simplified Chinese UX Pass`
- localizes Fleet / Recorder / Toolkit owner-facing UX;
- excludes PYLAUNCH while Slot 1 owns it.

### Slot 6 — one-click distribution
`Owner One-Click Package`
- creates download -> double-click -> update/install/open workflow;
- no directory hunting / GitHub Desktop requirement.

### Slot 7 — evidence pipeline
`Evidence Auto-Ingestor`
- owns `parallel/EVIDENCE_INGESTOR/**`;
- auto-summarizes Windows proof / recorder / regression / diagnostics results.

### Slot 8 — PM status pipeline
`Project Status Scanner`
- owns `parallel/PROJECT_STATUS/**`;
- auto-generates project state / owner action / next-stage suggestions.

### Slot 9 — downstream acceptance prep
`Alpha Transport-Aware Acceptance Prep`
- owns acceptance tooling only;
- prepares future transport acceptance before implementation lands.

### Slot 10 — downstream Beta prep
`Beta Rule Candidate Triage`
- owns `parallel/BETA_TRIAGE/**`;
- consumes existing evidence only and prepares the next prospective validation queue.

## Dependency-triggered next stages

When PYLAUNCH live Worker proof PASSes:
1. immediately open fresh `Alpha Safe Transport Integration` implementation stage;
2. Worker Surface audit closes unless it found an independent unresolved issue;
3. WOF-052L live capture is authorized to proceed if its own readiness gate is also green.

When Alpha transport integration offline/mock PASSes:
1. immediately open fresh integrated QA;
2. activate prepared bounded Browser Acceptance;
3. do not wait for owner to ask PM what comes next.

When 10-room WOF-052L capture produces sufficient target evidence:
1. automatic analysis identifies best ordered discriminator candidate;
2. immediately open a fresh prospective ordered validator lane;
3. do not promote directly to production from discovery evidence.

When Alpha Browser Acceptance PASSes:
1. immediately run PM release gate review;
2. either approve Alpha candidate release or issue one fresh blocking fix/QA stage.

## Concurrency principle

Use available parallel workers aggressively, but parallelize by independent ownership rather than splitting the same file across multiple chats.

Target normal operating range: 6-10 non-overlapping active execution lanes while meaningful work exists.

If fewer than 6 useful lanes exist, do not invent low-value work merely to fill slots; instead prioritize real-world gates and downstream preparation.