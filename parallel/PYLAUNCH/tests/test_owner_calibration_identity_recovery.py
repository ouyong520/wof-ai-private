from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
ROOT = HERE.parents[3]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.proof import compact_proof_snapshot
from wof_launcher.state import StatusStore
from wof_launcher.tray import TkUiDispatcher

WORLD_SHA = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"


class OwnerCalibrationIdentityRecoveryTests(unittest.TestCase):
    def test_field_adapter_lifecycle_identity_matrix_is_strict(self) -> None:
        adapter = ROOT / "product/alpha/wof_alpha_field_adapter.js"
        script = r"""
const A=require(process.argv[1]);
const assert=(x,m)=>{if(!x)throw new Error(m)};
const specs=A.PLAYER_LOCAL_IDENTITY;
function run(rows){
  const b=new Map(),u=new Map();
  for(let i=0;i<specs.length;i++){b.set(specs[i].base,rows[i][0]);u.set(specs[i].base+0x7C,rows[i][1]);}
  return A.evaluatePlayerLocalIdentities(a=>b.get(a)??0,a=>u.get(a)??0);
}
let x=run([[1,0],[1,4],[1,8]]);assert(x.ok&&x.activePlayers.join(',')==='P1,P2,P3','all-active exact must pass');
x=run([[1,0],[0,0],[0,0]]);assert(x.ok&&x.activePlayers.join(',')==='P1'&&x.inactivePlayers.join(',')==='P2,P3','inactive zeroed P2/P3 must defer/pass');
x=run([[1,0],[0,4],[0,8]]);assert(x.ok&&x.inactivePlayers.join(',')==='P2,P3','inactive retained exact identity must pass');
x=run([[1,0],[1,0],[0,0]]);assert(!x.ok&&x.badPlayers.includes('P2'),'active invalid self-index must fail');
x=run([[1,0],[0,0],[0,4]]);assert(!x.ok&&x.badPlayers.includes('P3'),'inactive contradictory self-index must fail closed');
x=run([[0,0],[0,0],[0,0]]);assert(x.ok&&x.inactivePlayers.length===3,'all inactive zeroed remains a lifecycle-valid exact-World state');
"""
        cp = subprocess.run(["node", "-e", script, str(adapter)], text=True, capture_output=True, check=False)
        self.assertEqual(0, cp.returncode, cp.stderr or cp.stdout)

    def test_hudanchor_need_more_pauses_and_resumes_without_losing_samples(self) -> None:
        worker = ROOT / "parallel/HUDANCHOR_PROOF/wof_owner_projection_worker.js"
        script = r"""
const fs=require('fs');const src=fs.readFileSync(process.argv[1],'utf8');
const assert=(x,m)=>{if(!x)throw new Error(m)};
const buf=new ArrayBuffer(5_000_000),M=new Uint8Array(buf),U=new Uint32Array(buf),R=0x1000;
U[0x2e39e4>>>2]=R;globalThis._0x515056={HEAPU8:M,HEAPU32:U};
let tick=null;globalThis.setInterval=(fn)=>{tick=fn;return 1};globalThis.clearInterval=()=>{};
class BC{constructor(){this.messages=[]}postMessage(m){this.messages.push(m)}close(){}}globalThis.BroadcastChannel=BC;
const BADDR=a=>R+((((a-0xFF0000)&0xffff)^1));
const setB=(a,v)=>{M[BADDR(a)]=v&255};
const setU16=(a,v)=>{setB(a,(v>>>8)&255);setB(a+1,v&255)};
const setU32=(a,v)=>{setB(a,(v>>>24)&255);setB(a+1,(v>>>16)&255);setB(a+2,(v>>>8)&255);setB(a+3,v&255)};
const setF=(a,v)=>setU32(a,Math.round(v*65536)>>>0);
const P=0xFFBE1C,C=0xFF1000;setB(P,1);setF(P+4,100);setF(P+8,80);setF(P+12,0);setU16(C,0);
(0,eval)(src);assert(typeof tick==='function','worker tick not installed');
for(let i=1;i<29;i++){setF(P+4,100+i);setU16(C,i);tick();}
let s=globalThis.WOFOWNERPROJECTION.status();assert(s.samples===29,'expected retained 29 samples, got '+s.samples);assert(s.cameraQuality.reason==='NEED_MORE_SAMPLES','under-target must be NEED_MORE_SAMPLES: '+JSON.stringify(s.cameraQuality));assert(s.cameraQuality.targetSamples===80&&s.cameraQuality.remainingSamples===51,'target/remaining missing');assert(String(s.guidance.actionZh).includes('29/80')&&s.guidance.nextCommandZh,'NEED_MORE must give action + next command');
setB(P,0);tick();s=globalThis.WOFOWNERPROJECTION.status();assert(s.samples===29,'inactive P1 must not discard/advance samples');assert(s.cameraQuality.reason==='WAITING_FOR_ACTIVE_P1','inactive P1 reason missing');assert(s.sampling.retainedSamples===29&&s.sampling.continuable===true,'partial sample retention missing');
setB(P,1);setF(P+4,129);setU16(C,29);tick();s=globalThis.WOFOWNERPROJECTION.status();assert(s.samples===30,'reactivated P1 must continue from retained samples');assert(s.cameraQuality.reason==='NEED_MORE_SAMPLES','continued partial evidence should remain NEED_MORE until target');
globalThis.WOFOWNERPROJECTION.stop();
"""
        cp = subprocess.run(["node", "-e", script, str(worker)], text=True, capture_output=True, check=False)
        self.assertEqual(0, cp.returncode, cp.stderr or cp.stdout)
        top = (ROOT / "parallel/HUDANCHOR_PROOF/wof_owner_projection_top.js").read_text(encoding="utf-8")
        self.assertIn("cameraQuality:last?.cameraQuality", top)
        self.assertIn("guidance:{actionZh:nextAction()", top)
        self.assertIn("无需做数学选择", top)
        self.assertIn("不要重新运行工具", (ROOT / "parallel/HUDANCHOR_PROOF/wof_owner_projection_worker.js").read_text(encoding="utf-8"))

    def test_significant_live_state_survives_terminal_disconnect(self) -> None:
        store = StatusStore()
        store.update(
            browser_connected=True, wof_page_found=True, page_target_id="page-a", page_url="https://game/wof",
            worker_found=True, worker_target_id="worker-a", worker_url="blob:a", wasm_module_found=True,
            wasm_module_key="m", heap_found=True, heap_bytes=4_000_000, world_921031=True,
            identity_sha256=WORLD_SHA, identity_reason="exact World 921031", discovery_path="exact-identity",
            alpha_requested=True, alpha_running=False, alpha_error="Alpha release activation failed: P1/P2/P3 local identity mismatch",
            state="WAITING_WOF",
        )
        store.update(
            alpha_error=None,
            alpha_status={"projectionRecovery": {"state": "CALIBRATING", "ui": {
                "samples": 29,
                "cameraQuality": {"ok": False, "samples": 29, "targetSamples": 80, "remainingSamples": 51, "reason": "NEED_MORE_SAMPLES", "conditioning": "UNDER_TARGET", "continuable": True},
                "sampling": {"retainedSamples": 29, "pausedReason": None, "continuable": True},
                "guidance": {"actionZh": "继续左右卷屏", "nextCommandZh": "保持当前窗口"},
                "terminal": False,
            }}},
        )
        store.reset_runtime(error="Launcher 与浏览器连接中断：CDP is not connected")
        snap = store.get().snapshot()
        self.assertEqual(WORLD_SHA, snap["last_accepted_authority"]["worldSha256"])
        self.assertIn("local identity mismatch", snap["last_alpha_failure"]["error"])
        self.assertEqual(29, snap["last_calibration_progress"]["samples"])
        self.assertEqual("NEED_MORE_SAMPLES", snap["last_calibration_progress"]["reason"])
        self.assertLessEqual(len(snap["significant_events"]), StatusStore.EVENT_LIMIT)
        proof = compact_proof_snapshot(snap)
        self.assertEqual("ERROR", proof["launcherState"])
        self.assertEqual(WORLD_SHA, proof["lastAcceptedAuthority"]["worldSha256"])
        self.assertIn("local identity mismatch", proof["lastAlphaFailure"]["error"])
        self.assertEqual(29, proof["lastCalibrationProgress"]["samples"])

    def test_significant_event_history_is_bounded(self) -> None:
        store = StatusStore()
        for i in range(150):
            store.update(state="ERROR", last_error=f"e-{i}", last_accepted_authority={"worldSha256": WORLD_SHA})
        self.assertLessEqual(len(store.get().significant_events), StatusStore.EVENT_LIMIT)

    def test_tk_dispatcher_repeated_callbacks_use_one_ui_thread_and_close_cleanly(self) -> None:
        class FakeRoot:
            def __init__(self): self.callbacks = queue.Queue(); self.quit_now = False
            def withdraw(self): pass
            def after(self, _ms, fn): self.callbacks.put(fn)
            def mainloop(self):
                while not self.quit_now:
                    try: fn = self.callbacks.get(timeout=0.2)
                    except queue.Empty: continue
                    fn()
            def quit(self): self.quit_now = True
            def destroy(self): self.quit_now = True

        dispatcher = TkUiDispatcher(root_factory=FakeRoot)
        seen: list[int] = []; done = threading.Event()
        for i in range(10):
            self.assertTrue(dispatcher.submit(lambda _root, i=i: (seen.append(threading.get_ident()), done.set() if i == 9 else None)))
        self.assertTrue(done.wait(2.0), dispatcher.status())
        dispatcher.close()
        self.assertEqual(10, len(seen))
        self.assertEqual(1, len(set(seen)))
        self.assertNotEqual(threading.get_ident(), seen[0])
        status = dispatcher.status()
        self.assertFalse(status["running"])
        self.assertIsNone(status["lastError"])
        self.assertEqual(10, status["executed"])

    def test_tk_dispatcher_close_after_empty_observation_still_consumes_stop(self) -> None:
        class RaceQueue:
            def __init__(self):
                self.inner = queue.Queue()
                self.arm_empty_race = False
                self.empty_observed = threading.Event()
                self.release_empty = threading.Event()
                self.stop_enqueued = threading.Event()
                self.put_count = 0

            def put(self, item):
                self.put_count += 1
                self.inner.put(item)
                if self.put_count >= 2:
                    self.stop_enqueued.set()

            def get_nowait(self):
                try:
                    return self.inner.get_nowait()
                except queue.Empty:
                    if self.arm_empty_race:
                        self.arm_empty_race = False
                        self.empty_observed.set()
                        self.release_empty.wait(2.0)
                    raise

        class FakeRoot:
            def __init__(self): self.callbacks = queue.Queue(); self.quit_now = False
            def withdraw(self): pass
            def after(self, _ms, fn): self.callbacks.put(fn)
            def mainloop(self):
                while not self.quit_now:
                    try: fn = self.callbacks.get(timeout=0.2)
                    except queue.Empty: continue
                    fn()
            def quit(self): self.quit_now = True
            def destroy(self): self.quit_now = True

        dispatcher = TkUiDispatcher(root_factory=FakeRoot)
        race_queue = RaceQueue()
        dispatcher._queue = race_queue  # force the exact close-vs-drain-tail interleaving
        callback_done = threading.Event()

        def callback(_root):
            race_queue.arm_empty_race = True
            callback_done.set()

        self.assertTrue(dispatcher.submit(callback))
        self.assertTrue(callback_done.wait(2.0), dispatcher.status())
        self.assertTrue(race_queue.empty_observed.wait(2.0), dispatcher.status())

        close_done = threading.Event()
        closer = threading.Thread(target=lambda: (dispatcher.close(), close_done.set()))
        closer.start()
        self.assertTrue(race_queue.stop_enqueued.wait(2.0), dispatcher.status())
        race_queue.release_empty.set()
        closer.join(timeout=2.0)

        self.assertTrue(close_done.is_set(), dispatcher.status())
        self.assertFalse(dispatcher.status()["running"])
        self.assertIsNone(dispatcher.status()["lastError"])


if __name__ == "__main__":
    unittest.main()
