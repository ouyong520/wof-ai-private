import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import hudanchor_proof as base
import proof_policy as policy


def sample(i, *, y, z, x, visual=None, score=9.0):
    s={"workerEpochMs":1000+i*100,"pageEpochMs":1030+i*100,"pageFound":True,"workerFound":True,
       "identitySha256":base.WORLD_SHA256,"player":{"x":x,"y":y,"z":z},
       "camera":{"address":"0xFF2468","value":20+i*5,"proofScore":score},
       "canvas":{"left":0,"top":0,"width":768,"height":448},"drawingBuffer":{"width":1536,"height":896},**base.SAFETY}
    if visual is not None:
        s["visualReference"]=visual
    return s


class PolicyTests(unittest.TestCase):
    def trace(self):
        ys=[70,76,82,76,70,74]
        zs=[0,0,16,8,0,12]
        return [sample(i,y=ys[i],z=zs[i],x=100+i*12) for i in range(6)]

    def test_reference_still_requires_absolute_anchor(self):
        ref={"worldSha256":base.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"}
        r=policy.evaluate_trace(self.trace(),projection_reference=ref)
        self.assertEqual(r["result"],"BLOCKED")
        self.assertIn("absolute above-head anchor not calibrated/proven",r["reasons"])

    def test_reference_plus_single_click_can_pass(self):
        t=self.trace()
        t[2]["visualReference"]={"nativeX":160,"nativeY":90,"kind":"single-calibration-click"}
        ref={"worldSha256":base.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"}
        r=policy.evaluate_trace(t,projection_reference=ref)
        self.assertEqual(r["result"],"PASS")
        self.assertIsNotNone(r["calibration"])
        self.assertTrue(r["cameraConfident"])

    def test_low_camera_confidence_blocks(self):
        t=self.trace()
        for s in t:
            s["camera"]["proofScore"]=3
        ref={"worldSha256":base.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z","absoluteAnchorProven":True}
        r=policy.evaluate_trace(t,projection_reference=ref)
        self.assertEqual(r["result"],"BLOCKED")
        self.assertIn("camera model confidence too low",r["reasons"])

    def test_camera_warmup_swap_then_tail_stable_passes(self):
        t=[]
        for i in range(18):
            row=sample(i,y=70+(i%4)*4,z=(0,8,16,0)[i%4],x=100+i*9)
            if i < 5:
                row["camera"]["address"]="0xFF1111" if i%2 else "0xFF2222"
            t.append(row)
        ref={"worldSha256":base.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z","absoluteAnchorProven":True}
        r=policy.evaluate_trace(t,projection_reference=ref)
        self.assertEqual(r["result"],"PASS")
        self.assertEqual(r["cameraAddress"],"0xFF2468")
        self.assertGreaterEqual(r["cameraDominance"],0.8)

    def test_calibration_before_camera_settles_blocks(self):
        t=self.trace()
        t[0]["camera"]["address"]="0xFF1111"
        t[0]["visualReference"]={"nativeX":160,"nativeY":90,"kind":"single-calibration-click"}
        ref={"worldSha256":base.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"}
        r=policy.evaluate_trace(t,projection_reference=ref)
        self.assertEqual(r["result"],"BLOCKED")
        self.assertIn("calibration camera differs from stable camera",r["reasons"])

    def test_absolute_reference_can_remove_click(self):
        ref={"worldSha256":base.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z","absoluteAnchorProven":True}
        self.assertEqual(policy.evaluate_trace(self.trace(),projection_reference=ref)["result"],"PASS")


if __name__=='__main__':
    unittest.main()
