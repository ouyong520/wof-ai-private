# WOF Future Danger AI — Global PM / Worker Handoff Rules

Updated: 2026-09-03
Status: **AUTHORITATIVE — ALL PRODUCT MANAGERS AND ALL NEW WORKER HANDOFFS MUST FOLLOW THIS**

This file is project-wide PM operating policy. It applies to Alpha/V1, Collector, Training Farm, QA, recovery, audit, setup, acceptance, packaging and future workstreams unless the Owner explicitly overrides a rule for a specific task.

It supplements, and must be read consistently with:

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/OWNER_SHORTHAND_CONVENTIONS.md`

## 1. Owner shorthand: standalone `1` means continue

When the Owner sends a message whose trimmed content is exactly `1`, interpret it as:

**Continue the current task / execution chain from the latest authoritative Git state.**

Do not treat standalone `1` as “choose option 1” unless the Owner explicitly says they are selecting a numbered option.

PM must re-read current durable Git truth as needed, review terminal RESULT / claims / HEAD, and continue the shortest legitimate next step. Do not restart completed work, invent a new recovery/QA stage without need, or merely repeat the previous status.

## 2. All PM-to-worker handoffs must stay short

Default Owner-facing handoff format:

1. Start with roughly **100 Chinese characters** of plain-language task description. State the concrete responsibility, outcome and most important boundary. Do not paste a long history when Git already contains the durable specification.
2. Put the authoritative Git repository path / START_PROMPT reference in the **middle** of the handoff.
3. Keep the rest compact. The Git START_PROMPT is the detailed authority; the chat handoff is only a concise execution entry point.
4. Prefer one coherent worker instruction instead of many verbose sections.
5. PM should not make the Owner interpret implementation summaries or choose routine technical solutions.

Typical middle form:

```text
仓库：ouyong520/wof-ai-private
读取：parallel/PM/<START_PROMPT>.md
```

## 3. Default terminal execution instruction for implementation/setup/recovery workers

Unless the Owner explicitly overrides it, PM must end implementation/setup/recovery handoffs with an instruction equivalent to:

```text
如果遇到问题，不要停在一句报错。继续自动诊断和修复所有安全可修复的环境问题，直到：SETUP COMPLETE，或给出一个真正需要 Owner 手工处理的精确 BLOCKED。少汇报，直接执行。
```

For tasks whose terminal success state is `COMPLETE` rather than `SETUP COMPLETE`, PM may adapt the success token while preserving the same behavior: keep diagnosing and safely fixing recoverable problems until the authorized stage reaches its real terminal state or a genuinely Owner-required precise blocker remains.

This rule means:

- do not stop after the first dependency, path, shell, package, CI, permission, cache, launcher or other recoverable environment error;
- continue automatic diagnosis and safe remediation inside the authorized scope;
- do not ask Owner for routine confirmations between recoverable steps;
- do not stop merely because one intermediate patch/test/setup step finished;
- implementation workers finish the coherent module, integration, self-check, durable RESULT and required claim closeout before terminal reporting when the START_PROMPT requires them;
- report sparingly and spend the turn executing rather than narrating routine progress.

It does **not** authorize destructive changes, unsafe actions, secret disclosure, bypassing dedup/safety gates, weakening proof authority, inventing scope, or fabricating PASS/COMPLETE evidence.

## 4. Terminal reporting

Normal worker behavior is:

**clear handoff -> sustained execution -> terminal report**.

Workers should stop/report primarily at one of the authorized terminal states for the stage, such as:

- `SETUP COMPLETE` / `COMPLETE` / `PASS`;
- precise `BLOCKED` that truly requires Owner/manual/external action or cannot safely be repaired inside scope;
- canonical duplicate `NO EXECUTION` / duplicate stop.

A one-line error is not a terminal result when safe automatic diagnosis/remediation remains possible.

## 5. Mandatory PM application

All product managers creating or resurfacing worker prompts must apply this file by default. New PM START_PROMPTs and recovery prompts should be written so their Owner-facing handoff can follow these rules without restating large amounts of background context.

If another older PM document conflicts only in handoff verbosity or routine stop/report behavior, this global policy governs the newer Owner interaction convention. Safety, canonical dedup, exact proof authority, testing cadence, source/runtime boundaries and explicit task-specific START_PROMPT constraints remain fully authoritative.
