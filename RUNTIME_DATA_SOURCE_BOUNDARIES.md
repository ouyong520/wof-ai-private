# WOF Runtime / Data Source Boundaries

Updated: 2026-09-02
Status: **AUTHORITATIVE — PROJECT-WIDE ARCHITECTURE AND DATA-PROVENANCE RULE**

Owner directive:

> V1、WinKawaks Collector、10训 Training Farm 可以并行，但职责必须清楚；不要重复造同一套东西，也不能把不同来源的数据、地址、runtime authority 混在一起。

This document defines the project-wide separation and cooperation model for the three main runtime/data lanes:

1. **Browser / Alpha V1 product runtime**
2. **WinKawaks Collector**
3. **Training Farm / Stable-Retro + FBNeo multi-instance training**

The three lanes may share research knowledge, schemas where appropriate, and derived hypotheses, but they MUST NOT silently share runtime authority or pretend that evidence from one source is authoritative for another.

---

## 1. Executive model

Use this mental model:

```text
Browser / Alpha V1
= real product / real online acceptance authority

WinKawaks Collector
= real local observation / high-frequency read-only evidence acquisition

Training Farm
= automated experimentation / savestate branching / action search / training data generation
```

They are complementary, not substitutes.

Preferred long-term flow:

```text
real gameplay question / production failure
-> WinKawaks Collector for fast controlled observation when useful
-> Training Farm for large-scale automated counterfactual/action exploration when useful
-> candidate understanding / policy / rule
-> Browser / Alpha real-product prospective validation
-> production conclusion
```

No arrow in that flow implies that numeric offsets, runtime identity, lifecycle authority, or evidence provenance automatically transfer across sources.

---

## 2. Browser / Alpha V1 lane

Primary repository/runtime area:

```text
ouyong520/wof-ai-private
product/alpha/**
Browser / WASM / Worker / HUD / OneClick runtime
```

Primary role:

- actual user-facing product;
- real online/browser runtime semantics;
- real `1P / 2P / 3P` target behavior;
- real danger warning behavior;
- production HUD/projection behavior;
- real Browser/Worker/WASM lifecycle and authority;
- final bounded acceptance before release;
- final prospective validation before promoting a detection rule to production.

Authority rule:

> Browser/WASM facts are authoritative only for Browser/WASM/product runtime unless separately mapped and proven elsewhere.

Training Farm or WinKawaks evidence can motivate a Browser test, but cannot by itself prove a Browser production rule or Browser numeric offset.

---

## 3. WinKawaks Collector lane

Primary repository:

```text
ouyong520/wof-winkawaks-bridge
```

Primary role:

- real local WinKawaks runtime observation;
- raw CPS RAM snapshots;
- high-frequency raw streams;
- long-session segmented capture;
- controlled human-prepared scenes;
- repeated scene experiments;
- field-change and transition discovery;
- reverse engineering;
- large reusable local datasets;
- structured acquisition metadata;
- local-first raw evidence retention.

Default authority / safety boundary:

```text
readOnly = true
writesGameMemory = false
inputInjection = false
containsAiDecisionLogic = false
```

Collector answers primarily:

> “真实 WinKawaks 运行时现在发生了什么？”

It is an observation/evidence system, not a gameplay policy engine.

Collector should not grow into a live input bot merely because Training Farm supports automated actions.

---

## 4. Training Farm / 10训 lane

Primary repository/runtime area:

```text
ouyong520/wof-ai-private
training/farm/**
Stable-Retro + FBNeo
```

Primary role:

- isolated emulator experimentation;
- `reset / step / read_ram / save_state / load_state`;
- programmatic per-instance input through emulator/core APIs;
- deterministic or measured replay;
- savestate fork search;
- one state -> multiple action branches;
- automatic counterfactual experiments;
- branch scoring;
- trajectory generation;
- search-teacher data;
- later supervised/RL training;
- eventual 1 -> 2 -> 4 -> 8 -> 10 worker scaling.

Training Farm answers primarily:

