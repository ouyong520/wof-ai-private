#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

SCHEMA = "wof-project-status-v1"
RESULT_PATTERNS = (
    "RESULT*.md",
    "*RESULT*.md",
    "IMPLEMENTATION_RESULT.md",
    "AUDIT_STATUS.md",
)
STATUS_LABELS = {
    "IN_PROGRESS": "进行中",
    "READY": "仓库侧 READY",
    "WAITING_HUMAN": "等待真人",
    "PASS": "PASS",
    "FAIL": "FAIL",
    "BLOCKED": "BLOCKED",
    "CLOSED": "CLOSED",
    "NEEDS_PM_REVIEW": "NEEDS_PM_REVIEW",
    "UNKNOWN": "NEEDS_PM_REVIEW",
}
STATUS_PATTERNS = [
    ("CLOSED", re.compile(r"\bCLOSED\b|已关闭|关闭(?:阶段|状态)", re.I)),
    ("FAIL", re.compile(r"\bFAIL(?:ED)?\b|失败", re.I)),
    ("BLOCKED", re.compile(r"\bBLOCKED\b|阻塞|被阻断", re.I)),
    ("WAITING_HUMAN", re.compile(r"WAITING (?:LIVE|REAL|HUMAN)|等待(?:真人|实机|Windows|live)|真人(?:验证|测试|proof)|real Windows proof", re.I)),
    ("PASS", re.compile(r"\bPASS(?:ED)?\b|通过", re.I)),
    ("READY", re.compile(r"REPOSITORY[- ]SIDE READY|仓库侧 READY|(?:^|\W)READY(?:\W|$)|implementation-ready", re.I)),
    ("IN_PROGRESS", re.compile(r"IN PROGRESS|进行中|正在进行|CURRENT P0|当前 P0", re.I)),
]
NEGATIVE_CONTEXT = re.compile(r"\bformer\b|旧|old|previous|不再|已解决|closed|remains closed", re.I)
PROMPT_SUFFIX = "_START_PROMPT.md"

@dataclass
class CommitInfo:
    sha: str
    date: str
    subject: str
    files: list[str] = field(default_factory=list)

@dataclass
class Lane:
    lane: str
    path: str
    status: str
    status_zh: str
    result_files: list[str]
    current_result_files: list[str]
    prompt_files: list[str]
    stop_condition: str | None = None
    remaining_owner_action: str | None = None
    evidence: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    recent_commits: list[dict] = field(default_factory=list)

def repo_root_from(start: Path) -> Path:
    start = start.resolve()
    try:
        p = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True, encoding="utf-8", errors="replace"
        )
        return Path(p.stdout.strip()).resolve()
    except Exception:
        for candidate in [start, *start.parents]:
            if (candidate / "parallel").is_dir():
                return candidate
        raise RuntimeError("未找到 WOF 仓库根目录。请从仓库内运行，或使用 --repo-root 指定目录。")

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""

def find_result_files(repo: Path) -> list[Path]:
    parallel = repo / "parallel"
    if not parallel.exists():
        return []
    found: set[Path] = set()
    for pattern in RESULT_PATTERNS:
        for p in parallel.rglob(pattern):
            if p.is_file() and "PROJECT_STATUS" not in p.parts:
                found.add(p)
    return sorted(found)

def find_prompts(repo: Path) -> list[Path]:
    pm = repo / "parallel" / "PM"
    return sorted(pm.glob(f"*{PROMPT_SUFFIX}")) if pm.exists() else []

def normalize_lane_name(path: Path, repo: Path) -> str:
    rel = path.relative_to(repo)
    if len(rel.parts) >= 2 and rel.parts[0] == "parallel" and rel.parts[1] != "PM":
        return rel.parts[1]
    stem = path.stem
    stem = re.sub(r"_START_PROMPT$", "", stem, flags=re.I)
    return stem

def explicit_status_lines(text: str) -> list[str]:
    lines = text.splitlines()
    selected = []
    for line in lines[:100]:
        s = line.strip()
        if re.match(r"^(?:#+\s*)?(?:verdict|status|状态|结论|判定|gate|current status)\s*[:：—-]", s, re.I):
            selected.append(s)
        elif re.match(r"^#{1,3}\s+.*(?:PASS|FAIL|BLOCKED|READY|CLOSED|等待真人|进行中)", s, re.I):
            selected.append(s)
    return selected

