(()=>{
  'use strict';

  const CHANNEL='wof-anchor-proof-v1';
  const NATIVE_W=384,NATIVE_H=224;
  const hasDom=typeof document!=='undefined'&&typeof window!=='undefined';
  const hasRam=!!(self._0x515056?.HEAPU8&&self._0x515056?.HEAPU32?.[0x2e39e4>>>2]);

  function startWorker(){
    try{self.WOFANCHORPROBE?.stop?.();}catch(_){}
    const M=self._0x515056.HEAPU8,R=self._0x515056.HEAPU32[0x2e39e4>>>2]>>>0;
    if(!R)throw new Error('CPS RAM base unavailable');
    const PBASE={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC};
    const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
    const U16=a=>((B(a)<<8)|B(a+1))>>>0;
    const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
    const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
    const W=v=>v/65536;
    const player=name=>{const a=PBASE[name];if(!a||!B(a))return null;return{name,x:W(S32(a+4)),y:W(S32(a+8)),z:W(S32(a+12))};};

    // Same bounded horizontal camera correlation model as wof_camera_probe.js.
    const START=0x0000,END=0xBE00,STEP=2,N=(END-START)/STEP;
    const last=new Uint16Array(N),minv=new Uint16Array(N),maxv=new Uint16Array(N),changes=new Uint32Array(N),valid=new Uint32Array(N),strong=new Uint32Array(N),follow=new Uint32Array(N),smooth=new Uint32Array(N);
    minv.fill(0xFFFF);
    let samples=0,prevPX=null,running=true,timer=null,lastSentAt=0,lockedAddress=null;
    const bc=new BroadcastChannel(CHANNEL);

    function addressIndex(address){
      const v=typeof address==='string'?parseInt(address,16):Number(address);
      if(!Number.isFinite(v)||v<0xFF0000||v>=0xFFBE00||((v-0xFF0000)&1))return null;
      return (v-0xFF0000)/2;
    }
    function cameraRows(limit=12){
      const p=player('P1');if(!p)return[];
      const px=p.x,rows=[];
      for(let i=0,off=START;i<N;i++,off+=STEP){
        const ch=changes[i],rng=maxv[i]-minv[i];if(samples<10||rng<4||valid[i]<samples*.55)continue;
        const vr=valid[i]/samples,sr=strong[i]/samples,fr=ch?follow[i]/ch:0,sm=samples>1?smooth[i]/(samples-1):0;
        const score=vr*4+sr*3+Math.min(1,rng/96)*1.5+Math.min(1,ch/20)*1.2+fr*1.5+sm*.3;
        rows.push({address:'0x'+(0xFF0000+off).toString(16).toUpperCase(),value:last[i],screenX:+(px-last[i]).toFixed(2),range:rng,changes:ch,valid:+vr.toFixed(3),strong:+sr.toFixed(3),follow:+fr.toFixed(3),score:+score.toFixed(3)});
      }
      rows.sort((a,b)=>b.score-a.score);return rows.slice(0,limit);
    }
    function lockedCamera(){
      if(!lockedAddress)return null;const i=addressIndex(lockedAddress);if(i==null)return null;
      return{address:'0x'+(0xFF0000+i*2).toString(16).toUpperCase(),value:last[i]};
    }
    function snapshot(){return{
      schema:CHANNEL,kind:'state',sentAt:Date.now(),samples,
      players:{P1:player('P1'),P2:player('P2'),P3:player('P3')},
      cameraTop:cameraRows(12),lockedCamera:lockedCamera()
    };}
    function send(){const m=snapshot();bc.postMessage(m);lastSentAt=m.sentAt;return m;}
    function tick(){
      if(!running)return;const p=player('P1');if(!p)return;
      const px=p.x,dpx=prevPX==null?0:px-prevPX;
      for(let i=0,off=START;i<N;i++,off+=STEP){
        const v=U16(0xFF0000+off),old=last[i];
        if(v<minv[i])minv[i]=v;if(v>maxv[i])maxv[i]=v;
        if(samples&&v!==old){changes[i]++;const dv=v-old;if(Math.abs(dv)<=8)smooth[i]++;if(dpx!==0&&Math.sign(dv)===Math.sign(dpx))follow[i]++;}
        const sx=px-v;if(sx>=-48&&sx<=432)valid[i]++;if(sx>=8&&sx<=376)strong[i]++;
        last[i]=v;
      }
      samples++;prevPX=px;send();
    }
    bc.onmessage=e=>{
      const m=e.data;if(m?.schema!==CHANNEL)return;
      if(m.kind==='lock-camera'){
        const i=addressIndex(m.address);if(i!=null){lockedAddress='0x'+(0xFF0000+i*2).toString(16).toUpperCase();send();console.log('🔒 HUDANCHOR camera locked',lockedAddress);}
      }else if(m.kind==='unlock-camera'){lockedAddress=null;send();}
    };
    timer=setInterval(tick,100);tick();
    self.WOFANCHORPROBE={
      version:'wof-player-anchor-browser-proof-v2',mode:'worker',channel:CHANNEL,
      result(){const out=snapshot();console.table(out.cameraTop);console.log(out);return out;},
      lock(address){const i=addressIndex(address);if(i==null)throw new Error('invalid camera address');lockedAddress='0x'+(0xFF0000+i*2).toString(16).toUpperCase();return send();},
      unlock(){lockedAddress=null;return send();},
      status(){return{running,samples,lastSentAt,lockedAddress};},
      stop(){running=false;if(timer)clearInterval(timer);try{bc.close();}catch(_){};delete self.WOFANCHORPROBE;console.log('⛔ HUDANCHOR Worker probe stopped');}
    };
    console.log('✅ HUDANCHOR Worker probe v2 started');
    console.log('🎮 先让 P1 向右移动到背景明显横向滚动约 15 秒；Top Console 会自动收到 camera candidates。');
    return;
  }

  function startTop(){
    try{window.WOFANCHORPROBE?.stop?.();}catch(_){}
    const canvas=window.I_GF1TC||document.getElementById('whathis');
    const gl=window.I_fdC8Q;
    if(!canvas||String(canvas.tagName).toLowerCase()!=='canvas')throw new Error('game WebGL canvas unavailable');
    const bc=new BroadcastChannel(CHANNEL);
    let running=true,last=null,lastRx=0,focus='P1',armed=true,cal=null,raf=0;

    function gameContentRect(){
      const r=canvas.getBoundingClientRect(),target=NATIVE_W/NATIVE_H,ratio=r.width/r.height;
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
    function cameraCandidate(){return last?.cameraTop?.[0]||null;}
    function currentLockedCamera(){return last?.lockedCamera||null;}
    function insideGame(x,y){const r=gameContentRect();return x>=r.left&&x<=r.right&&y>=r.top&&y<=r.bottom;}

    function calibrateAt(clientX,clientY){
      const p=last?.players?.P1,cam=cameraCandidate();
      if(!p)throw new Error('no live P1 state from Worker');
      if(!cam||(+last.samples||0)<60)throw new Error('camera candidate not ready; scroll first');
      const n=clientToNative(clientX,clientY);
      cal={
        at:Date.now(),cameraAddress:cam.address,cameraAtClick:cam.value,nativeX:n.x,nativeY:n.y,
        worldX:p.x,worldY:p.y,z:p.z,
        xBias:n.x-(p.x-cam.value),
        yBiasMinus:n.y-(p.y-p.z),yBiasPlus:n.y-(p.y+p.z),yBiasNone:n.y-p.y
      };
      bc.postMessage({schema:CHANNEL,kind:'lock-camera',address:cam.address});
      armed=false;
      console.log('🎯 HUDANCHOR calibration',calibrationSummary());
      return calibrationSummary();
    }
    function calibrationSummary(){if(!cal)return null;return{
      at:cal.at,cameraAddress:cal.cameraAddress,cameraAtClick:cal.cameraAtClick,
      nativeClick:{x:+cal.nativeX.toFixed(2),y:+cal.nativeY.toFixed(2)},
      playerAtClick:{x:+cal.worldX.toFixed(2),y:+cal.worldY.toFixed(2),z:+cal.z.toFixed(2)},
      xBias:+cal.xBias.toFixed(3)
    };}
    function modelPoint(name,kind='minus'){
      if(!cal||!last)return null;const p=last.players?.[name],cam=currentLockedCamera();if(!p||!cam||cam.address!==cal.cameraAddress)return null;
      const x=p.x-cam.value+cal.xBias;
      let y;if(kind==='plus')y=p.y+p.z+cal.yBiasPlus;else if(kind==='none')y=p.y+cal.yBiasNone;else y=p.y-p.z+cal.yBiasMinus;
      const c=nativeToClient(x,y),db=nativeToDb(x,y);
      return{player:p,camera:cam,native:{x,y},db,client:c};
    }

    const root=document.createElement('div');root.id='wof-anchor-probe-ui';root.style.cssText='position:fixed;inset:0;z-index:2147483647;pointer-events:none;font:12px/1.35 system-ui,sans-serif;color:white';
    const tip=document.createElement('div');tip.style.cssText='position:absolute;left:12px;top:12px;max-width:560px;padding:9px 11px;background:rgba(0,0,0,.82);border:1px solid white;border-radius:8px;white-space:normal';
    tip.textContent='等待 Worker HUDANCHOR 数据… 先在 Worker Console 加载同一脚本，并让 P1 向右移动到背景明显滚动约15秒。';root.appendChild(tip);
    const marks={};
    for(const [kind,label] of [['minus','Y-Z'],['plus','Y+Z'],['none','Y']]){
      const e=document.createElement('div');e.textContent=label;e.style.cssText='position:absolute;transform:translate(-50%,-100%);padding:2px 5px;background:rgba(0,0,0,.78);border:1px solid white;border-radius:5px;font-weight:800;white-space:nowrap';root.appendChild(e);marks[kind]=e;
    }
    document.documentElement.appendChild(root);

    bc.onmessage=e=>{const m=e.data;if(m?.schema===CHANNEL&&m.kind==='state'){last=m;lastRx=Date.now();}};
    function onClick(e){
      if(!armed||!insideGame(e.clientX,e.clientY))return;
      try{calibrateAt(e.clientX,e.clientY);}catch(err){console.warn('HUDANCHOR calibration not ready:',err.message);tip.textContent='还不能校准：'+err.message+'。先继续让背景横向滚动，等 camera candidate 稳定。';}
    }
    function onKey(e){
      if(e.code==='F6'){focus=focus==='P1'?'P2':focus==='P2'?'P3':'P1';console.log('HUDANCHOR focus',focus);}
      else if(e.code==='F7'){cal=null;armed=true;bc.postMessage({schema:CHANNEL,kind:'unlock-camera'});console.log('HUDANCHOR recalibration armed');}
    }
    addEventListener('click',onClick,true);addEventListener('keydown',onKey,true);

    function draw(){
      if(!running)return;
      const age=lastRx?Date.now()-lastRx:Infinity,cam=cameraCandidate();
      if(!last||age>600){tip.textContent='等待 Worker HUDANCHOR 数据…';for(const e of Object.values(marks))e.style.display='none';}
      else if(!cal){
        for(const e of Object.values(marks))e.style.display='none';
        tip.textContent='Worker samples '+last.samples+' | Camera '+(cam?.address||'?')+' score '+(cam?.score??'?')+'。背景已经明显横向滚动约15秒后，只点击一次 P1 头顶上方希望警告中心出现的位置。';
      }else{
        for(const kind of ['minus','plus','none']){
          const q=modelPoint(focus,kind),e=marks[kind];
          if(!q||!Number.isFinite(q.client.x)||!Number.isFinite(q.client.y)){e.style.display='none';continue;}
          e.style.display='block';e.style.left=q.client.x+'px';e.style.top=q.client.y+'px';e.textContent=focus+' '+(kind==='minus'?'Y-Z':kind==='plus'?'Y+Z':'Y');
        }
        const locked=currentLockedCamera();
        tip.textContent='Locked camera '+(locked?.address||cal.cameraAddress)+' | '+focus+' | 继续滚屏→上下纵深→跳一次。观察 Y-Z / Y+Z / Y 哪个始终贴住人物头顶上方。F6 可切 P1/P2/P3，F7 重校准。';
      }
      raf=requestAnimationFrame(draw);
    }

    function result(){
      const pts={};for(const k of ['minus','plus','none'])pts[k]=modelPoint(focus,k);
      const cr=canvas.getBoundingClientRect(),gr=gameContentRect();
      const out={
        version:'wof-player-anchor-browser-proof-v2',mode:'top',running,focus,lastAgeMs:lastRx?Date.now()-lastRx:null,
        calibrated:!!cal,calibration:calibrationSummary(),workerSamples:last?.samples||0,
        cameraSelected:currentLockedCamera()||cameraCandidate(),cameraTop:last?.cameraTop||[],
        currentPlayer:last?.players?.[focus]||null,models:pts,nativeHypothesis:{width:NATIVE_W,height:NATIVE_H},
        canvasCss:{left:+cr.left.toFixed(2),top:+cr.top.toFixed(2),width:+cr.width.toFixed(2),height:+cr.height.toFixed(2)},
        gameContentCss:{left:+gr.left.toFixed(2),top:+gr.top.toFixed(2),width:+gr.width.toFixed(2),height:+gr.height.toFixed(2),mode:gr.mode},
        drawingBuffer:{width:gl?.drawingBufferWidth||canvas.width,height:gl?.drawingBufferHeight||canvas.height},
        operatorDecision:'Report PASS only if one labeled Y model stays above the player through continued camera scroll, depth movement and jump. Otherwise report which axis/model drifts.'
      };
      console.log('=== HUDANCHOR TOP RESULT ===');console.table(out.cameraTop);console.log(out);return out;
    }
    function stop(){running=false;if(raf)cancelAnimationFrame(raf);removeEventListener('click',onClick,true);removeEventListener('keydown',onKey,true);try{bc.close();}catch(_){};root.remove();delete window.WOFANCHORPROBE;console.log('⛔ HUDANCHOR Top probe stopped');}
    raf=requestAnimationFrame(draw);
    window.WOFANCHORPROBE={version:'wof-player-anchor-browser-proof-v2',mode:'top',channel:CHANNEL,result,focus(name){if(['P1','P2','P3'].includes(name))focus=name;return focus;},recalibrate(){cal=null;armed=true;bc.postMessage({schema:CHANNEL,kind:'unlock-camera'});return true;},stop};
    console.log('✅ HUDANCHOR Top probe v2 started');
    console.log('同一脚本还需要在游戏 Worker Console 加载一次；两边通过 BroadcastChannel 自动桥接。');
  }

  if(hasDom)startTop();
  else if(hasRam)startWorker();
  else throw new Error('HUDANCHOR: run this script in either the game Worker Console or the Top page Console');
})();
