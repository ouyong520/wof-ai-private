from __future__ import annotations

import base64
import io
import json
import math
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

from .cdp import CdpClient, CdpSession

SCHEMA = "wof-p1-head-visual-v3"
SAFETY = {"readOnly": True, "ramWrites": 0, "inputInjection": False}
MAX_OWNER_CLICKS_PER_AUTHORITY = 1
MAX_TEMPLATES = 6
MIN_TEMPLATES = 3
MIN_TRACKED_FRAMES = 10
AUTO_SEED_MAX_FRAMES = 10
AUTO_SEED_CONFIRM_FRAMES = 2
AUTO_SEED_MIN_SCORE = 0.50
AUTO_SEED_MIN_MARGIN = 0.065

_PAGE_HELPER = r"""
(()=>{
'use strict';
const K='WOFHEADVISUALV3';
try{window[K]?.dispose?.()}catch(_){}
let click=null,clickCount=0,armed=false,box=null,marker=null,action=null;
const canvases=()=>[...document.querySelectorAll('canvas')].map(c=>{const r=c.getBoundingClientRect();const st=getComputedStyle(c);return {c,r,area:Math.max(0,r.width)*Math.max(0,r.height),visible:r.width>=120&&r.height>=80&&st.display!=='none'&&st.visibility!=='hidden'&&Number(st.opacity||1)>0};}).filter(x=>x.visible).sort((a,b)=>b.area-a.area);
const surface=()=>{const xs=canvases();if(!xs.length)return null;const x=xs[0],r=x.r;return {left:r.left,top:r.top,pageX:r.left+scrollX,pageY:r.top+scrollY,width:r.width,height:r.height,backingWidth:x.c.width,backingHeight:x.c.height,dpr:devicePixelRatio||1,visibleCanvasCount:xs.length,layoutKey:[Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height),x.c.width,x.c.height].join(':')};};
const rm=n=>{try{n?.remove?.()}catch(_){}};
const ensureMarker=()=>{if(marker&&marker.isConnected)return marker;marker=document.createElement('div');Object.assign(marker.style,{position:'fixed',width:'22px',height:'22px',marginLeft:'-11px',marginTop:'-11px',border:'2px solid #fff',borderRadius:'50%',boxShadow:'0 0 0 2px rgba(0,0,0,.65)',pointerEvents:'none',zIndex:'2147483646',display:'none'});document.documentElement.appendChild(marker);return marker;};
const ensureAction=()=>{if(action&&action.isConnected)return action;action=document.createElement('div');Object.assign(action.style,{position:'fixed',left:'50%',top:'12px',transform:'translateX(-50%)',padding:'7px 12px',background:'rgba(0,0,0,.78)',color:'#fff',font:'600 14px system-ui,sans-serif',borderRadius:'6px',pointerEvents:'none',zIndex:'2147483647',maxWidth:'80vw',textAlign:'center',display:'none'});document.documentElement.appendChild(action);return action;};
function setAction(text){const a=ensureAction();if(text){a.textContent=String(text);a.style.display='block';}else a.style.display='none';return true;}
function showMarker(x,y,visible){const s=surface(),m=ensureMarker();if(!visible||!s||!Number.isFinite(x)||!Number.isFinite(y)){m.style.display='none';return true;}m.style.left=(s.left+x)+'px';m.style.top=(s.top+y)+'px';m.style.display='block';return true;}
function armClick(){if(clickCount>=1||click)return false;const s=surface();if(!s)return false;rm(box);box=document.createElement('div');Object.assign(box.style,{position:'fixed',left:s.left+'px',top:s.top+'px',width:s.width+'px',height:s.height+'px',cursor:'crosshair',background:'rgba(0,0,0,.001)',zIndex:'2147483645',touchAction:'none'});const take=e=>{if(clickCount>=1)return;e.preventDefault();e.stopPropagation();e.stopImmediatePropagation?.();const now=surface();if(!now)return;click={x:Math.max(0,Math.min(now.width,e.clientX-now.left)),y:Math.max(0,Math.min(now.height,e.clientY-now.top)),layoutKey:now.layoutKey,at:Date.now()};clickCount++;armed=false;rm(box);box=null;setAction('');};box.addEventListener('pointerdown',take,{capture:true,once:true});document.documentElement.appendChild(box);armed=true;setAction('请点一下场景中 P1 人物实际头部（只需一次）');return true;}
function status(){return {schema:'wof-p1-head-visual-v3',surface:surface(),click,clickCount,armed,readOnly:true,ramWrites:0,inputInjection:false};}
function dispose(){rm(box);rm(marker);rm(action);box=marker=action=null;armed=false;return true;}
window[K]={schema:'wof-p1-head-visual-v3',surface,status,armClick,setAction,showMarker,dispose};
return status();
})()
"""