def statuses_in_text(text: str) -> list[str]:
    candidates = explicit_status_lines(text)
    probe = "\n".join(candidates) if candidates else "\n".join(text.splitlines()[:60])
    found = []
    for status, pattern in STATUS_PATTERNS:
        for m in pattern.finditer(probe):
            line_start = probe.rfind("\n", 0, m.start()) + 1
            line_end = probe.find("\n", m.end())
            if line_end < 0:
                line_end = len(probe)
            line = probe[line_start:line_end]
            if status in {"FAIL", "BLOCKED", "WAITING_HUMAN"} and NEGATIVE_CONTEXT.search(line):
                continue
            found.append(status)
            break
    return found

def choose_status(texts: Sequence[str], has_prompt: bool) -> tuple[str, list[str]]:
    per_doc = [statuses_in_text(t) for t in texts if t.strip()]
    all_status = {s for statuses in per_doc for s in statuses}
    conflicts = []
    terminal = all_status & {"PASS", "FAIL", "BLOCKED", "CLOSED", "READY", "WAITING_HUMAN"}
    if "FAIL" in terminal and terminal & {"PASS", "READY", "CLOSED"}:
        conflicts.append("同一 lane 的结果文件同时出现 FAIL 与 PASS/READY/CLOSED。")
    if "BLOCKED" in terminal and terminal & {"PASS", "CLOSED"}:
        conflicts.append("同一 lane 的结果文件同时出现 BLOCKED 与 PASS/CLOSED。")
    if conflicts:
        return "NEEDS_PM_REVIEW", conflicts

    for s in ("CLOSED", "FAIL", "BLOCKED", "WAITING_HUMAN", "PASS", "READY", "IN_PROGRESS"):
        if s in all_status:
            if s == "WAITING_HUMAN" and "READY" in all_status:
                return "WAITING_HUMAN", conflicts
            return s, conflicts
    if has_prompt:
        return "IN_PROGRESS", conflicts
    return "UNKNOWN", ["未找到明确状态标记。"]

def section_after_heading(text: str, headings: Sequence[str], max_lines: int = 6) -> str | None:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        normalized = re.sub(r"^#+\s*", "", line.strip()).lower()
        if any(h.lower() in normalized for h in headings):
            out = []
            for nxt in lines[i+1:]:
                s = nxt.strip()
                if re.match(r"^#{1,6}\s+", s):
                    break
                if not s:
                    if out:
                        break
                    continue
                out.append(re.sub(r"^[-*]\s+", "", s))
                if len(out) >= max_lines:
                    break
            if out:
                return " ".join(out)
    return None

def git_recent_commits(repo: Path, limit: int) -> list[CommitInfo]:
    sep = "\x1f"
    rec = "\x1e"
    # Prefix each commit header with a record separator. With --name-only the
    # changed files follow that header until the next record separator.
    fmt = f"{rec}%H{sep}%aI{sep}%s"
    try:
        p = subprocess.run(
            ["git", "-C", str(repo), "log", f"-n{limit}", f"--pretty=format:{fmt}", "--name-only"],
            capture_output=True, text=True, check=True, encoding="utf-8", errors="replace"
        )
    except Exception:
        return []
    commits: list[CommitInfo] = []
    for chunk in p.stdout.split(rec):
        chunk = chunk.strip("\n")
        if not chunk.strip():
            continue
        lines = chunk.splitlines()
        head = lines[0].split(sep)
        if len(head) < 3:
            continue
        files = [x.strip() for x in lines[1:] if x.strip()]
        commits.append(CommitInfo(head[0], head[1], sep.join(head[2:]), files))
    return commits

def commits_for_lane(commits: Sequence[CommitInfo], lane_path: str, prompt_names: Sequence[str], limit: int = 5) -> list[dict]:
    needles = [lane_path.rstrip("/") + "/"] if lane_path else []
    needles += [f"parallel/PM/{p}" for p in prompt_names]
    out = []
    for c in commits:
        if any(any(f == n or f.startswith(n) for n in needles) for f in c.files):
            out.append({"sha": c.sha, "date": c.date, "subject": c.subject})
            if len(out) >= limit:
                break
    return out


