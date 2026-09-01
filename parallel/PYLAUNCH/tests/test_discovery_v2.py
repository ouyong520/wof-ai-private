import unittest
from wof_launcher.cdp import CdpClient, CdpError, CdpSession
from wof_launcher.discovery_v2 import discover
from wof_launcher.probe import WORLD_SHA256
from wof_launcher.state import StatusStore

GOOD_LIGHT={"moduleOk":True,"heapOk":True,"moduleKey":"m","heapBytes":123,"readOnly":True,"ramWrites":0,"inputInjection":False}
GOOD_ID={"ok":True,"sha256":WORLD_SHA256,"reason":"exact World 921031 full CPU-logical SHA-256","readOnly":True,"ramWrites":0,"inputInjection":False}

class FakeClient:
    def __init__(self, targets, page=None, light=None, identity=None, related=None, stale=None):
        self.targets=targets; self.page=page or {}; self.light=light or {}; self.identity=identity or {}; self.related=related or {}; self.stale=set(stale or [])
        self.sessions={}; self.next=1; self.auto=set(); self.sent=set()
    def attach(self, tid):
        if tid in self.stale: raise CdpError("stale target")
        sid=f"s{self.next}"; self.next+=1; self.sessions[sid]=tid; return CdpSession(self,tid,sid)
    def event_cursor(self): return 0
    def wait_for_events(self,cursor,*,timeout,predicate=None):
        out=[]
        for sid,tid in list(self.sessions.items()):
            if sid not in self.auto or (sid,tid) in self.sent: continue
            self.sent.add((sid,tid))
            for i,info in enumerate(self.related.get(tid,[])):
                cs=f"{sid}c{i}"; self.sessions[cs]=info["targetId"]
                e={"method":"Target.attachedToTarget","sessionId":sid,"params":{"sessionId":cs,"targetInfo":info}}
                if predicate is None or predicate(e): out.append(e)
        return cursor+len(out),out
    def request(self,method,params=None,*,session_id=None,timeout=None):
        params=params or {}
        if method=="Target.getTargets": return {"targetInfos":self.targets}
        if method=="Target.detachFromTarget": self.sessions.pop(params.get("sessionId"),None); return {}
        if method=="Target.setAutoAttach": self.auto.add(session_id); return {}
        if method=="Runtime.enable": return {}
        if method=="Runtime.evaluate":
            tid=self.sessions.get(session_id); expr=params.get("expression","")
            if "gameSurface" in expr: value=self.page.get(tid,{"gameSurface":False,"readOnly":True})
            elif "ramWithinHeap" in expr: value=self.light.get(tid,{"moduleOk":False,"heapOk":False,"readOnly":True,"ramWrites":0,"inputInjection":False})
            elif "const EXPECTED=" in expr: value=self.identity.get(tid,{"ok":False,"reason":"wrong World","readOnly":True,"ramWrites":0,"inputInjection":False})
            else: value=None
            return {"result":{"value":value}}
        raise CdpError(method)

