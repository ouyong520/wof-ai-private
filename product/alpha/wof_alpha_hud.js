(()=>{
'use strict';
const VERSION='wof-alpha-hud-rc4';
const SCHEMA='wof-alpha-v2';
const cfg=window.__WOF_ALPHA_CONFIG;
if(!cfg||cfg.release!=='wof-alpha-rc3'||typeof cfg.session!=='string'||cfg.session.length<16||typeof cfg.channel!=='string')throw new Error('WOF Alpha RC3 session config missing');
const SESSION=cfg.session,CHANNEL=cfg.channel;
const TRANSPORT=window.__WOF_ALPHA_TRANSPORT_V1;
if(!TRANSPORT||TRANSPORT.version!=='wof-alpha-safe-transport-v1'||typeof TRANSPORT.matches!=='function')throw new Error('WOF Alpha Safe Transport 配对接口缺失');
if(!window.WOFAlphaHudModel?.summarizeWarnings)throw new Error('WOF Alpha HUD model missing');
if(!window.WOFAlphaEnemyTargetLabels?.buildPlan)throw new Error('WOF Alpha enemy target-label model missing');
const TARGET_LABELS=window.WOFAlphaEnemyTargetLabels;

// Product takeover is allowed only after legacy research resources are actually released.
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
if(!canvas||!gl||typeof gl.drawArrays!=='function')throw new Error('game WebGL canvas/context not found');
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
const uTex=gl.getUniformLocation(prog,'t'),buf=gl.createBuffer(),tex=gl.createTexture(),labelTex=gl.createTexture(),hud=document.createElement('canvas');
hud.width=520;hud.height=248;const c=hud.getContext('2d');
const labelHud=document.createElement('canvas');labelHud.width=96;labelHud.height=24;const lc=labelHud.getContext('2d');
const LABEL_ORDER=['1P','2P','3P'],LABEL_TILE_W=32,LABEL_TILE_H=24,MAX_LABELS=20,labelVertices=new Float32Array(MAX_LABELS*6*4);

const STARTUP_MS=15000,STALE_MS=1500,MARKER_STALE_MS=300,loadedAt=Date.now();
let disposed=false,visible=true,lastMsg=null,lastRx=0,lastDiag=null,lastKey='',drawCount=0,callbackCount=0;
let lastMarkerMsg=null,lastMarkerRx=0,lastLabelPlan=null,labelDrawCount=0;

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
function drawTexture(x,y,w,h){
  const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(W>0&&H>0))return;
  const l=x/W*2-1,r=(x+w)/W*2-1,t=1-y/H*2,b=1-(y+h)/H*2;
  const v=new Float32Array([l,t,0,1,l,b,0,0,r,b,1,0,l,t,0,1,r,b,1,0,r,t,1,1]),s=snapGL();
  try{
    gl.viewport(0,0,W,H);gl.disable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.SCISSOR_TEST);gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.colorMask(true,true,true,true);gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,v,gl.STREAM_DRAW);gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0,4,gl.FLOAT,false,0,0);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,tex);gl.uniform1i(uTex,0);
    bridge.nativeDraw.call(gl,gl.TRIANGLES,0,6);drawCount++;
  }finally{restoreGL(s);}
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
function drawHud(){
  callbackCount++;if(disposed||!visible)return;
  const now=Date.now();drawEnemyTargetLabels(now);
  const fresh=!!lastRx&&now-lastRx<=STALE_MS;
  if(fresh){
    const model=window.WOFAlphaHudModel.summarizeWarnings(Array.isArray(lastMsg?.warnings)?lastMsg.warnings:[]);
    if(model.count){
      const h=paintBox(model.count+' 个危险',model.lines);
      const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height,w=Math.min(520,W-8),hh=Math.min(h,H-8);
      drawTexture(Math.max(4,(W-w)/2),Math.max(4,H-hh-8),w,hh);return;
    }
  }
  if(lastDiag&&now-lastDiag.at<5000){
    const h=paintBox('Alpha 已禁用',[String(lastDiag.reason||'运行环境未通过身份校验')]);
    const W=gl.drawingBufferWidth||canvas.width,w=Math.min(520,W-8);drawTexture(Math.max(4,(W-w)/2),8,w,h);return;
  }
  if(now-loadedAt<STARTUP_MS){
    const h=paintBox('WOF Alpha RC4 已加载',[fresh?'检测器已连接 · 当前无生产危险':'等待 921031 身份校验/检测器连接']);
    const W=gl.drawingBufferWidth||canvas.width,w=Math.min(520,W-8);drawTexture(Math.max(4,(W-w)/2),8,w,h);
  }
}
paintLabelAtlas();
bridge.callback=drawHud;

const bc=new BroadcastChannel(CHANNEL);
bc.onmessage=e=>{
  const m=e.data;
  if(!(m&&m.schema===SCHEMA&&m.session===SESSION&&TRANSPORT.matches(m)))return;
  if(m.kind==='state'){lastMsg=m;lastRx=Date.now();lastDiag=null;lastKey='';}
  else if(m.kind==='enemy-target-markers'){lastMarkerMsg=m;lastMarkerRx=Date.now();}
  else if(m.kind==='diag'){lastMsg=null;lastRx=0;lastDiag={at:Date.now(),reason:m.reason||m.status||'diagnostic'};lastKey='';}
  if(m.kind==='diag'){lastMarkerMsg=null;lastMarkerRx=0;lastLabelPlan=null;}
};

function transportReset(){lastMsg=null;lastRx=0;lastMarkerMsg=null;lastMarkerRx=0;lastLabelPlan=null;lastDiag=null;lastKey='';}
function dispose(){
  if(disposed)return;disposed=true;
  if(bridge.callback===drawHud)bridge.callback=null;
  try{bc.close();}catch(_){}
  try{gl.deleteTexture(tex);gl.deleteTexture(labelTex);gl.deleteBuffer(buf);gl.deleteProgram(prog);}catch(_){}
}
window.WOFALPHAHUD={
  version:VERSION,session:SESSION,show(){visible=true;lastKey='';},hide(){visible=false;lastKey='';},transportReset,dispose,
  status(){
    const fresh=!!lastRx&&Date.now()-lastRx<=STALE_MS;
    const markerFresh=!!lastMarkerRx&&Date.now()-lastMarkerRx<=MARKER_STALE_MS;
    const summary=window.WOFAlphaHudModel.summarizeWarnings(fresh&&Array.isArray(lastMsg?.warnings)?lastMsg.warnings:[]);
    return{version:VERSION,release:'wof-alpha-rc3',session:SESSION,connected:fresh,ageMs:lastRx?Date.now()-lastRx:null,warningCount:summary.count,
      groups:summary.groups,drawHooked:gl.drawArrays===bridge.wrapper,drawCount,callbackCount,lastError:bridge.lastError||null,researchHudDisposed:true,
      enemyTargetLabels:{connected:markerFresh,ageMs:lastMarkerRx?Date.now()-lastMarkerRx:null,count:markerFresh?(lastLabelPlan?.labels?.length||0):0,suppressed:markerFresh?(lastLabelPlan?.suppressed?.length||0):0,
        reason:markerFresh?(lastLabelPlan?.reason||null):'STALE_OR_MISSING_MARKERS',drawCount:labelDrawCount,holdMs:0,smoothing:false}};
  }
};
console.log('✅ WOF Alpha RC4 HUD installed · session',SESSION.slice(0,8));
})();
