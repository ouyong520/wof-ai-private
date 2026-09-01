from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from common import (
    CANDIDATE_SIG, FEATURE_LABEL_ZH, FEATURE_ORDER, SCHEMA, TARGET_ATTACKS,
    WORLD_SHA256, Dataset, add_chain_features, feature_chain, normalize_attack,
    stats, top_counter, utc_iso,
)


def analyze(dataset: Dataset, *, min_per_outcome: int, min_sequence_support: int) -> dict[str, Any]:
    by_attack_traces: dict[str, list[dict[str, Any]]] = defaultdict(list)
    features: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    lead_first: dict[str, list[float]] = defaultdict(list)
    lead_last: dict[str, list[float]] = defaultdict(list)
    stable_counts: dict[str, Counter[str]] = defaultdict(Counter)
    candidate_cycles_total = 0
    malformed_candidate_traces = 0

    for tr in dataset.traces:
        exact, family = feature_chain(tr)
        if not exact or exact[0] != CANDIDATE_SIG:
            malformed_candidate_traces += 1
            continue
        candidate_cycles_total += 1
        attack = normalize_attack(tr.get("activeAttack"))
        by_attack_traces[attack].append(tr)
        add_chain_features(features[attack], exact, family)
        if tr.get("candidateFirstLeadMs") is not None:
            lead_first[attack].append(float(tr["candidateFirstLeadMs"]))
        if tr.get("candidateLastLeadMs") is not None:
            lead_last[attack].append(float(tr["candidateLastLeadMs"]))
        stable_counts[attack]["cycles"] += 1
        stable_counts[attack]["targetStable"] += int(bool(tr.get("targetStable")))
        stable_counts[attack]["sideStable"] += int(bool(tr.get("sideStable")))
        stable_counts[attack]["retargetFree"] += int(not bool(tr.get("retargets")))

    distribution = {attack: len(by_attack_traces.get(attack, [])) for attack in TARGET_ATTACKS}
    other_distribution = {
        attack: len(rows) for attack, rows in sorted(by_attack_traces.items())
        if attack not in TARGET_ATTACKS
    }
    all_attacks = sorted(set(by_attack_traces) | set(TARGET_ATTACKS))
    feature_tables = {
        feature_name: {
            attack: top_counter(features[attack][feature_name], 100)
            for attack in all_attacks
        }
        for feature_name in FEATURE_ORDER
    }

    candidates: list[dict[str, Any]] = []
    for outcome in TARGET_ATTACKS:
        other = TARGET_ATTACKS[1] if outcome == TARGET_ATTACKS[0] else TARGET_ATTACKS[0]
        for rank, feature_name in enumerate(FEATURE_ORDER):
            own, opp = features[outcome][feature_name], features[other][feature_name]
            for pattern, support in own.items():
                opposite = int(opp.get(pattern, 0))
                purity = support / (support + opposite)
                candidates.append({
                    "outcome": outcome,
                    "feature": feature_name,
                    "featureLabelZh": FEATURE_LABEL_ZH[feature_name],
                    "pattern": pattern,
                    "support": int(support),
                    "oppositeSupport": opposite,
                    "purity": round(purity, 4),
                    "exclusive": opposite == 0,
                    "_rank": rank,
                })
    candidates.sort(key=lambda row: (
        -int(row["exclusive"]), -int(row["support"]), int(row["oppositeSupport"]),
        row["_rank"], -float(row["purity"]), row["pattern"],
    ))
    ordered_candidates = [row for row in candidates if row["feature"] not in {"exact_final", "tm_final"}]
    strongest = {k: v for k, v in ordered_candidates[0].items() if k != "_rank"} if ordered_candidates else None

    stable_summary: dict[str, Any] = {}
    for attack in all_attacks:
        cycles = stable_counts[attack]["cycles"]
        stable_summary[attack] = {
            "cycles": cycles,
            "targetStable": stable_counts[attack]["targetStable"],
            "targetStableRate": round(stable_counts[attack]["targetStable"] / cycles, 4) if cycles else None,
            "sideStable": stable_counts[attack]["sideStable"],
            "sideStableRate": round(stable_counts[attack]["sideStable"] / cycles, 4) if cycles else None,
            "retargetFree": stable_counts[attack]["retargetFree"],
            "retargetFreeRate": round(stable_counts[attack]["retargetFree"] / cycles, 4) if cycles else None,
        }

    reasons: list[str] = []
    enough_outcomes = all(distribution[a] >= min_per_outcome for a in TARGET_ATTACKS)
    if not enough_outcomes:
        for attack in TARGET_ATTACKS:
            if distribution[attack] < min_per_outcome:
                reasons.append(f"{attack} 候选周期只有 {distribution[attack]}，至少需要 {min_per_outcome}。")
    strong_sequence = bool(strongest and strongest["exclusive"] and int(strongest["support"]) >= min_sequence_support)
    if not strong_sequence:
        reasons.append(f"尚未找到支持数 >= {min_sequence_support}、对另一结果 0 命中的有序 tail/pair/triple 区分序列。")

    stable_enough = True
    for attack in TARGET_ATTACKS:
        if distribution[attack] and (
            stable_summary[attack]["targetStableRate"] != 1.0
            or stable_summary[attack]["sideStableRate"] != 1.0
            or stable_summary[attack]["retargetFreeRate"] != 1.0
        ):
            stable_enough = False
            reasons.append(f"{attack} 存在目标/侧向/重定向不稳定周期，自动结论保持保守。")

    identity_known = bool(dataset.identity_shas)
    identity_ok = dataset.identity_shas == {WORLD_SHA256}
    if not identity_known:
        reasons.append("输入没有可验证的房间身份 SHA-256，不能给出已解决结论。")
    elif not identity_ok:
        reasons.append("输入包含非 World 921031 黄金 SHA-256 身份，不能给出已解决结论。")
    safety_ok = not dataset.safety_violations
    if not safety_ok:
        reasons.append("输入安全元数据不满足 read-only / ramWrites=0 / no input injection。")

    resolved = enough_outcomes and strong_sequence and stable_enough and identity_ok and safety_ok
    if resolved:
        reasons.append("两种最终攻击均有重复候选周期，并出现跨结果互斥的有序序列候选；可进入新的前瞻验证器，但仍禁止自动晋级生产规则。")

    strongest_for_validator = None
    for row in ordered_candidates:
        if row["exclusive"] and int(row["support"]) >= min_sequence_support:
            strongest_for_validator = {k: v for k, v in row.items() if k != "_rank"}
            break

    return {
        "schema": SCHEMA,
        "generatedAt": utc_iso(),
        "inputs": dataset.inputs,
        "safety": {
            "analysisReadOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "productionRuleAutoPromotion": False,
            "inputSafetyViolations": dataset.safety_violations,
        },
        "identity": {
            "required": "Warriors of Fate (World 921031)",
            "requiredSha256": WORLD_SHA256,
            "observedSha256": sorted(dataset.identity_shas),
            "known": identity_known,
            "ok": identity_ok,
        },
        "t18": {
            "candidateSignature": CANDIDATE_SIG,
            "guardrail": {
                "singleStateA4704SpecificPromotionForbidden": True,
                "reason": "WOF-051 前瞻证据已经观察到同一个 exact 状态分别出现在 A4704 与 A4712 之前。",
            },
            "verdict": "resolved" if resolved else "insufficient",
            "verdictZh": "已解决" if resolved else "仍不足",
            "supportSamples": candidate_cycles_total,
            "malformedOrNonCandidateEvidence": malformed_candidate_traces,
            "distribution": distribution,
            "otherAttackDistribution": other_distribution,
            "candidateLeadMs": {
                attack: {"first": stats(lead_first[attack]), "last": stats(lead_last[attack])}
                for attack in all_attacks
            },
            "stability": stable_summary,
            "features": feature_tables,
            "strongestDiscriminator": strongest,
            "topDiscriminators": [
                {k: v for k, v in row.items() if k != "_rank"} for row in ordered_candidates[:25]
            ],
            "decisionReasonsZh": reasons,
            "prospectiveValidator": {
                "worthEntering": resolved and strongest_for_validator is not None,
                "candidate": strongest_for_validator,
                "noteZh": "只建议建立新的前瞻验证器；不会自动写入 Alpha 或生产规则。" if resolved else "证据未达到保守门槛，继续自然采集即可。",
            },
            "thresholds": {
                "minCandidateCyclesPerOutcome": min_per_outcome,
                "minExclusiveSequenceSupport": min_sequence_support,
                "requireTargetAndSideStableRate": 1.0,
                "requireRetargetFreeRate": 1.0,
            },
        },
        "secondaryCoverage": {
            "roomCount": len(dataset.room_ids),
            "rooms": sorted(dataset.room_ids),
            "counts": {k: int(v) for k, v in sorted(dataset.counts.items())},
            "t18CandidateTraceCount": len(dataset.traces),
            "t23TraceCount": len(dataset.t23_traces),
            "playerCountHistogram": dataset.player_hist,
            "targetSamples": dict(dataset.target_samples),
            "enemyTypeFrequencyTop": top_counter(dataset.type_samples, 80),
            "typeAttackFrequencyTop": top_counter(dataset.attack_frequency, 120),
            "sceneTypeSetTop": top_counter(dataset.scene_sets, 100),
            "rareDescriptorAttackTop": top_counter(dataset.rare_edges, 120),
        },
        "notesZh": dataset.notes,
    }
