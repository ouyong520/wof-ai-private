(()=>{
'use strict';
const VERSION='wof-alpha-hud-rc5';
const SCHEMA='wof-alpha-v2';
const CANONICAL_INPUT_SCHEMA='wof-alpha-canonical-anchor-runtime-envelope-input-v1';
const FIXED_SMOKE_SCHEMA='wof-alpha-fixed-draw-smoke-v1';
const FIXED_SMOKE_STATUS_KEY='__WOF_ALPHA_FIXED_DRAW_SMOKE_STATUS_V1';
const FIXED_NATIVE_W=384,FIXED_NATIVE_H=224,FIXED_NATIVE_X=192,FIXED_NATIVE_Y=112;
const fixedSmoke={
  schema:FIXED_SMOKE_SCHEMA,enabled:false,state:'DISABLED',hudInjected:true,gameCanvasContextPresent:false,drawHooked:false,
  callbackCount:0,drawCount:0,nativeWidth:FIXED_NATIVE_W,nativeHeight:FIXED_NATIVE_H,nativeX:FIXED_NATIVE_X,nativeY:FIXED_NATIVE_Y,
  drawingBuffer:null,lastError:null,lastCallbackAt:null,lastDrawAt:null,readOnly:true,ramWrites:0,inputInjection:false
};
window[FIXED_SMOKE_STATUS_KEY]=fixedSmoke;
function fixedSmokeSet(state,patch){fixedSmoke.state=state;if(patch&&typeof patch==='object')Object.assign(fixedSmoke,patch);return {...fixedSmoke};}

const cfg=window.__WOF_ALPHA_CONFIG;
if(!cfg||cfg.release!=='wof-alpha-rc3'||typeof cfg.session!=='string'||cfg.session.length<16||typeof cfg.channel!=='string')throw new Error('WOF Alpha RC3 session config missing');
const SESSION=cfg.session,CHANNEL=cfg.channel;
const TRANSPORT=window.__WOF_ALPHA_TRANSPORT_V1;
if(!TRANSPORT||TRANSPORT.version!=='wof-alpha-safe-transport-v1'||typeof TRANSPORT.matches!=='function')throw new Error('WOF Alpha Safe Transport 配对接口缺失');
if(!window.WOFAlphaHudModel?.summarizeWarnings)throw new Error('WOF Alpha HUD model missing');
if(!window.WOFAlphaEnemyTargetLabels?.buildPlan)throw new Error('WOF Alpha enemy target-label model missing');
if(!window.WOFAlphaPlayerHeadWarning?.buildPlan)throw new Error('WOF Alpha player-head warning model missing');
if(!window.WOFAlphaCanonicalAnchorEnvelope?.normalizeEnvelope||typeof window.WOFAlphaCanonicalAnchorEnvelope?.validateAuthorityBinding!=='function')throw new Error('WOF Alpha canonical anchor envelope P9 missing');
if(!window.WOFAlphaCanonicalOverlayPlan?.buildCanonicalPlan)throw new Error('WOF Alpha canonical overlay plan P8 missing');
const TARGET_LABELS=window.WOFAlphaEnemyTargetLabels;
const PLAYER_WARNING=window.WOFAlphaPlayerHeadWarning;
const CANONICAL_ENVELOPE=window.WOFAlphaCanonicalAnchorEnvelope;
const CANONICAL_PLAN=window.WOFAlphaCanonicalOverlayPlan;

try{
  const legacy=window.WOFHUD;
  if(legacy){
    if(typeof legacy.dispose==='function')legacy.dispose();
    else throw new Error('legacy WOFHUD has no dispose(); refusing Alpha takeover');
  }
  window.WOFCANVAS?.stop?.();
}catch(e){throw new Error('legacy research HUD teardown failed: '+String(e?.message||e));}
try{window.WOFALPHAHUD?.dispose?.();}catch(_){}

const canvas=window.I_GF1TC||document.getElementById('whathis'),gl=window.I_fdC8Q;
if(!canvas||!gl||typeof gl.drawArrays!=='function'){
  fixedSmokeSet('GAME_CANVAS_CONTEXT_MISSING',{gameCanvasContextPresent:false});
  throw new Error('game WebGL canvas/context not found');
}
fixedSmoke.gameCanvasContextPresent=true;
const isGL2=typeof WebGL2RenderingContext!=='undefined'&&gl instanceof WebGL2RenderingContext;

let bridge=window.__WOF_GL_HOOK;
if(!bridge||bridge.gl!==gl||typeof bridge.wrapper!=='function'){
  const proto=isGL2?WebGL2RenderingContext.prototype:WebGLRenderingContext.prototype;
  const nativeDraw=proto.drawArrays;
  if(typeof nativeDraw!=='function')throw new Error('native WebGL drawArrays not found');
  bridge={gl,nativeDraw,callback:null,inCallback:false,wrapper:null,gameDraws:0,installs:0};
  bridge.wrapper=function(){
    const out=bridge.nativeDraw.apply(this,arguments);
    if(this===gl)bridge.gameDraws++;
    const cb=bridge.callback;
    if(this===gl&&cb&&!bridge.inCallback){
      bridge.inCallback=true;try{cb();}catch(e){bridge.lastError=String(e?.stack||e);}finally{bridge.inCallback=false;}
    }
    return out;
  };
  try{Object.defineProperty(gl,'drawArrays',{value:bridge.wrapper,writable:true,configurable:true});}catch(_){gl.drawArrays=bridge.wrapper;}
  if(gl.drawArrays!==bridge.wrapper)throw new Error('persistent WebGL draw hook install failed');
  window.__WOF_GL_HOOK=bridge;
}else if(gl.drawArrays!==bridge.wrapper){
  try{Object.defineProperty(gl,'drawArrays',{value:bridge.wrapper,writable:true,configurable:true});}catch(_){gl.drawArrays=bridge.wrapper;}
}
bridge.installs++;

const V=`${isGL2?'#version 300 es\n':''}${isGL2?'in':'attribute'} vec4 a;${isGL2?'out':'varying'} vec2 v;void main(){gl_Position=vec4(a.xy,0.,1.);v=a.zw;}`;
const F=`${isGL2?'#version 300 es\n':''}precision mediump float;${isGL2?'in':'varying'} vec2 v;uniform sampler2D t;${isGL2?'out vec4 o;':''}void main(){${isGL2?'o=texture(t,v);':'gl_FragColor=texture2D(t,v);'}}`;
const shader=(type,src)=>{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){const m=gl.getShaderInfoLog(s)||'shader';gl.deleteShader(s);throw new Error(m);}return s;};
const vs=shader(gl.VERTEX_SHADER,V),fs=shader(gl.FRAGMENT_SHADER,F),prog=gl.createProgram();
gl.attachShader(prog,vs);gl.attachShader(prog,fs);gl.bindAttribLocation(prog,0,'a');gl.linkProgram(prog);gl.deleteShader(vs);gl.deleteShader(fs);
if(!gl.getProgramParameter(prog,gl.LINK_STATUS)){const m=gl.getProgramInfoLog(prog)||'link';gl.deleteProgram(prog);throw new Error(m);}
const uTex=gl.getUniformLocation(prog,'t'),buf=gl.createBuffer(),tex=gl.createTexture(),labelTex=gl.createTexture(),warningTex=gl.createTexture(),fixedSmokeTex=gl.createTexture(),hud=document.createElement('canvas');
hud.width=520;hud.height=248;const c=hud.getContext('2d');
const labelHud=document.createElement('canvas');labelHud.width=96;labelHud.height=24;const lc=labelHud.getContext('2d');
const warningHud=document.createElement('canvas');warningHud.width=84;warningHud.height=26;const wc=warningHud.getContext('2d');
const fixedSmokeHud=document.createElement('canvas');fixedSmokeHud.width=96;fixedSmokeHud.height=36;const fsc=fixedSmokeHud.getContext('2d');
const LABEL_ORDER=['1P','2P','3P'],LABEL_TILE_W=32,LABEL_TILE_H=24,MAX_LABELS=20,labelVertices=new Float32Array(MAX_LABELS*6*4);

const STARTUP_MS=15000,STALE_MS=1500,MARKER_STALE_MS=300,PLAYER_SPATIAL_RX_STALE_MS=120,P1_TRACKER_STALE_MS=650,loadedAt=Date.now();
let disposed=false,visible=true,lastMsg=null,lastRx=0,lastDiag=null,lastKey='',drawCount=0,callbackCount=0;
let lastMarkerMsg=null,lastMarkerRx=0,lastLabelPlan=null,labelDrawCount=0;
let lastPlayerMsg=null,lastPlayerRx=0,lastPlayerPlan=null,playerWarningDrawCount=0,lastDirectP1WarningCount=0,p1TrackerWarningDrawCount=0;
let p1TrackerAuthority=null,p1Tracker=null,p1TrackerRx=0,p1TrackerDrawCount=0,p1TrackerHideReason='NOT_BOUND';
let canonicalOverlayBinding=null,canonicalOverlayPayload=null,canonicalOverlayEnvelope=null,canonicalOverlayPlan=null,canonicalOverlayRx=0;
let canonicalOverlayState='SUPPRESSED',canonicalOverlayReason='NOT_BOUND';

function snapGL(){
  const active=gl.getParameter(gl.ACTIVE_TEXTURE),activeTex=gl.getParameter(gl.TEXTURE_BINDING_2D);
  gl.activeTexture(gl.TEXTURE0);const tex0=gl.getParameter(gl.TEXTURE_BINDING_2D);gl.activeTexture(active);
  return{program:gl.getParameter(gl.CURRENT_PROGRAM),array:gl.getParameter(gl.ARRAY_BUFFER_BINDING),active,activeTex,tex0,
    viewport:Array.from(gl.getParameter(gl.VIEWPORT)),blend:gl.isEnabled(gl.BLEND),depth:gl.isEnabled(gl.DEPTH_TEST),
    cull:gl.isEnabled(gl.CULL_FACE),scissor:gl.isEnabled(gl.SCISSOR_TEST),srcRGB:gl.getParameter(gl.BLEND_SRC_RGB),
    dstRGB:gl.getParameter(gl.BLEND_DST_RGB),srcA:gl.getParameter(gl.BLEND_SRC_ALPHA),dstA:gl.getParameter(gl.BLEND_DST_ALPHA),
    eqRGB:gl.getParameter(gl.BLEND_EQUATION_RGB),eqA:gl.getParameter(gl.BLEND_EQUATION_ALPHA),
    mask:Array.from(gl.getParameter(gl.COLOR_WRITEMASK)),flip:gl.getParameter(gl.UNPACK_FLIP_Y_WEBGL),
    premul:gl.getParameter(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL),
    a0:{enabled:!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_ENABLED),buf:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_BUFFER_BINDING),
      size:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_SIZE),type:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_TYPE),
      norm:!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_NORMALIZED),stride:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_STRIDE),
      offset:gl.getVertexAttribOffset(0,gl.VERTEX_ATTRIB_ARRAY_POINTER)}};
}
function restoreGL(s){
  s.blend?gl.enable(gl.BLEND):gl.disable(gl.BLEND);s.depth?gl.enable(gl.DEPTH_TEST):gl.disable(gl.DEPTH_TEST);
  s.cull?gl.enable(gl.CULL_FACE):gl.disable(gl.CULL_FACE);s.scissor?gl.enable(gl.SCISSOR_TEST):gl.disable(gl.SCISSOR_TEST);
  gl.blendFuncSeparate(s.srcRGB,s.dstRGB,s.srcA,s.dstA);gl.blendEquationSeparate(s.eqRGB,s.eqA);gl.colorMask(...s.mask);gl.viewport(...s.viewport);
  if(s.a0.buf){gl.bindBuffer(gl.ARRAY_BUFFER,s.a0.buf);gl.vertexAttribPointer(0,s.a0.size,s.a0.type,s.a0.norm,s.a0.stride,s.a0.offset);}
  s.a0.enabled?gl.enableVertexAttribArray(0):gl.disableVertexAttribArray(0);gl.useProgram(s.program);
  gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,s.tex0);gl.activeTexture(s.active);
  if(s.active!==gl.TEXTURE0)gl.bindTexture(gl.TEXTURE_2D,s.activeTex);
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,s.flip);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,s.premul);gl.bindBuffer(gl.ARRAY_BUFFER,s.array);
}
function uploadCanvas(source,target){
  const s=snapGL();try{
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,target);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,source);
  }finally{restoreGL(s);}
}
function upload(){uploadCanvas(hud,tex);}
function drawTexture(x,y,w,h,target=tex){
  const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(W>0&&H>0))return false;
  const l=x/W*2-1,r=(x+w)/W*2-1,t=1-y/H*2,b=1-(y+h)/H*2;
  const v=new Float32Array([l,t,0,1,l,b,0,0,r,b,1,0,l,t,0,1,r,b,1,0,r,t,1,1]),s=snapGL();
  try{
    gl.viewport(0,0,W,H);gl.disable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.SCISSOR_TEST);gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.colorMask(true,true,true,true);gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,v,gl.STREAM_DRAW);gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0,4,gl.FLOAT,false,0,0);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,target);gl.uniform1i(uTex,0);
    bridge.nativeDraw.call(gl,gl.TRIANGLES,0,6);drawCount++;return true;
  }finally{restoreGL(s);}
}
function paintFixedSmoke(){
  fsc.clearRect(0,0,fixedSmokeHud.width,fixedSmokeHud.height);
  fsc.fillStyle='rgba(0,0,0,.92)';fsc.fillRect(1,1,fixedSmokeHud.width-2,fixedSmokeHud.height-2);
  fsc.strokeStyle='rgba(255,255,255,.99)';fsc.lineWidth=2;fsc.strokeRect(2,2,fixedSmokeHud.width-4,fixedSmokeHud.height-4);
  fsc.fillStyle='#fff';fsc.textBaseline='middle';fsc.textAlign='center';fsc.font='bold 22px sans-serif';fsc.fillText('TEST',fixedSmokeHud.width/2,fixedSmokeHud.height/2+.5);
  uploadCanvas(fixedSmokeHud,fixedSmokeTex);
}
function mapFixedNativeRectToDrawingBuffer(W,H){
  const nativeRect={x:FIXED_NATIVE_X-fixedSmokeHud.width/2,y:FIXED_NATIVE_Y-fixedSmokeHud.height/2,width:fixedSmokeHud.width,height:fixedSmokeHud.height};
  const sx=W/FIXED_NATIVE_W,sy=H/FIXED_NATIVE_H;
  return{x:nativeRect.x*sx,y:nativeRect.y*sy,width:nativeRect.width*sx,height:nativeRect.height*sy};
}
function fixedDrawSmokeStatus(){
  const hooked=!disposed&&gl.drawArrays===bridge.wrapper&&bridge.callback===drawHud;
  fixedSmoke.drawHooked=hooked;
  if(fixedSmoke.enabled&&!hooked)fixedSmoke.state='DRAW_HOOK_NOT_FIRING';
  return{...fixedSmoke,drawingBuffer:fixedSmoke.drawingBuffer?{...fixedSmoke.drawingBuffer}:null};
}
function setFixedDrawSmokeEnabled(enabled){
  fixedSmoke.enabled=enabled===true;
  fixedSmoke.lastError=null;
  if(!fixedSmoke.enabled)return fixedSmokeSet('DISABLED',{drawingBuffer:null});
  const hooked=!disposed&&gl.drawArrays===bridge.wrapper&&bridge.callback===drawHud;
  return fixedSmokeSet('DRAW_HOOK_NOT_FIRING',{drawHooked:hooked});
}
function drawFixedSmoke(){
  fixedSmoke.callbackCount++;fixedSmoke.lastCallbackAt=Date.now();
  const W=Number(gl.drawingBufferWidth),H=Number(gl.drawingBufferHeight);
  if(!(Number.isFinite(W)&&Number.isFinite(H)&&W>0&&H>0)){
    fixedSmokeSet('DRAWING_BUFFER_INVALID',{drawingBuffer:{width:W,height:H},lastError:'invalid WebGL drawing buffer'});
    return false;
  }
  const rect=mapFixedNativeRectToDrawingBuffer(W,H);
  fixedSmoke.drawingBuffer={width:W,height:H,rect,nativeWidth:FIXED_NATIVE_W,nativeHeight:FIXED_NATIVE_H};
  try{
    const before=drawCount;
    const ok=drawTexture(rect.x,rect.y,rect.width,rect.height,fixedSmokeTex);
    if(ok===true&&drawCount===before+1){
      fixedSmoke.drawCount++;fixedSmoke.lastDrawAt=Date.now();fixedSmoke.lastError=null;
      fixedSmokeSet('FIXED_TEST_ACTUALLY_DRAWN');
      return true;
    }
    fixedSmokeSet('DRAW_FAILED',{lastError:'maintained production renderer did not complete a native draw'});
  }catch(e){
    fixedSmokeSet('DRAW_FAILED',{lastError:String(e?.stack||e)});
  }
  return false;
}
function paintLabelAtlas(){
  lc.clearRect(0,0,labelHud.width,labelHud.height);lc.textBaseline='middle';lc.textAlign='center';lc.font='bold 15px sans-serif';
  for(let i=0;i<LABEL_ORDER.length;i++){
    const x=i*LABEL_TILE_W;lc.fillStyle='rgba(0,0,0,.82)';lc.fillRect(x+1,1,LABEL_TILE_W-2,LABEL_TILE_H-2);
    lc.strokeStyle='rgba(255,255,255,.99)';lc.lineWidth=2;lc.strokeRect(x+2,2,LABEL_TILE_W-4,LABEL_TILE_H-4);
    lc.fillStyle='#fff';lc.fillText(LABEL_ORDER[i],x+LABEL_TILE_W/2,LABEL_TILE_H/2+.5);
  }
  uploadCanvas(labelHud,labelTex);
}
function paintWarningBadge(){
  wc.clearRect(0,0,warningHud.width,warningHud.height);
  wc.fillStyle='rgba(0,0,0,.88)';wc.fillRect(1,1,warningHud.width-2,warningHud.height-2);
  wc.strokeStyle='rgba(255,255,255,.99)';wc.lineWidth=2;wc.strokeRect(2,2,warningHud.width-4,warningHud.height-4);
  wc.fillStyle='#fff';wc.textBaseline='middle';wc.textAlign='center';wc.font='bold 15px sans-serif';wc.fillText('危险',warningHud.width/2,warningHud.height/2+.5);
  uploadCanvas(warningHud,warningTex);
}
function drawLabelPlan(plan){
  const labels=Array.isArray(plan?.labels)?plan.labels:[];if(!labels.length)return;
  const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(W>0&&H>0))return;
  let count=0,p=0;
  for(const item of labels){
    if(count>=MAX_LABELS)break;
    const idx=LABEL_ORDER.indexOf(item.label);if(idx<0)continue;
    const r=item.drawRectDb;if(!r)continue;
    const l=r.x/W*2-1,rr=(r.x+r.width)/W*2-1,t=1-r.y/H*2,b=1-(r.y+r.height)/H*2,u0=idx/LABEL_ORDER.length,u1=(idx+1)/LABEL_ORDER.length;
    const vals=[l,t,u0,1,l,b,u0,0,rr,b,u1,0,l,t,u0,1,rr,b,u1,0,rr,t,u1,1];
    for(let i=0;i<vals.length;i++)labelVertices[p++]=vals[i];
    count++;
  }
  if(!count)return;
  const s=snapGL();try{
    gl.viewport(0,0,W,H);gl.disable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.SCISSOR_TEST);gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.colorMask(true,true,true,true);gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,labelVertices,gl.STREAM_DRAW);gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0,4,gl.FLOAT,false,0,0);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,labelTex);gl.uniform1i(uTex,0);
    bridge.nativeDraw.call(gl,gl.TRIANGLES,0,count*6);labelDrawCount+=count;drawCount++;
  }finally{restoreGL(s);}
}
function p1TrackerStatus(now=Date.now()){
  const fresh=!!p1Tracker&&!!p1TrackerRx&&now-p1TrackerRx<=P1_TRACKER_STALE_MS;
  return{schema:'wof-alpha-direct-p1-tracker-v1',bound:!!p1TrackerAuthority,authorityKey:p1TrackerAuthority?.authorityKey||null,runtimeEpoch:p1TrackerAuthority?.runtimeEpoch||null,visible:fresh,ageMs:p1TrackerRx?now-p1TrackerRx:null,staleMs:P1_TRACKER_STALE_MS,hideReason:fresh?null:p1TrackerHideReason,drawCount:p1TrackerDrawCount,readOnly:true,ramWrites:0,inputInjection:false};
}
function drawP1Tracker(now){
  const st=p1TrackerStatus(now);if(!st.visible)return false;
  const r=canvas.getBoundingClientRect(),W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(r.width>0&&r.height>0&&W>0&&H>0))return false;
  const x=p1Tracker.x/r.width*W,y=p1Tracker.y/r.height*H,w=Math.max(32,Math.min(44,W*.075)),h=w*LABEL_TILE_H/LABEL_TILE_W;
  drawLabelPlan({labels:[{label:'1P',drawRectDb:{x:x-w/2,y:y-h-4,width:w,height:h}}]});p1TrackerDrawCount++;return true;
}
function bindP1HeadTrackerAuthority(binding){
  if(!binding||typeof binding.authorityKey!=='string'||!binding.authorityKey||typeof binding.runtimeEpoch!=='string'||!binding.runtimeEpoch)throw new Error('direct P1 tracker authority binding missing');
  p1TrackerAuthority={authorityKey:binding.authorityKey,runtimeEpoch:binding.runtimeEpoch};p1Tracker=null;p1TrackerRx=0;p1TrackerHideReason='BOUND_WAITING_FOR_TRACKER';return p1TrackerStatus();
}
function setP1HeadTracker(payload){
  try{window.WOFHEADVISUALV3?.showMarker?.(0,0,false);}catch(_){}
  if(!p1TrackerAuthority||!payload||payload.authorityKey!==p1TrackerAuthority.authorityKey||payload.runtimeEpoch!==p1TrackerAuthority.runtimeEpoch){p1Tracker=null;p1TrackerRx=Date.now();p1TrackerHideReason='STALE_OR_MISMATCHED_AUTHORITY';return p1TrackerStatus();}
  const x=+payload.x,y=+payload.y;if(payload.visible!==true||!Number.isFinite(x)||!Number.isFinite(y)){p1Tracker=null;p1TrackerRx=Date.now();p1TrackerHideReason=String(payload.reason||'TRACKER_NOT_VISIBLE');return p1TrackerStatus();}
  p1Tracker={x,y,seedSource:payload.seedSource||null};p1TrackerRx=Date.now();p1TrackerHideReason=null;return p1TrackerStatus();
}
function clearP1HeadTracker(reason='TRACKER_HIDDEN'){try{window.WOFHEADVISUALV3?.showMarker?.(0,0,false);}catch(_){}p1Tracker=null;p1TrackerRx=Date.now();p1TrackerHideReason=String(reason);return p1TrackerStatus();}
function clearP1HeadTrackerAuthority(reason='AUTHORITY_REVOKED'){p1TrackerAuthority=null;return clearP1HeadTracker(reason);}
function drawingBufferState(now,projectionEpoch){
  const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(W>0&&H>0))return null;
  let vp;try{vp=Array.from(gl.getParameter(gl.VIEWPORT));}catch(_){return null;}
  if(!Array.isArray(vp)||vp.length!==4||!vp.every(Number.isFinite)||vp[2]<=0||vp[3]<=0)return null;
  const x=vp[0],y=H-(vp[1]+vp[3]),width=vp[2],height=vp[3];
  if(x<0||y<0||x+width>W||y+height>H)return null;
  return{width:W,height:H,contentRect:{x,y,width,height},sampleAt:now,confidence:1,epoch:projectionEpoch||null,projectionEpoch:projectionEpoch||null,
    mappingVersion:[W,H,...vp].join(':'),fullscreen:!!document.fullscreenElement};
}
function drawEnemyTargetLabels(now){
  if(!lastMarkerRx||now-lastMarkerRx>MARKER_STALE_MS){lastLabelPlan=null;return;}
  const projection=lastMarkerMsg?.projection||null;
  const db=drawingBufferState(now,projection?.epoch||null);
  const plan=TARGET_LABELS.buildPlan({markers:Array.isArray(lastMarkerMsg?.markers)?lastMarkerMsg.markers:[],projection,drawingBufferState:db,nowMs:now});
  lastLabelPlan=plan;
  if(plan.labels.length)drawLabelPlan(plan);
}
function drawP1HeadWarningFromTracker(now,warnings){
  const rows=Array.isArray(warnings)?warnings.filter(w=>w?.target==='P1'):[];
  const remaining=Array.isArray(warnings)?warnings.filter(w=>w?.target!=='P1'):[];
  lastDirectP1WarningCount=0;
  if(!rows.length)return{handled:0,remaining};
  const st=p1TrackerStatus(now);if(!st.visible)return{handled:0,remaining:Array.isArray(warnings)?warnings:[]};
  const r=canvas.getBoundingClientRect(),W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(r.width>0&&r.height>0&&W>0&&H>0))return{handled:0,remaining:Array.isArray(warnings)?warnings:[]};
  const x=p1Tracker.x/r.width*W,y=p1Tracker.y/r.height*H,w=Math.max(68,Math.min(104,W*.18)),h=w*warningHud.height/warningHud.width;
  const dx=Math.max(0,Math.min(W-w,x-w/2)),dy=Math.max(0,Math.min(H-h,y-h*2-8));
  drawTexture(dx,dy,w,h,warningTex);playerWarningDrawCount++;p1TrackerWarningDrawCount++;lastDirectP1WarningCount=rows.length;
  return{handled:rows.length,remaining};
}
function drawPlayerHeadWarnings(now,warnings){
  const spatialFresh=!!lastPlayerRx&&now-lastPlayerRx<=PLAYER_SPATIAL_RX_STALE_MS;
  const msg=spatialFresh?lastPlayerMsg:null;
  const projection=msg?.projection||null;
  const db=drawingBufferState(now,projection?.epoch||null);
  const plan=PLAYER_WARNING.buildPlan({
    warnings,
    players:msg?.players||{},
    projection,
    drawingBufferState:db,
    nowMs:now,
    warningEpoch:lastMsg?.runtimeEpoch,
    warningSampleAt:lastMsg?.sampleAt
  });
  lastPlayerPlan=plan;
  for(const item of plan.anchored||[]){
    const r=item.drawRectDb;if(!r)continue;
    drawTexture(r.x,r.y,r.width,r.height,warningTex);playerWarningDrawCount++;
  }
  return plan;
}
function canonicalOverlayStatus(now=Date.now()){
  const emitted=canonicalOverlayPlan?.diagnostics?.emitted||{};
  return{
    schema:'wof-alpha-maintained-hud-canonical-overlay-status-v1',bound:!!canonicalOverlayBinding,state:canonicalOverlayState,reason:canonicalOverlayReason,
    authority:canonicalOverlayBinding?{...canonicalOverlayBinding}:null,envelopeAgeMs:canonicalOverlayRx?Math.max(0,now-canonicalOverlayRx):null,lastReceiveAt:canonicalOverlayRx||null,
    emittedEnemyLabelCount:Number.isInteger(emitted.enemyTargetLabels)?emitted.enemyTargetLabels:0,
    emittedPlayerDangerCount:Number.isInteger(emitted.playerDangerWarnings)?emitted.playerDangerWarnings:0,
    fallback:'NONE',readOnly:true,ramWrites:0,inputInjection:false
  };
}
function resetCanonicalOverlayPlan(reason,clearPayload=true){
  if(clearPayload)canonicalOverlayPayload=null;
  canonicalOverlayEnvelope=null;canonicalOverlayPlan=null;canonicalOverlayState='SUPPRESSED';canonicalOverlayReason=String(reason||'CANONICAL_OVERLAY_SUPPRESSED');
  lastLabelPlan=null;lastPlayerPlan=null;lastDirectP1WarningCount=0;
  return canonicalOverlayStatus();
}
function sameCanonicalBinding(left,right){
  if(!left||!right)return false;
  for(const key of ['authorityKey','runtimeEpoch','rendererEpoch'])if(left[key]!==right[key])return false;
  const lw=left.worldSha256??null,rw=right.worldSha256??null;
  return lw===rw;
}
function normalizedCanonicalBinding(binding){
  const result=CANONICAL_ENVELOPE.validateAuthorityBinding(binding);
  return result?.ok===true?result.value:null;
}
function bindCanonicalOverlayAuthority(binding){
  const normalized=normalizedCanonicalBinding(binding);
  if(!normalized){canonicalOverlayBinding=null;canonicalOverlayRx=0;resetCanonicalOverlayPlan('CANONICAL_AUTHORITY_INVALID');return canonicalOverlayStatus();}
  canonicalOverlayBinding={...normalized};canonicalOverlayRx=0;
  return resetCanonicalOverlayPlan('BOUND_WAITING_FOR_ENVELOPE');
}
function clearCanonicalOverlayAuthority(reason='AUTHORITY_REVOKED'){
  canonicalOverlayBinding=null;canonicalOverlayRx=0;
  return resetCanonicalOverlayPlan(String(reason||'AUTHORITY_REVOKED'));
}
function normalizeCanonicalPayload(payload,now){
  if(!canonicalOverlayBinding)return{ok:false,reason:'CANONICAL_AUTHORITY_NOT_BOUND'};
  if(!payload||payload.schema!==CANONICAL_INPUT_SCHEMA)return{ok:false,reason:'CANONICAL_TRANSPORT_SCHEMA_INVALID'};
  const payloadBinding=normalizedCanonicalBinding(payload.authorityBinding);
  if(!payloadBinding||!sameCanonicalBinding(canonicalOverlayBinding,payloadBinding))return{ok:false,reason:'CANONICAL_AUTHORITY_BINDING_MISMATCH'};
  const envelope=CANONICAL_ENVELOPE.normalizeEnvelope({records:payload.records,authorityBinding:payload.authorityBinding,nowMs:now});
  if(!envelope?.ok)return{ok:false,reason:envelope?.reason||'CANONICAL_ENVELOPE_INVALID'};
  const authority=envelope.authority||{};
  for(const key of ['authorityKey','runtimeEpoch','rendererEpoch'])if(authority[key]!==canonicalOverlayBinding[key])return{ok:false,reason:'CANONICAL_NORMALIZED_AUTHORITY_MISMATCH'};
  if(canonicalOverlayBinding.worldSha256&&authority.worldSha256!==canonicalOverlayBinding.worldSha256)return{ok:false,reason:'CANONICAL_WORLD_IDENTITY_MISMATCH'};
  return{ok:true,envelope};
}
function canonicalDrawingBufferState(now){
  if(!canonicalOverlayBinding)return null;
  const db=drawingBufferState(now,canonicalOverlayBinding.runtimeEpoch);
  return db?{...db,runtimeEpoch:canonicalOverlayBinding.runtimeEpoch,rendererEpoch:canonicalOverlayBinding.rendererEpoch}:null;
}
function canonicalEnemyInputs(envelope,now){
  const anchors=CANONICAL_ENVELOPE.toEnemyAnchorArray(envelope);
  if(!lastMarkerRx||now-lastMarkerRx>MARKER_STALE_MS)return{markers:[],anchors};
  const bySlot=new Map();for(const row of anchors||[])if(Number.isInteger(row?.slot))bySlot.set(row.slot,row);
  const markers=(Array.isArray(lastMarkerMsg?.markers)?lastMarkerMsg.markers:[]).map(marker=>{
    const row=bySlot.get(marker?.slot);
    return{...marker,
      actor:typeof marker?.actor==='string'&&marker.actor?marker.actor:(row?.actor||((Number.isInteger(marker?.slot))?'enemy-slot-'+marker.slot:null)),
      generation:Number.isInteger(marker?.generation)?marker.generation:row?.generation};
  });
  return{markers,anchors};
}
function canonicalPlayerGenerations(envelope){
  const out={};for(const row of envelope?.records||[])if(row?.kind==='player'&&typeof row.actor==='string'&&Number.isInteger(row.generation))out[row.actor]=row.generation;return out;
}
function buildCanonicalOverlayPlanAt(now){
  if(!canonicalOverlayBinding)return resetCanonicalOverlayPlan('CANONICAL_AUTHORITY_NOT_BOUND',false),null;
  if(!canonicalOverlayPayload)return resetCanonicalOverlayPlan('BOUND_WAITING_FOR_ENVELOPE',false),null;
  const normalized=normalizeCanonicalPayload(canonicalOverlayPayload,now);
  if(!normalized.ok){resetCanonicalOverlayPlan(normalized.reason,false);return null;}
  const envelope=normalized.envelope;
  const enemy=canonicalEnemyInputs(envelope,now);
  const fresh=!!lastRx&&now-lastRx<=STALE_MS;
  const warnings=fresh&&Array.isArray(lastMsg?.warnings)?lastMsg.warnings:[];
  const db=canonicalDrawingBufferState(now);
  const plan=CANONICAL_PLAN.buildCanonicalPlan({
    enemy:{markers:enemy.markers,canonicalAnchors:enemy.anchors},
    player:{warnings,canonicalAnchors:CANONICAL_ENVELOPE.toPlayerAnchorSamples(envelope),playerGenerations:canonicalPlayerGenerations(envelope),warningSampleAt:lastMsg?.sampleAt},
    canonicalAuthority:canonicalOverlayBinding,authorityBinding:envelope.authority,drawingBufferState:db,nowMs:now
  });
  if(!plan||plan.mode!=='canonical-render-anchor'||plan.coordinateSpace!=='webgl-drawing-buffer'||plan.fallback!=='NONE'){
    resetCanonicalOverlayPlan('CANONICAL_PRODUCT_PLAN_INVALID',false);return null;
  }
  canonicalOverlayEnvelope=envelope;canonicalOverlayPlan=plan;canonicalOverlayState=plan.state==='READY'?'READY':'SUPPRESSED';canonicalOverlayReason=plan.reason||null;
  lastLabelPlan={labels:Array.isArray(plan.enemyTargetLabels)?plan.enemyTargetLabels:[],suppressed:plan.suppression?.enemy||[],reason:plan.reason||null};
  lastPlayerPlan={anchored:Array.isArray(plan.playerDangerWarnings)?plan.playerDangerWarnings:[],fixed:[],suppressed:plan.suppression?.player||[]};
  lastDirectP1WarningCount=0;
  return plan;
}
function ingestCanonicalAnchorEnvelope(payload){
  canonicalOverlayRx=Date.now();
  if(!canonicalOverlayBinding)return resetCanonicalOverlayPlan('CANONICAL_AUTHORITY_NOT_BOUND');
  const normalized=normalizeCanonicalPayload(payload,canonicalOverlayRx);
  if(!normalized.ok)return resetCanonicalOverlayPlan(normalized.reason);
  canonicalOverlayPayload=payload;canonicalOverlayEnvelope=normalized.envelope;
  buildCanonicalOverlayPlanAt(canonicalOverlayRx);
  return canonicalOverlayStatus(canonicalOverlayRx);
}
function drawCanonicalOverlay(now){
  const plan=buildCanonicalOverlayPlanAt(now);if(!plan)return plan;
  const enemyLabels=[],playerWarnings=[];
  for(const intent of Array.isArray(plan.drawIntents)?plan.drawIntents:[]){
    if(intent?.kind==='enemy-target-label'&&intent.payload)enemyLabels.push(intent.payload);
    else if(intent?.kind==='player-danger-warning'&&intent.payload)playerWarnings.push(intent.payload);
  }
  if(enemyLabels.length)drawLabelPlan({labels:enemyLabels});
  for(const item of playerWarnings){const r=item?.drawRectDb;if(!r)continue;drawTexture(r.x,r.y,r.width,r.height,warningTex);playerWarningDrawCount++;}
  return plan;
}
function paintBox(title,lines){
  const h=Math.min(hud.height,48+Math.max(1,lines.length)*20);
  const key=title+'|'+lines.join('|');if(key===lastKey)return h;lastKey=key;
  c.clearRect(0,0,hud.width,hud.height);c.fillStyle='rgba(0,0,0,.90)';c.fillRect(1,1,hud.width-2,h-2);
  c.strokeStyle='rgba(255,255,255,.99)';c.lineWidth=2;c.strokeRect(2,2,hud.width-4,h-4);
  c.fillStyle='#fff';c.textBaseline='middle';c.textAlign='center';c.font='bold 22px sans-serif';c.fillText(title,hud.width/2,25);
  c.textAlign='left';c.font='bold 14px sans-serif';let y=50;
  for(const line of lines){c.fillText(line,12,y);y+=20;}
  upload();return h;
}
function drawFixedWarnings(warnings){
  const model=window.WOFAlphaHudModel.summarizeWarnings(warnings);
  if(!model.count)return;
  const h=paintBox(model.count+' 个危险',model.lines);
  const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height,w=Math.min(520,W-8),hh=Math.min(h,H-8);
  drawTexture(Math.max(4,(W-w)/2),Math.max(4,H-hh-8),w,hh);
}
function drawHud(){
  callbackCount++;
  if(disposed)return;
  if(fixedSmoke.enabled)drawFixedSmoke();
  if(!visible)return;
  const now=Date.now();
  if(canonicalOverlayBinding)drawCanonicalOverlay(now);else drawEnemyTargetLabels(now);
  const trackerVisible=drawP1Tracker(now);
  const fresh=!!lastRx&&now-lastRx<=STALE_MS;
  if(fresh){
    const warnings=Array.isArray(lastMsg?.warnings)?lastMsg.warnings:[];
    const model=window.WOFAlphaHudModel.summarizeWarnings(warnings);
    if(model.count){
      if(canonicalOverlayBinding)return;
      const direct=drawP1HeadWarningFromTracker(now,warnings);
      const plan=drawPlayerHeadWarnings(now,direct.remaining);
      const fixedWarnings=[];
      for(const row of plan.fixed||[]){
        if(Array.isArray(row.warnings))fixedWarnings.push(...row.warnings);
        else if(row.warning)fixedWarnings.push(row.warning);
      }
      if(fixedWarnings.length)drawFixedWarnings(fixedWarnings);
      return;
    }
  }
  lastDirectP1WarningCount=0;if(!canonicalOverlayBinding)lastPlayerPlan=null;
  if(lastDiag&&now-lastDiag.at<5000){
    const h=paintBox('Alpha 已禁用',[String(lastDiag.reason||'运行环境未通过身份校验')]);
    const W=gl.drawingBufferWidth||canvas.width,w=Math.min(520,W-8);drawTexture(Math.max(4,(W-w)/2),8,w,h);return;
  }
  if(!trackerVisible&&now-loadedAt<STARTUP_MS){
    const h=paintBox('WOF Alpha RC5 已加载',[fresh?'检测器已连接 · 当前无生产危险':'等待 921031 身份校验/检测器连接']);
    const W=gl.drawingBufferWidth||canvas.width,w=Math.min(520,W-8);drawTexture(Math.max(4,(W-w)/2),8,w,h);
  }
}
paintLabelAtlas();
paintWarningBadge();
paintFixedSmoke();
bridge.callback=drawHud;