> “从这个状态开始，如果自动尝试很多不同动作，结果分别会怎样？”

This is intentionally different from Collector's observational role.

Training Farm automation is allowed only inside the isolated emulator/training environment. It does not grant permission to add autonomous input to the live Browser product or WinKawaks Collector.

---

## 5. What is shared, and what must remain separate

### May be shared

The project SHOULD reuse common concepts where doing so prevents duplicate infrastructure:

- generic observation field names after semantics are proven;
- trajectory/event envelope concepts;
- SHA-256 / artifact integrity helpers;
- dataset catalog concepts;
- structured scene metadata vocabulary;
- experiment IDs / trial grouping concepts;
- analysis algorithms that operate on an explicit source adapter;
- generic transition/diff/statistical tooling;
- human-readable semantic names once cross-source mappings are proven.

Shared tooling must accept an explicit source namespace rather than assuming all runtimes expose the same bytes/offsets.

### Must remain separate

The following MUST NOT be silently shared or inferred across sources:

- numeric memory offsets;
- raw address-space layout;
- runtime/session identity;
- process/Worker generation;
- lifecycle generation;
- savestate identity;
- drawing-buffer/projection authority;
- Browser/WASM target fields vs WinKawaks normalized fields;
- WinKawaks raw capture identity vs Training Farm trajectory identity;
- Browser production evidence vs local emulator evidence;
- source-specific timing/cadence assumptions;
- source-specific RNG/state semantics.

Every durable dataset/artifact must state its source.

Recommended source namespace values:

```text
browser-wasm
winkawaks
stable-retro-fbneo
```

Derived cross-source datasets must preserve the provenance of every contributing source rather than replacing them with a generic `wof` label.

---

## 6. No silent offset transfer

Hard rule:

> Same game does not mean same host/runtime memory contract.

Examples already known in this project include different numeric selectors/normalized offsets between Browser/WASM and WinKawaks.

Therefore:

```text
Browser offset
!= automatically WinKawaks offset
!= automatically Stable-Retro/FBNeo memory offset
```

A semantic mapping is valid only after explicit calibration/proof.

For Training Farm specifically, WOF RAM semantics must be calibrated against emulator/core-visible CPS memory using controlled scenes, invariants, savestates, or other authoritative evidence. Do not copy WinKawaks host addresses into Stable-Retro code and call them proven.

---

## 7. Dataset identity and provenance

Every reusable dataset should identify at minimum:

- `sourceNamespace`;
- runtime/core/emulator identity;
- game/ROM identity where legally and operationally available;
- session/capture/trajectory identity;
- producer task/experiment identity;
- timestamps / frame ranges;
- Hz or frame-step semantics;
- byte/schema/layout version;
- artifact SHA-256;
- scene metadata;
- player configuration;
- changed variable;
- held-stable variables;
- research question;
- confounders/notes;
- completeness/interruption state.

Source-specific identity remains mandatory:

### Browser

Preserve Browser/Worker/runtime/proof authority needed by the product contract.

### WinKawaks

Preserve Collector taskId/taskBlobSha, WinKawaks runtime/session identity, capture/session/segment identity and hashes.

### Training Farm

Preserve core/runtime version, worker identity, savestate hash/id, branch/trial identity, action sequence and deterministic replay metadata.

Never merge two source datasets merely because their visible game scene appears similar.

---

## 8. Collector vs Training Farm: overlap policy

Some infrastructure can appear similar in both systems:

- RAM readers;
- trajectory/frame records;
- manifests;
- hashing;
- dataset catalogs;
- analysis/diff tools.

The default response is **not** to build two incompatible generic stacks.

Instead:

1. keep source adapters/runtime ownership separate;
2. identify genuinely source-agnostic data concepts;
3. reuse or extract generic tooling only when semantics are explicit;
4. require `sourceNamespace` at the boundary;
5. never refactor source-specific authority into a generic abstraction that hides provenance.

Example:

```text
GOOD:
common transition analyzer
  <- winkawaks adapter
  <- stable-retro-fbneo adapter

BAD:
one generic WOF RAM reader that assumes identical offsets everywhere
```

