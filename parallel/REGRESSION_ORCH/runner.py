from __future__ import annotations

from pathlib import Path
from typing import Any

import orchestrator as core


_CORE_DISCOVER_CANDIDATES = core.discover_candidates
_CORE_BUILD_ALLOWLIST_GUARD = core.build_allowlist_guard
_CORE_WRITE_OUTPUTS = core.write_outputs

IGNORED_PARTS = {
    ".venv",
    "venv",
    "env",
    "site-packages",
    "node_modules",
    "__pycache__",
    ".git",
}

DISCOVERY_V2_SUITES = {
    "PYLAUNCH": ("parallel/PYLAUNCH", "pylaunch_offline"),
    "Browser Fleet": ("parallel/BROWSER_FLEET", "browser_fleet"),
    "WOF-052L Recorder": ("parallel/WOF052L_RECORDER", "wof052l_recorder"),
    "Prospective Validator": ("parallel/PROSPECTIVE_VALIDATOR", "prospective_validator"),
}
RECORDER_V2_ENTRYPOINT = "parallel/WOF052L_RECORDER/owner_v2_zh_cn.py"
PROSPECTIVE_DISCOVERY_V2_TEST = "parallel/PROSPECTIVE_VALIDATOR/test_discovery_v2.py"


def _norm(path: str | Path) -> str:
    return str(path).replace("\\", "/").strip("/")


def is_generated_or_dependency_path(path: str | Path) -> bool:
    parts = {part.lower() for part in Path(path).parts}
    return bool(parts & IGNORED_PARTS)


def discover_candidates(root: Path) -> list[str]:
    return [
        path
        for path in _CORE_DISCOVER_CANDIDATES(root)
        if not is_generated_or_dependency_path(path)
    ]


def is_discovery_v2_safety_candidate(path: str | Path) -> bool:
    """Conservatively promote untrusted Discovery V2 tests outside known component roots.

    Parallel hardening/QA lanes are intentionally allowed to land outside the four
    component directories. A test path carrying DISCOVERY_V2 is therefore treated as
    safety-critical until it is explicitly reviewed and allowlisted.
    """
    path_n = _norm(path)
    if not core.is_test_candidate(Path(path_n)):
        return False
    return any("DISCOVERY_V2" in part.upper() for part in Path(path_n).parts)


def _under_root(path: str, root: str) -> bool:
    path_n = _norm(path)
    root_n = _norm(root)
    return path_n == root_n or path_n.startswith(root_n + "/")


def _suite_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row.get("id")): row for row in manifest.get("suites", [])}


def _command_mentions_path(suite: dict[str, Any], path: str) -> bool:
    basename = Path(path).name
    for command in suite.get("commands", []):
        argv = [str(token).replace("\\", "/") for token in command.get("argv", [])]
        if any(Path(token).name == basename for token in argv):
            return True
    return False


def _has_recorder_v2_selftest(suite: dict[str, Any]) -> bool:
    basename = Path(RECORDER_V2_ENTRYPOINT).name
    for command in suite.get("commands", []):
        argv = [str(token).replace("\\", "/") for token in command.get("argv", [])]
        if "--self-test" in argv and any(Path(token).name == basename for token in argv):
            return True
    return False


def _has_recorder_v2_compile(suite: dict[str, Any]) -> bool:
    basename = Path(RECORDER_V2_ENTRYPOINT).name
    for command in suite.get("commands", []):
        argv = [str(token).replace("\\", "/") for token in command.get("argv", [])]
        if "py_compile" in argv and any(Path(token).name == basename for token in argv):
            return True
    return False


