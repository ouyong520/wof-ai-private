(()=>{
  'use strict';

  try{window.WOFANCHORPROBE?.stop?.();}catch(_){}

  const M=self._0x515056?.HEAPU8;
  const R=self._0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;
  const canvas=self.I_GF1TC||document.getElementById('whathis');
  const gl=self.I_fdC8Q;
  if(!M||!R)throw new Error('CPS RAM base unavailable');
  if(!canvas||String(canvas.tagName).toLowerCase()!=='canvas')throw new Error('game canvas unavailable');

  const PBASE={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC};
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
  const U16=a=>((B(a)<<8)|B(a+1))>>>0;
  const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
  const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
  const W=v=>v/65536;
  const player=name=>{const a=PBASE[name];if(!a||!B(a))return null;return{name,x:W(S32(a+4)),y:W(S32(a+8)),z:W(S32(a+12))};};

  // WOF/CPS native visible coordinate hypothesis already used by the existing camera probe.
  // This probe validates it visually; it does not promote it automatically.
  const NATIVE_W=384,NATIVE_H=224;

  // Reuse the bounded camera-correlation model from wof_camera_probe.js.
  const START=0x0000,END=0xBE00,STEP=2,N=(END-START)/STEP;
  const last=new Uint16Array(N),minv=new Uint16Array(N),maxv=new Uint16Array(N),changes=new Uint32Array(N),valid=new Uint32Array(N),strong=new Uint32Array(N),follow=new Uint32Array(N),smooth=new Uint32Array(N);
  minv.fill(0xFFFF);
  let samples=0,prevPX=null,running=true,timer=null,raf=0,forcedIdx=null,focus='P1',armed=true;

  function camTick(){
    if(!running)return;
    const p=player('P1');if(!p)return;
    const px=p.x,dpx=prevPX==null?0:px-prevPX;
    for(let i=0,off=START;i<N;i++,off+=STEP){
      const v=U16(0xFF0000+off),old=last[i];
      if(v<minv[i])minv[i]=v;if(v>maxv[i])maxv[i]=v;
      if(samples&&v!==old){changes[i]++;const dv=v-old;if(Math.abs(dv)<=8)smooth[i]++;if(dpx!==0&&Math.sign(dv)===Math.sign(dpx))follow[i]++;}
      const sx=px-v;if(sx>=-48&&sx<=432)valid[i]++;if(sx>=8&&sx<=376)strong[i]++;
      last[i]=v;
    }
    samples++;prevPX=px;
  }

  function cameraRows(limit=12){
    const p=player('P1');if(!p)return[];
    const px=p.x,rows=[];
    for(let i=0,off=START;i<N;i++,off+=STEP){
      const ch=changes[i],rng=maxv[i]-minv[i];if(samples<10||rng<4||valid[i]<samples*.55)continue;
      const vr=valid[i]/samples,sr=strong[i]/samples,fr=ch?follow[i]/ch:0,sm=samples>1?smooth[i]/(samples-1):0;
      const score=vr*4+sr*3+Math.min(1,rng/96)*1.5+Math.min(1,ch/20)*1.2+fr*1.5+sm*.3;
      rows.push({idx:i,address:'0x'+(0xFF0000+off).toString(16).toUpperCase(),value:last[i],screenX:+(px-last[i]).toFixed(2),range:rng,changes:ch,valid:+vr.toFixed(3),strong:+sr.toFixed(3),follow:+fr.toFixed(3),score:+score.toFixed(3)});
    }
    rows.sort((a,b)=>b.score-a.score);return rows.slice(0,limit);
  }

  function currentCamera(){
    if(forcedIdx!=null)return{idx:forcedIdx,address:'0x'+(0xFF0000+START+forcedIdx*STEP).toString(16).toUpperCase(),value:last[forcedIdx],forced:true};
    const r=cameraRows(1)[0];return r||null;
  }

  function gameContentRect(){
    const r=canvas.getBoundingClientRect(),target=NATIVE_W/NATIVE_H,ratio=r.width/r.height;
    // If the canvas is already at game aspect, this is the full rect. Otherwise use a
    // conservative aspect-preserving content rect; the visual proof will expose if the emulator stretches instead.
    if(Math.abs(ratio-target)/target<0.02)return{left:r.left,top:r.top,width:r.width,height:r.height,right:r.right,bottom:r.bottom,mode:'full'};
    const scale=Math.min(r.width/NATIVE_W,r.height/NATIVE_H),w=NATIVE_W*scale,h=NATIVE_H*scale,left=r.left+(r.width-w)/2,top=r.top+(r.height-h)/2;
    return{left,top,width:w,height:h,right:left+w,bottom:top+h,mode:'contain'};
  }
  function clientToNative(x,y){const r=gameContentRect();return{x:(x-r.left)/r.width*NATIVE_W,y:(y-r.top)/r.height*NATIVE_H};}
  function nativeToClient(x,y){const r=gameContentRect();return{x:r.left+x/NATIVE_W*r.width,y:r.top+y/NATIVE_H*r.height};}
  function nativeToDb(x,y){
    const r=gameContentRect(),cr=canvas.getBoundingClientRect();
    const dbw=gl?.drawingBufferWidth||canvas.width,dbh=gl?.drawingBufferHeight||canvas.height;
    const cx=r.left-cr.left+x/NATIVE_W*r.width,cy=r.top-cr.top+y/NATIVE_H*r.height;
    return{x:cx/cr.width*dbw,y:cy/cr.height*dbh};
  }

  let cal=null;
  function calibrateAt(clientX,clientY){
    const p=player('P1');if(!p)throw new Error('P1 is not live');
    const n=clientToNative(clientX,clientY),snap=new Uint16Array(N);
    for(let i=0,off=START;i<N;i++,off+=STEP)snap[i]=U16(0xFF0000+off);
    cal={at:Date.now(),nativeX:n.x,nativeY:n.y,worldX:p.x,worldY:p.y,z:p.z,camSnapshot:snap,yBiasMinus:n.y-(p.y-p.z),yBiasPlus:n.y-(p.y+p.z),yBiasNone:n.y-p.y};
    armed=false;tip.textContent='校准完成：现在让画面明显横向滚动，再上下移动并跳一次；观察 Y-Z / Y+Z / Y 三个标签谁始终贴在人物头顶上方。';
    return calibrationSummary();
  }
  function calibrationSummary(){if(!cal)return null;return{at:cal.at,nativeClick:{x:+cal.nativeX.toFixed(2),y:+cal.nativeY.toFixed(2)},playerAtClick:{x:+cal.worldX.toFixed(2),y:+cal.worldY.toFixed(2),z:+cal.z.toFixed(2)}};}

  function modelPoint(name,kind='minus'){
    if(!cal)return null;const p=player(name),cam=currentCamera();if(!p||!cam)return null;
    const i=cam.idx,cam0=cal.camSnapshot[i],xBias=cal.nativeX-(cal.worldX-cam0),x=p.x-cam.value+xBias;
    let y;
    if(kind==='plus')y=p.y+p.z+cal.yBiasPlus;
    else if(kind==='none')y=p.y+cal.yBiasNone;
    else y=p.y-p.z+cal.yBiasMinus;
    const c=nativeToClient(x,y),db=nativeToDb(x,y);
    return{player:p,camera:{address:cam.address,value:cam.value,forced:!!cam.forced},native:{x,y},db,client:c,xBias};
  }

  const root=document.createElement('div');root.id='wof-anchor-probe-ui';root.style.cssText='position:fixed;inset:0;z-index:2147483647;pointer-events:none;font:12px/1.35 system-ui,sans-serif;color:white';
  const tip=document.createElement('div');tip.style.cssText='position:absolute;left:12px;top:12px;max-width:520px;padding:9px 11px;background:rgba(0,0,0,.82);border:1px solid white;border-radius:8px;white-space:normal';
  tip.textContent='HUDANCHOR 最小证明：请只点击一次——点在当前 P1 头顶上方、你希望警告中心出现的位置。然后让画面横向滚动、上下移动、跳一次。';
  root.appendChild(tip);
  const marks={};
  for(const [kind,label] of [['minus','Y-Z'],['plus','Y+Z'],['none','Y']]){
    const e=document.createElement('div');e.textContent=label;e.style.cssText='position:absolute;transform:translate(-50%,-100%);padding:2px 5px;background:rgba(0,0,0,.78);border:1px solid white;border-radius:5px;font-weight:800;white-space:nowrap';root.appendChild(e);marks[kind]=e;
  }
  document.documentElement.appendChild(root);

  function insideGame(x,y){const r=gameContentRect();return x>=r.left&&x<=r.right&&y>=r.top&&y<=r.bottom;}
  function onClick(e){if(!armed||!insideGame(e.clientX,e.clientY))return;try{calibrateAt(e.clientX,e.clientY);console.log('🎯 HUDANCHOR calibration',calibrationSummary());}catch(err){console.error(err);}}
  addEventListener('click',onClick,true);
  function onKey(e){
    if(e.code==='F6'){focus=focus==='P1'?'P2':focus==='P2'?'P3':'P1';console.log('HUDANCHOR focus',focus);}
    else if(e.code==='F7'){armed=true;tip.textContent='重新校准已启用：点击 P1 头顶上方希望警告中心出现的位置。';}
  }
  addEventListener('keydown',onKey,true);

  function draw(){
    if(!running)return;
    const rows=cameraRows(1),cam=currentCamera();
    tip.dataset.camera=cam?.address||'';
    if(cal&&cam){
      for(const kind of ['minus','plus','none']){
        const q=modelPoint(focus,kind),e=marks[kind];
        if(!q||!Number.isFinite(q.client.x)||!Number.isFinite(q.client.y)){e.style.display='none';continue;}
        e.style.display='block';e.style.left=q.client.x+'px';e.style.top=q.client.y+'px';e.textContent=focus+' '+(kind==='minus'?'Y-Z':kind==='plus'?'Y+Z':'Y');
      }
      const top=rows[0];
      tip.textContent='Camera '+(cam.address||'?')+' score '+(top?.score??'?')+' | 焦点 '+focus+' | F6切P1/P2/P3，F7重新点校准。请滚屏→上下移动→跳一次，观察哪个标签始终贴住人物头顶上方。';
    }
    raf=requestAnimationFrame(draw);
  }

  function result(){
    const top=cameraRows(12),pts={};for(const k of ['minus','plus','none'])pts[k]=modelPoint(focus,k);
    const cr=canvas.getBoundingClientRect(),gr=gameContentRect();
    const out={
      version:'wof-player-anchor-browser-proof-v1',running,samples,focus,calibrated:!!cal,
      calibration:calibrationSummary(),
      cameraSelected:currentCamera(),cameraTop:top,
      currentPlayer:player(focus),models:pts,
      native:{width:NATIVE_W,height:NATIVE_H},
      canvasCss:{left:+cr.left.toFixed(2),top:+cr.top.toFixed(2),width:+cr.width.toFixed(2),height:+cr.height.toFixed(2)},
      gameContentCss:{left:+gr.left.toFixed(2),top:+gr.top.toFixed(2),width:+gr.width.toFixed(2),height:+gr.height.toFixed(2),mode:gr.mode},
      drawingBuffer:{width:gl?.drawingBufferWidth||canvas.width,height:gl?.drawingBufferHeight||canvas.height},
      operatorDecision:'Report PASS if one model stays above the player through scroll/depth/jump; otherwise report which axis drifts.'
    };
    console.log('=== HUDANCHOR RESULT ===');console.table(top);console.log(out);return out;
  }
  function use(address){
    const v=typeof address==='string'?parseInt(address,16):Number(address);if(!Number.isFinite(v)||v<0xFF0000||v>=0xFFBE00||((v-0xFF0000)&1))throw new Error('camera address must be even 0xFF0000..0xFFBDFE');
    forcedIdx=(v-0xFF0000)/2;console.log('HUDANCHOR forced camera','0x'+v.toString(16).toUpperCase());return result();
  }
  function autoCamera(){forcedIdx=null;return result();}
  function stop(){running=false;if(timer)clearInterval(timer);if(raf)cancelAnimationFrame(raf);removeEventListener('click',onClick,true);removeEventListener('keydown',onKey,true);root.remove();delete window.WOFANCHORPROBE;console.log('⛔ HUDANCHOR Browser probe stopped');}

  timer=setInterval(camTick,100);camTick();raf=requestAnimationFrame(draw);
  window.WOFANCHORPROBE={version:'wof-player-anchor-browser-proof-v1',result,use,autoCamera,focus(name){if(PBASE[name])focus=name;return focus;},recalibrate(){armed=true;return true;},stop};
  console.log('✅ HUDANCHOR Browser proof v1 started');
  console.log('1) 点击一次 P1 头顶上方希望警告中心出现的位置');
  console.log('2) 让背景明显横向滚动，然后上下移动并跳一次');
  console.log('3) 运行 WOFANCHORPROBE.result()；同时说明 Y-Z / Y+Z / Y 哪个标签始终最贴合');
})();
