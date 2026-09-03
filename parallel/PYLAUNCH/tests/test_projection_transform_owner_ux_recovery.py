from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
ROOT = HERE.parents[3]
OPTOOLKIT = ROOT / "parallel" / "OPTOOLKIT"
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))
if str(OPTOOLKIT) not in sys.path:
    sys.path.insert(0, str(OPTOOLKIT))

from wof_launcher.state import StatusStore


class ProjectionTransformOwnerUxRecoveryTests(unittest.TestCase):
    def test_actual_top_affine_fitter_recovers_nonlegacy_depth_and_jump_signs(self) -> None:
        top = ROOT / "parallel/HUDANCHOR_PROOF/wof_owner_projection_top.js"
        script = r"""
const fs=require('fs');const src=fs.readFileSync(process.argv[1],'utf8');
const assert=(x,m)=>{if(!x)throw new Error(m)};
const start=src.indexOf('function solve3('),end=src.indexOf('function layoutSnapshot()',start);
assert(start>=0&&end>start,'fit function block missing');
const MIN_TRACKED=36,MIN_HOLDOUT=8,FIT_RMS_MAX=3.25,FIT_HOLDOUT_RMS_MAX=4.0,FIT_HOLDOUT_MAX=8.0;
const finite=v=>typeof v==='number'&&Number.isFinite(v);
eval(src.slice(start,end));
const rows=[];
for(let i=0;i<70;i++){
  const worldX=40+((i*7)%23)*2,cameraRaw=100+((i*5)%17),worldY=18+((i*11)%19),worldZ=((i*7)%15);
  const n=((i%5)-2)*0.12;
  rows.push({worldX,cameraRaw,worldY,worldZ,headX:1.23*worldX-0.71*cameraRaw+96+n,headY:-0.84*worldY-1.37*worldZ+191-n});
}
const fit=fitProjection(rows);assert(fit.ok,'arbitrary affine fit failed: '+JSON.stringify(fit));
assert(Math.abs(fit.coefficients.xWorld-1.23)<.03,'worldX coefficient drift');
assert(Math.abs(fit.coefficients.xCameraRaw+0.71)<.03,'camera coefficient/sign drift');
assert(Math.abs(fit.coefficients.floorY+0.84)<.03,'depth coefficient/sign drift');
assert(Math.abs(fit.coefficients.z+1.37)<.03,'jump Z coefficient/sign drift');
assert(fit.residuals.holdoutRms<1,'holdout residual unexpectedly high');
const noDepth=rows.map(x=>({...x,worldY:20,headY:-0.84*20-1.37*x.worldZ+191}));
assert(fitProjection(noDepth).reason==='NEED_DEPTH_COVERAGE','depth undercoverage must fail closed');
const noJump=rows.map(x=>({...x,worldZ:0,headY:-0.84*x.worldY+191}));
assert(fitProjection(noJump).reason==='NEED_JUMP_COVERAGE','jump undercoverage must fail closed');
const noisy=rows.map((x,i)=>({...x,headX:x.headX+(i%2?20:-20),headY:x.headY+(i%3?15:-15)}));
assert(fitProjection(noisy).reason==='RESIDUAL_GATE_FAILED','bad residuals must fail closed');
"""
        cp = subprocess.run(["node", "-e", script, str(top)], text=True, capture_output=True, check=False)
        self.assertEqual(0, cp.returncode, cp.stderr or cp.stdout)

    def test_normal_owner_surface_has_no_math_model_choice_or_candidate_flood(self) -> None:
        top = (ROOT / "parallel/HUDANCHOR_PROOF/wof_owner_projection_top.js").read_text(encoding="utf-8")
        owner = (ROOT / "parallel/OPTOOLKIT/owner_zh_cn.py").read_text(encoding="utf-8")
        for forbidden in ("Y-Z", "Y+Z", "选择模型", "候选模型"):
            self.assertNotIn(forbidden, top)
            self.assertNotIn(forbidden, owner)
        self.assertNotIn("<button", top.lower())
        self.assertIn("getPoints:()=>[]", top)
        self.assertIn("maxCalibrationClicksPerAuthorityGeneration:1", top)
        self.assertIn("if(!running||pendingCal||cal||resultCache", top)
        self.assertIn("需要一次确认：请点一下 P1 头顶", top)
        self.assertIn("正在自动校准，请正常玩", top)
        self.assertIn("本次无法可靠确定头顶位置", top)
        self.assertIn("无需做数学选择", top)

    def test_production_modules_fail_closed_outside_live_proof_envelope(self) -> None:
        player = ROOT / "product/alpha/wof_alpha_player_head_warning.js"
        enemy = ROOT / "product/alpha/wof_alpha_enemy_target_labels.js"
        script = r"""
const P=require(process.argv[1]),E=require(process.argv[2]);
const assert=(x,m)=>{if(!x)throw new Error(m)};const epoch='a'.repeat(32),now=1000;
const authorityBinding={workerSessionId:'s',cameraAuthorityGeneration:1,p1LifecycleGeneration:1,launcherAuthorityKeySha256:'b'.repeat(64)};
const env={worldX:[40,90],worldY:[10,30],worldZ:[0,12],cameraRaw:[100,112]},motion={worldXStep:3,worldYStep:2,worldZStep:4,cameraRawStep:2};
const pp={schema:P.PROFILE_SCHEMA,status:'PROVED',proofId:'live-v2-test',projectionVersion:'live-v2-test',projectionKind:P.PROJECTION_KIND,activation:'LIVE_PROCESS_BOUND_OWNER_PROOF_V2',nativeWidth:384,nativeHeight:224,cameraAddress:0xFF1234,cameraSign:1,cameraScale:.75,worldXScale:1.2,xBias:80,floorYScale:-.8,zScale:-1.3,yBias:190,headClearanceNative:0,validationBounds:{minX:0,maxX:384,minY:0,maxY:224},validationEnvelope:env,motionEnvelope:motion,authorityBinding};
assert(P.validateProofProfile(pp).ok,'live player profile must validate');const built=P.buildProjectionSnapshot(pp,{cameraRaw:105,epoch,sampleAt:now});assert(built.ok,'projection build failed');
const db={width:384,height:224,contentRect:{x:0,y:0,width:384,height:224},sampleAt:now,confidence:1,epoch,projectionEpoch:epoch,mappingVersion:'m',fullscreen:false};
const outside=P.resolveAnchor({player:'P1',playerState:{present:true,x:100,y:20,z:0,sampleAt:now,confidence:1,epoch,projectionEpoch:epoch},projection:built.projection,drawingBufferState:db,nowMs:now,warningEpoch:epoch,warningSampleAt:now});
assert(!outside.ok&&outside.reason==='PROJECTION_OUTSIDE_PROOF_ENVELOPE','player outside envelope must suppress');
const ep={schema:E.PROJECTION_SCHEMA,verdict:E.PROJECTION_VERDICT,proofId:'live-v2-enemy',romSha256:E.SUPPORTED_ROM_SHA,nativeWidth:384,nativeHeight:224,cameraAddress:0xFF1234,cameraRead:'u16be',cameraSign:1,cameraScale:.75,projectionKind:E.AFFINE_KIND,worldXScale:1.2,xBias:80,floorYScale:-.8,zScale:-1.3,yBias:190,validationEnvelope:env,motionEnvelope:motion,authorityBinding,enemyHeadOffsetsByType:{18:-18},enemyHeadEvidenceByType:{18:{sampleCount:12,mad:1,slot:0,lifecycleGeneration:1}},epoch,projectionEpoch:epoch,sampleAt:now,confidence:1,cameraRaw:105,cameraX:78.75};
const plan=E.buildPlan({markers:[{slot:0,sourceId:'e',type:18,target7E:0,target:'P1',enemyX:95,enemyY:20,enemyZ:0,sampleAt:now,confidence:1,epoch,projectionEpoch:epoch}],projection:ep,drawingBufferState:db,nowMs:now});
assert(plan.labels.length===0&&plan.suppressed[0].reason==='PROJECTION_OUTSIDE_PROOF_ENVELOPE','enemy outside envelope must suppress');
"""
        cp = subprocess.run(["node", "-e", script, str(player), str(enemy)], text=True, capture_output=True, check=False)
        self.assertEqual(0, cp.returncode, cp.stderr or cp.stdout)
        adapter = (ROOT / "product/alpha/wof_alpha_field_adapter.js").read_text(encoding="utf-8")
        for token in ("CAMERA_TRANSITION_OUTSIDE_PROOF_MOTION", "PLAYER_MOTION_OUTSIDE_PROOF_MOTION", "ENEMY_MOTION_OUTSIDE_PROOF_MOTION", "suppressionCount"):
            self.assertIn(token, adapter)

    def test_tracker_fit_suppression_and_proof_result_survive_disconnect(self) -> None:
        proof_result = {"schema": "wof-owner-projection-proof-result-v2", "verdict": "IMPLEMENTATION_READY", "proofId": "live-v2-x"}
        ui = {
            "samples": 88,
            "workerSessionId": "worker-session-a",
            "lastSequence": 88,
            "guidance": {"actionZh": "正在自动验证头顶位置，请继续正常玩。", "nextCommandZh": "继续当前 menu 6 真人验证。"},
            "fit": {"ok": True, "sampleCount": 48, "residuals": {"holdoutRms": 1.5}, "coverage": {"worldZ": {"range": 12}}},
            "tracker": {"score": .91, "margin": .08, "accepted": 48, "rejected": 2},
            "enemyEvidenceTypes": [18, 22],
            "suppression": [{"reason": "LAYOUT_TRANSITION", "count": 2}],
            "authorityTimeline": [{"eventId": "projection:1", "kind": "AFFINE_FIT_READY", "sequence": 70}],
            "terminal": True,
            "verdict": "IMPLEMENTATION_READY",
        }
        store = StatusStore()
        store.update(alpha_status={"projectionRecovery": {"state": "PROVED_LIVE_PROCESS_AUTHORITY", "ui": ui, "proofResult": proof_result}}, state="CONNECTED")
        store.reset_runtime(error="terminal disconnect")
        progress = store.get().last_calibration_progress
        self.assertEqual(1.5, progress["fit"]["residuals"]["holdoutRms"])
        self.assertEqual(.91, progress["tracker"]["score"])
        self.assertEqual([18, 22], progress["enemyEvidenceTypes"])
        self.assertEqual("LAYOUT_TRANSITION", progress["suppression"][0]["reason"])
        self.assertEqual(proof_result, progress["proofResult"])

        import live_session
        compact = {"lastCalibrationProgress": progress}
        self.assertEqual(proof_result, live_session._extract_projection_result(compact))

    def test_menu6_zip_is_authoritative_and_generic_results_are_explicitly_not_live_proof(self) -> None:
        live = (ROOT / "parallel/OPTOOLKIT/live_session.py").read_text(encoding="utf-8")
        owner = (ROOT / "parallel/OPTOOLKIT/owner_zh_cn.py").read_text(encoding="utf-8")
        self.assertIn('WOF_LIVE_ACCEPTANCE_', live)
        self.assertIn('AUTHORITATIVE_LIVE_ACCEPTANCE_ZIP.txt', live)
        self.assertIn('genericWofResultsZipIsAuthoritativeLiveProof', live)
        self.assertIn('PROJECTION_RUNTIME_EVIDENCE.json', live)
        self.assertIn('WOF_LIVE_ACCEPTANCE_', owner)
        self.assertIn('WOF_RESULTS_', owner)

    def test_safety_and_frozen_target_semantics_remain_explicit(self) -> None:
        adapter = (ROOT / "product/alpha/wof_alpha_field_adapter.js").read_text(encoding="utf-8")
        labels = (ROOT / "product/alpha/wof_alpha_enemy_target_labels.js").read_text(encoding="utf-8")
        for token in ("readOnly:true", "ramWrites:0", "inputInjection:false"):
            self.assertIn(token, adapter)
        self.assertIn("{0:'P1',4:'P2',8:'P3'}", labels)


if __name__ == "__main__":
    unittest.main(verbosity=2)
