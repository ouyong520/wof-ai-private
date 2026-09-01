from __future__ import annotations

import argparse, hashlib, json, os, re, sys, time, zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

VERSION = "wof-evidence-auto-ingestor-v1"
SUMMARY_SCHEMA = "wof-evidence-auto-ingestor-summary-v1"
WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
WORLD_LABEL = "World 921031"
GENERATED_DIR_NAME = "_自动整理"
SUPPORTED_SUFFIXES = {".json", ".log", ".txt"}
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}
KNOWN_SCHEMAS = {"wof-python-launcher-windows-proof-v1", "wof-052l-recorder-v1", "wof-052l-fleet-supervisor-v1"}
KNOWN_VERSIONS = {"wof-browser-fleet-v1", "wof-windows-operator-toolkit-v1", "wof-windows-operator-toolkit-v2-cn"}
KNOWN_ARTIFACTS = {"wof-alpha-rc5", "wof-alpha-rc5-independent-qa-retest"}


def utc_iso(): return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
def stamp(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def sha(data: bytes): return hashlib.sha256(data).hexdigest()
def dct(v): return v if isinstance(v, dict) else {}


def default_results_root() -> Path:
    if os.getenv("WOF_RESULTS_DIR"): return Path(os.environ["WOF_RESULTS_DIR"]).expanduser()
    h = Path.home(); docs = h / "Documents"
    return (docs if docs.exists() else h) / "WOF_RESULTS"


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    tmp.write_text(text, encoding="utf-8", newline="\n"); os.replace(tmp, path)


def write_json(path: Path, payload: Any): write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def source_files(root: Path) -> Iterable[Path]:
    if not root.exists(): return
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in SUPPORTED_SUFFIXES: continue
        try: rel = p.relative_to(root)
        except ValueError: continue
        if rel.parts and rel.parts[0] == GENERATED_DIR_NAME: continue
        yield p


def run_hint(rel: str):
    for part in Path(rel).parts:
        if re.match(r"^(?:diagnostics|regression|live_proof|update)_\d{8}_\d{6}$", part, re.I) or re.match(r"^fleet-\d{8}_\d{6}$", part, re.I): return part
    return None


def date_of(payload: dict[str, Any], mtime: float):
    for k in ("lastUpdateUtc", "updatedAt", "finalizedAt", "startedAt", "time", "created", "generatedAt", "date"):
        v = payload.get(k)
        if isinstance(v, str):
            m = re.match(r"^(\d{4})[-]?(\d{2})[-]?(\d{2})", v.strip())
            if m: return "-".join(m.groups())
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")


def classify(payload: dict[str, Any], rel: str):
    s = payload.get("schema") if isinstance(payload.get("schema"), str) else None
    v = payload.get("version") if isinstance(payload.get("version"), str) else None
    if s == "wof-python-launcher-windows-proof-v1": return "PYLAUNCH", "PYLAUNCH_PROOF", s, v
    if s == "wof-052l-fleet-supervisor-v1": return "WOF-052L Fleet", "WOF052L_FLEET_MERGED", s, v
    if s == "wof-052l-recorder-v1": return "WOF-052L", "WOF052L_ROOM" if payload.get("roomId") is not None else "WOF052L_MERGED", s, v
    if v == "wof-browser-fleet-v1": return "Browser Fleet", "BROWSER_FLEET_STATUS", s, v
    a = payload.get("artifact")
    if a == "wof-alpha-rc5": return "Regression", "ALPHA_REGRESSION_RESULT", s, a
    if a == "wof-alpha-rc5-independent-qa-retest": return "Alpha QA", "ALPHA_QA_RESULT", s, a
    t = payload.get("toolkit")
    if t in {"wof-windows-operator-toolkit-v1", "wof-windows-operator-toolkit-v2-cn"}:
        if isinstance(payload.get("checks"), list) and "overall" in payload: return "Regression", "REGRESSION_SUMMARY", s, t
        if isinstance(payload.get("components"), dict) and "platform" in payload: return "Diagnostics", "DIAGNOSTICS_SUMMARY", s, t
        if "included" in payload and "created" in payload: return "Toolkit", "PACKAGE_MANIFEST", s, t
    low = rel.lower().replace("\\", "/")
    if "regression" in low and isinstance(payload.get("checks"), list): return "Regression", "REGRESSION_SUMMARY", s, v
    if "diagnostics" in low and isinstance(payload.get("components"), dict): return "Diagnostics", "DIAGNOSTICS_SUMMARY", s, v
    if isinstance(payload.get("instances"), list) and "readOnly" in payload and "ramWrites" in payload: return "Browser Fleet", "BROWSER_FLEET_STATUS", s, v
    return "未知 JSON", "UNKNOWN_JSON", s, v


def classify_text(rel: str):
    low = rel.lower().replace("\\", "/"); name = Path(rel).name.lower()
    if name == "toolkit.log": return "Toolkit", "TOOLKIT_LOG"
    if "regression" in low or name.endswith((".stdout.txt", ".stderr.txt")): return "Regression", "REGRESSION_LOG"
    if "diagnostics" in low: return "Diagnostics", "DIAGNOSTICS_LOG"
    if "pylaunch" in low or "live_proof" in low: return "PYLAUNCH", "PYLAUNCH_LOG"
    if "recorder" in low or "052l" in low: return "WOF-052L", "WOF052L_LOG"
    if "fleet" in low: return "Browser Fleet", "BROWSER_FLEET_LOG"
    return "未知日志", "LOG"


def add(rec: dict[str, Any], code: str, severity: str, message: str): rec["anomalies"].append({"code": code, "severity": severity, "message": message})


def safety_source(payload: dict[str, Any]):
    for k in ("safety", "preservedRc4SafetyGates", "blockers"):
        if isinstance(payload.get(k), dict): return payload[k], k
    return payload, "top-level"


def check_safety(rec: dict[str, Any], payload: dict[str, Any], required: bool):
    src, label = safety_source(payload); checks = rec["checks"]
    for k in ("readOnly", "ramWrites", "inputInjection"):
        if required and k not in src: add(rec, "MISSING_FIELD", "ERROR", f"缺少安全字段 {label}.{k}")
    ro, rw, ii = src.get("readOnly"), src.get("ramWrites"), src.get("inputInjection")
    checks["readOnly"] = "PASS" if ro is True else ("MISSING" if ro is None else "FAIL")
    checks["ramWritesZero"] = "PASS" if rw == 0 and rw is not True else ("MISSING" if rw is None else "FAIL")
    checks["inputInjectionFalse"] = "PASS" if ii is False else ("MISSING" if ii is None else "FAIL")
    if ro is not None and ro is not True: add(rec, "READ_ONLY_NOT_TRUE", "CRITICAL", f"readOnly 不是 true：{ro!r}")
    if rw is not None and not (rw == 0 and rw is not True): add(rec, "RAM_WRITES_NONZERO", "CRITICAL", f"ramWrites 非 0：{rw!r}")
    if ii is not None and ii is not False: add(rec, "INPUT_INJECTION_NOT_FALSE", "CRITICAL", f"inputInjection 不是 false：{ii!r}")


def world_pylaunch(p):
    check = dct(p.get("checks")).get("World 921031"); h = p.get("worldSha256")
    if isinstance(h, str) and h and h.lower() != WORLD_SHA256: return "FAIL", f"SHA-256 不匹配：{h}"
    if check == "OK" and (not h or str(h).lower() == WORLD_SHA256): return "PASS", None
    if check is None and not h: return "MISSING", "缺少 World 921031 身份结果"
    return "FAIL", f"World 921031 未确认：{check!r}"


def world_recorder(p, kind):
    if kind == "WOF052L_ROOM":
        h = dct(p.get("identity")).get("sha256")
        if not h: return "MISSING", "单房间结果缺少 identity.sha256"
        return ("PASS", None) if str(h).lower() == WORLD_SHA256 else ("FAIL", f"identity.sha256 不匹配：{h}")
    pol = dct(p.get("identityPolicy")); label = str(pol.get("required") or ""); h = pol.get("sha256")
    if not label and not h: return "MISSING", "merged 结果缺少 identityPolicy"
    if WORLD_LABEL not in label: return "FAIL", f"identityPolicy.required 不是 {WORLD_LABEL}：{label!r}"
    return ("PASS", None) if str(h or "").lower() == WORLD_SHA256 else ("FAIL", f"identityPolicy.sha256 不匹配：{h!r}")


def world_alpha(p, kind):
    if kind == "ALPHA_REGRESSION_RESULT":
        label, h = str(p.get("supportedIdentity") or ""), p.get("goldenSha256")
        if WORLD_LABEL.lower() not in label.lower(): return "FAIL", f"supportedIdentity 未确认 {WORLD_LABEL}：{label!r}"
        return ("PASS", None) if str(h or "").lower() == WORLD_SHA256 else ("FAIL", f"goldenSha256 不匹配：{h!r}")
    g = dct(p.get("preservedRc4SafetyGates")); h = g.get("goldenSha256")
    if g.get("exactWorld921031Full1MiBSha256Gate") is not True: return "FAIL", "QA 结果未确认 exact World 921031 full SHA-256 gate"
    return ("PASS", None) if str(h or "").lower() == WORLD_SHA256 else ("FAIL", f"goldenSha256 不匹配：{h!r}")


def check_world(rec: dict[str, Any], p: dict[str, Any]):
    k = rec["kind"]; required = k in {"PYLAUNCH_PROOF", "WOF052L_ROOM", "WOF052L_MERGED", "ALPHA_REGRESSION_RESULT", "ALPHA_QA_RESULT"}
    if k == "PYLAUNCH_PROOF": st, detail = world_pylaunch(p)
    elif k in {"WOF052L_ROOM", "WOF052L_MERGED"}: st, detail = world_recorder(p, k)
    elif k in {"ALPHA_REGRESSION_RESULT", "ALPHA_QA_RESULT"}: st, detail = world_alpha(p, k)
    else: st, detail = "NOT_APPLICABLE", None
    rec["checks"]["world921031"] = st
    if required and st == "MISSING": add(rec, "WORLD_IDENTITY_MISSING", "ERROR", detail or "缺少 World 921031 身份字段")
    if required and st == "FAIL": add(rec, "WORLD_IDENTITY_MISMATCH", "CRITICAL", detail or "World 921031 身份不匹配")


def validate(rec: dict[str, Any], p: dict[str, Any]):
    known = rec.get("schema") in KNOWN_SCHEMAS or rec.get("version") in KNOWN_VERSIONS or rec.get("version") in KNOWN_ARTIFACTS
    rec["checks"]["knownVersion"] = "PASS" if known else "FAIL"
    if not known: add(rec, "UNKNOWN_SCHEMA", "WARNING", f"未知或未登记的 schema/版本：{rec.get('schema') or rec.get('version') or '未提供 schema/version'}")
    req = rec["kind"] in {"PYLAUNCH_PROOF", "WOF052L_ROOM", "WOF052L_MERGED", "WOF052L_FLEET_MERGED", "BROWSER_FLEET_STATUS", "REGRESSION_SUMMARY", "DIAGNOSTICS_SUMMARY"}
    check_safety(rec, p, req); check_world(rec, p)
    if rec["kind"] == "PYLAUNCH_PROOF" and "automatedResult" not in p: add(rec, "MISSING_FIELD", "ERROR", "PYLAUNCH proof 缺少 automatedResult")
    if rec["kind"].startswith("WOF052L") and "runId" not in p: add(rec, "MISSING_FIELD", "ERROR", "WOF-052L 结果缺少 runId")
    if rec["kind"] == "BROWSER_FLEET_STATUS" and not isinstance(p.get("instances"), list): add(rec, "MISSING_FIELD", "ERROR", "Browser Fleet 缺少 instances 数组")


def record_for(root: Path, path: Path, seen: dict[str, str]):
    rel = path.relative_to(root).as_posix()
    try: st = path.stat(); size, mt = st.st_size, st.st_mtime; data = path.read_bytes(); err = None
    except OSError as e: size, mt, data, err = 0, time.time(), b"", str(e)
    digest = sha(data) if not err else ""
    rec = {"path": rel, "bytes": size, "sha256": digest, "kind": "UNKNOWN", "tool": "未知", "schema": None, "version": None,
           "runId": None, "roomId": None, "date": datetime.fromtimestamp(mt).strftime("%Y-%m-%d"), "duplicateOf": None,
           "checks": {"readable": "FAIL" if err else "PASS"}, "anomalies": []}
    if err: rec["kind"] = "UNREADABLE"; add(rec, "READ_ERROR", "ERROR", f"无法读取文件：{err}"); return rec
    if digest in seen: rec["duplicateOf"] = seen[digest]; add(rec, "DUPLICATE_FILE", "INFO", f"内容重复，首个文件：{seen[digest]}")
    else: seen[digest] = rel
    if path.suffix.lower() != ".json":
        rec["tool"], rec["kind"] = classify_text(rel); rec["runId"] = run_hint(rel)
        rec["checks"].update({k: "NOT_APPLICABLE" for k in ("jsonReadable", "knownVersion", "world921031", "readOnly", "ramWritesZero", "inputInjectionFalse")}); return rec
    try: p = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        rec["kind"], rec["tool"] = "BROKEN_JSON", "损坏 JSON"; rec["checks"]["jsonReadable"] = "FAIL"; add(rec, "BROKEN_JSON", "ERROR", f"JSON 无法解析：{e}"); return rec
    rec["checks"]["jsonReadable"] = "PASS"
    if not isinstance(p, dict): rec["kind"], rec["tool"] = "UNKNOWN_JSON", "未知 JSON"; add(rec, "JSON_ROOT_NOT_OBJECT", "WARNING", "JSON 根节点不是对象"); return rec
    rec["tool"], rec["kind"], rec["schema"], rec["version"] = classify(p, rel); rec["date"] = date_of(p, mt)
    run = p.get("runId") or p.get("managerRunId"); rec["runId"] = str(run) if isinstance(run, (str, int)) and str(run) else run_hint(rel)
    room = p.get("roomId"); rec["roomId"] = str(room) if isinstance(room, (str, int)) and str(room) else None
    validate(rec, p); return rec


def summarize(root: Path, records: list[dict[str, Any]]):
    sev, codes, tools, kinds, dates, world = Counter(), Counter(), Counter(), Counter(), Counter(), Counter(); safety = {k: Counter() for k in ("readOnly", "ramWritesZero", "inputInjectionFalse")}; runs = {}
    for r in records:
        tools[r["tool"]] += 1; kinds[r["kind"]] += 1; dates[r["date"]] += 1; world[r["checks"].get("world921031", "NOT_APPLICABLE")] += 1
        for k in safety: safety[k][r["checks"].get(k, "NOT_APPLICABLE")] += 1
        for a in r["anomalies"]: sev[a["severity"]] += 1; codes[a["code"]] += 1
        if r["runId"]:
            x = runs.setdefault(r["runId"], {"tools": set(), "dates": set(), "rooms": set(), "files": [], "anomalyCount": 0}); x["tools"].add(r["tool"]); x["dates"].add(r["date"]); x["files"].append(r["path"]); x["anomalyCount"] += sum(a["severity"] != "INFO" for a in r["anomalies"])
            if r["roomId"]: x["rooms"].add(r["roomId"])
    rr = [{"runId": k, "tools": sorted(v["tools"]), "dates": sorted(v["dates"]), "rooms": sorted(v["rooms"]), "files": sorted(v["files"]), "anomalyCount": v["anomalyCount"]} for k, v in runs.items()]
    rr.sort(key=lambda x: (x["dates"][-1] if x["dates"] else "", x["runId"]), reverse=True)
    critical, errors = sev["CRITICAL"], sev["ERROR"]; overall = "FAIL" if critical else ("ATTENTION" if errors or sev["WARNING"] else "PASS")
    unknown = sum(r["kind"] in {"UNKNOWN_JSON", "BROKEN_JSON", "UNREADABLE", "LOG"} or r["tool"].startswith(("未知", "损坏")) for r in records)
    return {"schema": SUMMARY_SCHEMA, "version": VERSION, "generatedAt": utc_iso(), "sourceRoot": str(root), "ingestorSafety": SAFETY, "overall": overall,
            "counts": {"files": len(records), "json": sum(r["path"].lower().endswith(".json") for r in records), "logs": sum(not r["path"].lower().endswith(".json") for r in records), "recognized": len(records)-unknown, "unknownOrBroken": unknown, "duplicates": sum(bool(r["duplicateOf"]) for r in records), "runs": len(rr), "rooms": len({r["roomId"] for r in records if r["roomId"]}), "critical": critical, "errors": errors, "warnings": sev["WARNING"], "info": sev["INFO"]},
            "safetySummary": {k: dict(sorted(v.items())) for k, v in safety.items()}, "world921031Summary": dict(sorted(world.items())), "tools": dict(sorted(tools.items())), "kinds": dict(sorted(kinds.items())), "dates": dict(sorted(dates.items(), reverse=True)), "anomalyCodes": dict(sorted(codes.items())), "runs": rr, "files": sorted(records, key=lambda r: r["path"].lower())}


def summary_text(s):
    c, w = s["counts"], s.get("world921031Summary", {}); cn = {"PASS": "通过", "FAIL": "失败", "ATTENTION": "需注意"}.get(s["overall"], s["overall"])
    lines = ["WOF 自动结果汇总", "="*60, f"生成时间：{s['generatedAt']}", f"扫描目录：{s['sourceRoot']}", f"总体结果：{cn}", "", "安全边界：只读模式；游戏内存写入 0；不注入游戏输入。", "", "文件统计", f"- 总文件：{c['files']}", f"- JSON：{c['json']}", f"- 日志/文本：{c['logs']}", f"- 已识别：{c['recognized']}", f"- 未知/损坏：{c['unknownOrBroken']}", f"- 重复文件：{c['duplicates']}", f"- Run：{c['runs']}", f"- Room：{c['rooms']}", "", "异常统计", f"- 严重安全/身份异常：{c['critical']}", f"- 错误：{c['errors']}", f"- 警告：{c['warnings']}", f"- 信息：{c['info']}", "", "World 921031", f"- 已确认：{w.get('PASS',0)}", f"- 不匹配：{w.get('FAIL',0)}", f"- 缺少身份字段：{w.get('MISSING',0)}", f"- 不适用：{w.get('NOT_APPLICABLE',0)}", "", "按工具统计"]
    lines += [f"- {k}：{v}" for k, v in s.get("tools", {}).items()]; lines += ["", "需要处理的异常"]
    bad = [(r, [a for a in r["anomalies"] if a["severity"] != "INFO"]) for r in s["files"]]; bad = [(r,a) for r,a in bad if a]
    if not bad: lines.append("- 未发现需要处理的异常。")
    for r, aa in bad:
        lines.append(f"- {r['path']} [{r['tool']}]"); lines += [f"  · {a['severity']} / {a['code']}：{a['message']}" for a in aa]
    lines += ["", "重复文件"]; dup = [r for r in s["files"] if r["duplicateOf"]]; lines += [f"- {r['path']} -> {r['duplicateOf']}" for r in dup] if dup else ["- 无。"]
    lines += ["", "说明", "- 原始证据没有被删除、移动或修改。", "- 单个损坏文件不会阻止其他文件整理。", "- JSON key/schema 保持英文以便自动化；本文件面向普通用户使用简体中文。", ""]
    return "\n".join(lines)


def make_zip(root: Path, out: Path, sp: Path, tp: Path, records):
    z = out / f"WOF_结果包_{stamp()}.zip"; manifest = {"version": VERSION, "createdAt": utc_iso(), "sourceRoot": str(root), "includedEvidence": [], "duplicateEvidenceSkipped": []}
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as a:
        a.write(sp, "SUMMARY.json"); a.write(tp, "结果汇总.txt")
        for r in records:
            if r["duplicateOf"]: manifest["duplicateEvidenceSkipped"].append({"path": r["path"], "duplicateOf": r["duplicateOf"]}); continue
            p = root / Path(r["path"])
            try: a.write(p, "evidence/" + r["path"]); manifest["includedEvidence"].append(r["path"])
            except OSError: pass
        a.writestr("PACKAGE_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2)+"\n")
    return z


def ingest(root: Path, *, output_parent: Path | None = None, make_package=False):
    root = root.expanduser().resolve(); root.mkdir(parents=True, exist_ok=True); seen = {}; records = [record_for(root, p, seen) for p in sorted(source_files(root), key=lambda x: str(x).lower())]; s = summarize(root, records)
    parent = output_parent.expanduser().resolve() if output_parent else root / GENERATED_DIR_NAME; out = parent / stamp(); i = 1
    while out.exists(): out = parent / f"{stamp()}_{i:02d}"; i += 1
    out.mkdir(parents=True); sp, tp = out/"SUMMARY.json", out/"结果汇总.txt"; write_json(sp, s); write_text(tp, summary_text(s)); z = make_zip(root, out, sp, tp, records) if make_package else None
    return s, sp, tp, z


def main(argv=None):
    p = argparse.ArgumentParser(description="WOF Evidence Auto-Ingestor / 自动结果整理器"); p.add_argument("--root", type=Path, default=default_results_root(), help="结果根目录，默认 Documents/WOF_RESULTS"); p.add_argument("--output-parent", type=Path); p.add_argument("--package", action="store_true"); p.add_argument("--quiet", action="store_true"); a = p.parse_args(argv)
    try: s, sp, tp, z = ingest(a.root, output_parent=a.output_parent, make_package=a.package)
    except Exception as e: print("自动结果整理器无法完成本次扫描。", file=sys.stderr); print(f"技术详情：{e}", file=sys.stderr); print("原始证据没有被修改；游戏没有受到影响。", file=sys.stderr); return 2
    if not a.quiet:
        c=s["counts"]; print("\nWOF 自动结果整理完成\n"+"-"*60); print("总体结果："+{"PASS":"通过","FAIL":"失败","ATTENTION":"需注意"}.get(s["overall"],s["overall"])); print(f"已扫描：{c['files']}；已识别：{c['recognized']}；未知/损坏：{c['unknownOrBroken']}"); print(f"严重异常：{c['critical']}；错误：{c['errors']}；警告：{c['warnings']}；重复：{c['duplicates']}"); print(f"SUMMARY.json：{sp}\n中文汇总：{tp}"); print(f"结果包：{z}" if z else "未生成 ZIP 结果包。"); print("原始证据未被删除、移动或修改。\n只读模式：开启；游戏内存写入：0；游戏输入注入：0。")
    return 1 if s["overall"] == "FAIL" else 0


if __name__ == "__main__": raise SystemExit(main())
