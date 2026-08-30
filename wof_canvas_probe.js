(()=>{
  'use strict';

  try{window.WOFCANVAS?.stop?.();}catch(_){}

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
  const hud=document.createElement('canvas');hud.width=220;hud.height=46;
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
    restoreAttrib0(s.attrib0);
    gl.useProgram(s.program);
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,s.tex0);
    gl.activeTexture(s.active);if(s.active!==gl.TEXTURE0)gl.bindTexture(gl.TEXTURE_2D,s.activeTex);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,s.flip);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,s.premul);
    gl.bindBuffer(gl.ARRAY_BUFFER,s.arrayBuffer);
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
  function paintHud(sec){
    hctx.clearRect(0,0,hud.width,hud.height);
    hctx.fillStyle='rgba(0,0,0,.82)';hctx.fillRect(1,1,hud.width-2,hud.height-2);
    hctx.strokeStyle='rgba(255,255,255,.98)';hctx.lineWidth=2;hctx.strokeRect(1,1,hud.width-2,hud.height-2);
    hctx.fillStyle='#fff';hctx.font='bold 18px sans-serif';hctx.textBaseline='middle';
    hctx.fillText(`WOF HUD OK · ${sec}s`,12,hud.height/2);
    uploadTexture();
  }

  const startedAt=performance.now(),durationMs=60000,expiresAt=startedAt+durationMs;
  let running=true,drawing=false,drawCount=0,lastDrawAt=0,lastSec=-1,rafId=0;

  function draw(){
    if(!running||drawing)return;
    const now=performance.now();
    if(now>=expiresAt)return;
    const sec=Math.max(1,Math.ceil((expiresAt-now)/1000));
    if(sec!==lastSec){lastSec=sec;paintHud(sec);}
    drawing=true;const s=snapshot();
    try{
      const W=gl.drawingBufferWidth||canvas.width,H=gl.drawingBufferHeight||canvas.height;
      if(!(W>0&&H>0))return;
      const x=8,y=8,w=Math.min(220,Math.max(110,W-16)),h=Math.min(46,Math.max(28,H-16));
      const l=x/W*2-1,r=(x+w)/W*2-1,t=1-y/H*2,b=1-(y+h)/H*2;
      const v=new Float32Array([l,t,0,1,l,b,0,0,r,b,1,0,l,t,0,1,r,b,1,0,r,t,1,1]);
      gl.viewport(0,0,W,H);gl.disable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.SCISSOR_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.colorMask(true,true,true,true);
      gl.useProgram(program);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,v,gl.STREAM_DRAW);gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,4,gl.FLOAT,false,0,0);
      gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,texture);gl.uniform1i(uTex,0);gl.drawArrays(gl.TRIANGLES,0,6);
      drawCount++;lastDrawAt=now;
    }finally{restore(s);drawing=false;}
  }
  function loop(){
    if(!running)return;
    if(performance.now()>=expiresAt){running=false;console.log('✅ WOF HUD 60-second probe finished');return;}
    try{draw();}catch(e){}
    rafId=requestAnimationFrame(loop);
  }

  paintHud(60);
  rafId=requestAnimationFrame(loop);

  window.WOFCANVAS={
    version:'webgl-game-probe-v3-60s',
    status(){return {running,secondsLeft:Math.max(0,Math.ceil((expiresAt-performance.now())/1000)),canvasId:canvas.id||null,size:{w:canvas.width,h:canvas.height},drawingBuffer:{w:gl.drawingBufferWidth,h:gl.drawingBufferHeight},webgl:isGL2?'webgl2':'webgl',drawCount,lastDrawAt};},
    draw,
    stop(){
      running=false;if(rafId)cancelAnimationFrame(rafId);
      try{gl.deleteTexture(texture);gl.deleteBuffer(buffer);gl.deleteProgram(program);}catch(_){}
      delete window.WOFCANVAS;console.log('⛔ WOF WebGL game-canvas probe stopped');
    }
  };
  console.log('✅ WOF WebGL game-canvas probe v3 installed | visible for 60 seconds',window.WOFCANVAS.status());
})();