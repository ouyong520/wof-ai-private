from __future__ import annotations

from pathlib import Path

import owner_zh_cn

REQUIRED_ALPHA_SOURCE = (
    "parallel/PYLAUNCH/render_authority_measurement_entry.py",
    "parallel/RENDER_AUTHORITY_V3/measurement_runner.py",
    "parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py",
    "parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py",
    "parallel/PYLAUNCH/wof_launcher/render_authority_capture.py",
    "product/alpha/wof_alpha_hud.js",
    "product/alpha/wof_alpha_relative_head_anchor.js",
    "product/alpha/wof_alpha_relative_enemy_overlay.js",
)


def _current_main_source_gate(root: Path) -> tuple[bool, str, dict | None]:
    root = Path(root).resolve()
    if not (root / ".git").exists():
        return False, "current-main source 模式必须从 Git checkout 运行。", None
    missing = [rel for rel in REQUIRED_ALPHA_SOURCE if not (root / rel).is_file()]
    if missing:
        return False, "current-main Alpha production runtime 文件缺失：" + ", ".join(missing), None
    return (
        True,
        "current-main exact source production runtime；仅用于 Owner 实机验收，不发布 immutable package",
        {"sourceMode": "CURRENT_MAIN_EXACT_SOURCE", "immutablePackagePublished": False},
    )


def main() -> int:
    owner_zh_cn._visible_overlay_package_gate = _current_main_source_gate
    return owner_zh_cn.main()


if __name__ == "__main__":
    raise SystemExit(main())
