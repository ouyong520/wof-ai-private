from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

from wof_launcher import browser, cdp
from wof_launcher.head_visual_tracker import (
    AUTO_SEED_MAX_FRAMES,
    HeadVisualError,
    MAX_OWNER_CLICKS_PER_AUTHORITY,
    P1HeadVisualTracker,
    SCHEMA,
    auto_seed_candidate,
    match_patch,
)

SURFACE={"width":320,"height":200,"left":0,"top":0,"pageX":0,"pageY":0,"layoutKey":"L"}
LIFECYCLE={"active":True,"generation":1,"type":7,"x":100.0,"y":90.0,"z":0.0}

class FakeSession:
    def __init__(self) -> None:
        self.surface=dict(SURFACE);self.click=None;self.click_count=0;self.armed=False;self.arm_count=0;self.expressions=[]
    def request(self,*_args,**_kwargs): return {}
    def close(self): return None
    def evaluate(self,expression:str,timeout:float=0):
        self.expressions.append(expression)
        if "status?.()" in expression:
            return {"schema":SCHEMA,"surface":dict(self.surface),"click":self.click,"clickCount":self.click_count,"armed":self.armed,"readOnly":True,"ramWrites":0,"inputInjection":False}
        if "armClick" in expression:
            if self.click_count>=1 or self.armed:return False
            self.armed=True;self.arm_count+=1;return True
        return True

