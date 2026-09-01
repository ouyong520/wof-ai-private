from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Iterable

WORLD_SHA256 = "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62"
SCHEMA = "wof-hudanchor-oneclick-browser-proof-v1"
NATIVE_W, NATIVE_H = 384.0, 224.0
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False, "workerReplacement": False}


def _num(v: Any) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _rms(values: Iterable[float]) -> float:
    a = [float(v) for v in values]
    return math.sqrt(sum(v * v for v in a) / len(a)) if a else math.inf


def fit_bias(predicted: list[float], observed: list[float]) -> tuple[float, float]:
    if len(predicted) != len(observed) or not predicted:
        return math.nan, math.inf
    bias = statistics.fmean(o - p for p, o in zip(predicted, observed))
    return bias, _rms((p + bias - o) for p, o in zip(predicted, observed))


def content_rect(canvas: dict[str, float]) -> dict[str, float | str]:
    left, top = float(canvas["left"]), float(canvas["top"])
    width, height = float(canvas["width"]), float(canvas["height"])
    target = NATIVE_W / NATIVE_H
    ratio = width / height if height else 0.0
    if height > 0 and abs(ratio - target) / target < 0.02:
        return {"left": left, "top": top, "width": width, "height": height, "mode": "full"}
    scale = min(width / NATIVE_W, height / NATIVE_H) if width > 0 and height > 0 else 0.0
    w, h = NATIVE_W * scale, NATIVE_H * scale
    return {"left": left + (width - w) / 2, "top": top + (height - h) / 2, "width": w, "height": h, "mode": "contain"}


def client_to_native(client_x: float, client_y: float, canvas: dict[str, float]) -> tuple[float, float]:
    r = content_rect(canvas)
    if not r["width"] or not r["height"]:
        raise ValueError("invalid canvas content rect")
    return ((client_x - float(r["left"])) / float(r["width"]) * NATIVE_W,
            (client_y - float(r["top"])) / float(r["height"]) * NATIVE_H)


def native_to_db(native_x: float, native_y: float, canvas: dict[str, float], db: dict[str, float]) -> tuple[float, float]:
    r = content_rect(canvas)
    cx = float(r["left"]) - float(canvas["left"]) + native_x / NATIVE_W * float(r["width"])
    cy = float(r["top"]) - float(canvas["top"]) + native_y / NATIVE_H * float(r["height"])
    if not canvas["width"] or not canvas["height"]:
        raise ValueError("invalid canvas size")
    return cx / float(canvas["width"]) * float(db["width"]), cy / float(canvas["height"]) * float(db["height"])


def score_camera_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        vr = _num(row.get("valid")) or 0.0
        sr = _num(row.get("strong")) or 0.0
        fr = _num(row.get("follow")) or 0.0
        rng = _num(row.get("range")) or 0.0
        changes = _num(row.get("changes")) or 0.0
        smooth = _num(row.get("smooth")) or 0.0
        score = vr * 4 + sr * 3 + min(1.0, rng / 96) * 1.5 + min(1.0, changes / 20) * 1.2 + fr * 1.5 + smooth * 0.3
        q = dict(row)
        q["proofScore"] = round(score, 4)
        out.append(q)
    return sorted(out, key=lambda x: float(x.get("proofScore", 0)), reverse=True)


def model_native_y(player: dict[str, Any], model: str) -> float:
    y, z = float(player["y"]), float(player["z"])
    if model == "Y-Z":
        return y - z
    if model == "Y+Z":
        return y + z
    if model == "Y":
        return y
    raise ValueError(model)