def commit_rank_for_file(commits: Sequence[CommitInfo], rel_path: str) -> int:
    for idx, commit in enumerate(commits):
        if rel_path in commit.files:
            return idx
    return 10**9

def select_current_results(results: Sequence[Path], repo: Path, commits: Sequence[CommitInfo]) -> list[Path]:
    if not results:
        return []
    ranked = sorted(
        results,
        key=lambda p: (
            commit_rank_for_file(commits, str(p.relative_to(repo)).replace(os.sep, "/")),
            0 if p.name.upper() in {"RESULT.MD", "IMPLEMENTATION_RESULT.MD", "AUDIT_STATUS.MD"} else 1,
            len(p.parts),
            str(p),
        ),
    )
    best_rank = commit_rank_for_file(commits, str(ranked[0].relative_to(repo)).replace(os.sep, "/"))
    if best_rank < 10**9:
        return [
            p for p in ranked
            if commit_rank_for_file(commits, str(p.relative_to(repo)).replace(os.sep, "/")) == best_rank
        ]
    canonical = [p for p in ranked if p.name.upper() in {"RESULT.MD", "IMPLEMENTATION_RESULT.MD", "AUDIT_STATUS.MD"}]
    return canonical[:1] if canonical else ranked[:1]

def prompt_topic_tags(name: str, text: str) -> set[str]:
    hay = (name + "\n" + "\n".join(text.splitlines()[:45])).lower()
    tags = set()
    groups = {
        "worker-discovery": ("worker discovery", "worker 自动发现", "worker surface", "gstyphoon worker"),
        "owner-ux": ("chinese", "简体中文", "owner ux", "owner-facing"),
        "one-click": ("one-click", "一键", "bootstrap", "direct download"),
        "transport": ("transport", "wasm / heap", "alpha safe"),
        "recorder": ("recorder", "wof-052l"),
        "browser-fleet": ("browser fleet", "fleet manager"),
        "evidence": ("evidence", "证据"),
        "qa": (" qa", "qa ", "retest", "regression"),
    }
    for tag, needles in groups.items():
        if any(n in hay for n in needles):
            tags.add(tag)
    return tags

def duplicate_prompt_risks(prompt_texts: dict[str, str], active_prompt_names: set[str]) -> list[dict]:
    items = []
    names = sorted(active_prompt_names)
    for i, a in enumerate(names):
        ta = prompt_topic_tags(a, prompt_texts.get(a, ""))
        for b in names[i+1:]:
            tb = prompt_topic_tags(b, prompt_texts.get(b, ""))
            common = ta & tb
            risky = common & {"worker-discovery", "owner-ux", "one-click", "transport", "recorder", "browser-fleet"}
            if risky:
                items.append({
                    "lanes": [a.removesuffix(PROMPT_SUFFIX), b.removesuffix(PROMPT_SUFFIX)],
                    "shared_topics": sorted(risky),
                    "judgment": "可能重复/边界重叠，请按各自 scope 保持隔离；不是自动判定为重复工作。"
                })
    return items

def parse_priorities(text: str) -> dict:
    p0, p1, nonblocking = [], [], []
    for line in text.splitlines():
        m = re.match(r"^#{1,4}\s+(P0|P1|非阻塞|NON[- ]?BLOCKING)\b\s*[-—:]?\s*(.*)", line.strip(), re.I)
        if not m:
            continue
        value = m.group(2).strip() or m.group(1).upper()
        key = m.group(1).upper()
        if key == "P0":
            p0.append(value)
        elif key == "P1":
            p1.append(value)
        else:
            nonblocking.append(value)
    return {"p0": p0, "p1": p1, "non_blocking": nonblocking}

def parse_required_sequence(text: str) -> list[str]:
    lines = text.splitlines()
    capture = False
    seq = []
    for line in lines:
        if re.match(r"^#{1,4}\s+.*(?:Required sequence|所需顺序|Required sequence|当前最快路径)", line, re.I):
            capture = True
            continue
        if capture and re.match(r"^#{1,4}\s+", line):
            break
        if capture:
            m = re.match(r"^\s*\d+[.)]\s+(.*)", line)
            if m:
                seq.append(m.group(1).strip())
    return seq