Collector PM and Training Farm PM should check for reusable generic tooling before creating a duplicate dataset/index/analysis subsystem.

---

## 9. Runtime and machine-resource conflict policy

Code ownership can be parallel, but runtime workload can still conflict on the Owner's machine.

Training Farm multi-instance execution can consume substantial:

- CPU;
- RAM;
- disk I/O;
- scheduler time;
- thermal budget.

A critical WinKawaks long capture can depend on stable sampling cadence and low read error/jitter.

Therefore, until measured resource isolation proves safe:

> Do not run heavy 8/10-worker Training Farm workloads at the same time as an important long-duration WinKawaks Collector capture.

Recommended operating priority:

```text
critical/canonical WinKawaks capture
-> pause or cap heavy Training Farm fleet
-> capture completes
-> resume Training Farm
```

Small repository development/self-check work may proceed in parallel when it does not materially load the local runtime.

Future fleet/resource management may relax this rule only after objective measurements show Collector cadence/integrity is unaffected.

---

## 10. Repository/write boundaries

Default ownership:

### V1 / Product PM

Writes primarily:

```text
product/alpha/**
release/proof/package-specific lanes
V1 PM prompts/results
```

Must not casually redesign Collector or Training Farm internals.

### Collector PM

Writes primarily:

```text
ouyong520/wof-winkawaks-bridge/**
Collector-specific PM/data catalog integration in wof-ai-private
```

Must not modify `product/alpha/**`, production danger rules, target semantics, Transport or OneClick merely to make Collector work.

### Training Farm PM

Writes primarily:

```text
training/farm/**
training-specific schemas/results/plans
```

Must not weaken the live Collector read-only boundary or V1 product input-safety boundary.

Shared files require explicit coordination and current-main reread before mutation.

Canonical dedup remains mandatory for equivalent work.

---

## 11. Testing cadence applies independently to each module

Authoritative test policy:

```text
parallel/PM/TESTING_CADENCE_POLICY.md
```

Do not use the existence of three lanes as an excuse to triple QA.

Each lane follows:

```text
finish coherent functional module
-> implementation self-check
-> freeze candidate
-> one meaningful module-level QA when needed
-> fix concrete failures
-> focused retest
```

Cross-source validation is required only when a conclusion intentionally crosses source boundaries.

Example:

- proving a WinKawaks offset works in WinKawaks does not require Browser QA;
- promoting that finding into a Browser production rule does require Browser-side prospective authority;
- Training Farm trajectory generation does not need to be relabeled as Collector QA.

---

## 12. Product relationship

The three lanes serve one product roadmap:

```text
V1 product
<- trustworthy production rules / projection / target semantics

Collector
-> faster real local reverse engineering and reusable evidence
-> broader/better V1.x danger coverage

Training Farm
-> automated counterfactual exploration and action-result data
-> future movement guidance / Safe Path / low-damage policy
```

Collector and Training Farm are R&D accelerators. Neither is itself a user-facing version milestone unless its work produces a real gameplay improvement in the product.

---

## 13. PM decision rule before opening work

Before scheduling a Collector or Training Farm task, answer:

1. Is this observational evidence acquisition or automated action exploration?
2. Which runtime/source is authoritative for the question?
3. Does equivalent generic tooling already exist in the other lane?
4. Can shared infrastructure be reused without hiding source provenance?
5. Will this task write into another lane's authority domain?
6. Could the runtime workload interfere with another important capture/test?

Routing default:

```text
observe real WinKawaks state / collect raw data
-> Collector

automatically try actions / fork savestates / generate trajectories
-> Training Farm

prove real online product behavior
-> Browser / Alpha V1
```

---

## 14. Governing principle

**V1 is the product. Collector observes reality. Training Farm explores possibilities.**

They may share knowledge and carefully designed generic tooling, but:

**never merge runtime authority, never silently reuse offsets, never erase provenance, and never let automated training permissions leak into the live read-only Collector or production product.**
