import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve()
OPTOOLKIT = HERE.parents[1]
REPO = HERE.parents[3]
if str(OPTOOLKIT) not in sys.path:
    sys.path.insert(0, str(OPTOOLKIT))

owner = importlib.import_module("owner_zh_cn")


class ChineseOwnerUxTests(unittest.TestCase):
    def test_operator_translation_values_are_chinese(self):
        self.assertEqual(owner.translate_text("PASS"), "通过")
        self.assertEqual(owner.translate_text("FAIL"), "失败")
        self.assertEqual(owner.translate_text("READY"), "已就绪")
        self.assertEqual(owner.translate_text("MISSING"), "缺失")
        self.assertEqual(owner.translate_text("1 Update Project"), "1 更新项目")
        self.assertEqual(owner.translate_text("6 运行真人浏览器验证"), "6 打开 WOF 头顶显示")
        self.assertEqual(owner.translate_prompt("Choose 0-9: "), "请选择 0-9：")

    def test_cmd_entrypoints_enable_utf8_and_use_chinese_frontends(self):
        cases = [
            (REPO / "WOF_TOOLKIT.cmd", "parallel\\OPTOOLKIT\\owner_zh_cn.py"),
            (REPO / "parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd", "fleet_owner_zh_cn.py"),
            (REPO / "parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd", "owner_zh_cn.py"),
        ]
        for path, frontend in cases:
            text = path.read_text(encoding="utf-8")
            self.assertIn("chcp 65001", text, path.name)
            self.assertIn("PYTHONUTF8=1", text, path.name)
            self.assertIn("PYTHONIOENCODING=utf-8", text, path.name)
            self.assertIn(frontend, text, path.name)

    def test_frontends_contain_required_chinese_owner_labels(self):
        fleet = (REPO / "parallel/BROWSER_FLEET/fleet_owner_zh_cn.py").read_text(encoding="utf-8")
        recorder = (REPO / "parallel/WOF052L_RECORDER/owner_zh_cn.py").read_text(encoding="utf-8")
        toolkit = (REPO / "parallel/OPTOOLKIT/owner_zh_cn.py").read_text(encoding="utf-8")
        for required in ["浏览器实例", "WOF 页面", "Worker 已找到", "游戏内存写入：0", "技术详情："]:
            self.assertIn(required, fleet)
        for required in ["在线房间", "已完成房间", "保存目录", "自检通过", "技术详情："]:
            self.assertIn(required, recorder)
        for required in ["更新项目", "运行回归测试", "收集诊断信息", "结果包已生成", "技术详情："]:
            self.assertIn(required, toolkit)

    def test_toolkit_recorder_action_keeps_child_console_chinese(self):
        src = (REPO / "parallel/OPTOOLKIT/owner_zh_cn.py").read_text(encoding="utf-8")
        self.assertIn('parallel/WOF052L_RECORDER/owner_zh_cn.py', src)
        self.assertNotIn('self.root / "parallel/WOF052L_RECORDER/recorder.py"', src)

    def test_menu_six_selects_only_pinned_production_top_overlay(self):
        src = (REPO / "parallel/OPTOOLKIT/owner_zh_cn.py").read_text(encoding="utf-8")
        status = (REPO / "parallel/PYLAUNCH/wof_launcher/render_measurement_ui.py").read_text(encoding="utf-8")
        self.assertIn('parallel/PYLAUNCH/render_authority_measurement_entry.py', src)
        self.assertIn("sliceARuntimeCommit", src)
        self.assertIn('selectedNormalPath") == "production-top-overlay"', src)
        self.assertIn('productionOverlayEnabled") is True', src)
        self.assertIn('productionOverlaySuppressed") is False', src)
        self.assertIn('diagnosticOnly") is False', src)
        self.assertIn('whiteAcquisitionMarkerIsProduct") is False', src)
        for label in ["等待 WOF", "正在自动找 P1", "需要一次点击 P1 真实头部", "头顶已显示", "暂时丢失，恢复中", "BLOCKED"]:
            self.assertIn(label, status)
        self.assertIn("不会把空白浏览器当成功", src)
        self.assertIn("白色 acquisition marker 不是正式产品", src)
        self.assertNotIn('parallel/OPTOOLKIT/live_session.py', src)

    def test_menu_eight_is_local_self_contained_and_uses_core_zip_packager(self):
        src = (REPO / "parallel/OPTOOLKIT/owner_zh_cn.py").read_text(encoding="utf-8")
        core = (REPO / "parallel/OPTOOLKIT/toolkit.py").read_text(encoding="utf-8")
        self.assertIn("return super().package()", src)
        self.assertNotIn("EVIDENCE_INGESTOR", src)
        self.assertIn("zipfile.ZipFile", core)
        self.assertIn("self.results/'packages'", core)
        self.assertNotIn("latest('packages_')", core)

    def test_chinese_path_and_utf8_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "中文结果目录" / "状态.json"
            payload = {
                "schema": "owner-ux-smoke-v1",
                "status": "PASS",
                "readOnly": True,
                "ramWrites": 0,
                "inputInjection": False,
                "display": "中文路径正常",
            }
            owner.toolkit.wj(out, payload)
            loaded = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(loaded["schema"], "owner-ux-smoke-v1")
            self.assertEqual(loaded["status"], "PASS")
            self.assertTrue(loaded["readOnly"])
            self.assertEqual(loaded["ramWrites"], 0)
            self.assertFalse(loaded["inputInjection"])
            self.assertEqual(loaded["display"], "中文路径正常")

    def test_internal_machine_contracts_remain_english(self):
        fleet_core = (REPO / "parallel/BROWSER_FLEET/fleet_manager.py").read_text(encoding="utf-8")
        recorder_core = (REPO / "parallel/WOF052L_RECORDER/recorder.py").read_text(encoding="utf-8")
        self.assertIn('"readOnly": True', fleet_core)
        self.assertIn('"ramWrites": 0', fleet_core)
        self.assertIn('"inputInjection": False', fleet_core)
        self.assertIn('"schema":SCHEMA_VERSION', recorder_core)
        self.assertIn('"readOnly":True', recorder_core)
        self.assertIn('"ramWrites":0', recorder_core)
        self.assertIn('"inputInjection":False', recorder_core)

    def test_scope_does_not_route_through_product_alpha(self):
        for rel in [
            "parallel/BROWSER_FLEET/fleet_owner_zh_cn.py",
            "parallel/WOF052L_RECORDER/owner_zh_cn.py",
            "parallel/OPTOOLKIT/owner_zh_cn.py",
        ]:
            text = (REPO / rel).read_text(encoding="utf-8")
            self.assertNotIn("product/alpha/wof_alpha", text)


if __name__ == "__main__":
    unittest.main()