class RenderAuthorityOwnerVisibleV3Tests(unittest.TestCase):
    @staticmethod
    def _avatar(draw:ImageDraw.ImageDraw,cx:int,cy:int)->None:
        draw.rectangle((cx-14,cy-14,cx+14,cy+14),fill=(190,130,80));draw.ellipse((cx-8,cy-9,cx+5,cy+7),fill=(35,30,22));draw.line((cx-12,cy-11,cx+11,cy+10),fill=(245,235,210),width=2)

    @classmethod
    def scene(cls,cx:int=102,cy:int=100,*,lookalike:bool=False,effect:bool=False,scene_actor:bool=True)->Image.Image:
        image=Image.new("RGB",(320,200),(18,18,18));draw=ImageDraw.Draw(image);cls._avatar(draw,38,30)
        if scene_actor:cls._avatar(draw,cx,cy)
        if lookalike:cls._avatar(draw,220,110)
        if effect:
            draw.rectangle((160,90,198,128),fill=(255,245,230));draw.line((158,110,200,108),fill=(255,255,255),width=5)
        return image

    @staticmethod
    def old_frame(cx:int,cy:int,lookalike:bool=False)->Image.Image:
        image=Image.new("RGB",(320,200),(18,18,18));draw=ImageDraw.Draw(image)
        draw.rectangle((cx-17,cy-17,cx+17,cy+17),fill=(190,130,80));draw.ellipse((cx-9,cy-11,cx+5,cy+8),fill=(35,30,22));draw.line((cx-14,cy-13,cx+13,cy+12),fill=(245,235,210),width=2)
        if lookalike:draw.rectangle((20,20,54,54),fill=(190,130,80))
        return image

    @classmethod
    def tracker(cls,frame:Image.Image)->tuple[P1HeadVisualTracker,FakeSession]:
        tracker=P1HeadVisualTracker(Path(tempfile.mkdtemp()));session=FakeSession();tracker._session=session;tracker._authority_key="authority";tracker._runtime_epoch="r"*16;tracker._layout=dict(SURFACE);tracker._patch_radius=12;tracker._capture=lambda _surface:frame.copy();return tracker,session

    def test_read_only_cdp_allows_screenshot_but_never_input(self):
        self.assertIn("Page.captureScreenshot",cdp.READ_ONLY_METHODS);self.assertNotIn("Input.dispatchMouseEvent",cdp.READ_ONLY_METHODS)

    def test_bounded_local_visual_match_tracks_motion_without_far_rebind(self):
        seed=self.old_frame(100,90).crop((82,72,118,108));moved=match_patch(self.old_frame(119,97),[seed],(100,90),18,50)
        self.assertTrue(moved["ok"]);self.assertLessEqual(abs(moved["center"][0]-119),4);self.assertLessEqual(abs(moved["center"][1]-97),4)
        far=match_patch(self.old_frame(240,60,True),[seed],(100,90),18,45);self.assertFalse(far["ok"])

    def test_safe_auto_seed_reaches_head_tracking_with_zero_click_and_never_arms_ui(self):
        tracker,session=self.tracker(self.scene());first=tracker.poll(dict(LIFECYCLE));second=tracker.poll(dict(LIFECYCLE))
        self.assertEqual(first["state"],"HEAD_ACQUIRING");self.assertEqual(second["state"],"HEAD_TRACKING");self.assertEqual(second["ownerClickCount"],0);self.assertEqual(second["seedSource"],"AUTO_P1_HUD_SCENE_UNIQUE");self.assertTrue(second["measurementMarkerVisible"]);self.assertEqual(session.arm_count,0)

    def test_ambiguous_auto_seed_hides_marker_then_arms_exactly_one_fallback(self):
        tracker,session=self.tracker(self.scene(lookalike=True))
        for _ in range(AUTO_SEED_MAX_FRAMES):status=tracker.poll(dict(LIFECYCLE))
        self.assertEqual(status["state"],"ONE_CLICK_REQUIRED");self.assertEqual(status["ownerClickCount"],0);self.assertFalse(status["measurementMarkerVisible"]);self.assertEqual(status["autoSeedReason"],"AMBIGUOUS_SCENE_P1");self.assertEqual(session.arm_count,1)
        again=tracker.poll(dict(LIFECYCLE));self.assertEqual(again["state"],"ONE_CLICK_REQUIRED");self.assertEqual(session.arm_count,1)
        session.armed=False;session.click_count=1;session.click={"x":102,"y":100,"layoutKey":"L","at":12345};fallback=tracker.poll(dict(LIFECYCLE))
        self.assertEqual(fallback["state"],"HEAD_TRACKING");self.assertEqual(fallback["ownerClickCount"],1);self.assertEqual(fallback["seedSource"],"OWNER_FALLBACK_CLICK");tracker._arm_once();self.assertEqual(session.arm_count,1)

    def test_second_click_and_hud_click_remain_impossible(self):
        self.assertEqual(MAX_OWNER_CLICKS_PER_AUTHORITY,1);tracker=P1HeadVisualTracker(Path(tempfile.mkdtemp()))
        with self.assertRaises(HeadVisualError):tracker._seed_from_click({"click":{"x":100,"y":90},"clickCount":2},self.old_frame(100,90),{"width":320,"height":200,"layoutKey":"L"})
        with self.assertRaises(HeadVisualError):tracker._seed_from_click({"click":{"x":38,"y":25,"layoutKey":"L","at":1},"clickCount":1},self.scene(),{"width":320,"height":200,"layoutKey":"L"})

    def test_hud_lookalike_enemy_and_bright_effect_are_not_scene_authority(self):
        hud_only=auto_seed_candidate(self.scene(scene_actor=False),12,dict(LIFECYCLE));self.assertFalse(hud_only["ok"])
        enemy_lookalike=auto_seed_candidate(self.scene(lookalike=True),12,dict(LIFECYCLE));self.assertFalse(enemy_lookalike["ok"]);self.assertEqual(enemy_lookalike["reason"],"AMBIGUOUS_SCENE_P1")
        with_effect=auto_seed_candidate(self.scene(effect=True),12,dict(LIFECYCLE));self.assertTrue(with_effect["ok"]);self.assertGreater(with_effect["center"][1],with_effect["sceneRegionTop"]);self.assertLess(abs(with_effect["center"][0]-102),18)

    def test_lifecycle_and_layout_invalidation_revoke_stale_visual_authority(self):
        tracker,session=self.tracker(self.scene());tracker.poll(dict(LIFECYCLE));tracker.poll(dict(LIFECYCLE));self.assertEqual(tracker.status()["templateCount"],1)
        tracker.update_lifecycle({**LIFECYCLE,"generation":2});revoked=tracker.status();self.assertEqual(revoked["state"],"HEAD_ACQUIRING");self.assertEqual(revoked["templateCount"],0);self.assertIsNone(revoked["center"]);self.assertFalse(revoked["measurementMarkerVisible"]);self.assertEqual(revoked["revocationReason"],"P1_GENERATION_CHANGED")
        tracker2,session2=self.tracker(self.scene());tracker2.poll(dict(LIFECYCLE));tracker2.poll(dict(LIFECYCLE));session2.surface={**SURFACE,"layoutKey":"L2"};layout=tracker2.poll(dict(LIFECYCLE));self.assertEqual(layout["templateCount"],0);self.assertEqual(layout["revocationReason"],"LAYOUT_CHANGED");self.assertFalse(layout["measurementMarkerVisible"])

    def test_confidence_loss_hides_and_confident_reacquisition_restores(self):
        tracker,_session=self.tracker(self.scene());tracker.poll(dict(LIFECYCLE));tracker.poll(dict(LIFECYCLE));tracker._capture=lambda _surface:Image.new("RGB",(320,200),(18,18,18));lost=tracker.poll(dict(LIFECYCLE));self.assertEqual(lost["state"],"HEAD_ACQUIRING");self.assertFalse(lost["measurementMarkerVisible"]);self.assertGreater(lost["lostFrames"],0)
        tracker._capture=lambda _surface:self.scene();recovered=tracker.poll(dict(LIFECYCLE));self.assertEqual(recovered["state"],"HEAD_TRACKING");self.assertTrue(recovered["measurementMarkerVisible"]);self.assertEqual(recovered["recoveryCount"],1)

    def test_browser_restores_known_owner_flow_without_blank_destination(self):
        url,source=browser.known_owner_game_url("https://example.test/wof");self.assertEqual(url,"https://example.test/wof");self.assertEqual(source,"explicit")
        captured=[]
        class Proc:pass
        with tempfile.TemporaryDirectory() as td,patch.object(browser.subprocess,"Popen",lambda args,**kwargs:captured.append(args) or Proc()):browser.launch_debug_browser(Path("/fake/chrome.exe"),user_data_dir=Path(td),restore_last_session=True)
        self.assertIn("--restore-last-session",captured[0]);self.assertNotIn("about:blank",captured[0])

    def test_owner_runner_and_worker_publish_zero_click_first_contract(self):
        root=Path(__file__).resolve().parents[2];runner=(root/"RENDER_AUTHORITY_V3/measurement_runner.py").read_text(encoding="utf-8");owner=(root/"OPTOOLKIT/owner_zh_cn.py").read_text(encoding="utf-8");worker=(root/"RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js").read_text(encoding="utf-8")
        for token in ("WAITING_FOR_WOF","EXACT_WORLD_LOCKED","CAMERA_PREPARING","RUNTIME_REDISCOVERY","COMPLETE","BLOCKED","ownerClickExpectedNormal"):self.assertIn(token,runner)
        self.assertNotIn("Y/Y-Z/Y+Z",runner);self.assertIn("正常路径无需点击",owner);self.assertIn("自动识别 P1",owner);self.assertIn("x:p1.x,y:p1.y,z:p1.z",worker);self.assertIn("零点击",worker)

    def test_package_manifest_pins_corrected_zero_click_runtime(self):
        parallel=Path(__file__).resolve().parents[2];repo=parallel.parent;manifest=json.loads((parallel/"OWNER_ONECLICK/package_manifest.json").read_text(encoding="utf-8"));component=manifest["components"]["renderAuthorityV3"]
        self.assertIn("zero-click-first",manifest["selectionPolicy"]);self.assertEqual(component["ownerClickExpectedNormal"],0);self.assertEqual(component["ownerClickFallbackMaximumPerAuthorityGeneration"],1);self.assertTrue(component["automaticSeedRequiredBeforeFallback"]);self.assertTrue(component["hudPortraitMayIdentifyButNeverSeedSceneHead"])
        rows={row["path"]:row["gitBlobSha"] for row in manifest["files"]}
        for rel in ("parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py","parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js","parallel/RENDER_AUTHORITY_V3/measurement_runner.py"):
            data=(repo/rel).read_bytes();actual=hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest();self.assertEqual(rows[rel],actual,rel)

if __name__=="__main__":unittest.main()