class DiscoveryV2Tests(unittest.TestCase):
    def test_page_autoattach_shared_worker_url_variation(self):
        p={"targetId":"p","type":"page","url":"https://host/game"}; w={"targetId":"w","type":"shared_worker","url":"https://cdn/runtime-v151.js"}
        c=FakeClient([p],page={"p":{"gameSurface":True}},light={"w":GOOD_LIGHT},identity={"w":GOOD_ID},related={"p":[w]})
        x=discover(c); self.assertEqual("page-autoattach",x.diagnostics["path"]); self.assertEqual("w",x.worker["targetId"]); self.assertTrue(x.identity["ok"])

    def test_existing_blob_and_data_workers_accept_only_after_exact_runtime_identity(self):
        for url in ("blob:https://host/abc","data:text/javascript,worker","https://cdn/9f8e7d6c"):
            with self.subTest(url=url):
                p={"targetId":"p","type":"page","url":"https://host/wof"}; w={"targetId":"w","type":"worker","url":url}
                x=discover(FakeClient([p,w],page={"p":{"gameSurface":True}},light={"w":GOOD_LIGHT},identity={"w":GOOD_ID}))
                self.assertEqual("w",x.worker["targetId"]); self.assertTrue(x.identity["ok"]); self.assertEqual("direct-worker",x.diagnostics["path"])

    def test_wrong_identity_blob_and_data_fail_closed(self):
        wrong={"ok":False,"sha256":"0"*64,"reason":"full CPU-logical SHA-256 mismatch"}
        for url in ("blob:https://host/abc","data:text/javascript,worker"):
            with self.subTest(url=url):
                p={"targetId":"p","type":"page","url":"https://host/wof"}; w={"targetId":"w","type":"worker","url":url}
                x=discover(FakeClient([p,w],page={"p":{"gameSurface":True}},light={"w":GOOD_LIGHT},identity={"w":wrong}))
                self.assertFalse(x.identity["ok"]); self.assertIn("mismatch",x.reason)

    def test_page_found_without_root_worker(self):
        p={"targetId":"p","type":"page","url":"https://host/wof"}; x=discover(FakeClient([p],page={"p":{"gameSurface":True}}))
        self.assertEqual("p",x.page["targetId"]); self.assertIsNone(x.worker)

    def test_direct_worker_backward_compatible(self):
        p={"targetId":"p","type":"page","url":"https://host/wof"}; w={"targetId":"w","type":"worker","url":"https://cdn/gstyphoon123.js","parentId":"p"}
        x=discover(FakeClient([p,w],page={"p":{"gameSurface":True}},light={"w":GOOD_LIGHT},identity={"w":GOOD_ID}))
        self.assertEqual("direct-worker",x.diagnostics["path"]); self.assertEqual("p",x.page["targetId"])

    def test_misleading_opener_id_is_not_parent_authority(self):
        good={"targetId":"good","type":"page","url":"https://host/wof"}; other={"targetId":"other","type":"page","url":"https://host/other"}
        w={"targetId":"w","type":"worker","url":"blob:https://host/abc","openerId":"other"}
        x=discover(FakeClient([good,other,w],page={"good":{"gameSurface":True},"other":{"gameSurface":False}},light={"w":GOOD_LIGHT},identity={"w":GOOD_ID}))
        self.assertEqual("good",x.page["targetId"]); self.assertEqual("direct-worker",x.diagnostics["path"])

    def test_unique_wof_page_direct_fallback(self):
        good={"targetId":"good","type":"page","url":"https://host/wof"}; other={"targetId":"other","type":"page","url":"https://host/help"}; w={"targetId":"w","type":"worker","url":"https://cdn/runtime"}
        x=discover(FakeClient([good,other,w],page={"good":{"gameSurface":True},"other":{"gameSurface":False}},light={"w":GOOD_LIGHT},identity={"w":GOOD_ID}))
        self.assertEqual("good",x.page["targetId"]); self.assertEqual("w",x.worker["targetId"])

    def test_two_wof_pages_direct_fallback_fails_closed(self):
        p1={"targetId":"p1","type":"page","url":"https://a/wof"}; p2={"targetId":"p2","type":"page","url":"https://b/wof"}; w={"targetId":"w","type":"worker","url":"https://cdn/runtime"}
        x=discover(FakeClient([p1,p2,w],page={"p1":{"gameSurface":True},"p2":{"gameSurface":True}},light={"w":GOOD_LIGHT},identity={"w":GOOD_ID}))
        self.assertIsNone(x.worker); self.assertIn("association is ambiguous",x.reason)

    def test_nested_iframe_worker(self):
        p={"targetId":"p","type":"page","url":"https://host/wof"}; f={"targetId":"f","type":"iframe","url":"https://host/frame"}; w={"targetId":"w","type":"worker","url":"https://cdn/runtime.js"}
        x=discover(FakeClient([p],page={"p":{"gameSurface":True}},light={"w":GOOD_LIGHT},identity={"w":GOOD_ID},related={"p":[f],"f":[w]}))
        self.assertEqual("w",x.worker["targetId"]); self.assertTrue(any(t.get("depth")==2 for t in x.diagnostics["relatedTopology"]))

    def test_ambiguous_pairs_fail_closed(self):
        p1={"targetId":"p1","type":"page","url":"https://a/wof"}; p2={"targetId":"p2","type":"page","url":"https://b/wof"}; w1={"targetId":"w1","type":"worker","url":"https://a/r.js"}; w2={"targetId":"w2","type":"worker","url":"https://b/r.js"}
        x=discover(FakeClient([p1,p2],light={"w1":GOOD_LIGHT,"w2":GOOD_LIGHT},identity={"w1":GOOD_ID,"w2":GOOD_ID},related={"p1":[w1],"p2":[w2]}))
        self.assertIsNone(x.worker); self.assertIn("ambiguous",x.reason)

    def test_related_worker_wasm_not_ready(self):
        p={"targetId":"p","type":"page","url":"https://host/wof"}; w={"targetId":"w","type":"worker","url":"https://cdn/runtime.js"}
        x=discover(FakeClient([p],page={"p":{"gameSurface":True}},light={"w":{"moduleOk":False,"heapOk":False}},related={"p":[w]}))
        self.assertEqual("w",x.worker["targetId"]); self.assertFalse(x.worker_probe["moduleOk"]); self.assertIn("not ready",x.reason)

    def test_disconnect_reset_clears_stale_runtime_state(self):
        s=StatusStore(); s.update(browser_connected=True,wof_page_found=True,worker_found=True,world_921031=True,discovery_path="page-autoattach")
        s.reset_runtime(error="连接中断")
        snap=s.get(); self.assertFalse(snap.browser_connected); self.assertFalse(snap.worker_found); self.assertIsNone(snap.discovery_path); self.assertEqual("ERROR",snap.state)

    def test_wrong_world_fails_closed(self):
        p={"targetId":"p","type":"page","url":"https://host/wof"}; w={"targetId":"w","type":"worker","url":"https://cdn/r.js"}; wrong={"ok":False,"sha256":"0"*64,"reason":"full CPU-logical SHA-256 mismatch"}
        x=discover(FakeClient([p],page={"p":{"gameSurface":True}},light={"w":GOOD_LIGHT},identity={"w":wrong},related={"p":[w]}))
        self.assertFalse(x.identity["ok"]); self.assertIn("mismatch",x.reason)

    def test_stale_and_worker_replacement_prunes_identity_cache(self):
        p={"targetId":"p","type":"page","url":"https://host/wof"}; w2={"targetId":"new","type":"worker","url":"https://cdn/b.js"}; cache={"old":GOOD_ID}
        second=discover(FakeClient([p,w2],page={"p":{"gameSurface":True}},light={"new":GOOD_LIGHT},identity={"new":GOOD_ID}),identity_cache=cache)
        self.assertEqual("new",second.worker["targetId"]); self.assertNotIn("old",cache); self.assertIn("new",cache)

    def test_readonly_and_no_replacement_diagnostics(self):
        p={"targetId":"p","type":"page","url":"https://host/wof"}; w={"targetId":"w","type":"worker","url":"blob:https://host/abc"}
        x=discover(FakeClient([p,w],page={"p":{"gameSurface":True}},light={"w":GOOD_LIGHT},identity={"w":GOOD_ID}))
        self.assertTrue(x.diagnostics["readOnly"]); self.assertEqual(0,x.diagnostics["ramWrites"]); self.assertFalse(x.diagnostics["inputInjection"]); self.assertFalse(x.diagnostics["workerReplacement"]); self.assertFalse(x.diagnostics["urlRewrite"])

    def test_readonly_allowlist_still_blocks_input_and_function_calls(self):
        c=CdpClient("ws://invalid")
        for method in ("Input.dispatchKeyEvent","Runtime.callFunctionOn"):
            with self.assertRaises(CdpError): c.request(method,{})

if __name__=="__main__": unittest.main()
