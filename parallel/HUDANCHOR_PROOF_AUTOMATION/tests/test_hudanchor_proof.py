import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hudanchor_proof", HERE / "hudanchor_proof.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def sample(i, *, y=None, z=None, x=None, cam="0xFF1234", skew=0, identity=None, canvas=(768,448), db=(1536,896), visual=None):
    p={"x": float(x if x is not None else 100+i*8), "y": float(y if y is not None else 80+i), "z": float(z if z is not None else (0,8,16,8,0)[i%5])}
    s={"workerEpochMs":1000+i*100,"pageEpochMs":1000+i*100+skew,"pageFound":True,"workerFound":True,
       "identitySha256":identity or m.WORLD_SHA256,"player":p,"camera":{"address":cam,"value":20+i*5},
       "canvas":{"left":0,"top":0,"width":canvas[0],"height":canvas[1]},"drawingBuffer":{"width":db[0],"height":db[1]},**m.SAFETY}
    if visual is not None: s["visualReference"]={"nativeY":visual}
    return s

class ProofTests(unittest.TestCase):
    def test_two_context_sync(self):
        t=[sample(i,skew=35) for i in range(5)]; self.assertLessEqual(m.evaluate_trace(t,projection_reference={"worldSha256":m.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"})["maxContextSkewMs"],250)
    def test_stale_epoch_blocks(self):
        t=[sample(i,skew=400) for i in range(5)]; self.assertEqual(m.evaluate_trace(t,projection_reference={"worldSha256":m.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"})["result"],"BLOCKED")
    def test_wrong_identity_blocks(self):
        t=[sample(i,identity="0"*64) for i in range(5)]; self.assertIn("wrong World identity",m.evaluate_trace(t,projection_reference={"worldSha256":m.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"})["reasons"])
    def test_missing_worker_page(self):
        t=[sample(i) for i in range(5)]; t[0]["workerFound"]=False; t[1]["pageFound"]=False
        r=m.evaluate_trace(t,projection_reference={"worldSha256":m.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"}); self.assertIn("missing Worker",r["reasons"]); self.assertIn("missing page",r["reasons"])
    def test_resize_fullscreen_mapping_change_is_live_safe(self):
        t=[sample(i,canvas=(768,448),db=(1536,896)) for i in range(3)]+[sample(i+3,canvas=(1000,700),db=(2000,1400)) for i in range(3)]
        r=m.evaluate_trace(t,projection_reference={"worldSha256":m.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"}); self.assertTrue(r["mappingChanged"]); self.assertTrue(r["mappingValid"])
    def test_mapping_math_letterbox(self):
        c={"left":10,"top":20,"width":1000,"height":700}; x,y=m.client_to_native(510,370,c); self.assertAlmostEqual(x,192,places=4); self.assertAlmostEqual(y,112,places=4)
    def test_camera_scroll_trace_stable(self):
        t=[sample(i,cam="0xFF2468") for i in range(7)]; r=m.evaluate_trace(t,projection_reference={"worldSha256":m.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"}); self.assertTrue(r["cameraStable"])
    def test_depth_and_jump_excitation(self):
        ys=[70,76,82,76,70,74]; zs=[0,0,16,8,0,12]; t=[sample(i,y=ys[i],z=zs[i],x=100+i*12) for i in range(6)]
        r=m.evaluate_trace(t,projection_reference={"worldSha256":m.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"}); self.assertGreaterEqual(r["excitation"]["depthSpan"],4); self.assertGreaterEqual(r["excitation"]["jumpSpan"],4)
    def test_ambiguous_model_blocks_with_single_click(self):
        t=[sample(i) for i in range(6)]; t[2]["visualReference"]={"nativeY":100}
        r=m.evaluate_trace(t); self.assertEqual(r["result"],"BLOCKED"); self.assertIsNone(r["verticalModel"])
    def test_exact_good_trace_visual_selects_y_minus_z(self):
        ys=[80,84,88,86,82,78]; zs=[0,8,16,8,0,12]; t=[]
        for i,(y,z) in enumerate(zip(ys,zs)):
            visual=y-z+30
            t.append(sample(i,y=y,z=z,x=100+i*12,visual=visual))
        r=m.evaluate_trace(t); self.assertEqual(r["result"],"PASS"); self.assertEqual(r["verticalModel"],"Y-Z")
    def test_safety_invariants(self):
        t=[sample(i) for i in range(6)]; t[3]["ramWrites"]=1
        r=m.evaluate_trace(t,projection_reference={"worldSha256":m.WORLD_SHA256,"visuallyProven":True,"verticalModel":"Y-Z"}); self.assertEqual(r["result"],"BLOCKED"); self.assertIn("safety invariant mismatch",r["reasons"])
    def test_camera_scoring(self):
        rows=[{"address":"A","valid":.9,"strong":.8,"follow":.8,"range":120,"changes":30,"smooth":.8},{"address":"B","valid":.5,"strong":.4,"follow":.2,"range":10,"changes":3,"smooth":.2}]
        self.assertEqual(m.score_camera_rows(rows)[0]["address"],"A")

if __name__ == '__main__': unittest.main()