class HeadVisualError(RuntimeError):
    pass

@dataclass
class _Template:
    image: Image.Image
    normalized: Image.Image
    sample_class: str
    score_at_add: float
    created_at: float
    asymmetry: float

def _normalized(image: Image.Image, size: int = 18) -> Image.Image:
    return image.convert("L").resize((size, size), Image.Resampling.BILINEAR)

def _distance(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a, b)
    return float(ImageStat.Stat(diff).mean[0]) / 255.0

def _variance(image: Image.Image) -> float:
    st = ImageStat.Stat(image.convert("L"))
    return float(st.var[0]) if st.var else 0.0

def _asymmetry(image: Image.Image) -> float:
    g = image.convert("L")
    w, h = g.size
    if w < 4 or h < 2:
        return 0.0
    l = ImageStat.Stat(g.crop((0, 0, w // 2, h))).mean[0]
    r = ImageStat.Stat(g.crop((w - w // 2, 0, w, h))).mean[0]
    return (float(l) - float(r)) / 255.0

def _palette_signature(image: Image.Image) -> tuple[dict[int, float], float, float]:
    small = image.convert("RGB").resize((16, 16), Image.Resampling.BILINEAR)
    counts: Counter[int] = Counter(); saturated = 0; bright = 0
    pixels = list(small.getdata())
    for red, green, blue in pixels:
        hi = max(red, green, blue); lo = min(red, green, blue); chroma = hi - lo
        if hi > 235 and lo > 205: bright += 1
        if chroma >= 28: saturated += 1
        if hi < 48 or chroma < 24 or (hi > 240 and lo > 210):
            continue
        key = (red // 64) * 16 + (green // 64) * 4 + (blue // 64)
        counts[key] += 1
    kept = sum(counts.values())
    if kept < 12:
        return {}, saturated / len(pixels), bright / len(pixels)
    return ({k: v / kept for k, v in counts.most_common(8)}, saturated / len(pixels), bright / len(pixels))

def _palette_overlap(a: dict[int, float], b: dict[int, float]) -> float:
    return float(sum(min(value, b.get(key, 0.0)) for key, value in a.items()))

def _hud_identity_patch(frame: Image.Image, patch_radius: int) -> dict[str, Any] | None:
    w, h = frame.size; r = max(8, int(patch_radius)); x1 = max(r * 2, int(w * 0.34)); y1 = max(r * 2, int(h * 0.26)); step = max(4, r // 2)
    best: dict[str, Any] | None = None
    for cy in range(r, max(r, y1 - r) + 1, step):
        for cx in range(r, max(r, x1 - r) + 1, step):
            patch = frame.crop((cx-r, cy-r, cx+r, cy+r)); signature, saturated, bright = _palette_signature(patch); var = _variance(patch)
            if not signature or var < 45.0 or saturated < 0.12 or bright > 0.55: continue
            score = min(1.0, var / 1800.0) * 0.35 + saturated * 0.45 + (1.0 - cx / max(1.0, float(x1))) * 0.20
            row = {"center": (float(cx), float(cy)), "patch": patch, "signature": signature, "score": score}
            if best is None or score > float(best["score"]): best = row
    return best

def auto_seed_candidate(frame: Image.Image, patch_radius: int, p1_identity: dict[str, Any] | None) -> dict[str, Any]:
    """Find one unique live-scene P1-head seed without treating RAM/world coordinates as screen authority."""
    if not isinstance(p1_identity, dict) or p1_identity.get("active") is not True:
        return {"ok": False, "reason": "P1_NOT_ACTIVE", "candidateCount": 0}
    try: p1_type = int(p1_identity["type"])
    except (KeyError, TypeError, ValueError): return {"ok": False, "reason": "P1_IDENTITY_UNRESOLVED", "candidateCount": 0}
    hud = _hud_identity_patch(frame, patch_radius)
    if hud is None: return {"ok": False, "reason": "HUD_IDENTITY_UNRESOLVED", "candidateCount": 0, "p1Type": p1_type}
    w, h = frame.size; r = max(8, int(patch_radius)); scene_y0 = max(r * 2, int(h * 0.28)); step = max(4, r // 2); rows: list[dict[str, Any]] = []
    for cy in range(scene_y0, h-r+1, step):
        for cx in range(r, w-r+1, step):
            patch = frame.crop((cx-r, cy-r, cx+r, cy+r)); signature, saturated, bright = _palette_signature(patch); var = _variance(patch)
            if not signature or var < 45.0 or saturated < 0.10 or bright > 0.45: continue
            overlap = _palette_overlap(hud["signature"], signature)
            if overlap < 0.25: continue
            score = overlap + min(0.12, var / 5000.0 * 0.12) + min(0.06, saturated * 0.06) - bright * 0.12
            rows.append({"score": float(score), "center": (float(cx), float(cy)), "overlap": float(overlap), "variance": float(var)})
    rows.sort(key=lambda row: (-float(row["score"]), row["center"][1], row["center"][0]))
    peaks: list[dict[str, Any]] = []
    for row in rows:
        cx, cy = row["center"]
        if all(math.hypot(cx-p["center"][0], cy-p["center"][1]) >= r * 3.0 for p in peaks):
            peaks.append(row)
            if len(peaks) >= 8: break
    if not peaks: return {"ok": False, "reason": "NO_SCENE_P1_CANDIDATE", "candidateCount": 0, "p1Type": p1_type, "hudCenter": list(hud["center"])}
    best = peaks[0]; second_score = float(peaks[1]["score"]) if len(peaks) > 1 else 0.0; margin = float(best["score"]) - second_score
    plausible = [row for row in peaks if float(best["score"]) - float(row["score"]) < AUTO_SEED_MIN_MARGIN]
    ok = float(best["score"]) >= AUTO_SEED_MIN_SCORE and margin >= AUTO_SEED_MIN_MARGIN and len(plausible) == 1
    return {"ok": ok, "reason": None if ok else ("LOW_SCENE_IDENTITY_SCORE" if float(best["score"]) < AUTO_SEED_MIN_SCORE else "AMBIGUOUS_SCENE_P1"), "center": best["center"], "score": float(best["score"]), "margin": margin, "candidateCount": len(plausible), "p1Type": p1_type, "hudCenter": list(hud["center"]), "sceneRegionTop": scene_y0}

def match_patch(frame: Image.Image, templates: list[Image.Image], previous_center: tuple[float, float], patch_radius: int, search_radius: int) -> dict[str, Any]:
    """Pure bounded local matcher used by the live tracker and deterministic tests."""
    if not templates: return {"ok": False, "reason": "NO_TEMPLATES"}
    w, h = frame.size; cx, cy = previous_center; r = max(6, int(patch_radius)); sr = max(r, int(search_radius)); step = max(2, r // 5); norms = [_normalized(t) for t in templates]; rows: list[tuple[float, int, int]] = []
    x0 = max(r, int(cx) - sr); x1 = min(w - r, int(cx) + sr); y0 = max(r, int(cy) - sr); y1 = min(h - r, int(cy) + sr)
    if x0 > x1 or y0 > y1: return {"ok": False, "reason": "SEARCH_OUTSIDE_SURFACE"}
    for y in range(y0, y1 + 1, step):
        for x in range(x0, x1 + 1, step):
            p = _normalized(frame.crop((x-r, y-r, x+r, y+r))); score = min(_distance(p, t) for t in norms); rows.append((score, x, y))
    if not rows: return {"ok": False, "reason": "NO_SEARCH_CANDIDATES"}
    rows.sort(key=lambda v: v[0]); best = rows[0]; second = next((row for row in rows[1:] if math.hypot(row[1]-best[1], row[2]-best[2]) >= max(6, r * 0.75)), None); second_score = second[0] if second else 1.0; margin = second_score - best[0]; ok = best[0] <= 0.225 and margin >= 0.012
    return {"ok": ok, "reason": None if ok else ("LOW_CONFIDENCE" if best[0] > 0.225 else "AMBIGUOUS_MATCH"), "center": (float(best[1]), float(best[2])), "score": float(best[0]), "confidence": max(0.0, min(1.0, 1.0 - best[0])), "margin": float(margin)}

class P1HeadVisualTracker:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir); self.output_dir.mkdir(parents=True, exist_ok=True)
        self._client: CdpClient | None = None; self._session: CdpSession | None = None; self._page_id: str | None = None
        self._authority_key: str | None = None; self._runtime_epoch: str | None = None; self._state = "IDLE"; self._error: str | None = None
        self._center: tuple[float, float] | None = None; self._templates: list[_Template] = []; self._click_count = 0; self._layout: dict[str, Any] | None = None
        self._patch_radius = 20; self._tracked_frames = 0; self._lost_frames = 0; self._recovery_count = 0; self._action: str | None = None; self._bound_at = 0.0; self._last_template_at = 0.0
        self._p1_generation: int | None = None; self._p1_active = True; self._p1_type: int | None = None; self._p1_position: tuple[float, float, float] | None = None
        self._last_confidence: float | None = None; self._last_score: float | None = None; self._last_margin: float | None = None; self._template_meta: list[dict[str, Any]] = []
        self._auto_seed_attempts = 0; self._auto_seed_streak = 0; self._auto_seed_reason: str | None = None; self._auto_seed_candidate_count = 0; self._auto_seed_prior: dict[str, Any] | None = None; self._seed_source: str | None = None; self._click_seed_at: int | None = None; self._revocation_reason: str | None = None

    def bind(self, client: CdpClient, page_target_id: str, authority_key: str, runtime_epoch: str) -> dict[str, Any]:
        self.dispose(); self._client = client; self._page_id = page_target_id; self._authority_key = authority_key; self._runtime_epoch = runtime_epoch
        self._session = client.attach(page_target_id); self._session.request("Runtime.enable"); remote = self._session.evaluate(_PAGE_HELPER, timeout=10.0); self._validate_helper(remote)
        self._state = "CAMERA_PREPARING"; self._bound_at = time.monotonic(); self._click_count = 0; self._templates.clear(); self._template_meta.clear(); self._center = None
        self._tracked_frames = 0; self._lost_frames = 0; self._recovery_count = 0; self._layout = self._surface(remote); self._patch_radius = self._patch_radius_for(self._layout); self._set_action(None)
        self._p1_generation = None; self._p1_active = True; self._p1_type = None; self._p1_position = None; self._reset_auto_seed(); self._seed_source = None; self._click_seed_at = None; self._revocation_reason = None
        return self.status()

    @staticmethod
    def _validate_helper(remote: Any) -> None:
        if not isinstance(remote, dict) or remote.get("schema") != SCHEMA: raise HeadVisualError("P1 visual helper failed to install")
        if remote.get("readOnly") is not True or remote.get("ramWrites") != 0 or remote.get("inputInjection") is not False: raise HeadVisualError("P1 visual helper safety mismatch")

    @staticmethod
    def _surface(remote: dict[str, Any]) -> dict[str, Any] | None:
        s = remote.get("surface")
        if not isinstance(s, dict): return None
        try:
            if float(s.get("width", 0)) < 120 or float(s.get("height", 0)) < 80: return None
        except (TypeError, ValueError): return None
        return dict(s)

    @staticmethod
    def _patch_radius_for(surface: dict[str, Any] | None) -> int:
        if not surface: return 20
        m = min(float(surface.get("width", 0)), float(surface.get("height", 0)))
        return max(12, min(34, int(round(m * 0.045))))

    def _helper_status(self) -> dict[str, Any]:
        if not self._session: raise HeadVisualError("P1 visual page session unavailable")
        remote = self._session.evaluate("window.WOFHEADVISUALV3?.status?.()||null", timeout=5.0); self._validate_helper(remote); return remote

    def _set_action(self, text: str | None) -> None:
        self._action = text or None
        if self._session:
            try: self._session.evaluate(f"window.WOFHEADVISUALV3?.setAction?.({json.dumps(self._action or '')});true", timeout=3.0)
            except Exception: pass

    def _marker(self, visible: bool) -> None:
        if not self._session: return
        try:
            if visible and self._center and self._layout:
                sx = float(self._layout.get("width") or 1) / max(1.0, float(self._last_frame_size()[0])); sy = float(self._layout.get("height") or 1) / max(1.0, float(self._last_frame_size()[1])); x, y = self._center[0] * sx, self._center[1] * sy; expr = f"window.WOFHEADVISUALV3?.showMarker?.({x:.3f},{y:.3f},true);true"
            else: expr = "window.WOFHEADVISUALV3?.showMarker?.(0,0,false);true"
            self._session.evaluate(expr, timeout=3.0)
        except Exception: pass

    def _last_frame_size(self) -> tuple[int, int]:
        if hasattr(self, "_frame_size"): return self._frame_size
        if self._layout: return (max(1, int(float(self._layout.get("width") or 1))), max(1, int(float(self._layout.get("height") or 1))))
        return (1, 1)

    def _capture(self, surface: dict[str, Any]) -> Image.Image:
        if not self._session: raise HeadVisualError("P1 visual page session unavailable")
        try: x = max(0.0, float(surface.get("pageX", surface.get("left", 0)))); y = max(0.0, float(surface.get("pageY", surface.get("top", 0)))); w = max(1.0, float(surface["width"])); h = max(1.0, float(surface["height"]))
        except (KeyError, TypeError, ValueError) as exc: raise HeadVisualError(f"invalid game canvas geometry: {exc}") from exc
        result = self._session.request("Page.captureScreenshot", {"format": "png", "fromSurface": True, "captureBeyondViewport": False, "clip": {"x": x, "y": y, "width": w, "height": h, "scale": 1}}, timeout=8.0); data = result.get("data")
        if not isinstance(data, str) or not data: raise HeadVisualError("Page.captureScreenshot returned no image")
        try: image = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
        except Exception as exc: raise HeadVisualError(f"invalid canvas screenshot: {exc}") from exc
        self._frame_size = image.size; return image

    def _crop(self, frame: Image.Image, center: tuple[float, float]) -> Image.Image:
        r = self._patch_radius; x = int(round(center[0])); y = int(round(center[1]))
        if x-r < 0 or y-r < 0 or x+r > frame.width or y+r > frame.height: raise HeadVisualError("P1 head seed is too close to game-surface edge")
        patch = frame.crop((x-r, y-r, x+r, y+r))
        if _variance(patch) < 45.0: raise HeadVisualError("P1 head crop lacks enough visual detail")
        return patch

    def _add_template(self, patch: Image.Image, sample_class: str, score: float) -> bool:
        norm = _normalized(patch)
        if self._templates:
            ds = [_distance(norm, t.normalized) for t in self._templates]; nearest = min(ds)
            if nearest < 0.055 or nearest > 0.28: return False
        else: nearest = 0.0
        asym = _asymmetry(patch); row = _Template(patch.copy(), norm, sample_class, score, time.monotonic(), asym); self._templates.append(row)
        if len(self._templates) > MAX_TEMPLATES: self._templates.pop(1 if len(self._templates) > 1 else 0)
        self._last_template_at = time.monotonic(); idx = len(self._template_meta) + 1; path = self.output_dir / f"p1_head_template_{idx:02d}.png"; patch.save(path, format="PNG")
        self._template_meta.append({"index": idx, "sampleClass": sample_class, "nearestTemplateDistance": nearest, "scoreAtAdd": score, "asymmetry": asym, "path": path.name}); return True

    def _reset_auto_seed(self) -> None:
        self._auto_seed_attempts = 0; self._auto_seed_streak = 0; self._auto_seed_reason = None; self._auto_seed_candidate_count = 0; self._auto_seed_prior = None

    def _revoke_visual_authority(self, reason: str) -> None:
        self._templates.clear(); self._template_meta.clear(); self._center = None; self._tracked_frames = 0; self._lost_frames = 0; self._last_confidence = None; self._last_score = None; self._last_margin = None; self._seed_source = None; self._revocation_reason = reason; self._reset_auto_seed(); self._state = "HEAD_ACQUIRING"; self._marker(False); self._set_action(None)

    @staticmethod
    def _coarse_position(lifecycle: Any) -> tuple[float, float, float] | None:
        if not isinstance(lifecycle, dict): return None
        try: return (float(lifecycle["x"]), float(lifecycle["y"]), float(lifecycle["z"]))
        except (KeyError, TypeError, ValueError): return None

    def _attempt_auto_seed(self, frame: Image.Image, lifecycle: Any) -> bool:
        self._auto_seed_attempts += 1; result = auto_seed_candidate(frame, self._patch_radius, lifecycle if isinstance(lifecycle, dict) else None); self._auto_seed_reason = str(result.get("reason") or "SAFE_UNIQUE_CANDIDATE"); self._auto_seed_candidate_count = int(result.get("candidateCount") or 0)
        if not result.get("ok"):
            self._auto_seed_streak = 0; self._auto_seed_prior = None; self._marker(False); return False
        center = tuple(result["center"]); position = self._coarse_position(lifecycle); ident = (self._p1_generation, self._p1_type); prior = self._auto_seed_prior; consistent = False
        if prior and prior.get("identity") == ident:
            screen_delta = math.hypot(center[0]-prior["center"][0], center[1]-prior["center"][1]); prior_pos = prior.get("position"); coarse_delta = None if position is None or prior_pos is None else math.sqrt(sum((position[i]-prior_pos[i])**2 for i in range(3))); consistent = screen_delta <= max(18.0, self._patch_radius * 3.0) and (coarse_delta is None or coarse_delta <= 96.0)
        self._auto_seed_streak = self._auto_seed_streak + 1 if consistent else 1; self._auto_seed_prior = {"identity": ident, "center": center, "position": position}
        if self._auto_seed_streak < AUTO_SEED_CONFIRM_FRAMES:
            self._marker(False); return False
        patch = self._crop(frame, center); self._center = center; self._add_template(patch, "auto-seed", max(0.0, 1.0-float(result.get("score") or 0.0))); self._seed_source = "AUTO_P1_HUD_SCENE_UNIQUE"; self._state = "HEAD_TRACKING"; self._tracked_frames = 1; self._lost_frames = 0; self._last_confidence = min(1.0, float(result.get("score") or 0.0)); self._last_score = max(0.0, 1.0-float(result.get("score") or 0.0)); self._last_margin = float(result.get("margin") or 0.0); self._set_action(None); self._marker(True); return True

    def _seed_from_click(self, remote: dict[str, Any], frame: Image.Image, surface: dict[str, Any]) -> bool:
        click = remote.get("click")
        if not isinstance(click, dict): return False
        self._click_count = int(remote.get("clickCount") or 0)
        if self._click_count > MAX_OWNER_CLICKS_PER_AUTHORITY: raise HeadVisualError("P1 visual authority exceeded one-click maximum")
        click_at = int(click.get("at") or 0)
        if click_at and click_at == self._click_seed_at: return False
        if click.get("layoutKey") and click.get("layoutKey") != surface.get("layoutKey"): return False
        try: css_x, css_y = float(click["x"]), float(click["y"]); sw, sh = float(surface["width"]), float(surface["height"])
        except (KeyError, TypeError, ValueError) as exc: raise HeadVisualError(f"invalid P1 head click: {exc}") from exc
        if css_y < sh * 0.28: raise HeadVisualError("fallback click must target the live-scene P1 head, not HUD/portrait UI")
        center = (css_x * frame.width / max(1.0, sw), css_y * frame.height / max(1.0, sh)); patch = self._crop(frame, center); self._center = center; self._add_template(patch, "fallback-click-seed", 0.0); self._click_seed_at = click_at or int(time.time()*1000); self._seed_source = "OWNER_FALLBACK_CLICK"; self._state = "HEAD_TRACKING"; self._tracked_frames = 1; self._lost_frames = 0; self._last_confidence = 1.0; self._last_score = 0.0; self._last_margin = 1.0; self._set_action(None); self._marker(True); return True

    def _arm_once(self) -> None:
        if not self._session or self._click_count >= MAX_OWNER_CLICKS_PER_AUTHORITY: return
        remote = self._helper_status(); self._click_count = int(remote.get("clickCount") or 0)
        if self._click_count >= MAX_OWNER_CLICKS_PER_AUTHORITY or remote.get("armed") is True: return
        armed = self._session.evaluate("window.WOFHEADVISUALV3?.armClick?.()===true", timeout=3.0)
        if armed is not True: raise HeadVisualError("unable to arm one-time P1 head acquisition click")

    def _layout_changed(self, prior: dict[str, Any] | None, current: dict[str, Any]) -> bool:
        return bool(prior and prior.get("layoutKey") != current.get("layoutKey"))

    def _guidance(self) -> None:
        if self._state != "HEAD_TRACKING": return
        elapsed = time.monotonic() - self._bound_at
        if len(self._templates) < 2 and elapsed >= 6.0: self._set_action("现在左右走动一下")
        elif len(self._templates) < 3 and elapsed >= 11.0: self._set_action("现在换个方向走动一下")
        else: self._set_action(None)

    def update_lifecycle(self, lifecycle: Any) -> None:
        if not isinstance(lifecycle, dict): return
        previous_active = self._p1_active; previous_generation = self._p1_generation; active = lifecycle.get("active") is True; gen = lifecycle.get("generation")
        try: generation = int(gen) if gen is not None else None
        except (TypeError, ValueError): generation = None
        try: p1_type = int(lifecycle["type"]) if active and lifecycle.get("type") is not None else None
        except (TypeError, ValueError): p1_type = None
        generation_changed = previous_generation is not None and generation is not None and generation != previous_generation; became_inactive = previous_active and not active
        self._p1_generation = generation if generation is not None else self._p1_generation; self._p1_active = active; self._p1_type = p1_type; self._p1_position = self._coarse_position(lifecycle)
        if generation_changed: self._revoke_visual_authority("P1_GENERATION_CHANGED")
        elif became_inactive: self._revoke_visual_authority("P1_INACTIVE")
        if not active: self._marker(False); self._set_action(None)

    def poll(self, lifecycle: Any = None) -> dict[str, Any]:
        if not self._session or not self._authority_key or not self._runtime_epoch: return self.status()
        self.update_lifecycle(lifecycle); remote = self._helper_status(); self._click_count = int(remote.get("clickCount") or 0); surface = self._surface(remote)
        if surface is None: self._state = "CAMERA_PREPARING"; self._marker(False); self._set_action(None); return self.status()
        frame = self._capture(surface)
        if self._layout_changed(self._layout, surface): self._layout = surface; self._patch_radius = self._patch_radius_for(surface); self._revoke_visual_authority("LAYOUT_CHANGED")
        else: self._layout = surface; self._patch_radius = self._patch_radius_for(surface) if not self._templates else self._patch_radius
        if not self._templates:
            if self._seed_from_click(remote, frame, surface): return self.status()
            if not self._p1_active or self._p1_type is None:
                self._state = "HEAD_ACQUIRING"; self._set_action("正在自动识别 P1 角色；进入场景后无需点击。"); self._marker(False); return self.status()
            if self._auto_seed_attempts < AUTO_SEED_MAX_FRAMES:
                self._state = "HEAD_ACQUIRING"; self._set_action("正在自动识别 P1 角色并定位场景头部…")
                if self._attempt_auto_seed(frame, lifecycle): return self.status()
                if self._auto_seed_attempts < AUTO_SEED_MAX_FRAMES: return self.status()
            if self._click_count < MAX_OWNER_CLICKS_PER_AUTHORITY:
                self._state = "ONE_CLICK_REQUIRED"; self._set_action("自动定位无法安全唯一确认；请点一下场景中 P1 人物实际头部（只需一次）"); self._arm_once(); return self.status()
            self._state = "HEAD_ACQUIRING"; self._set_action("自动重新定位中；本 authority 已使用过一次 fallback，不会再次要求点击。"); self._marker(False); return self.status()
        if not self._p1_active: return self.status()
        if not self._center: self._state = "HEAD_ACQUIRING"; self._marker(False); return self.status()
        search_radius = min(max(36, self._patch_radius * (4 if self._lost_frames else 3)), max(42, min(frame.size)//4)); result = match_patch(frame, [t.image for t in self._templates], self._center, self._patch_radius, search_radius)
        if not result.get("ok"):
            self._lost_frames += 1; self._state = "HEAD_ACQUIRING"; self._last_confidence = float(result.get("confidence") or 0.0); self._last_score = float(result.get("score") or 1.0) if result.get("score") is not None else None; self._last_margin = float(result.get("margin") or 0.0) if result.get("margin") is not None else None; self._marker(False)
            if self._lost_frames >= 8: self._set_action("请让 P1 保持在游戏画面中正常活动")
            return self.status()
        old_center = self._center; self._center = tuple(result["center"])
        if self._lost_frames: self._recovery_count += 1
        self._lost_frames = 0; self._tracked_frames += 1; self._state = "HEAD_TRACKING"; self._last_confidence = float(result["confidence"]); self._last_score = float(result["score"]); self._last_margin = float(result["margin"]); self._marker(True)
        dx = math.hypot(self._center[0]-old_center[0], self._center[1]-old_center[1]); patch = self._crop(frame, self._center); nearest = min((_distance(_normalized(patch), t.normalized) for t in self._templates), default=0.0)
        cls = "walking" if dx >= max(2.5, self._patch_radius * 0.12) else "standing"; seed_asym = self._templates[0].asymmetry if self._templates else 0.0; cur_asym = _asymmetry(patch)
        if abs(seed_asym) > 0.025 and abs(cur_asym) > 0.025 and seed_asym * cur_asym < 0: cls = "facing-change"
        if self._tracked_frames >= 3 and time.monotonic()-self._last_template_at >= 0.8 and nearest >= 0.055: self._add_template(patch, cls, self._last_score or 0.0)
        self._guidance(); return self.status()

    def qualified(self) -> bool:
        return len(self._templates) >= MIN_TEMPLATES and self._tracked_frames >= MIN_TRACKED_FRAMES and self._state == "HEAD_TRACKING" and self._lost_frames == 0

    def status(self) -> dict[str, Any]:
        return {"schema": SCHEMA, "state": self._state, "authorityKey": self._authority_key, "runtimeEpoch": self._runtime_epoch, "ownerClickCount": self._click_count, "ownerClickMaximum": MAX_OWNER_CLICKS_PER_AUTHORITY, "ownerClickExpectedNormal": 0, "templateCount": len(self._templates), "templateMinimum": MIN_TEMPLATES, "templateSamples": list(self._template_meta), "trackedFrames": self._tracked_frames, "minimumTrackedFrames": MIN_TRACKED_FRAMES, "lostFrames": self._lost_frames, "recoveryCount": self._recovery_count, "confidence": self._last_confidence, "matchScore": self._last_score, "ambiguityMargin": self._last_margin, "center": list(self._center) if self._center else None, "actionZh": self._action, "p1Active": self._p1_active, "p1Generation": self._p1_generation, "p1Type": self._p1_type, "p1CoarsePosition": list(self._p1_position) if self._p1_position else None, "layoutKey": self._layout.get("layoutKey") if self._layout else None, "autoSeedAttemptCount": self._auto_seed_attempts, "autoSeedMaximumFrames": AUTO_SEED_MAX_FRAMES, "autoSeedConfirmFrames": AUTO_SEED_CONFIRM_FRAMES, "autoSeedStreak": self._auto_seed_streak, "autoSeedReason": self._auto_seed_reason, "autoSeedCandidateCount": self._auto_seed_candidate_count, "seedSource": self._seed_source, "revocationReason": self._revocation_reason, "qualified": self.qualified(), "productionOverlayEnabled": False, "measurementMarkerVisible": self._state == "HEAD_TRACKING" and self._lost_frames == 0, "error": self._error, **SAFETY}

    def result(self) -> dict[str, Any]: return {**self.status(), "terminal": True}

    def dispose(self) -> None:
        if self._session:
            try: self._session.evaluate("window.WOFHEADVISUALV3?.dispose?.();true", timeout=2.0)
            except Exception: pass
            try: self._session.close()
            except Exception: pass
        self._session = None; self._client = None; self._page_id = None; self._authority_key = None; self._runtime_epoch = None
