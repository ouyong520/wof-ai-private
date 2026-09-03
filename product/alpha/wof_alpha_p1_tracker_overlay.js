(()=>{
'use strict';
const VERSION='wof-alpha-p1-tracker-overlay-v1';
const SCHEMA='wof-alpha-p1-tracker-overlay-v1';
try{window.WOFALPHAP1TRACKER?.dispose?.();}catch(_){}
const canvas=window.I_GF1TC||document.getElementById('whathis'),gl=window.I_fdC8Q;
if(!canvas||!gl||typeof gl.drawArrays!=='function')throw new Error('game WebGL canvas/context not found');
const isGL2=typeof WebGL2RenderingContext!=='undefined'&&gl instanceof WebGL2RenderingContext;
const proto=isGL2?WebGL2RenderingContext.prototype:WebGLRenderingContext.prototype;
const nativeDraw=window.__WOF_GL_HOOK?.nativeDraw||proto.drawArrays;
if(typeof nativeDraw!=='function')throw new Error('native WebGL drawArrays not found');
let authorityKey=null,runtimeEpoch=null,anchor=null,lastUpdate=0,hideReason='NOT_BOUND',disposed=false,drawCount=0,hookCount=0,inOverlay=false,priorDraw=null,wrapper=null;
const STALE_MS=650;

const V=`${isGL2?'#version 300 es\n':''}${isGL2?'in':'attribute'} vec4 a;${isGL2?'out':'varying'} vec2 v;void main(){gl_Position=vec4(a.xy,0.,1.);v=a.zw;}`;
const F=`${isGL2?'#version 300 es\n':''}precision mediump float;${isGL2?'in':'varying'} vec2 v;uniform sampler2D t;${isGL2?'out vec4 o;':''}void main(){${isGL2?'o=texture(t,v);':'gl_FragColor=texture2D(t,v);'}}`;
const shader=(type,src)=>{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){const m=gl.getShaderInfoLog(s)||'shader';gl.deleteShader(s);throw new Error(m);}return s;};
const vs=shader(gl.VERTEX_SHADER,V),fs=shader(gl.FRAGMENT_SHADER,F),prog=gl.createProgram();
gl.attachShader(prog,vs);gl.attachShader(prog,fs);gl.bindAttribLocation(prog,0,'a');gl.linkProgram(prog);gl.deleteShader(vs);gl.deleteShader(fs);
if(!gl.getProgramParameter(prog,gl.LINK_STATUS)){const m=gl.getProgramInfoLog(prog)||'link';gl.deleteProgram(prog);throw new Error(m);}
const uTex=gl.getUniformLocation(prog,'t'),buf=gl.createBuffer(),tex=gl.createTexture(),badge=document.createElement('canvas'),bc=badge.getContext('2d');
badge.width=64;badge.height=34;
bc.clearRect(0,0,64,34);bc.fillStyle='rgba(0,0,0,.88)';bc.fillRect(7,1,50,25);bc.strokeStyle='rgba(255,255,255,.99)';bc.lineWidth=2;bc.strokeRect(8,2,48,23);bc.fillStyle='#fff';bc.textAlign='center';bc.textBaseline='middle';bc.font='bold 15px sans-serif';bc.fillText('P1',32,14.5);bc.beginPath();bc.moveTo(27,26);bc.lineTo(37,26);bc.lineTo(32,33);bc.closePath();bc.fill();

function snap(){
  const active=gl.getParameter(gl.ACTIVE_TEXTURE),activeTex=gl.getParameter(gl.TEXTURE_BINDING_2D);gl.activeTexture(gl.TEXTURE0);const tex0=gl.getParameter(gl.TEXTURE_BINDING_2D);gl.activeTexture(active);
  return{program:gl.getParameter(gl.CURRENT_PROGRAM),array:gl.getParameter(gl.ARRAY_BUFFER_BINDING),active,activeTex,tex0,viewport:Array.from(gl.getParameter(gl.VIEWPORT)),blend:gl.isEnabled(gl.BLEND),depth:gl.isEnabled(gl.DEPTH_TEST),cull:gl.isEnabled(gl.CULL_FACE),scissor:gl.isEnabled(gl.SCISSOR_TEST),srcRGB:gl.getParameter(gl.BLEND_SRC_RGB),dstRGB:gl.getParameter(gl.BLEND_DST_RGB),srcA:gl.getParameter(gl.BLEND_SRC_ALPHA),dstA:gl.getParameter(gl.BLEND_DST_ALPHA),eqRGB:gl.getParameter(gl.BLEND_EQUATION_RGB),eqA:gl.getParameter(gl.BLEND_EQUATION_ALPHA),mask:Array.from(gl.getParameter(gl.COLOR_WRITEMASK)),flip:gl.getParameter(gl.UNPACK_FLIP_Y_WEBGL),premul:gl.getParameter(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL),a0:{enabled:!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_ENABLED),buf:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_BUFFER_BINDING),size:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_SIZE),type:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_TYPE),norm:!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_NORMALIZED),stride:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_STRIDE),offset:gl.getVertexAttribOffset(0,gl.VERTEX_ATTRIB_ARRAY_POINTER)}};
}
function restore(s){
  s.blend?gl.enable(gl.BLEND):gl.disable(gl.BLEND);s.depth?gl.enable(gl.DEPTH_TEST):gl.disable(gl.DEPTH_TEST);s.cull?gl.enable(gl.CULL_FACE):gl.disable(gl.CULL_FACE);s.scissor?gl.enable(gl.SCISSOR_TEST):gl.disable(gl.SCISSOR_TEST);gl.blendFuncSeparate(s.srcRGB,s.dstRGB,s.srcA,s.dstA);gl.blendEquationSeparate(s.eqRGB,s.eqA);gl.colorMask(...s.mask);gl.viewport(...s.viewport);if(s.a0.buf){gl.bindBuffer(gl.ARRAY_BUFFER,s.a0.buf);gl.vertexAttribPointer(0,s.a0.size,s.a0.type,s.a0.norm,s.a0.stride,s.a0.offset);}s.a0.enabled?gl.enableVertexAttribArray(0):gl.disableVertexAttribArray(0);gl.useProgram(s.program);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,s.tex0);gl.activeTexture(s.active);if(s.active!==gl.TEXTURE0)gl.bindTexture(gl.TEXTURE_2D,s.activeTex);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,s.flip);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,s.premul);gl.bindBuffer(gl.ARRAY_BUFFER,s.array);
}
function upload(){const s=snap();try{gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,tex);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,badge);}finally{restore(s);}}
upload();
function visibleNow(){return !!anchor&&anchor.visible===true&&Date.now()-lastUpdate<=STALE_MS&&Number.isFinite(anchor.x)&&Number.isFinite(anchor.y);}
function draw(){
  if(disposed||!visibleNow())return;const rect=canvas.getBoundingClientRect(),W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;if(!(rect.width>0&&rect.height>0&&W>0&&H>0))return;
  const x=anchor.x/rect.width*W,y=anchor.y/rect.height*H,w=Math.min(64,Math.max(42,W*.085)),h=w*(34/64),left=x-w/2,top=y-h;
  if(left+w<0||left>W||top+h<0||top>H)return;const l=left/W*2-1,r=(left+w)/W*2-1,t=1-top/H*2,b=1-(top+h)/H*2,v=new Float32Array([l,t,0,1,l,b,0,0,r,b,1,0,l,t,0,1,r,b,1,0,r,t,1,1]),s=snap();
  try{gl.viewport(0,0,W,H);gl.disable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.SCISSOR_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.colorMask(true,true,true,true);gl.useProgram(prog);gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,v,gl.STREAM_DRAW);gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,4,gl.FLOAT,false,0,0);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,tex);gl.uniform1i(uTex,0);inOverlay=true;nativeDraw.call(gl,gl.TRIANGLES,0,6);drawCount++;}finally{inOverlay=false;restore(s);}
}
function ensureHook(){
  if(disposed)return false;if(wrapper&&gl.drawArrays===wrapper)return true;priorDraw=gl.drawArrays;wrapper=function(){const out=priorDraw.apply(this,arguments);if(this===gl&&!inOverlay){try{draw();}catch(e){window.__WOF_ALPHA_P1_TRACKER_LAST_ERROR=String(e?.stack||e);}}return out;};try{Object.defineProperty(gl,'drawArrays',{value:wrapper,writable:true,configurable:true});}catch(_){gl.drawArrays=wrapper;}if(gl.drawArrays!==wrapper)throw new Error('production P1 overlay draw hook install failed');hookCount++;return true;
}
function bind(cfg){
  if(!cfg||typeof cfg.authorityKey!=='string'||!cfg.authorityKey||typeof cfg.runtimeEpoch!=='string'||!cfg.runtimeEpoch)throw new Error('production P1 overlay authority binding missing');authorityKey=cfg.authorityKey;runtimeEpoch=cfg.runtimeEpoch;anchor=null;lastUpdate=Date.now();hideReason='BOUND_WAITING_FOR_TRACKER';ensureHook();return status();
}
function setAnchor(v){
  ensureHook();if(!authorityKey||!runtimeEpoch||!v||v.authorityKey!==authorityKey||v.runtimeEpoch!==runtimeEpoch){anchor=null;hideReason='STALE_OR_MISMATCHED_AUTHORITY';lastUpdate=Date.now();return status();}
  if(v.visible!==true||!Number.isFinite(+v.x)||!Number.isFinite(+v.y)){anchor=null;hideReason=String(v.reason||'TRACKER_NOT_VISIBLE');lastUpdate=Date.now();return status();}
  anchor={x:+v.x,y:+v.y,visible:true,label:'P1'};hideReason=null;lastUpdate=Date.now();return status();
}
function hide(reason='TRACKER_HIDDEN'){anchor=null;hideReason=String(reason);lastUpdate=Date.now();return status();}
function status(){const age=lastUpdate?Date.now()-lastUpdate:null;return{schema:SCHEMA,version:VERSION,authorityKey,runtimeEpoch,productionOverlayEnabled:true,visible:visibleNow(),anchor:visibleNow()?{x:anchor.x,y:anchor.y,label:'P1'}:null,hideReason,ageMs:age,staleMs:STALE_MS,drawHooked:gl.drawArrays===wrapper,drawCount,hookCount,lastError:window.__WOF_ALPHA_P1_TRACKER_LAST_ERROR||null,readOnly:true,ramWrites:0,inputInjection:false};}
function dispose(){if(disposed)return;disposed=true;anchor=null;hideReason='DISPOSED';if(wrapper&&gl.drawArrays===wrapper&&typeof priorDraw==='function'){try{Object.defineProperty(gl,'drawArrays',{value:priorDraw,writable:true,configurable:true});}catch(_){gl.drawArrays=priorDraw;}}try{gl.deleteTexture(tex);gl.deleteBuffer(buf);gl.deleteProgram(prog);}catch(_){}if(window.WOFALPHAP1TRACKER?.version===VERSION)delete window.WOFALPHAP1TRACKER;}
window.WOFALPHAP1TRACKER={version:VERSION,bind,setAnchor,hide,status,dispose};
})();
