from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Keep this regression deterministic and browser-free: provide only the two
# read-only PYLAUNCH interface symbols imported by real_adapter.py.
cdp_mod = types.ModuleType("wof_launcher.cdp")
class CdpClient:  # pragma: no cover - type/interface stub
    pass
cdp_mod.CdpClient = CdpClient
sys.modules["wof_launcher"] = types.ModuleType("wof_launcher")
sys.modules["wof_launcher.cdp"] = cdp_mod

discovery_mod = types.ModuleType("wof_launcher.discovery_v2")
class TargetChoice:
    def __init__(self, page=None, worker=None, identity=None, reason=None):
        self.page, self.worker, self.identity, self.reason = page, worker, identity, reason
def discover(*_args, **_kwargs):
    raise AssertionError("live discovery must not run in deterministic unit test")
discovery_mod.TargetChoice = TargetChoice
discovery_mod.discover = discover
sys.modules["wof_launcher.discovery_v2"] = discovery_mod

spec = importlib.util.spec_from_file_location("real_adapter", Path(__file__).with_name("real_adapter.py"))
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

PASS_ID = {"ok": True, "sha256": mod.GOLDEN_SHA, "readOnly": True, "ramWrites": 0, "inputInjection": False}

def choice(page="page-new", worker="worker-new", identity=None, reason=None):
    return TargetChoice({"targetId": page} if page else None, {"targetId": worker} if worker else None, PASS_ID if identity is None else identity, reason)

class FakeAdapter(mod.FormalRealAdapter):
    def __init__(self):
        super().__init__(object(), "worker-source")
        self.reset_fail = False
        self.stop_value = True
        self.stop_fail = False
        self.events = []
        self.page_status = None
        self.worker_status = None
    def _reset_page(self, page_id):
        self.events.append(("reset", page_id))
        if self.reset_fail:
            raise RuntimeError("reset failed")
    def _stop_worker(self, worker_id):
        self.events.append(("stop", worker_id))
        if self.stop_fail:
            raise RuntimeError("stop failed")
        return self.stop_value
    def _read_page_config(self, page_id):
        self.events.append(("config", page_id))
        return {"release": mod.RELEASE, "schema": mod.SCHEMA, "session": "1"*32, "channel": "WOF_ALPHA_"+"1"*32, "transport": mod.TRANSPORT}
    def _bind_page(self, page_id, pair_nonce):
        self.events.append(("bind", page_id))
        return {"bound": True, "pairGeneration": 9, "pairNonce": pair_nonce, "session": "1"*32, "transportVersion": mod.TRANSPORT}
    def _install_worker(self, worker_id, binding):
        self.events.append(("install", worker_id))
        return {"running": True, "identitySignature": mod.IDENTITY_SIGNATURE, "readOnly": True, "ramWrites": 0, "inputInjection": False, "workerReplacement": False, "queueDepth": 0}
    def _page_status(self, _page_id):
        return self.page_status
    def _worker_status(self, _worker_id):
        return self.worker_status

results = []
def check(name, fn):
    try:
        fn(); results.append((name, True, None))
    except Exception as exc:
        results.append((name, False, repr(exc)))

def expect_raises(fn):
    try:
        fn()
    except RuntimeError:
        return
    raise AssertionError("expected RuntimeError")

def old_binding(page="page-old", worker="worker-old"):
    return mod.ActiveBinding(page, worker, "1"*32, 7, "2"*32, "3"*32)

check("exact World identity accepted", lambda: (_ for _ in ()).throw(AssertionError()) if not mod._choice_supported(choice()) else None)
check("wrong World SHA rejected", lambda: (_ for _ in ()).throw(AssertionError()) if mod._choice_supported(choice(identity={**PASS_ID, "sha256": "0"*64})) else None)
check("input-injecting discovery rejected", lambda: (_ for _ in ()).throw(AssertionError()) if mod._choice_supported(choice(identity={**PASS_ID, "inputInjection": True})) else None)

def same_page_reset_must_succeed():
    a=FakeAdapter(); a.current=old_binding(page="same",worker="old"); a.reset_fail=True
    expect_raises(lambda:a._strict_revoke_for_rebind("same","new"))
check("same page old warning authority must revoke",same_page_reset_must_succeed)

def same_worker_stop_must_succeed():
    a=FakeAdapter(); a.current=old_binding(page="old",worker="same"); a.stop_value=False
    expect_raises(lambda:a._strict_revoke_for_rebind("new","same"))
check("same native Worker old observer must stop",same_worker_stop_must_succeed)

def worker_replacement_tolerates_dead_old_target_after_page_revoke():
    a=FakeAdapter(); a.current=old_binding(); a.stop_fail=True
    a._strict_revoke_for_rebind("page-new","worker-new")
    assert a.current is None and a.events[0]==("reset","page-old")
check("Worker replacement revokes page authority before best-effort old stop",worker_replacement_tolerates_dead_old_target_after_page_revoke)

def exact_current_authority_only():
    a=FakeAdapter(); b=old_binding(); a.current=b
    a.page_status={"bound":True,"transportVersion":mod.TRANSPORT,"session":b.session,"pairGeneration":b.pair_generation,"pairNonce":b.pair_nonce}
    a.worker_status={"running":True,"identitySignature":mod.IDENTITY_SIGNATURE,"runtimeEpoch":b.runtime_epoch,"session":b.session,"pairGeneration":b.pair_generation,"pairNonce":b.pair_nonce,"queueDepth":0,"readOnly":True,"ramWrites":0,"inputInjection":False,"workerReplacement":False}
    assert a._current_still_authoritative(choice(page=b.page_id,worker=b.worker_id))
    a.worker_status={**a.worker_status,"runtimeEpoch":"9"*32}
    assert not a._current_still_authoritative(choice(page=b.page_id,worker=b.worker_id))
check("runtime epoch replacement invalidates current authority",exact_current_authority_only)

def normal_bind_orders_revoke_before_bind_install():
    a=FakeAdapter(); a.current=old_binding()
    b=a.bind_choice(choice())
    names=[e[0] for e in a.events]
    assert names.index("reset") < names.index("bind") < names.index("install")
    assert b.pair_generation==9 and b.worker_id=="worker-new"
check("normal rebind revokes before fresh generation install",normal_bind_orders_revoke_before_bind_install)

def unsupported_fail_closed():
    a=FakeAdapter(); a.current=old_binding()
    original=mod.discover
    mod.discover=lambda *_a,**_k: choice(reason="ambiguous")
    try:
        r=a.step(); assert r["ok"] is False and r["warningAuthority"] is False and r["gameplayPlayable"] is True and a.current is None
    finally:
        mod.discover=original
check("unsupported discovery disables warnings but keeps gameplay playable",unsupported_fail_closed)

failed=[r for r in results if not r[1]]
print({"schema":"wof-alpha-formal-adapter-test-v1","status":"FAIL" if failed else "PASS","testCount":len(results),"passCount":len(results)-len(failed),"failCount":len(failed),"results":results})
raise SystemExit(1 if failed else 0)
