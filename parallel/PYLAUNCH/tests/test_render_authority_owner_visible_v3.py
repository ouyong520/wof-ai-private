from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

from wof_launcher import browser, cdp
from wof_launcher.head_visual_tracker import HeadVisualError, MAX_OWNER_CLICKS_PER_AUTHORITY, P1HeadVisualTracker, match_patch

class RenderAuthorityOwnerVisibleV3Tests(unittest.TestCase):
    @staticmethod
    def frame(cx: int, cy: int, lookalike: bool = False) -> Image.Image:
        image=Image.new("RGB",(320,200),(18,18,18));draw=ImageDraw.Draw(image)
        draw.rectangle((cx-17,cy-17,cx+17,cy+17),fill=(190,130,80));draw.ellipse((cx-9,cy-11,cx+5,cy+8),fill=(35,30,22));draw.line((cx-14,cy-13,cx+13,cy+12),fill=(245,235,210),width=2)
        if lookalike: draw.rectangle((20,20,54,54),fill=(190,130,80))
        return image

    def test_read_only_cdp_allows_screenshot_but_never_input(self):
        self.assertIn("Page.captureScreenshot",cdp.READ_ONLY_METHODS);self.assertNotIn("Input.dispatchMouseEvent",cdp.READ_ONLY_METHODS)

    def test_bounded_local_visual_match_tracks_motion_without_far_rebind(self):
        seed=self.frame(100,90).crop((82,72,118,108));moved=match_patch(self.frame(119,97),[seed],(100,90),18,50)
        self.assertTrue(moved["ok"]);self.assertLessEqual(abs(moved["center"][0]-119),4);self.assertLessEqual(abs(moved["center"][1]-97),4)
        far=match_patch(self.frame(240,60,True),[seed],(100,90),18,45);self.assertFalse(far["ok"])

    def test_one_click_budget_is_fail_closed(self):
        self.assertEqual(MAX_OWNER_CLICKS_PER_AUTHORITY,1);tracker=P1HeadVisualTracker(Path(tempfile.mkdtemp()))
        with self.assertRaises(HeadVisualError): tracker._seed_from_click({"click":{"x":100,"y":90},"clickCount":2},self.frame(100,90),{"width":320,"height":200})

    def test_lifecycle_change_revokes_stale_tracking(self):
        tracker=P1HeadVisualTracker(Path(tempfile.mkdtemp()));tracker._state="HEAD_TRACKING";tracker._p1_generation=1
        tracker.update_lifecycle({"active":True,"generation":2});self.assertEqual(tracker.status()["state"],"HEAD_ACQUIRING")
        tracker._state="HEAD_TRACKING";tracker.update_lifecycle({"active":False,"generation":2});self.assertEqual(tracker.status()["state"],"HEAD_ACQUIRING")

    def test_browser_restores_known_owner_flow_without_blank_destination(self):
        url,source=browser.known_owner_game_url("https://example.test/wof");self.assertEqual(url,"https://example.test/wof");self.assertEqual(source,"explicit")
        captured=[]
        class Proc: pass
        with tempfile.TemporaryDirectory() as td, patch.object(browser.subprocess,"Popen",lambda args,**kwargs:captured.append(args) or Proc()): browser.launch_debug_browser(Path("/fake/chrome.exe"),user_data_dir=Path(td),restore_last_session=True)
        self.assertIn("--restore-last-session",captured[0]);self.assertNotIn("about:blank",captured[0])

    def test_owner_entry_and_runner_have_required_visible_states(self):
        root=Path(__file__).resolve().parents[2];runner=(root/"RENDER_AUTHORITY_V3/measurement_runner.py").read_text(encoding="utf-8");owner=(root/"OPTOOLKIT/owner_zh_cn.py").read_text(encoding="utf-8")
        for token in ("WAITING_FOR_WOF","EXACT_WORLD_LOCKED","CAMERA_PREPARING","RUNTIME_REDISCOVERY","COMPLETE","BLOCKED"): self.assertIn(token,runner)
        self.assertNotIn("Y/Y-Z/Y+Z",runner);self.assertIn("Windows 右下角 WOF 托盘状态",owner);self.assertIn("最多点一次 P1 头顶",owner)

if __name__=="__main__": unittest.main()
