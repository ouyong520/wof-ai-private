(()=>{
  'use strict';

  const CHANNEL='wof-ai-hud-v1';
  const HOLD_MS={1:1100,2:1300,3:1800};
  const RELEASE_GRACE_MS=420;
  const STALE_MS=1500;

  try{window.WOFCANVAS?.stop?.();}catch(_){}
  try{window.WOFHUD?.destroy?.();}catch(_){}

  const canvas=window.I_GF1TC||document.getElementById('whathis');
  const gl=window.I_fdC8Q;
  if(!canvas||String(canvas.tagName).toLowerCase()!=='canvas')throw new Error('game WebGL canvas I_GF1TC/#whathis not found');
  if(!gl||typeof gl.drawArrays!=='function')throw new Error('game WebGL context I_fdC8Q not found');

  const isGL2=typeof WebGL2RenderingContext!=='undefined'&&gl instanceof WebGL2RenderingContext;
  const VERT=`${isGL2?'#version 300 es\n':''}${isGL2?'in':'attribute'} vec4 a_data;\n${isGL2?'out':'varying'} vec2 v_uv;\nvoid main(){gl_Position=vec4(a_data.xy,0.0,1.0);v_uv=a_data.zw;}`;
  const FRAG=`${isGL2?'#version 300 es\n':''}precision mediump float;\n${isGL2?'in':'varying'} vec2 v_uv;\nuniform sampler2D u_tex;\n${isGL2?'out vec4 outColor;\n':''}void main(){vec4 c=${isGL2?'texture(u_tex,v_uv)':'texture2D(u_tex,v_uv)'};${isGL2?'outColor':'gl_FragColor'}=c;}`;

  const compile=(type,src)=>{
    const sh=gl.createShader(type);gl.shaderSource(sh,src);gl.compileShader(sh);
    if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS)){const msg=gl.getShaderInfoLog(sh)||'shader compile failed';gl.deleteShader(sh);throw new Error(msg);}
    return sh;
  };
  const vs=compile(gl.VERTEX_SHADER,VERT),fs=compile(gl.FRAGMENT_SHADER,FRAG);
  const program=gl.createProgram();
  gl.attachShader(program,vs);gl.attachShader(program,fs);gl.bindAttribLocation(program,0,'a_data');gl.linkProgram(program);
  gl.deleteShader(vs);gl.deleteShader(fs);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS)){const msg=gl.getProgramInfoLog(program)||'program link failed';gl.deleteProgram(program);throw new Error(msg);}

  const uTex=gl.getUniformLocation(program,'u_tex');
  const buffer=gl.createBuffer();
  const texture=gl.createTexture();
  const hud=document.createElement('canvas');hud.width=320;hud.height=116;
  const hctx=hud.getContext('2d');

  function saveAttrib0(){
    const enabled=!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_ENABLED);
    const buf=gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_BUFFER_BINDING);
    return {enabled,buf,size:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_SIZE),type:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_TYPE),norm:!!gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_NORMALIZED),stride:gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_STRIDE),offset:gl.getVertexAttribOffset(0,gl.VERTEX_ATTRIB_ARRAY_POINTER)};
  }
  function restoreAttrib0(a){
    if(a.buf){gl.bindBuffer(gl.ARRAY_BUFFER,a.buf);gl.vertexAttribPointer(0,a.size,a.type,a.norm,a.stride,a.offset);}
    a.enabled?gl.enableVertexAttribArray(0):gl.disableVertexAttribArray(0);
  }
  function snapshot(){
    const active=gl.getParameter(gl.ACTIVE_TEXTURE),activeTex=gl.getParameter(gl.TEXTURE_BINDING_2D);
    gl.activeTexture(gl.TEXTURE0);const tex0=gl.getParameter(gl.TEXTURE_BINDING_2D);gl.activeTexture(active);
    return {
      program:gl.getParameter(gl.CURRENT_PROGRAM),arrayBuffer:gl.getParameter(gl.ARRAY_BUFFER_BINDING),active,activeTex,tex0,
      viewport:Array.from(gl.getParameter(gl.VIEWPORT)),blend:gl.isEnabled(gl.BLEND),depth:gl.isEnabled(gl.DEPTH_TEST),cull:gl.isEnabled(gl.CULL_FACE),scissor:gl.isEnabled(gl.SCISSOR_TEST),
      srcRGB:gl.getParameter(gl.BLEND_SRC_RGB),dstRGB:gl.getParameter(gl.BLEND_DST_RGB),srcA:gl.getParameter(gl.BLEND_SRC_ALPHA),dstA:gl.getParameter(gl.BLEND_DST_ALPHA),eqRGB:gl.getParameter(gl.BLEND_EQUATION_RGB),eqA:gl.getParameter(gl.BLEND_EQUATION_ALPHA),
      colorMask:Array.from(gl.getParameter(gl.COLOR_WRITEMASK)),flip:gl.getParameter(gl.UNPACK_FLIP_Y_WEBGL),premul:gl.getParameter(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL),attrib0:saveAttrib0()
    };
  }
  function restore(s){
    s.blend?gl.enable(gl.BLEND):gl.disable(gl.BLEND);s.depth?gl.enable(gl.DEPTH_TEST):gl.disable(gl.DEPTH_TEST);s.cull?gl.enable(gl.CULL_FACE):gl.disable(gl.CULL_FACE);s.scissor?gl.enable(gl.SCISSOR_TEST):gl.disable(gl.SCISSOR_TEST);
    gl.blendFuncSeparate(s.srcRGB,s.dstRGB,s.srcA,s.dstA);gl.blendEquationSeparate(s.eqRGB,s.eqA);gl.colorMask(...s.colorMask);gl.viewport(...s.viewport);
    restoreAttrib0(s.attrib0);gl.useProgram(s.program);
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,s.tex0);
    gl.activeTexture(s.active);if(s.active!==gl.TEXTURE0)gl.bindTexture(gl.TEXTURE_2D,s.activeTex);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,s.flip);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,s.premul);gl.bindBuffer(gl.ARRAY_BUFFER,s.arrayBuffer);
  }
  function uploadTexture(){
    const s=snapshot();
    try{
      gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,texture);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,hud);
    }finally{restore(s);}
  }

  let focus='P1',visible=true,detail=false,destroyed=false,lastMsg=null,lastRx=0,lastPaintKey='',rafId=0,drawCount=0,lastDrawAt=0;
  const HOLD={P1:null,P2:null,P3:null};
  const bc=new BroadcastChannel(CHANNEL);
  const roundMs=v=>v==null?null:(Number.isFinite(+v)?Math.max(0,Math.round(+v/50)*50):null);

  function holdKey(p){
    if(!p||(+p.level||0)<1)return '';
    return (+p.level||0)>=3?'ACTION|'+p.action:'WARN|'+(p.source||'WATCH')+'|'+(p.threatFacing||'')+'|'+(p.threatSide||'');
  }
  function updateHold(name,p,now){
    let h=HOLD[name];
    if(p&&(+p.level||0)>=1){
      const level=+p.level||1,k=holdKey(p),changed=!h||h.key!==k;
      if(changed)h=HOLD[name]={key:k,p:{...p},level,lastSeen:now,minUntil:now+(HOLD_MS[level]||1100)};
      else{h.p={...p};h.level=level;h.lastSeen=now;h.minUntil=Math.max(h.minUntil,now+260);}
      return h;
    }
    if(!h)return null;
    if(now>=h.minUntil&&now-h.lastSeen>RELEASE_GRACE_MS){HOLD[name]=null;return null;}
    return h;
  }
  function heldTime(h,now){const base=roundMs(h?.p?.hitMs);if(base==null)return null;return Math.max(0,base-Math.max(0,now-h.lastSeen));}
  function sideText(p){
    const fb=p?.threatFacing||null,side=p?.threatSide||null;
    const lr=side==='LEFT'?'左侧':side==='RIGHT'?'右侧':side==='CENTER'?'近身':null;
    if(fb&&lr)return fb+' · '+lr;
    return fb||lr||'危险方向未确认';
  }
  function mainText(h){
    if(!h||h.level<1)return null;
    const a=h.p?.action;
    if(h.level>=3){
      if(a==='UP')return '↑ 上躲';
      if(a==='DOWN')return '↓ 下躲';
      if(a==='LEFT')return '← 左躲';
      if(a==='RIGHT')return '→ 右躲';
      if(a==='AB')return 'AB';
    }
    return '注意';
  }
  function statusText(now){
    if(!lastRx||now-lastRx>STALE_MS)return focus+' · 等待预测';
    const p=lastMsg?.players?.[focus];
    if(!p)return focus+' · 无数据';
    return focus+' · '+((+p.level||0)>=1?'危险':'安全');
  }

  function paint(now){
    const fresh=lastRx&&now-lastRx<=STALE_MS;
    const h=fresh?HOLD[focus]:null;
    const main=mainText(h),t=heldTime(h,now),status=statusText(now);
    const threat=main?sideText(h.p):'';
    const timeText=main?(t!=null?(t>=1000?'约 '+(t/1000).toFixed(1)+' 秒':'约 '+t+' ms'):(h.level>=3?'立即':'保持注意')):'';
    const debug=detail&&h?[focus,h.p?.source,h.p?.family,h.p?.type!=null?'T'+h.p.type:null,h.p?.slot!=null?'slot '+h.p.slot:null].filter(Boolean).join(' · '):'';
    const bucket=t==null?'':Math.round(t/50);
    const key=[visible,status,main,threat,timeText,debug,bucket].join('|');
    if(key===lastPaintKey)return;
    lastPaintKey=key;

    hctx.clearRect(0,0,hud.width,hud.height);
    if(!visible){uploadTexture();return;}

    hctx.textBaseline='middle';hctx.textAlign='center';
    hctx.fillStyle='rgba(0,0,0,.78)';hctx.fillRect(84,2,152,26);
    hctx.strokeStyle='rgba(255,255,255,.90)';hctx.lineWidth=1.5;hctx.strokeRect(84.5,2.5,151,25);
    hctx.fillStyle='#fff';hctx.font='bold 13px sans-serif';hctx.fillText(status,160,15);

    if(main){
      hctx.fillStyle='rgba(0,0,0,.88)';hctx.fillRect(6,34,308,78);
      hctx.strokeStyle='rgba(255,255,255,.98)';hctx.lineWidth=2;hctx.strokeRect(7,35,306,76);
      hctx.fillStyle='#fff';hctx.font=h.level>=3?'bold 29px sans-serif':'bold 25px sans-serif';hctx.fillText(main,160,56);
      hctx.font='bold 17px sans-serif';hctx.fillText(threat,160,81);
      hctx.font='bold 13px sans-serif';hctx.fillText(timeText,160,101);
      if(debug){hctx.textAlign='left';hctx.font='10px sans-serif';hctx.fillText(debug,12,107);}
    }
    uploadTexture();
  }

  function draw(){
    if(destroyed||!visible)return;
    const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;
    if(!(W>0&&H>0))return;
    const w=Math.min(hud.width,Math.max(180,W-8)),h=Math.min(hud.height,Math.max(72,H-8));
    const x=(W-w)/2,y=Math.max(4,H-h-4);
    const l=x/W*2-1,r=(x+w)/W*2-1,t=1-y/H*2,b=1-(y+h)/H*2;
    const v=new Float32Array([l,t,0,1,l,b,0,0,r,b,1,0,l,t,0,1,r,b,1,0,r,t,1,1]);
    const s=snapshot();
    try{
      gl.viewport(0,0,W,H);gl.disable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.SCISSOR_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.colorMask(true,true,true,true);
      gl.useProgram(program);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,v,gl.STREAM_DRAW);gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,4,gl.FLOAT,false,0,0);
      gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,texture);gl.uniform1i(uTex,0);gl.drawArrays(gl.TRIANGLES,0,6);
      drawCount++;lastDrawAt=performance.now();
    }finally{restore(s);}
  }

  bc.onmessage=e=>{
    const m=e.data;if(m?.schema!=='wof-hud-v1'||m.kind!=='state')return;
    lastMsg=m;lastRx=Date.now();const now=lastRx;
    for(const n of ['P1','P2','P3'])updateHold(n,m.players?.[n],now);
  };

  function setFocus(name){
    if(!['P1','P2','P3'].includes(name))return focus;
    focus=name;lastPaintKey='';return focus;
  }
  function cycle(){return setFocus(focus==='P1'?'P2':focus==='P2'?'P3':'P1');}
  function key(e){
    if(e.code==='F6'){e.preventDefault();cycle();}
    else if(e.code==='F8'){e.preventDefault();visible=!visible;lastPaintKey='';}
    else if(e.code==='F9'){e.preventDefault();detail=!detail;lastPaintKey='';}
  }
  addEventListener('keydown',key,true);

  function loop(){
    if(destroyed)return;
    const now=Date.now();
    if(lastRx&&now-lastRx>STALE_MS){HOLD.P1=HOLD.P2=HOLD.P3=null;}
    try{paint(now);draw();}catch(_){}
    rafId=requestAnimationFrame(loop);
  }
  uploadTexture();rafId=requestAnimationFrame(loop);

  window.WOFHUD={
    version:'canvas-hud-v1-direct-webgl',
    show(){visible=true;lastPaintKey='';return true;},hide(){visible=false;lastPaintKey='';return true;},toggle(){visible=!visible;lastPaintKey='';return visible;},
    detail(on=!detail){detail=!!on;lastPaintKey='';return detail;},focus:setFocus,p1(){return setFocus('P1');},p2(){return setFocus('P2');},p3(){return setFocus('P3');},cycle,
    status(){return{visible,detail,focus,lastRx,ageMs:lastRx?Date.now()-lastRx:null,workerConnected:!!lastRx&&Date.now()-lastRx<=STALE_MS,lastMsg,hold:HOLD[focus],drawCount,lastDrawAt,canvasId:canvas.id||null};},
    destroy(){
      if(destroyed)return;destroyed=true;if(rafId)cancelAnimationFrame(rafId);removeEventListener('keydown',key,true);try{bc.close();}catch(_){}
      try{gl.deleteTexture(texture);gl.deleteBuffer(buffer);gl.deleteProgram(program);}catch(_){}
      delete window.WOFHUD;console.log('⛔ WOF direct canvas HUD stopped');
    }
  };

  console.log('✅ WOF direct WebGL HUD v1 started | display only, no player control');
  console.log('🎮 P1/P2/P3: WOFHUD.p1() / p2() / p3() | F6 cycle | F8 show/hide | F9 detail');
  console.log('📡 Worker Console must load wof_hud_worker.js to provide prediction data');
})();