from __future__ import annotations

import json
from typing import Any, Callable

from .cdp import CdpClient
from .discovery_v2 import TargetChoice
from .probe import WORLD_SHA256

SOURCE = "parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js"
SCHEMA = "wof-render-authority-capture-v2"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False, "overlayEnabled": False}

class RenderAuthorityCaptureError(RuntimeError): pass

class RenderAuthorityCapture:
    """Bounded fail-closed exact-runtime renderer-authority measurement."""
    def __init__(self, verified_text: Callable[[str], str]) -> None:
        self._verified_text=verified_text;self._authority_key=None;self._runtime_epoch=None;self._worker_id=None;self._state="UNRESOLVED";self._error=None;self._result=None
    @staticmethod
    def _eval(client:CdpClient,target_id:str,expression:str,*,timeout:float=15.0)->Any:
        session=client.attach(target_id)
        try:session.request("Runtime.enable");return session.evaluate(expression,timeout=timeout)
        finally:session.close()
    def status(self)->dict[str,Any]:
        return {"schema":SCHEMA,"state":self._state,"authorityKey":self._authority_key,"runtimeEpoch":self._runtime_epoch,"terminal":self._result is not None,"error":self._error,"ownerActionZh":"正常玩；Camera 会先自动识别 P1 身份并尝试零点击定位场景 P1 头部；只有自动定位无法安全唯一确认时才允许最多一次实际头部点击。","measurementRequired":"exact runtime renderer/object authority plus bounded zero-click-first P1 head visual authority",**SAFETY}
    def result(self)->dict[str,Any]|None:return None if self._result is None else json.loads(json.dumps(self._result))
    @staticmethod
    def _validate_remote(remote:Any,*,authority_key:str,runtime_epoch:str)->dict[str,Any]:
        if not isinstance(remote,dict) or remote.get("schema")!=SCHEMA:raise RenderAuthorityCaptureError("render-authority capture malformed remote schema")
        if remote.get("authorityKey")!=authority_key or remote.get("runtimeEpoch")!=runtime_epoch:raise RenderAuthorityCaptureError("render-authority capture stale/runtime-generation mismatch")
        if remote.get("readOnly") is not True or remote.get("ramWrites")!=0 or remote.get("inputInjection") is not False or remote.get("overlayEnabled") is not False:raise RenderAuthorityCaptureError("render-authority capture safety boundary mismatch")
        return remote
    def ensure_started(self,client:CdpClient,choice:TargetChoice,authority_key:str,runtime_epoch:str)->dict[str,Any]:
        if self._authority_key==authority_key and self._runtime_epoch==runtime_epoch and self._state in {"MEASURING","MEASUREMENT_COMPLETE"}:return self.status()
        if not choice.worker or not choice.identity or choice.identity.get("ok") is not True:raise RenderAuthorityCaptureError("render-authority capture requires accepted exact World page/Worker authority")
        if choice.identity.get("sha256")!=WORLD_SHA256:raise RenderAuthorityCaptureError("render-authority capture exact World SHA authority mismatch")
        worker_id=str(choice.worker.get("targetId") or "")
        if not worker_id:raise RenderAuthorityCaptureError("render-authority capture Worker target id missing")
        locator=choice.identity.get("locator")
        if not isinstance(locator,dict) or not isinstance(locator.get("heapBase"),int) or not isinstance(locator.get("swap16"),bool):raise RenderAuthorityCaptureError("render-authority capture exact World locator missing")
        self.stop_runtime(client);source=self._verified_text(SOURCE);binding={"worldSha256":WORLD_SHA256,"authorityKey":authority_key,"runtimeEpoch":runtime_epoch,"locator":{"heapBase":locator["heapBase"],"swap16":locator["swap16"]},"readOnly":True,"ramWrites":0,"inputInjection":False}
        try:
            self._eval(client,worker_id,"try{self.WOFRENDERAUTHV2?.stop?.('launcher-rebind')}catch(_){}; true")
            self._eval(client,worker_id,f"(0,eval)({json.dumps(source)}); true",timeout=20.0)
            remote=self._eval(client,worker_id,f"self.WOFRENDERAUTHV2.start({json.dumps(binding)})",timeout=20.0)
        except Exception as exc:self._state="ERROR";self._error=str(exc);raise RenderAuthorityCaptureError(str(exc)) from exc
        self._validate_remote(remote,authority_key=authority_key,runtime_epoch=runtime_epoch);self._authority_key=authority_key;self._runtime_epoch=runtime_epoch;self._worker_id=worker_id;self._state="MEASURING";self._error=None;self._result=None;return self.status()
    def poll(self,client:CdpClient,authority_key:str,runtime_epoch:str)->dict[str,Any]:
        if self._authority_key!=authority_key or self._runtime_epoch!=runtime_epoch or not self._worker_id:return self.status()
        try:
            remote=self._eval(client,self._worker_id,"self.WOFRENDERAUTHV2?.status?.()||null");self._validate_remote(remote,authority_key=authority_key,runtime_epoch=runtime_epoch)
            if remote.get("terminal") is True:
                result=self._eval(client,self._worker_id,"self.WOFRENDERAUTHV2?.result?.()||null");self._validate_remote(result,authority_key=authority_key,runtime_epoch=runtime_epoch)
                if result.get("state")!="MEASUREMENT_COMPLETE" or result.get("resultVerdict")!="BOUNDED_CAPTURE_READY_FOR_RENDER_AUTHORITY_ANALYSIS":raise RenderAuthorityCaptureError("render-authority capture terminal result is not complete")
                self._result=result;self._state="MEASUREMENT_COMPLETE"
            else:self._state="MEASURING"
            self._error=None;return {**self.status(),"remote":remote,"result":self.result()}
        except Exception as exc:self._state="ERROR";self._error=str(exc);return {**self.status(),"remote":None,"result":self.result()}
    def stop_runtime(self,client:CdpClient|None=None)->None:
        if client and self._worker_id:
            try:self._eval(client,self._worker_id,"try{self.WOFRENDERAUTHV2?.stop?.('authority-revoked');true}catch(_){false}")
            except Exception:pass
        self._authority_key=None;self._runtime_epoch=None;self._worker_id=None
        if self._result is None:self._state="UNRESOLVED"
        self._error=None
