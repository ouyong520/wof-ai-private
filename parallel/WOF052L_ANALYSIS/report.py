from __future__ import annotations

from typing import Any

from common import TARGET_ATTACKS


def render_text(result: dict[str, Any]) -> str:
    t18 = result["t18"]
    dist = t18["distribution"]
    strongest = t18.get("strongestDiscriminator")
    validator = t18["prospectiveValidator"]
    stability = t18["stability"]
    coverage = result["secondaryCoverage"]
    lines = [
        "WOF-052L 自动分析结果",
        "=" * 28,
        f"T18 判别：{t18['verdictZh']}",
        f"支撑样本数：{t18['supportSamples']} 个候选周期",
        f"A4704 / A4712 分布：{dist.get('A4704', 0)} / {dist.get('A4712', 0)}",
        "",
        "最强区分序列候选：",
    ]
    if strongest:
        lines.extend([
            f"- 类型：{strongest['featureLabelZh']}",
            f"- 指向：{strongest['outcome']}",
            f"- 支持：{strongest['support']}；另一结果命中：{strongest['oppositeSupport']}；纯度：{strongest['purity']}",
            f"- 序列：{strongest['pattern']}",
        ])
    else:
        lines.append("- 暂无。")
    lines.extend(["", "候选提前量（lead）："])
    for attack in TARGET_ATTACKS:
        lead = t18["candidateLeadMs"].get(attack, {})
        first, last = lead.get("first", {}), lead.get("last", {})
        lines.append(
            f"- {attack}: first n={first.get('count',0)} min/median/max={first.get('min')}/{first.get('median')}/{first.get('max')} ms; "
            f"last n={last.get('count',0)} min/median/max={last.get('min')}/{last.get('median')}/{last.get('max')} ms"
        )
    lines.extend(["", "目标 / 侧向 / 重定向稳定性："])
    for attack in TARGET_ATTACKS:
        s = stability.get(attack, {})
        lines.append(
            f"- {attack}: target={s.get('targetStableRate')} side={s.get('sideStableRate')} retarget-free={s.get('retargetFreeRate')}"
        )
    lines.extend([
        "",
        f"是否值得进入新的前瞻验证器：{'是' if validator['worthEntering'] else '否'}",
        validator["noteZh"],
        "",
        "判定原因：",
    ])
    lines.extend(f"- {reason}" for reason in t18.get("decisionReasonsZh") or [])
    lines.extend([
        "",
        "次级覆盖：",
        f"- 房间数：{coverage['roomCount']}",
        f"- T18 候选周期记录：{coverage['t18CandidateTraceCount']}",
        f"- T23 周期记录：{coverage['t23TraceCount']}",
        f"- 玩家占用 [0P,1P,2P,3P]：{coverage['playerCountHistogram']}",
        f"- 敌人类型/攻击频率条目：{len(coverage['typeAttackFrequencyTop'])}",
        f"- 稀有 descriptor+attack 条目：{len(coverage['rareDescriptorAttackTop'])}",
        "",
        "固定安全结论：",
        "- single state 不能单独推进 A4704-specific rule。",
        "- 本工具只做离线只读分析，不写游戏 RAM、不注入输入、不自动晋级生产规则。",
    ])
    if result.get("notesZh"):
        lines.extend(["", "备注："] + [f"- {x}" for x in result["notesZh"]])
    return "\n".join(lines) + "\n"