def validate_discovery_v2_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    suites = _suite_map(manifest)
    allowlisted = {_norm(path) for path in manifest.get("allowlistedTestPaths", [])}
    guard_roots = {_norm(path) for path in manifest.get("guardRoots", [])}

    for component, (root, suite_id) in DISCOVERY_V2_SUITES.items():
        if _norm(root) not in guard_roots:
            errors.append(f"{component} 未纳入 guardRoots：{root}")
        suite = suites.get(suite_id)
        if not suite:
            errors.append(f"缺少 Discovery V2 required suite：{suite_id}")
            continue
        if not suite.get("safetyCritical"):
            errors.append(f"Discovery V2 suite 不是 safetyCritical：{suite_id}")
            continue

        for path in suite.get("requiredPaths", []):
            path_n = _norm(path)
            if not _under_root(path_n, root) or not core.is_test_candidate(Path(path_n)):
                continue
            if path_n not in allowlisted:
                errors.append(f"required test 未进入 allowlist：{path_n}")
            if not _command_mentions_path(suite, path_n):
                errors.append(f"required test 没有执行命令：{path_n}")

    component_roots = [root for root, _suite_id in DISCOVERY_V2_SUITES.values()]
    required_component_tests: set[str] = set()
    for _component, (root, suite_id) in DISCOVERY_V2_SUITES.items():
        suite = suites.get(suite_id)
        if not suite:
            continue
        for path in suite.get("requiredPaths", []):
            path_n = _norm(path)
            if _under_root(path_n, root) and core.is_test_candidate(Path(path_n)):
                required_component_tests.add(path_n)

    allowlisted_component_tests = {
        path
        for path in allowlisted
        if any(_under_root(path, root) for root in component_roots)
        and core.is_test_candidate(Path(path))
    }
    for path in sorted(allowlisted_component_tests - required_component_tests):
        errors.append(f"allowlist 中的 Discovery V2 test 未设为 required：{path}")

    prospective = suites.get("prospective_validator")
    if prospective:
        required = {_norm(path) for path in prospective.get("requiredPaths", [])}
        if PROSPECTIVE_DISCOVERY_V2_TEST not in allowlisted:
            errors.append("Prospective test_discovery_v2.py 未进入 allowlist")
        if PROSPECTIVE_DISCOVERY_V2_TEST not in required:
            errors.append("Prospective test_discovery_v2.py 不是 required path")
        if not _command_mentions_path(prospective, PROSPECTIVE_DISCOVERY_V2_TEST):
            errors.append("Prospective test_discovery_v2.py 没有 required command")

    recorder = suites.get("wof052l_recorder")
    if recorder:
        required = {_norm(path) for path in recorder.get("requiredPaths", [])}
        if RECORDER_V2_ENTRYPOINT not in required:
            errors.append("Recorder owner_v2_zh_cn.py 不是 required integration path")
        if not _has_recorder_v2_compile(recorder):
            errors.append("Recorder owner_v2_zh_cn.py 未纳入 py_compile integration surface")
        if not _has_recorder_v2_selftest(recorder):
            errors.append("Recorder owner_v2_zh_cn.py 未作为官方 V2 self-test entrypoint")

    return errors


def _append_block_reason(guard: dict[str, Any], reason: str) -> None:
    if guard.get("reasonZh"):
        guard["reasonZh"] = str(guard["reasonZh"]) + "；" + reason
    else:
        guard["reasonZh"] = reason
    guard["status"] = "BLOCKED"