def human_owner_action(owner_text: str) -> tuple[str, str]:
    low = owner_text.lower()
    if ("do not" in low and ("rerun" in low or "reopen the game" in low)) or ("不要" in owner_text and ("真人" in owner_text or "游戏" in owner_text)):
        if "fresh stage" in low or "新" in owner_text:
            return "NO", "当前不需要真人 Browser/Windows 操作；仅有项目调度/开 fresh stage 动作。"
        return "NO", "当前不需要真人操作。"
    if re.search(r"current owner action required:\s*yes", owner_text, re.I):
        return "YES", "PM 文件声明当前需要 Owner Action。"
    return "NO", "未发现必须立即由真人执行的动作。"

def stage_dispatch_action(owner_text: str) -> tuple[str, list[str]]:
    prompts = re.findall(r"`(parallel/PM/[^`]+_START_PROMPT\.md)`", owner_text)
    if prompts:
        return "YES", prompts
    return "NO", []

def old_stage_warnings(prompts: Sequence[Path], lanes: Sequence[Lane], repo: Path) -> list[str]:
    warnings = []
    terminal_dirs = {l.lane for l in lanes if l.status in {"CLOSED", "PASS"}}
    for p in prompts:
        stem = p.stem.replace("_START_PROMPT", "")
        if any(d.lower() in stem.lower() or stem.lower() in d.lower() for d in terminal_dirs):
            warnings.append(f"{p.relative_to(repo)}：对应 lane 已 {next((l.status for l in lanes if l.lane.lower() in stem.lower() or stem.lower() in l.lane.lower()), '完成')}，避免误开旧阶段。")
    rcs = []
    for l in lanes:
        m = re.search(r"RC(\d+)", l.lane, re.I)
        if m and l.status in {"PASS", "CLOSED"}:
            rcs.append((int(m.group(1)), l))
    if rcs:
        top = max(x for x,_ in rcs)
        for n,l in rcs:
            if n < top:
                warnings.append(f"{l.lane}：旧 RC{n} 阶段已完成；当前已存在更高 RC{top} 完成态。")
    return sorted(set(warnings))

