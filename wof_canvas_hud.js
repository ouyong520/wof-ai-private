(()=>{
'use strict';
const CHANNEL='wof-ai-hud-v1',STALE_MS=1500,HOLD_MS={1:1100,2:1300,3:1800},RELEASE_GRACE_MS=420,STARTUP_MS=60000;
const canvas=window.I_GF1TC||document.getElementById('whathis'),gl=window.I_fdC8Q;
if(!canvas||!gl||typeof gl.drawArrays!=='function')throw new Error('game WebGL canvas/context not found');
const isGL2=typeof WebGL2RenderingContext!=='undefined'&&gl instanceof WebGL2RenderingContext;

// One persistent WebGL bridge per room. It is NEVER removed during HUD reloads.
let bridge=window.__WOF_GL_HOOK;
if(!bridge||bridge.gl!==gl||typeof bridge.wrapper!=='function'){
  const proto=isGL2?WebGL2RenderingContext.prototype:WebGLRenderingContext.prototype;
  const nativeDraw=proto.drawArrays;
  if(typeof nativeDraw!=='function')throw new Error('native WebGL drawArrays not found');
  bridge={gl,nativeDraw,callback:null,inCallback:false,installs:0,wrapper:null};
  bridge.wrapper=function(mode,first,count){
    const r=bridge.nativeDraw.apply(this,arguments);
    const cb=bridge.callback;
    if(this===gl&&cb&&!bridge.inCallback){
      bridge.inCallback=true;
      try{cb(mode,first,count);}catch(_){}
      finally{bridge.inCallback=false;}
    }
    return r;
  };
  try{Object.defineProperty(gl,'drawArrays',{value:bridge.wrapper,writable:true,configurable:true});}
  catch(_){gl.drawArrays=bridge.wrapper;}
  if(gl.drawArrays!==bridge.wrapper)throw new Error('persistent WebGL draw hook install failed');
  window.__WOF_GL_HOOK=bridge;
}else if(gl.drawArrays!==bridge.wrapper){
  try{Object.defineProperty(gl,'drawArrays',{value:bridge.wrapper,writable:true,configurable:true});}
  catch(_){gl.drawArrays=bridge.wrapper;}
}
bridge.installs++;

// Only dispose a reload-safe v4/v5 instance. Never call legacy v3 destroy().
if(window.WOFHUD?.version?.startsWith?.('canvas-hud-v4')||window.WOFHUD?.version?.startsWith?.('canvas-hud-v5')){
  try{window.WOFHUD.dispose?.();}catch(_){}
}else{
  try{window.WOFHUD?.hide?.();}catch(_){}
}
try{window.WOFCANVAS?.stop?.();}catch(_){}

const V=`${isGL2?'#version 300 es\n':''}${isGL2?'in':'attribute'} vec4 a;${isGL2?'out':'varying'} vec2 v;void main(){gl_Position=vec4(a.xy,0.,1.);v=a.zw;}`;
const F=`${isGL2?'#version 300 es\n':''}precision mediump float;${isGL2?'in':'varying'} vec2 v;uniform sampler2D t;${isGL2?'out vec4 o;':''}void main(){${isGL2?'o=texture(t,v);':'gl_FragColor=texture2D(t,v);'}}`;
const shader=(type,src)=>{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){const m=gl.getShaderInfoLog(s)||'shader';gl.deleteShader(s);throw new Error(m);}return s;};
const vs=shader(gl.VERTEX_SHADER,V),fs=shader(gl.FRAGMENT_SHADER,F),prog=gl.createProgram();
gl.attachShader(prog,vs);gl.attachShader(prog,fs);gl.bindAttribLocation(prog,0,'a');gl.linkProgram(prog);gl.deleteShader(vs);gl.deleteShader(fs);
if(!gl.getProgramParameter(prog,gl.LINK_STATUS)){const m=gl.getProgramInfoLog(prog)||'link';gl.deleteProgram(prog);throw new Error(m);}
const uTex=gl.getUniformLocation(prog,'t'),buf=gl.createBuffer(),tex=gl.createTexture(),hud=document.createElement('canvas');
hud.width=260;hud.height=86;const c=hud.getContext('2d');

const HOLD={P1:null,P2:null,P3:null};
const loadedAt=Date.now(),startupUntil=loadedAt+STARTUP_MS;
let focus='P1',visible=true,detail=false,lastMsg=null,lastRx=0,lastKey='',disposed=false,drawCount=0,lastDrawAt=0;
const roundMs=v=>v==null?null:(Number.isFinite(+v)?Math.max(0,Math.round(+v/50)*50):null);
const holdKey=p=>!p||(+p.level||0)<1?'':(+p.level||0)>=3?'A|'+p.action:'W|'+(p.source||'WATCH')+'|'+(p.threatFacing||'')+'|'+(p.threatSide||'');
function updateHold(name,p,now){let h=HOLD[name];if(p&&(+p.level||0)>=1){const level=+p.level||1,k=holdKey(p);if(!h||h.key!==k)h=HOLD[name]={key:k,p:{...p},level,lastSeen:now,minUntil:now+(HOLD_MS[level]||1100)};else{h.p={...p};h.level=level;h.lastSeen=now;h.minUntil=Math.max(h.minUntil,now+260);}return h;}if(!h)return null;if(now>=h.minUntil&&now-h.lastSeen>RELEASE_GRACE_MS){HOLD[name]=null;return null;}return h;}
function heldTime(h,now){const b=roundMs(h?.p?.hitMs);return b==null?null:Math.max(0,b-Math.max(0,now-h.lastSeen));}
function mainText(h){if(!h||h.level<1)return null;const a=h.p?.action;if(h.level>=3){if(a==='UP')return '↑ 上躲';if(a==='DOWN')return '↓ 下躲';if(a==='LEFT')return '← 左躲';if(a==='RIGHT')return '→ 右躲';if(a==='AB')return 'AB';}return '注意';}
function sideText(p){const fb=p?.threatFacing||'',s=p?.threatSide,lr=s==='LEFT'?'左侧':s==='RIGHT'?'右侧':s==='CENTER'?'近身':'';return [fb,lr].filter(Boolean).join(' · ')||'危险方向未确认';}

function snap(){
  const active=gl.getParameter(gl.ACTIVE_TEXTURE),activeTex=gl.getParameter(gl.TEXTURE_BINDING_2D);gl.activeTexture(gl.TEXTURE0);const tex0=gl.getParameter(gl.TEXTURE_BINDING_2D);gl.activeTexture(active);
  return{program:gl.getParameter(gl.CURRENT_PROGRAM),array:gl.getParameter(gl.ARRAY_BUFFER_BINDING),active,activeTex,tex0,viewport:Array.from(gl.getParameter(gl.VIEWPORT)),blend:gl.isEnabled(gl.BLEND),depth:gl.isEnabled(gl.DEPTH_TEST),cull:gl.isEnabled(gl.CULL_FACE),scissor:gl.isEnabled(gl.SCISSOR_TEST),srcRGB:gl.getParameter(gl.BLEND_SRC_RGB),dstRGB:gl.getParameter(gl.BLEND_DST_RGB),srcA:gl.getParameter(gl.BLEND_SRC_ALPHA),dstA:gl.getParameter(gl.BLEND_DST_ALPHA),eqRGB:gl.getParameter(gl.BLEND_EQUATION_RGB),eqA:gl.getParameter(gl.BLEND_EQUATION_ALPHA),mask:Array.from(gl.getParameter(gl.COLOR_WRITEMASK)),flip:gl.getParameter(gl.UNPACK_FLIP_Y_WEBGL),premul:gl.getParameter(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL),a0:{enabled:!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_ENABLED),buf:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_BUFFER_BINDING),size:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_SIZE),type:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_TYPE),norm:!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_NORMALIZED),stride:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_STRIDE),offset:gl.getVertexAttribOffset(0,gl.VERTEX_ATTRIB_ARRAY_POINTER)}};
}
function restore(s){s.blend?gl.enable(gl.BLEND):gl.disable(gl.BLEND);s.depth?gl.enable(gl.DEPTH_TEST):gl.disable(gl.DEPTH_TEST);s.cull?gl.enable(gl.CULL_FACE):gl.disable(gl.CULL_FACE);s.scissor?gl.enable(gl.SCISSOR_TEST):gl.disable(gl.SCISSOR_TEST);gl.blendFuncSeparate(s.srcRGB,s.dstRGB,s.srcA,s.dstA);gl.blendEquationSeparate(s.eqRGB,s.eqA);gl.colorMask(...s.mask);gl.viewport(...s.viewport);if(s.a0.buf){gl.bindBuffer(gl.ARRAY_BUFFER,s.a0.buf);gl.vertexAttribPointer(0,s.a0.size,s.a0.type,s.a0.norm,s.a0.stride,s.a0.offset);}s.a0.enabled?gl.enableVertexAttribArray(0):gl.disableVertexAttribArray(0);gl.useProgram(s.program);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,s.tex0);gl.activeTexture(s.active);if(s.active!==gl.TEXTURE0)gl.bindTexture(gl.TEXTURE_2D,s.activeTex);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,s.flip);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,s.premul);gl.bindBuffer(gl.ARRAY_BUFFER,s.array);}
function upload(){const s=snap();try{gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,tex);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,hud);}finally{restore(s);}}
function paintDanger(h,now){const main=mainText(h),t=heldTime(h,now),threat=sideText(h.p),time=t!=null?(t<200?'立即':t>=1000?'约 '+(t/1000).toFixed(2)+' 秒':'约 '+(t/1000).toFixed(2)+' 秒'):(h.level>=3?'立即':'保持注意'),dbg=detail?[focus,h.p?.source,h.p?.family,h.p?.type!=null?'T'+h.p.type:null,h.p?.slot!=null?'slot '+h.p.slot:null].filter(Boolean).join(' · '):'',key=['danger',main,threat,time,dbg,Math.round((t||0)/50)].join('|');if(key===lastKey)return;lastKey=key;c.clearRect(0,0,hud.width,hud.height);c.fillStyle='rgba(0,0,0,.88)';c.fillRect(1,1,258,84);c.strokeStyle='rgba(255,255,255,.98)';c.lineWidth=2;c.strokeRect(2,2,256,82);c.fillStyle='#fff';c.textAlign='center';c.textBaseline='middle';c.font=h.level>=3?'bold 27px sans-serif':'bold 23px sans-serif';c.fillText(main,130,25);c.font='bold 16px sans-serif';c.fillText(threat,130,51);c.font='bold 12px sans-serif';c.fillText(time,130,71);if(dbg){c.textAlign='left';c.font='9px sans-serif';c.fillText(dbg,7,80);}upload();}
function paintStartup(now){const sec=Math.max(1,Math.ceil((startupUntil-now)/1000)),key='startup|'+sec;if(key===lastKey)return;lastKey=key;c.clearRect(0,0,hud.width,hud.height);c.fillStyle='rgba(0,0,0,.82)';c.fillRect(1,1,218,34);c.strokeStyle='rgba(255,255,255,.98)';c.lineWidth=2;c.strokeRect(2,2,216,32);c.fillStyle='#fff';c.textAlign='center';c.textBaseline='middle';c.font='bold 15px sans-serif';c.fillText('HUD 已加载 · '+sec+'s',110,18);upload();}
function activeHold(now){if(!visible||!lastRx||now-lastRx>STALE_MS)return null;return updateHold(focus,lastMsg?.players?.[focus],now);}
function drawTexture(x,y,w,hh){
  const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(W>0&&H>0))return;
  const l=x/W*2-1,r=(x+w)/W*2-1,t=1-y/H*2,b=1-(y+hh)/H*2;
  const v=new Float32Array([l,t,0,1,l,b,0,0,r,b,1,0,l,t,0,1,r,b,1,0,r,t,1,1]),s=snap();
  try{gl.viewport(0,0,W,H);gl.disable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.SCISSOR_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.colorMask(true,true,true,true);gl.useProgram(prog);gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,v,gl.STREAM_DRAW);gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,4,gl.FLOAT,false,0,0);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,tex);gl.uniform1i(uTex,0);bridge.nativeDraw.call(gl,gl.TRIANGLES,0,6);drawCount++;lastDrawAt=performance.now();}finally{restore(s);}
}
function drawHud(mode,first,count){
  if(disposed||count!==6||!visible)return;
  const now=Date.now(),h=activeHold(now),W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(W>0&&H>0))return;
  if(h){
    paintDanger(h,now);
    const w=Math.min(260,W-8),hh=Math.min(86,H-8),x=(W-w)/2,y=Math.max(4,H-hh-8);
    drawTexture(x,y,w,hh);
    return;
  }
  if(now<startupUntil){
    paintStartup(now);
    const w=Math.min(220,W-8),hh=Math.min(36,H-8);
    drawTexture(8,8,w,hh);
  }
}
bridge.callback=drawHud;