def build_allowlist_guard(
    root: Path,
    manifest: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    guard, outside_unknown = _CORE_BUILD_ALLOWLIST_GUARD(root, manifest)

    promoted = sorted(
        path for path in outside_unknown
        if is_discovery_v2_safety_candidate(path)
    )
    if promoted:
        existing = list(guard.get("unallowlisted", []))
        guard["unallowlisted"] = sorted(set(existing + promoted))
        guard["promotedDiscoveryV2SafetyTests"] = promoted
        _append_block_reason(
            guard,
            "发现 guard 外新增 Discovery V2 safety-critical test，必须显式评审/allowlist："
            + "、".join(promoted),
        )
        promoted_set = set(promoted)
        outside_unknown = [path for path in outside_unknown if path not in promoted_set]
    else:
        guard["promotedDiscoveryV2SafetyTests"] = []

    contract_errors = validate_discovery_v2_manifest(manifest)
    guard["manifestContractStatus"] = "PASS" if not contract_errors else "BLOCKED"
    guard["contractErrors"] = contract_errors
    if contract_errors:
        _append_block_reason(
            guard,
            "Discovery V2 manifest 契约不完整：" + "；".join(contract_errors),
        )
    return guard, outside_unknown


def _status_for_suite_ids(
    suite_by_id: dict[str, dict[str, Any]],
    suite_ids: list[str],
) -> str:
    rows: list[dict[str, Any]] = []
    for suite_id in suite_ids:
        row = suite_by_id.get(suite_id)
        if row is None:
            return "BLOCKED"
        rows.append(row)
    return core.compute_offline_overall(rows)


def augment_summary(summary: dict[str, Any]) -> dict[str, Any]:
    suite_by_id = {str(row.get("id")): row for row in summary.get("suites", [])}
    contract_status = _status_for_suite_ids(
        suite_by_id,
        ["orchestrator_selftest", "allowlist_guard"],
    )

    components: dict[str, dict[str, Any]] = {}
    component_suite_ids: list[str] = []
    for component, (_root, suite_id) in DISCOVERY_V2_SUITES.items():
        component_suite_ids.append(suite_id)
        row = suite_by_id.get(suite_id)
        if row is None:
            components[component] = {
                "suiteId": suite_id,
                "status": "BLOCKED",
                "reasonZh": "required suite 未产生结果。",
            }
        else:
            components[component] = {
                "suiteId": suite_id,
                "status": row.get("status", "BLOCKED"),
                "reasonZh": row.get("reasonZh"),
                "failedCommands": list(row.get("failedCommands", [])),
            }

    component_health = _status_for_suite_ids(suite_by_id, component_suite_ids)
    summary["orchestratorContract"] = {
        "status": contract_status,
        "ready": contract_status == "PASS",
        "selfTestStatus": suite_by_id.get("orchestrator_selftest", {}).get("status", "BLOCKED"),
        "allowlistGuardStatus": suite_by_id.get("allowlist_guard", {}).get("status", "BLOCKED"),
        "meaningZh": "READY 仅表示编排器契约、自检和漏测门正确；组件自身 FAIL/BLOCKED 会继续真实暴露。",
    }
    summary["discoveryV2ComponentHealth"] = {
        "overall": component_health,
        "components": components,
    }
    return summary


def write_outputs(root: Path, summary: dict[str, Any]) -> None:
    augment_summary(summary)
    _CORE_WRITE_OUTPUTS(root, summary)

    contract = summary["orchestratorContract"]
    health = summary["discoveryV2ComponentHealth"]
    lines = [
        "Discovery V2 编排器契约 / 组件健康",
        "-" * 60,
        f"编排器契约：{contract['status']} / {'READY' if contract['ready'] else 'NOT READY'}",
        f"Discovery V2 组件健康：{health['overall']}",
    ]
    for component, row in health["components"].items():
        lines.append(f"- {component}: {row['status']}")
        if row.get("reasonZh"):
            lines.append(f"  原因：{row['reasonZh']}")
        for command in row.get("failedCommands", []):
            lines.append(f"  失败命令：{command}")
    lines.extend([
        "说明：编排器契约 READY 与组件健康分开报告；不会为了 overall green 吞掉组件 FAIL/BLOCKED。",
        "",
    ])

    text = core.TEXT_PATH.read_text(encoding="utf-8")
    marker = "离线 suites："
    block = "\n".join(lines)
    if marker in text:
        text = text.replace(marker, block + "\n" + marker, 1)
    else:
        text = block + "\n" + text
    core.TEXT_PATH.write_text(text, encoding="utf-8")


def install_guarded_runtime() -> None:
    core.discover_candidates = discover_candidates
    core.build_allowlist_guard = build_allowlist_guard
    core.write_outputs = write_outputs


def main() -> int:
    install_guarded_runtime()
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
