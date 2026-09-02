from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3] if "parallel" in HERE.parts else Path("/mnt/data")
PYLAUNCH = ROOT / "parallel/PYLAUNCH"
if PYLAUNCH.exists() and str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))


class CameraReadyStabilityRecoveryTests(unittest.TestCase):
    def _worker_path(self) -> Path:
        p = ROOT / "parallel/HUDANCHOR_PROOF/wof_owner_projection_worker.js"
        return p if p.exists() else Path("/mnt/data/wof_owner_projection_worker.js")

    def _top_path(self) -> Path:
        p = ROOT / "parallel/HUDANCHOR_PROOF/wof_owner_projection_top.js"
        return p if p.exists() else Path("/mnt/data/wof_owner_projection_top.js")

    def test_stable_ready_is_bounded_latched_and_exact_lock_only(self) -> None:
        script = r"""
const fs=require('fs');const src=fs.readFileSync(process.argv[1],'utf8');
const assert=(x,m)=>{if(!x)throw new Error(m)};
const buf=new ArrayBuffer(5_000_000),M=new Uint8Array(buf),U=new Uint32Array(buf),R=0x1000;U[0x2e39e4>>>2]=R;globalThis._0x515056={HEAPU8:M,HEAPU32:U};
let tick=null;globalThis.setInterval=(fn)=>{tick=fn;return 1};globalThis.clearInterval=()=>{};
class BC{constructor(){globalThis.__bc=this;this.messages=[]}postMessage(m){this.messages.push(m)}close(){}}globalThis.BroadcastChannel=BC;
const BADDR=a=>R+((((a-0xFF0000)&0xffff)^1));const setB=(a,v)=>{M[BADDR(a)]=v&255};
const setU16=(a,v)=>{setB(a,(v>>>8)&255);setB(a+1,v&255)};const setU32=(a,v)=>{setB(a,(v>>>24)&255);setB(a+1,(v>>>16)&255);setB(a+2,(v>>>8)&255);setB(a+3,v&255)};const setF=(a,v)=>setU32(a,Math.round(v*65536)>>>0);
const P=0xFFBE1C,A=0xFF1000,B=0xFF2000;setB(P,1);setF(P+4,100);setF(P+8,80);setF(P+12,0);setU16(A,0);setU16(B,0);
(0,eval)(src);assert(typeof tick==='function','worker tick missing');
function step(i,{b=false,freezeA=false}={}){setF(P+4,100+i);setU16(A,freezeA?99:i);if(b)setU16(B,i);tick();return globalThis.WOFOWNERPROJECTION.status();}
let firstQualified=null;
for(let i=1;i<140;i++){const s=step(i);if(s.cameraQuality.reason==='READY_STABILITY_WINDOW'){firstQualified=s;break;}}
assert(firstQualified,'must reach instant qualified state');
assert(firstQualified.cameraQuality.ready===false,'one instant qualified candidate must not READY');
assert(firstQualified.cameraQuality.stableSamples<firstQualified.cameraQuality.requiredStableSamples,'stable window must be incomplete');
let ready=null;for(let i=firstQualified.samples;i<firstQualified.samples+40;i++){const s=step(i+1);if(s.cameraQuality.ready){ready=s;break;}}
assert(ready,'same candidate must become READY after bounded stable window');
assert(ready.cameraAuthority&&ready.cameraAuthority.state==='READY','READY authority missing');
assert(ready.cameraAuthority.stableSamples>=20,'READY stability window too short');
assert(ready.cameraAuthority.sampleEnd>=ready.cameraAuthority.sampleStart,'proof sample window missing');
assert(ready.cameraAuthority.authorityId&&ready.cameraAuthority.authorityGeneration>=1,'authority identity/generation missing');
const id=ready.cameraAuthority.authorityId,gen=ready.cameraAuthority.authorityGeneration,address=ready.cameraAuthority.address;
const driftStart=ready.samples;for(let i=driftStart+1;i<driftStart+70;i++)ready=step(i,{b:true,freezeA:true});
assert(ready.cameraAuthority.authorityId===id&&ready.cameraAuthority.authorityGeneration===gen&&ready.cameraAuthority.address===address,'latched authority drifted after ranking change');
assert(ready.cameraQuality.ready===true&&ready.cameraQuality.authorityId===id,'owner-facing READY must remain authority-bound');
globalThis.__bc.onmessage({data:{schema:'wof-owner-projection-proof-v1',kind:'lock-camera',address:'0xFF2000',authorityId:id,authorityGeneration:gen}});
let s=globalThis.WOFOWNERPROJECTION.status();assert(!s.locked&&s.lockRejectReason&&s.lockRejectReason.reason==='AUTHORITY_ADDRESS_MISMATCH','wrong address must fail closed');
globalThis.__bc.onmessage({data:{schema:'wof-owner-projection-proof-v1',kind:'lock-camera',address,authorityId:id,authorityGeneration:gen+1}});
s=globalThis.WOFOWNERPROJECTION.status();assert(!s.locked&&s.lockRejectReason&&s.lockRejectReason.reason==='AUTHORITY_GENERATION_MISMATCH','wrong generation must fail closed');
globalThis.__bc.onmessage({data:{schema:'wof-owner-projection-proof-v1',kind:'lock-camera',address,authorityId:id,authorityGeneration:gen}});
s=globalThis.WOFOWNERPROJECTION.status();assert(s.locked&&s.locked.authorityId===id&&s.locked.authorityGeneration===gen&&s.locked.address===address,'exact READY authority lock failed');
assert(s.authorityTimeline.some(e=>e.kind==='CANDIDATE_GENERATION'),'candidate generation event missing');
assert(s.authorityTimeline.some(e=>e.kind==='READY_CREATED'),'READY_CREATED missing');
assert(s.authorityTimeline.some(e=>e.kind==='LOCK_REJECTED'),'LOCK_REJECTED missing');
assert(s.authorityTimeline.some(e=>e.kind==='CAMERA_LOCKED'),'CAMERA_LOCKED missing');
const seq=s.sequence;globalThis.WOFOWNERPROJECTION.stop();
const final=globalThis.__bc.messages.at(-1);assert(final.sequence>seq,'stop must publish a newer revoke sequence');assert(final.authorityTimeline.some(e=>e.kind==='READY_REVOKED'),'READY_REVOKED missing on runtime stop');
"""
        cp = subprocess.run(["node", "-e", script, str(self._worker_path())], text=True, capture_output=True, check=False)
        self.assertEqual(0, cp.returncode, cp.stderr or cp.stdout)

    def test_pre_ready_ambiguity_resets_streak_and_never_uses_instant_ok(self) -> None:
        src = self._worker_path().read_text(encoding="utf-8")
        self.assertIn("READY_STABLE_SAMPLES=20", src)
        self.assertIn("CANDIDATE_STREAK_RESET", src)
        self.assertIn("TOP_CANDIDATE_CHANGED", src)
        self.assertIn("READY_STABILITY_WINDOW", src)
        self.assertNotIn("if(q.ok)return{actionZh:'Camera 证据已满足阈值", src)
        self.assertIn("CANDIDATE_AMBIGUOUS_LIMIT_REACHED", src)
        self.assertIn("AMBIGUOUS_ACTIVE_SAMPLE_LIMIT=1200", src)

    def test_top_click_is_two_phase_and_authority_bound(self) -> None:
        top = self._top_path().read_text(encoding="utf-8")
        self.assertIn("function exactReadySnapshot()", top)
        self.assertIn("STALE_READY_SNAPSHOT", top)
        self.assertIn("READY_CAMERA_AUTHORITY_MISMATCH", top)
        self.assertIn("pendingCal={", top)
        self.assertIn("kind:'lock-camera'", top)
        self.assertIn("authorityId:auth.authorityId", top)
        self.assertIn("authorityGeneration:auth.authorityGeneration", top)
        self.assertIn("function maybeFinalizeCalibration()", top)
        self.assertIn("CALIBRATION_LOCK_ACKED", top)
        self.assertIn("WORKER_SESSION_REPLACED", top)
        self.assertNotIn("const candidate=()=>last?.cameraTop?.[0]", top)

    def test_status_store_preserves_authority_generation_sequence_and_timeline(self) -> None:
        if not PYLAUNCH.exists():
            self.skipTest("repo PYLAUNCH not mounted in local authoring smoke")
        from wof_launcher.state import StatusStore
        store = StatusStore()
        timeline = [
            {"eventId": "s:1", "kind": "CANDIDATE_GENERATION", "sequence": 10, "candidateGeneration": 1, "address": "0xFF1000"},
            {"eventId": "s:2", "kind": "READY_CREATED", "sequence": 30, "authorityId": "auth-1", "authorityGeneration": 1, "address": "0xFF1000"},
            {"eventId": "s:3", "kind": "CAMERA_LOCKED", "sequence": 32, "authorityId": "auth-1", "authorityGeneration": 1, "address": "0xFF1000"},
        ]
        ui = {
            "samples": 100, "workerSessionId": "session-1", "lastSequence": 32, "snapshotId": "session-1:32",
            "cameraQuality": {"ok": True, "ready": True, "clickReady": True, "conditioning": "READY_LATCHED", "stableSamples": 20, "requiredStableSamples": 20},
            "cameraAuthority": {"state": "READY", "authorityId": "auth-1", "authorityGeneration": 1, "candidateGeneration": 1, "address": "0xFF1000", "sampleStart": 80, "sampleEnd": 99},
            "candidateStability": {"generation": 1, "address": "0xFF1000", "qualifiedSamples": 20},
            "authorityTimeline": timeline,
            "guidance": {"actionZh": "Camera 稳定 authority 已锁定。现在只点击一次 P1 头顶。", "nextCommandZh": "消费 authority #1"},
            "terminal": False,
        }
        store.update(alpha_status={"projectionRecovery": {"state": "CALIBRATING", "ui": ui}})
        snap = store.get().snapshot(); progress = snap["last_calibration_progress"]
        self.assertEqual("auth-1", progress["cameraAuthority"]["authorityId"])
        self.assertEqual(32, progress["snapshotSequence"])
        self.assertEqual("session-1", progress["workerSessionId"])
        kinds = [e["kind"] for e in snap["significant_events"]]
        self.assertIn("camera-authority-ready-created", kinds)
        self.assertIn("camera-authority-camera-locked", kinds)
        before = len(snap["significant_events"])
        store.update(alpha_status={"projectionRecovery": {"state": "CALIBRATING", "ui": ui}})
        self.assertEqual(before, len(store.get().significant_events), "re-poll must not duplicate authority timeline events")


if __name__ == "__main__":
    unittest.main()