const bc=new BroadcastChannel(CHANNEL);
bc.onmessage=e=>{const m=e.data;if(m?.schema!=='wof-hud-v1'||m.kind!=='state')return;lastMsg=m;lastRx=Date.now();for(const n of ['P1','P2','P3'])updateHold(n,m.players?.[n],lastRx);};
function setFocus(n){if(!['P1','P2','P3'].includes(n))return focus;focus=n;lastKey='';return focus;}
function cycle(){return setFocus(focus==='P1'?'P2':focus==='P2'?'P3':'P1');}
function key(e){if(e.code==='F6'){e.preventDefault();cycle();}else if(e.code==='F8'){e.preventDefault();visible=!visible;lastKey='';}else if(e.code==='F9'){e.preventDefault();detail=!detail;lastKey='';}}
addEventListener('keydown',key,true);
function dispose(){if(disposed)return;disposed=true;if(bridge.callback===drawHud)bridge.callback=null;removeEventListener('keydown',key,true);try{bc.close();}catch(_){}try{gl.deleteTexture(tex);gl.deleteBuffer(buf);gl.deleteProgram(prog);}catch(_){};}
window.WOFHUD={version:'canvas-hud-v5-load-confirm-60s',p1(){return setFocus('P1')},p2(){return setFocus('P2')},p3(){return setFocus('P3')},focus:setFocus,cycle,show(){visible=true;lastKey='';return true},hide(){visible=false;lastKey='';return true},toggle(){visible=!visible;lastKey='';return visible},detail(v=!detail){detail=!!v;lastKey='';return detail},status(){return{focus,visible,detail,workerConnected:!!lastRx&&Date.now()-lastRx<=STALE_MS,ageMs:lastRx?Date.now()-lastRx:null,drawHooked:gl.drawArrays===bridge.wrapper,bridgeInstalls:bridge.installs,drawCount,lastDrawAt,loadConfirmSecondsLeft:Math.max(0,Math.ceil((startupUntil-Date.now())/1000)),hold:HOLD[focus],note:'SAFE hidden after 60-second load confirmation; player-follow waits for real camera scroll RAM'}},dispose,destroy(){dispose();delete window.WOFHUD;console.log('⛔ WOF HUD disposed; persistent WebGL bridge kept for safe reload');}};
console.log('✅ WOF direct WebGL HUD v5 started | in-game 60s load confirmation | SAFE hidden');
console.log('♻️ 以后直接重复运行加载命令即可；不需要先 destroy()');
})();