def evaluate_trace(trace: list[dict[str, Any]], *, projection_reference: dict[str, Any] | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    if not trace:
        return {"result": "BLOCKED", "reasons": ["missing Worker/page samples"], "modelScores": {}}
    safety_ok = all(all(s.get(k) == v for k, v in SAFETY.items()) for s in trace)
    if not safety_ok:
        reasons.append("safety invariant mismatch")
    identity_ok = all(s.get("identitySha256") == WORLD_SHA256 for s in trace)
    if not identity_ok:
        reasons.append("wrong World identity")
    sync_skews = [abs(float(s.get("pageEpochMs", 0)) - float(s.get("workerEpochMs", 0))) for s in trace]
    max_skew = max(sync_skews) if sync_skews else math.inf
    if max_skew > 250:
        reasons.append("stale/two-context epoch skew")
    if not all(bool(s.get("pageFound")) for s in trace):
        reasons.append("missing page")
    if not all(bool(s.get("workerFound")) for s in trace):
        reasons.append("missing Worker")

    mapping_keys = []
    mapping_valid = True
    for s in trace:
        c, d = s.get("canvas") or {}, s.get("drawingBuffer") or {}
        try:
            key = (round(float(c["width"]), 3), round(float(c["height"]), 3), int(d["width"]), int(d["height"]))
            mapping_keys.append(key)
            mapping_valid &= key[0] > 0 and key[1] > 0 and key[2] > 0 and key[3] > 0
        except (KeyError, TypeError, ValueError):
            mapping_valid = False
    if not mapping_valid:
        reasons.append("invalid resize/fullscreen mapping")

    cameras = [s.get("camera") for s in trace if isinstance(s.get("camera"), dict)]
    camera_addresses = [str(c.get("address")) for c in cameras if c.get("address")]
    camera_stable = bool(camera_addresses) and len(set(camera_addresses)) == 1
    if not camera_stable:
        reasons.append("ambiguous/unstable camera model")

    players = [s.get("player") for s in trace if isinstance(s.get("player"), dict)]
    depth_span = max((float(p["y"]) for p in players), default=0.0) - min((float(p["y"]) for p in players), default=0.0)
    jump_span = max((float(p["z"]) for p in players), default=0.0) - min((float(p["z"]) for p in players), default=0.0)
    x_span = max((float(p["x"]) for p in players), default=0.0) - min((float(p["x"]) for p in players), default=0.0)
    excitation = {"xSpan": round(x_span, 3), "depthSpan": round(depth_span, 3), "jumpSpan": round(jump_span, 3)}
    if x_span < 8:
        reasons.append("insufficient horizontal movement")
    if depth_span < 4:
        reasons.append("insufficient depth movement")
    if jump_span < 4:
        reasons.append("insufficient jump movement")

    model_scores: dict[str, Any] = {}
    visual = [(s, s.get("visualReference")) for s in trace if isinstance(s.get("visualReference"), dict)]
    for name in ("Y-Z", "Y+Z", "Y"):
        pred, obs = [], []
        for s, ref in visual:
            p = s.get("player")
            if not isinstance(p, dict):
                continue
            y = _num(ref.get("nativeY"))
            if y is None:
                continue
            pred.append(model_native_y(p, name))
            obs.append(y)
        if len(pred) >= 2:
            bias, err = fit_bias(pred, obs)
            model_scores[name] = {"visualSamples": len(pred), "bias": round(bias, 4), "rmsNativePx": round(err, 4)}
        else:
            model_scores[name] = {"visualSamples": len(pred), "bias": None, "rmsNativePx": None}

    chosen = None
    if projection_reference:
        ref_ok = projection_reference.get("worldSha256") == WORLD_SHA256 and projection_reference.get("visuallyProven") is True
        ref_model = projection_reference.get("verticalModel")
        if ref_ok and ref_model in model_scores:
            chosen = str(ref_model)
        else:
            reasons.append("projection reference is absent/unproven/wrong identity")
    else:
        ranked = [(m, q["rmsNativePx"]) for m, q in model_scores.items() if q["rmsNativePx"] is not None]
        ranked.sort(key=lambda x: float(x[1]))
        if len(ranked) >= 2 and ranked[0][1] <= 2.5 and ranked[1][1] - ranked[0][1] >= 2.0:
            chosen = ranked[0][0]
        else:
            reasons.append("vertical model ambiguous without an independent visual/projection oracle")

    if len(visual) == 1 and not projection_reference:
        chosen = None
        if "vertical model ambiguous without an independent visual/projection oracle" not in reasons:
            reasons.append("single calibration click cannot distinguish Y-Z/Y+Z/Y")

    result = "PASS" if not reasons and chosen else "BLOCKED"
    return {
        "result": result,
        "reasons": reasons,
        "verticalModel": chosen,
        "modelScores": model_scores,
        "maxContextSkewMs": round(max_skew, 3),
        "cameraStable": camera_stable,
        "cameraAddress": camera_addresses[0] if camera_stable else None,
        "mappingChanged": len(set(mapping_keys)) > 1,
        "mappingValid": mapping_valid,
        "excitation": excitation,
        **SAFETY,
    }


WORKER_INSTALL = r"""(()=>{
'use strict';
const KEY='__WOF_HUDANCHOR_AUTOPROOF_V1';
try{self[KEY]?.stop?.();}catch(_){}
const mod=self._0x515056;
if(!(mod?.HEAPU8 instanceof Uint8Array)||!(mod?.HEAPU32 instanceof Uint32Array))return {ok:false,reason:'WASM module unavailable'};
const M=mod.HEAPU8,R=mod.HEAPU32[0x2e39e4>>>2]>>>0;if(!R)return {ok:false,reason:'CPS RAM base unavailable'};
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0,U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0,S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v};
const P={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC},player=n=>{const a=P[n];if(!a||!B(a))return null;return{name:n,x:S32(a+4)/65536,y:S32(a+8)/65536,z:S32(a+12)/65536}};
const START=0,END=0xBE00,STEP=2,N=(END-START)/STEP,last=new Uint16Array(N),minv=new Uint16Array(N),maxv=new Uint16Array(N),changes=new Uint32Array(N),valid=new Uint32Array(N),strong=new Uint32Array(N),follow=new Uint32Array(N),smooth=new Uint32Array(N);minv.fill(0xffff);
let samples=0,prevX=null,running=true,timer=null;
function rows(limit=8){const p=player('P1');if(!p)return[];const a=[];for(let i=0,off=0;i<N;i++,off+=2){const rng=maxv[i]-minv[i],ch=changes[i];if(samples<10||rng<4||valid[i]<samples*.55)continue;const vr=valid[i]/samples,sr=strong[i]/samples,fr=ch?follow[i]/ch:0,sm=samples>1?smooth[i]/(samples-1):0,score=vr*4+sr*3+Math.min(1,rng/96)*1.5+Math.min(1,ch/20)*1.2+fr*1.5+sm*.3;a.push({address:'0x'+(0xFF0000+off).toString(16).toUpperCase(),value:last[i],range:rng,changes:ch,valid:vr,strong:sr,follow:fr,smooth:sm,score});}a.sort((x,y)=>y.score-x.score);return a.slice(0,limit)}
function tick(){if(!running)return;const p=player('P1');if(!p)return;const dx=prevX==null?0:p.x-prevX;for(let i=0,off=0;i<N;i++,off+=2){const v=U16(0xFF0000+off),old=last[i];if(v<minv[i])minv[i]=v;if(v>maxv[i])maxv[i]=v;if(samples&&v!==old){changes[i]++;const dv=v-old;if(Math.abs(dv)<=8)smooth[i]++;if(dx&&Math.sign(dv)===Math.sign(dx))follow[i]++;}const sx=p.x-v;if(sx>=-48&&sx<=432)valid[i]++;if(sx>=8&&sx<=376)strong[i]++;last[i]=v;}samples++;prevX=p.x}
const api={snapshot(){return{ok:true,epochMs:Date.now(),samples,players:{P1:player('P1'),P2:player('P2'),P3:player('P3')},cameraTop:rows(8),readOnly:true,ramWrites:0,inputInjection:false,workerReplacement:false}},stop(){running=false;if(timer)clearInterval(timer);delete self[KEY]}};self[KEY]=api;timer=setInterval(tick,100);tick();return {ok:true,installed:true,readOnly:true,ramWrites:0,inputInjection:false,workerReplacement:false};
})()"""
WORKER_SNAPSHOT = "(()=>self.__WOF_HUDANCHOR_AUTOPROOF_V1?.snapshot?.()||null)()"
WORKER_STOP = "(()=>{try{self.__WOF_HUDANCHOR_AUTOPROOF_V1?.stop?.();return true}catch(_){return false}})()"

PAGE_INSTALL = r"""(()=>{
'use strict';const KEY='__WOF_HUDANCHOR_AUTOPROOF_V1';try{window[KEY]?.stop?.()}catch(_){}
const canvas=window.I_GF1TC||document.getElementById('whathis'),gl=window.I_fdC8Q;if(!canvas)return {ok:false,reason:'game canvas unavailable'};
let click=null;
function rect(){const r=canvas.getBoundingClientRect();return {left:r.left,top:r.top,width:r.width,height:r.height}}
function content(){const r=rect(),tw=384,th=224,t=tw/th,ratio=r.width/r.height;if(Math.abs(ratio-t)/t<.02)return {...r,mode:'full'};const s=Math.min(r.width/tw,r.height/th),w=tw*s,h=th*s;return {left:r.left+(r.width-w)/2,top:r.top+(r.height-h)/2,width:w,height:h,mode:'contain'}}
function snap(){const r=rect(),q=content(),db={width:gl?.drawingBufferWidth||canvas.width,height:gl?.drawingBufferHeight||canvas.height};return {ok:true,epochMs:Date.now(),canvas:r,content:q,drawingBuffer:db,calibrationClick:click,readOnly:true,ramWrites:0,inputInjection:false,workerReplacement:false}}
function onClick(e){if(click)return;const q=content();if(e.clientX<q.left||e.clientX>q.left+q.width||e.clientY<q.top||e.clientY>q.top+q.height)return;click={epochMs:Date.now(),clientX:e.clientX,clientY:e.clientY,nativeX:(e.clientX-q.left)/q.width*384,nativeY:(e.clientY-q.top)/q.height*224};}
addEventListener('click',onClick,true);window[KEY]={snapshot:snap,stop(){removeEventListener('click',onClick,true);delete window[KEY]}};return {ok:true,installed:true,...snap()};
})()"""
PAGE_SNAPSHOT = "(()=>window.__WOF_HUDANCHOR_AUTOPROOF_V1?.snapshot?.()||null)()"
PAGE_STOP = "(()=>{try{window.__WOF_HUDANCHOR_AUTOPROOF_V1?.stop?.();return true}catch(_){return false}})()"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_reference(path: str | None) -> dict[str, Any] | None:
    candidates: list[Path] = []
    if path:
        candidates.append(Path(path))
    root = _repo_root()
    candidates += [
        root / "parallel/HUDANCHOR_PLAYER_PROJECTION_REVERSE/PROJECTION_MODEL.json",
        root / "parallel/HUDANCHOR_PLAYER_PROJECTION_REVERSE/RESULT.json",
    ]
    for p in candidates:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            return data.get("projectionModel") if isinstance(data.get("projectionModel"), dict) else data
    return None


def _select_endpoint(host: str, port: int | None):
    root = _repo_root()
    sys.path.insert(0, str(root / "parallel/PYLAUNCH"))
    from wof_launcher.browser import probe_endpoint
    from wof_launcher.fleet import discover_fleet_instances
    if port is not None:
        return probe_endpoint(host, port)
    for instance in discover_fleet_instances(live_only=True):
        ep = probe_endpoint(instance.host, instance.port)
        if ep:
            return ep
    for p in (9223, 9222, 9224, 9333):
        ep = probe_endpoint(host, p)
        if ep:
            return ep
    return None


def live_run(args: argparse.Namespace) -> dict[str, Any]:
    root = _repo_root()
    sys.path.insert(0, str(root / "parallel/PYLAUNCH"))
    from wof_launcher.cdp import CdpClient
    from wof_launcher.discovery_v2 import discover

    out: dict[str, Any] = {"schema": SCHEMA, "result": "BLOCKED", "startedAtUtc": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **SAFETY}
    endpoint = _select_endpoint(args.host, args.port)
    if endpoint is None:
        out["reason"] = "未发现 localhost CDP；请先用现有 PYLAUNCH/Browser Fleet 打开 WOF。"
        return out
    out["browserEndpoint"] = endpoint.http_base
    out["browser"] = endpoint.browser
    client = CdpClient(endpoint.websocket_url, timeout=6.0)
    page_s = worker_s = None
    try:
        client.connect()
        choice = discover(client, identity_timeout=25.0, identity_cache={})
        out["discoveryReason"] = choice.reason
        out["discoveryDiagnostics"] = choice.diagnostics
        if not choice.page or not choice.worker or not choice.identity or choice.identity.get("ok") is not True:
            out["reason"] = choice.reason or "WOF page/Worker/World 921031 未唯一确认"
            return out
        if choice.identity.get("sha256") != WORLD_SHA256:
            out["reason"] = "World 921031 SHA-256 不匹配"
            return out
        out["identity"] = choice.identity
        page_s = client.attach(str(choice.page["targetId"]))
        worker_s = client.attach(str(choice.worker["targetId"]))
        worker_s.request("Runtime.enable")
        page_s.request("Runtime.enable")
        wi = worker_s.evaluate(WORKER_INSTALL)
        pi = page_s.evaluate(PAGE_INSTALL)
        if not isinstance(wi, dict) or wi.get("ok") is not True or not isinstance(pi, dict) or pi.get("ok") is not True:
            out["reason"] = "proof probe 安装失败"
            out["workerInstall"] = wi
            out["pageInstall"] = pi
            return out

        print("已连接 WOF / World 921031。")
        print("请正常让 P1 横向移动到背景明显滚动，再上下走位并跳一次。")
        print("如仍需绝对头顶高度，只在 P1 头顶希望警告中心的位置点击一次；无需 DevTools。")
        deadline = time.monotonic() + args.duration
        trace: list[dict[str, Any]] = []
        seen_click = False
        while time.monotonic() < deadline:
            w = worker_s.evaluate(WORKER_SNAPSHOT)
            p = page_s.evaluate(PAGE_SNAPSHOT)
            if isinstance(w, dict) and isinstance(p, dict):
                cam_rows = score_camera_rows(w.get("cameraTop") or [])
                sample = {
                    "workerEpochMs": w.get("epochMs"), "pageEpochMs": p.get("epochMs"),
                    "pageFound": True, "workerFound": True, "identitySha256": WORLD_SHA256,
                    "player": (w.get("players") or {}).get("P1"), "camera": cam_rows[0] if cam_rows else None,
                    "canvas": p.get("canvas"), "drawingBuffer": p.get("drawingBuffer"), **SAFETY,
                }
                click = p.get("calibrationClick")
                if isinstance(click, dict) and not seen_click:
                    sample["visualReference"] = {"nativeX": click.get("nativeX"), "nativeY": click.get("nativeY"), "kind": "single-calibration-click"}
                    seen_click = True
                trace.append(sample)
            time.sleep(args.interval)
        reference = _load_reference(args.projection_model)
        verdict = evaluate_trace(trace, projection_reference=reference)
        out.update({
            "result": verdict["result"], "verdict": verdict, "traceSamples": len(trace),
            "projectionReferenceUsed": reference,
            "completedAtUtc": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        })
        out["reason"] = "HUDANCHOR projection proof PASS" if verdict["result"] == "PASS" else "; ".join(verdict.get("reasons") or ["proof not established"])
        return out
    except Exception as exc:
        out["reason"] = f"proof harness error: {exc}"
        return out
    finally:
        for s, expr in ((worker_s, WORKER_STOP), (page_s, PAGE_STOP)):
            if s:
                try:
                    s.evaluate(expr)
                except Exception:
                    pass
                try:
                    s.close()
                except Exception:
                    pass
        try:
            client.close()
        except Exception:
            pass


def write_outputs(out: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, output)
    summary = output.with_name("HUDANCHOR_PROOF_中文摘要.txt")
    lines = [
        "HUDANCHOR 一键 Browser Proof", f"结果: {out.get('result')}", f"原因: {out.get('reason')}",
        f"只读: {out.get('readOnly')}  RAM 写入: {out.get('ramWrites')}  输入注入: {out.get('inputInjection')}",
    ]
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="WOF HUDANCHOR one-click browser proof (read-only)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int)
    ap.add_argument("--duration", type=float, default=28.0)
    ap.add_argument("--interval", type=float, default=0.25)
    ap.add_argument("--projection-model")
    ap.add_argument("--output", default=str(Path(__file__).resolve().parent / "results/HUDANCHOR_PROOF.json"))
    args = ap.parse_args(argv)
    out = live_run(args)
    write_outputs(out, Path(args.output))
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("result") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