const bc=new BroadcastChannel(CHANNEL);
bc.onmessage=e=>{
  const m=e.data;
  if(!(m&&m.schema===SCHEMA&&m.session===SESSION&&TRANSPORT.matches(m)))return;
  if(m.kind==='state'){lastMsg=m;lastRx=Date.now();lastDiag=null;lastKey='';lastPlayerPlan=null;lastDirectP1WarningCount=0;}
  else if(m.kind==='player-head-spatial'){lastPlayerMsg=m;lastPlayerRx=Date.now();}
  else if(m.kind==='enemy-target-markers'){lastMarkerMsg=m;lastMarkerRx=Date.now();}
  else if(m.kind==='diag'){lastMsg=null;lastRx=0;lastDiag={at:Date.now(),reason:m.reason||m.status||'diagnostic'};lastKey='';}
  if(m.kind==='diag'){lastMarkerMsg=null;lastMarkerRx=0;lastLabelPlan=null;lastPlayerMsg=null;lastPlayerRx=0;lastPlayerPlan=null;lastDirectP1WarningCount=0;}
};

function transportReset(){lastMsg=null;lastRx=0;lastMarkerMsg=null;lastMarkerRx=0;lastLabelPlan=null;lastPlayerMsg=null;lastPlayerRx=0;lastPlayerPlan=null;lastDirectP1WarningCount=0;lastDiag=null;lastKey='';if(canonicalOverlayBinding){canonicalOverlayPayload=null;canonicalOverlayEnvelope=null;canonicalOverlayPlan=null;canonicalOverlayState='SUPPRESSED';canonicalOverlayReason='TRANSPORT_RESET';canonicalOverlayRx=0;}}
function dispose(){
  if(disposed)return;disposed=true;clearCanonicalOverlayAuthority('HUD_DISPOSED');clearP1HeadTrackerAuthority('HUD_DISPOSED');setFixedDrawSmokeEnabled(false);
  if(bridge.callback===drawHud)bridge.callback=null;
  try{bc.close();}catch(_){}
  try{gl.deleteTexture(tex);gl.deleteTexture(labelTex);gl.deleteTexture(warningTex);gl.deleteTexture(fixedSmokeTex);gl.deleteBuffer(buf);gl.deleteProgram(prog);}catch(_){}
}
window.WOFALPHAHUD={
  version:VERSION,session:SESSION,show(){visible=true;lastKey='';},hide(){visible=false;lastKey='';},transportReset,dispose,
  bindP1HeadTrackerAuthority,setP1HeadTracker,clearP1HeadTracker,clearP1HeadTrackerAuthority,p1HeadTrackerStatus:p1TrackerStatus,
  bindCanonicalOverlayAuthority,ingestCanonicalAnchorEnvelope,clearCanonicalOverlayAuthority,canonicalOverlayStatus,
  setFixedDrawSmokeEnabled,fixedDrawSmokeStatus,
  status(){
    const now=Date.now(),fresh=!!lastRx&&now-lastRx<=STALE_MS;
    const markerFresh=!!lastMarkerRx&&now-lastMarkerRx<=MARKER_STALE_MS;
    const playerFresh=!!lastPlayerRx&&now-lastPlayerRx<=PLAYER_SPATIAL_RX_STALE_MS;
    const summary=window.WOFAlphaHudModel.summarizeWarnings(fresh&&Array.isArray(lastMsg?.warnings)?lastMsg.warnings:[]);
    const fixedReasons=Array.isArray(lastPlayerPlan?.fixed)?lastPlayerPlan.fixed.map(x=>x.reason):[];
    const canonical=canonicalOverlayStatus(now);
    return{version:VERSION,release:'wof-alpha-rc3',session:SESSION,connected:fresh,ageMs:lastRx?now-lastRx:null,warningCount:summary.count,
      groups:summary.groups,drawHooked:gl.drawArrays===bridge.wrapper,drawCount,callbackCount,lastError:bridge.lastError||null,researchHudDisposed:true,
      fixedDrawSmoke:fixedDrawSmokeStatus(),canonicalOverlay:canonical,
      p1HeadTracker:p1TrackerStatus(now),
      playerHeadWarning:{connected:canonical.bound?canonical.emittedPlayerDangerCount>0:(playerFresh||lastDirectP1WarningCount>0),ageMs:canonical.bound?canonical.envelopeAgeMs:(lastPlayerRx?now-lastPlayerRx:null),anchored:canonical.bound?canonical.emittedPlayerDangerCount:((lastPlayerPlan?.anchored?.length||0)+(lastDirectP1WarningCount>0?1:0)),fixed:canonical.bound?0:(lastPlayerPlan?.fixed?.length||0),
        directP1WarningCount:canonical.bound?0:lastDirectP1WarningCount,directP1TrackerDrawCount:p1TrackerWarningDrawCount,fixedReasons:canonical.bound?[]:fixedReasons,drawCount:playerWarningDrawCount,holdMs:0,smoothing:false,maxSpatialAgeMs:canonical.bound?CANONICAL_ENVELOPE.DEFAULT_MAX_AGE_MS:PLAYER_WARNING.MAX_PLAYER_AGE_MS,fallback:canonical.bound?'NONE':null},
      enemyTargetLabels:{connected:canonical.bound?canonical.state==='READY':markerFresh,ageMs:canonical.bound?canonical.envelopeAgeMs:(lastMarkerRx?now-lastMarkerRx:null),count:canonical.bound?canonical.emittedEnemyLabelCount:(markerFresh?(lastLabelPlan?.labels?.length||0):0),suppressed:canonical.bound?(canonicalOverlayPlan?.suppression?.enemy?.length||0):(markerFresh?(lastLabelPlan?.suppressed?.length||0):0),
        reason:canonical.bound?canonical.reason:(markerFresh?(lastLabelPlan?.reason||null):'STALE_OR_MISSING_MARKERS'),drawCount:labelDrawCount,holdMs:0,smoothing:false,fallback:canonical.bound?'NONE':null}};
  }
};
fixedSmoke.drawHooked=gl.drawArrays===bridge.wrapper&&bridge.callback===drawHud;
console.log('✅ WOF Alpha RC5 HUD installed · session',SESSION.slice(0,8));
})();