def build_status(repo: Path, commit_limit: int = 60) -> dict:
    pm_dir = repo / "parallel" / "PM"
    active_text = read_text(pm_dir / "ACTIVE_PRIORITIES.md")
    owner_text = read_text(pm_dir / "OWNER_ACTIONS.md")
    release_text = read_text(pm_dir / "RELEASE_READINESS.md")

    prompts = find_prompts(repo)
    prompt_texts = {p.name: read_text(p) for p in prompts}
    result_files = find_result_files(repo)
    commits = git_recent_commits(repo, commit_limit)

    grouped: dict[str, dict] = {}
    for p in result_files:
        lane = normalize_lane_name(p, repo)
        grouped.setdefault(lane, {"results": [], "prompts": []})["results"].append(p)
    for p in prompts:
        stem = p.stem.replace("_START_PROMPT", "")
        best = None
        for lane in grouped:
            lane_norm = re.sub(r"[^A-Z0-9]+", "_", lane.upper()).strip("_")
            stem_norm = re.sub(r"[^A-Z0-9]+", "_", stem.upper()).strip("_")
            if lane_norm and (lane_norm in stem_norm or stem_norm in lane_norm):
                if best is None or len(lane_norm) > len(best):
                    best = lane
        lane = best or stem
        grouped.setdefault(lane, {"results": [], "prompts": []})["prompts"].append(p)

    lanes: list[Lane] = []
    for lane, data in sorted(grouped.items()):
        results: list[Path] = data["results"]
        lane_prompts: list[Path] = data["prompts"]
        current_results = select_current_results(results, repo, commits)
        status_sources = current_results or lane_prompts
        texts = [read_text(p) for p in status_sources]
        status, conflicts = choose_status(texts, bool(lane_prompts))
        evidence = []
        for p, txt in zip(status_sources, texts):
            explicit = explicit_status_lines(txt)
            evidence.extend([f"{p.relative_to(repo)}: {x[:240]}" for x in explicit[:3]])
        stop = next((section_after_heading(read_text(p), ("stop condition", "停止条件")) for p in current_results if section_after_heading(read_text(p), ("stop condition", "停止条件"))), None)
        remaining = next((section_after_heading(read_text(p), ("remaining owner action", "owner action", "真人", "remaining real")) for p in current_results if section_after_heading(read_text(p), ("remaining owner action", "owner action", "真人", "remaining real"))), None)
        lane_path = f"parallel/{lane}" if (repo / "parallel" / lane).exists() else "parallel/PM"
        recent = commits_for_lane(commits, lane_path, [p.name for p in lane_prompts])
        lanes.append(Lane(
            lane=lane,
            path=lane_path,
            status=status,
            status_zh=STATUS_LABELS[status],
            result_files=[str(p.relative_to(repo)).replace(os.sep, "/") for p in results],
            current_result_files=[str(p.relative_to(repo)).replace(os.sep, "/") for p in current_results],
            prompt_files=[str(p.relative_to(repo)).replace(os.sep, "/") for p in lane_prompts],
            stop_condition=stop,
            remaining_owner_action=remaining,
            evidence=evidence[:8],
            conflicts=conflicts,
            recent_commits=recent,
        ))

    priorities = parse_priorities(active_text)
    owner_action, owner_reason = human_owner_action(owner_text)
    dispatch_action, dispatch_prompts = stage_dispatch_action(owner_text)
    required_sequence = parse_required_sequence(release_text)
    next_stage = required_sequence[0] if required_sequence else (priorities["p0"][0] if priorities["p0"] else None)

    drift = []
    recent_subjects = [c.subject for c in commits[:20]]
    checks = [
        ("owner-ux", ("owner-ux", "Chinese"), "近期提交显示 Owner Tools 简体中文 UX 有新进展；若 PM 总控仍写“需要 UX pass”，请 PM 复核。"),
        ("owner-oneclick", ("Owner one-click",), "近期提交显示 Owner one-click/bootstrap 有新进展；若 PM 总控仍写“待实现”，请 PM 复核。"),
    ]
    for _, needles, msg in checks:
        if any(any(n.lower() in s.lower() for n in needles) for s in recent_subjects):
            drift.append(msg)

    active_prompt_names = {Path(x).name for x in dispatch_prompts if (repo / x).exists()}
    active_prompt_names |= {Path(x).name for x in re.findall(r"`(parallel/PM/[^`]+_START_PROMPT\.md)`", active_text)}
    duplicate_risks = duplicate_prompt_risks(prompt_texts, active_prompt_names)

    head = commits[0].sha if commits else None
    generated = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    data = {
        "schema": SCHEMA,
        "generated_at": generated,
        "repository_root": ".",
        "repository_name": repo.name,
        "source_head": head,
        "safety": {
            "read_only_scanner": True,
            "product_alpha_modified": False,
            "game_ram_writes": 0,
            "input_injection": False,
        },
        "priorities": priorities,
        "owner_action": {
            "required": owner_action,
            "reason": owner_reason,
            "pm_stage_dispatch_required": dispatch_action,
            "fresh_stage_prompts": dispatch_prompts,
        },
        "release": {
            "required_sequence": required_sequence,
            "next_fresh_stage": next_stage,
        },
        "lanes": [asdict(l) for l in lanes],
        "duplicate_active_lane_risks": duplicate_risks,
        "old_stage_warnings": old_stage_warnings(prompts, lanes, repo),
        "pm_review": {
            "required": bool(drift or duplicate_risks or any(l.conflicts for l in lanes)),
            "items": drift + [f"{l.lane}: {c}" for l in lanes for c in l.conflicts],
        },
        "recent_commits": [asdict(c) for c in commits[:20]],
        "inputs": {
            "active_priorities": "parallel/PM/ACTIVE_PRIORITIES.md",
            "owner_actions": "parallel/PM/OWNER_ACTIONS.md",
            "release_readiness": "parallel/PM/RELEASE_READINESS.md",
            "chinese_ui_requirement": "parallel/PM/CHINESE_UI_UX_REQUIREMENT.md",
            "result_file_count": len(result_files),
            "prompt_file_count": len(prompts),
            "recent_commit_count": len(commits),
        },
    }
    return data

