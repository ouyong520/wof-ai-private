(()=>{
'use strict';
const VERSION='wof-alpha-relative-enemy-overlay-v1';
const cfg=window.__WOF_ALPHA_CONFIG,TRANSPORT=window.__WOF_ALPHA_TRANSPORT_V1,R=window.WOFAlphaRelativeHeadAnchor,hud=window.WOFALPHAHUD;
if(!cfg||typeof cfg.session!=='string'||typeof cfg.channel!=='string'||!TRANSPORT?.matches||R?.VERSION!=='wof-alpha-relative-head-anchor-v1'||!hud)throw new Error('relative enemy overlay prerequisites missing');
try{window.WOFALPHARELATIVEENEMY?.dispose?.();}catch(_){}
const canvas=window.I_GF1TC||document.getElementById('whathis'),gl=window.I_fdC8Q;
if(!canvas||!gl)throw new Error('relative enemy overlay game canvas/context missing');

const LABELS=Object.freeze({P1:'1P',P2:'2P',P3:'3P'}),MARKER_STALE_MS=300,PLAYER_STALE_MS=120,TRACKER_STALE_MS=650,MAX_SAMPLES=80;
const layer=document.createElement('canvas'),ctx=layer.getContext('2d');
Object.assign(layer.style,{position:'fixed',pointerEvents:'none',zIndex:'2147483643',display:'block'});document.documentElement.appendChild(layer);
let disposed=false,lastPlayerMsg=null,lastPlayerRx=0,lastMarkerMsg=null,lastMarkerRx=0,p1Tracker=null,p1TrackerRx=0,samples=[],fit=null,lastSampleAt=null,drawCount=0,suppressedReason='WAITING_P1_TRACKER';

function drawingBufferState(now){
  const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(W>0&&H>0))return null;
  let vp;try{vp=Array.from(gl.getParameter(gl.VIEWPORT));}catch(_){return null;}
  if(!Array.isArray(vp)||vp.length!==4||!vp.every(Number.isFinite)||vp[2]<=0||vp[3]<=0)return null;
  const x=vp[0],y=H-(vp[1]+vp[3]),width=vp[2],height=vp[3];
  if(x<0||y<0||x+width>W||y+height>H)return null;
  return{width:W,height:H,contentRect:{x,y,width,height},sampleAt:now,confidence:1,mappingVersion:[W,H,...vp].join(':')};
}
function syncLayer(){
  const r=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
  layer.style.left=r.left+'px';layer.style.top=r.top+'px';layer.style.width=r.width+'px';layer.style.height=r.height+'px';
  const w=Math.max(1,Math.round(r.width*dpr)),h=Math.max(1,Math.round(r.height*dpr));
  if(layer.width!==w||layer.height!==h){layer.width=w;layer.height=h;}
  ctx.setTransform(dpr,0,0,dpr,0,0);return{rect:r,dpr};
}
function clearFit(reason){samples=[];fit=null;lastSampleAt=null;suppressedReason=reason;}
function trackerNative(now){
  if(!p1Tracker||!p1TrackerRx||now-p1TrackerRx>TRACKER_STALE_MS)return null;
  const r=canvas.getBoundingClientRect(),db=drawingBufferState(now);if(!(r.width>0&&r.height>0)||!db)return null;
  return R.nativeFromCss({x:p1Tracker.x,y:p1Tracker.y,cssWidth:r.width,cssHeight:r.height,drawingBufferState:db});
}
function captureSample(now){
  if(!lastPlayerMsg||!lastPlayerRx||now-lastPlayerRx>PLAYER_STALE_MS)return;
  const p1=lastPlayerMsg?.players?.P1;if(!p1?.present)return;
  const native=trackerNative(now);if(!native)return;
  const sampleAt=Number(lastPlayerMsg.sampleAt||p1.sampleAt||0);if(sampleAt&&sampleAt===lastSampleAt)return;
  lastSampleAt=sampleAt||now;samples.push({headNativeY:native.y,worldY:Number(p1.y),worldZ:Number(p1.z)});if(samples.length>MAX_SAMPLES)samples.shift();
  fit=R.fitVertical(samples,{minSamples:6,minYRange:5,minZRange:5,maxResidual:3.5,minGap:.65});
  suppressedReason=fit?.ok?null:(fit?.reason||'GEOMETRY_NOT_READY');
}
function drawLabel(x,y,text){
  ctx.font='700 14px system-ui,sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
  const w=34,h=22,px=Math.max(w/2,Math.min(layer.getBoundingClientRect().width-w/2,x)),py=Math.max(h/2,Math.min(layer.getBoundingClientRect().height-h/2,y-18));
  ctx.fillStyle='rgba(0,0,0,.82)';ctx.fillRect(px-w/2,py-h/2,w,h);ctx.lineWidth=2;ctx.strokeStyle='rgba(255,255,255,.98)';ctx.strokeRect(px-w/2+1,py-h/2+1,w-2,h-2);ctx.fillStyle='#fff';ctx.fillText(text,px,py+.5);drawCount++;
}
function render(now){
  const view=syncLayer();ctx.clearRect(0,0,view.rect.width,view.rect.height);captureSample(now);
  if(!fit?.ok){suppressedReason=fit?.reason||'GEOMETRY_NOT_READY';return;}
  if(!lastMarkerMsg||!lastMarkerRx||now-lastMarkerRx>MARKER_STALE_MS){suppressedReason='STALE_OR_MISSING_ENEMIES';return;}
  if(!lastPlayerMsg||!lastPlayerRx||now-lastPlayerRx>PLAYER_STALE_MS){suppressedReason='STALE_OR_MISSING_P1_WORLD';return;}
  const p1=lastPlayerMsg?.players?.P1,native=trackerNative(now);if(!p1?.present||!native){suppressedReason='P1_HEAD_AUTHORITY_MISSING';return;}
  const db=drawingBufferState(now);if(!db){suppressedReason='DRAWING_BUFFER_INVALID';return;}
  let rendered=0;
  for(const m of Array.isArray(lastMarkerMsg.markers)?lastMarkerMsg.markers:[]){
    const label=LABELS[m?.target];if(!label)continue;
    const p=R.projectEnemyRelative({enemy:{x:Number(m.enemyX),y:Number(m.enemyY),z:Number(m.enemyZ)},p1:{x:Number(p1.x),y:Number(p1.y),z:Number(p1.z)},p1HeadNative:native,fit,extraClearanceNative:0});
    if(!p.ok)continue;
    const q=R.nativeToDb(p,db);if(!q)continue;
    const xCss=q.x/db.width*view.rect.width,yCss=q.y/db.height*view.rect.height;drawLabel(xCss,yCss,label);rendered++;
  }
  suppressedReason=rendered?null:'NO_SAFE_RELATIVE_ENEMY_ANCHOR';
}
let raf=0;function loop(){if(disposed)return;render(Date.now());raf=requestAnimationFrame(loop);}raf=requestAnimationFrame(loop);

const bc=new BroadcastChannel(cfg.channel);bc.onmessage=e=>{
  const m=e.data;if(!(m&&m.schema==='wof-alpha-v2'&&m.session===cfg.session&&TRANSPORT.matches(m)))return;
  if(m.kind==='player-head-spatial'){lastPlayerMsg=m;lastPlayerRx=Date.now();}
  else if(m.kind==='enemy-target-markers'){lastMarkerMsg=m;lastMarkerRx=Date.now();}
  else if(m.kind==='diag'){lastPlayerMsg=null;lastPlayerRx=0;lastMarkerMsg=null;lastMarkerRx=0;clearFit('RUNTIME_DIAG');}
};

const original={
  bind:hud.bindP1HeadTrackerAuthority.bind(hud),set:hud.setP1HeadTracker.bind(hud),clear:hud.clearP1HeadTracker.bind(hud),clearAuthority:hud.clearP1HeadTrackerAuthority.bind(hud),dispose:hud.dispose.bind(hud)
};
function bindWrapper(binding){clearFit('NEW_TRACKER_AUTHORITY');p1Tracker=null;p1TrackerRx=0;return original.bind(binding);}
function setWrapper(payload){const out=original.set(payload);if(out?.visible===true&&payload?.visible===true&&Number.isFinite(+payload.x)&&Number.isFinite(+payload.y)){p1Tracker={x:+payload.x,y:+payload.y};p1TrackerRx=Date.now();}else{p1Tracker=null;p1TrackerRx=Date.now();}return out;}
function clearWrapper(reason){p1Tracker=null;p1TrackerRx=Date.now();return original.clear(reason);}
function clearAuthorityWrapper(reason){clearFit('TRACKER_AUTHORITY_REVOKED');p1Tracker=null;p1TrackerRx=0;return original.clearAuthority(reason);}
function disposeInternal(restore=true){
  if(disposed)return;disposed=true;try{cancelAnimationFrame(raf);}catch(_){}try{bc.close();}catch(_){}try{layer.remove();}catch(_){}
  if(restore){if(hud.bindP1HeadTrackerAuthority===bindWrapper)hud.bindP1HeadTrackerAuthority=original.bind;if(hud.setP1HeadTracker===setWrapper)hud.setP1HeadTracker=original.set;if(hud.clearP1HeadTracker===clearWrapper)hud.clearP1HeadTracker=original.clear;if(hud.clearP1HeadTrackerAuthority===clearAuthorityWrapper)hud.clearP1HeadTrackerAuthority=original.clearAuthority;}
}
function disposeWrapper(){disposeInternal(false);return original.dispose();}
hud.bindP1HeadTrackerAuthority=bindWrapper;hud.setP1HeadTracker=setWrapper;hud.clearP1HeadTracker=clearWrapper;hud.clearP1HeadTrackerAuthority=clearAuthorityWrapper;hud.dispose=disposeWrapper;

window.WOFALPHARELATIVEENEMY={version:VERSION,dispose:()=>disposeInternal(true),status:()=>({version:VERSION,fit:fit?{ok:fit.ok,reason:fit.reason,sign:fit.sign??null,model:fit.model??null,preferredModel:fit.preferredModel??null,residual:fit.residual??null,sampleCount:fit.sampleCount??samples.length}:null,sampleCount:samples.length,enemyFresh:!!lastMarkerRx&&Date.now()-lastMarkerRx<=MARKER_STALE_MS,playerFresh:!!lastPlayerRx&&Date.now()-lastPlayerRx<=PLAYER_STALE_MS,trackerFresh:!!p1TrackerRx&&Date.now()-p1TrackerRx<=TRACKER_STALE_MS,drawCount,suppressedReason,readOnly:true,ramWrites:0,inputInjection:false})};
})();
