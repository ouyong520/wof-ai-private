from __future__ import annotations

import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]


class OwnerRootCurrentMainToolboxTests(unittest.TestCase):
    def test_git_checkout_uses_original_cmd_then_original_chinese_toolbox(self) -> None:
        cmd = (ROOT / "WOF_一键工具.cmd").read_text(encoding="utf-8")
        self.assertIn('if exist "%LAUNCH_DIR%\\.git" goto :source_checkout', cmd)
        self.assertIn('current_main_owner_entry.py" --root "%LAUNCH_DIR%"', cmd)
        self.assertNotIn('render_authority_measurement_entry.py" --root "%LAUNCH_DIR%"', cmd)
        self.assertIn('将打开原中文工具箱；只有选择菜单 6 才启动 Alpha。', cmd)

    def test_source_adapter_reuses_owner_menu_and_only_replaces_menu6_gate(self) -> None:
        source = (ROOT / "parallel" / "OPTOOLKIT" / "current_main_owner_entry.py").read_text(encoding="utf-8")
        self.assertIn("import owner_zh_cn", source)
        self.assertIn("owner_zh_cn._visible_overlay_package_gate = _current_main_source_gate", source)
        self.assertIn("return owner_zh_cn.main()", source)
        self.assertNotIn("subprocess", source)

    def test_current_main_menu6_keeps_live_product_open_for_p1_enemy_acceptance(self) -> None:
        cmd = (ROOT / "WOF_一键工具.cmd").read_text(encoding="utf-8")
        self.assertIn('set "WOF_ALPHA_LIVE_ACCEPTANCE_HOLD=1"', cmd)
        self.assertIn('set "WOF_ALPHA_ACCEPTANCE_COMMIT=!HEAD_SHA!"', cmd)
        self.assertIn('git -C "%LAUNCH_DIR%" fetch --quiet https://github.com/ouyong520/wof-ai-private.git', cmd)

    def test_non_git_portable_flow_still_uses_installed_owner_toolbox(self) -> None:
        cmd = (ROOT / "WOF_一键工具.cmd").read_text(encoding="utf-8")
        self.assertIn(':direct', cmd)
        self.assertIn('"!CURRENT_RELEASE!\\parallel\\OPTOOLKIT\\owner_zh_cn.py" --root "!CURRENT_RELEASE!"', cmd)


if __name__ == "__main__":
    unittest.main()