def render_chinese(data: dict) -> str:
    lines = ["WOF 项目状态", "", f"扫描时间：{data['generated_at']}"]
    if data.get("source_head"):
        lines.append(f"仓库 HEAD：{data['source_head'][:12]}")
    lines += ["", "当前优先级"]
    p = data["priorities"]
    lines.append("P0：" + ("；".join(p["p0"]) if p["p0"] else "无明确项"))
    lines.append("P1：" + ("；".join(p["p1"]) if p["p1"] else "无明确项"))
    lines.append("非阻塞：" + ("；".join(p["non_blocking"]) if p["non_blocking"] else "未单独列出"))
    lines += ["", "各 Lane 状态"]
    for lane in data["lanes"]:
        lines.append(f"- {lane['lane']}：{lane['status_zh']}")
        if lane.get("stop_condition"):
            lines.append(f"  停止条件：{lane['stop_condition']}")
        if lane.get("remaining_owner_action"):
            lines.append(f"  剩余真人动作：{lane['remaining_owner_action']}")
        if lane.get("conflicts"):
            lines.append("  冲突：" + "；".join(lane["conflicts"]))
    oa = data["owner_action"]
    lines += ["", f"项目所有者当前真人操作：{oa['required']}", f"说明：{oa['reason']}"]
    lines.append(f"PM Fresh Stage 调度：{oa['pm_stage_dispatch_required']}")
    if oa["fresh_stage_prompts"]:
        lines.append("Fresh Stage：")
        lines.extend(f"- {x}" for x in oa["fresh_stage_prompts"])
    lines += ["", f"下一阶段建议：{data['release'].get('next_fresh_stage') or 'NEEDS_PM_REVIEW'}"]

    dup = data["duplicate_active_lane_risks"]
    lines += ["", "重复工作风险："]
    if dup:
        for x in dup:
            lines.append(f"- {' <-> '.join(x['lanes'])}（{', '.join(x['shared_topics'])}）：{x['judgment']}")
    else:
        lines.append("- 无")

    old = data["old_stage_warnings"]
    lines += ["", "旧阶段误开风险："]
    if old:
        lines.extend(f"- {x}" for x in old)
    else:
        lines.append("- 无")

    pmr = data["pm_review"]
    lines += ["", f"PM 复核：{'NEEDS_PM_REVIEW' if pmr['required'] else '无需'}"]
    for x in pmr["items"]:
        lines.append(f"- {x}")

    lines += ["", "安全边界：只读扫描；不修改 product/alpha；游戏 RAM 写入 0；不注入游戏输入。", ""]
    return "\n".join(lines)

def write_outputs(data: dict, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    j = output_dir / "PROJECT_STATUS.json"
    t = output_dir / "项目状态.txt"
    j.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    t.write_text(render_chinese(data), encoding="utf-8")
    return j, t

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WOF 项目状态扫描器（只读仓库扫描）")
    parser.add_argument("--repo-root", type=Path, help="WOF 仓库根目录")
    parser.add_argument("--output-dir", type=Path, help="输出目录，默认 parallel/PROJECT_STATUS")
    parser.add_argument("--commit-limit", type=int, default=60, help="扫描最近 commit 数量，默认 60")
    parser.add_argument("--quiet", action="store_true", help="只写文件，不打印摘要")
    args = parser.parse_args(argv)
    try:
        repo = args.repo_root.resolve() if args.repo_root else repo_root_from(Path(__file__).parent)
        out = args.output_dir.resolve() if args.output_dir else repo / "parallel" / "PROJECT_STATUS"
        data = build_status(repo, max(1, min(args.commit_limit, 300)))
        j, t = write_outputs(data, out)
    except Exception as exc:
        print(f"项目状态扫描失败：{exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        print("WOF 项目状态扫描完成")
        print(f"机器可读：{j}")
        print(f"中文摘要：{t}")
        print(f"项目所有者当前真人操作：{data['owner_action']['required']}")
        print(f"下一阶段：{data['release'].get('next_fresh_stage') or 'NEEDS_PM_REVIEW'}")
        if data["pm_review"]["required"]:
            print("PM 复核：NEEDS_PM_REVIEW")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
