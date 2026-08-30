(()=>{
  'use strict';
  const CHANNEL='wof-ai-hud-v1',ROOT_ID='wof-ai-hud-root',STYLE_ID='wof-ai-hud-style';
  const HOLD_MS={2:1000,3:1600},RELEASE_GRACE_MS=320;
  const LW=384,LH=224,SCAN_MS=50,TRACK_LOST_MS=850,FREEZE_MS=260;
  try{window.WOFHUD?.destroy?.();}catch(_){}
  document.getElementById(ROOT_ID)?.remove();
  document.getElementById(STYLE_ID)?.remove();

  const style=document.createElement('style');style.id=STYLE_ID;style.textContent=`
#${ROOT_ID}{position:fixed;z-index:2147483646;pointer-events:none;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#fff;box-sizing:border-box;transform:translateZ(0)}
#${ROOT_ID} *{box-sizing:border-box}
#${ROOT_ID}.wof-hidden{display:none!important}
#${ROOT_ID} .wof-status{position:absolute;left:7px;bottom:7px;display:flex;align-items:center;gap:5px;font-size:9px;line-height:1;padding:4px 6px;border-radius:8px;background:rgba(0,0,0,.28);opacity:.62}
#${ROOT_ID} .wof-led{width:6px;height:6px;border-radius:50%;background:#5ee27d;box-shadow:0 0 6px rgba(94,226,125,.8)}
#${ROOT_ID}.wof-stale .wof-led{background:#999;box-shadow:none}
#${ROOT_ID} .wof-anchor{position:absolute;left:50%;top:55%;transform:translate(-50%,-100%);display:flex;flex-direction:column;align-items:center;gap:3px;will-change:left,top}
#${ROOT_ID} .wof-dot{min-width:46px;text-align:center;padding:3px 7px;border-radius:10px;background:rgba(0,0,0,.22);font-size:10px;font-weight:850;opacity:.30;white-space:nowrap;box-shadow:0 1px 5px rgba(0,0,0,.24)}
#${ROOT_ID} .wof-dot.l1{opacity:.92;color:#ffe17a;background:rgba(45,35,0,.43)}
#${ROOT_ID} .wof-dot.l2{opacity:1;color:#ffb15b;background:rgba(50,25,0,.54);text-shadow:0 0 5px rgba(255,177,91,.7)}
#${ROOT_ID} .wof-dot.l3{opacity:1;color:#ff7777;background:rgba(65,0,0,.58);text-shadow:0 0 7px rgba(255,90,90,.95)}
#${ROOT_ID} .wof-alerts{display:flex;flex-direction:column;align-items:center}
#${ROOT_ID} .wof-alert{position:relative;overflow:hidden;text-align:center;backdrop-filter:blur(2px);white-space:nowrap}
#${ROOT_ID} .wof-alert.l2{min-width:112px;padding:6px 10px 8px;border-radius:10px;border:1px solid rgba(255,177,91,.74);background:rgba(30,20,4,.69);box-shadow:0 3px 13px rgba(0,0,0,.36)}
#${ROOT_ID} .wof-alert.l3{min-width:145px;padding:8px 12px 10px;border-radius:12px;border:2px solid rgba(255,92,92,.95);background:rgba(55,0,0,.77);box-shadow:0 4px 18px rgba(0,0,0,.48),0 0 15px rgba(255,70,70,.16)}
#${ROOT_ID} .wof-main{font-weight:950;line-height:1;letter-spacing:.3px}
#${ROOT_ID} .wof-alert.l2 .wof-main{font-size:17px}
#${ROOT_ID} .wof-alert.l3 .wof-main{font-size:31px}
#${ROOT_ID} .wof-time{margin-top:4px;font-size:13px;font-weight:850;opacity:.96}
#${ROOT_ID} .wof-sub{margin-top:4px;font-size:9px;opacity:.68;max-width:220px;overflow:hidden;text-overflow:ellipsis}
#${ROOT_ID} .wof-bar{position:absolute;left:0;bottom:0;height:3px;background:rgba(255,255,255,.84);transition:width .08s linear}
#${ROOT_ID}.wof-locking{pointer-events:auto;cursor:crosshair}
#${ROOT_ID} .wof-lock-tip{display:none;position:absolute;left:50%;top:14%;transform:translateX(-50%);padding:8px 12px;border-radius:10px;background:rgba(0,0,0,.74);font-size:13px;font-weight:800;white-space:nowrap}
#${ROOT_ID}.wof-locking .wof-lock-tip{display:block}
`;
  document.head.appendChild(style);

  const root=document.createElement('div');root.id=ROOT_ID;
  root.innerHTML='<div class="wof-status"><span class="wof-led"></span><span class="wof-status-text">P1 HUD</span></div><div class="wof-lock-tip">点击游戏里浮动的 1P/2P/3P 字样</div><div class="wof-anchor"><div class="wof-alerts"></div><div class="wof-dot">P1 ·</div></div>';
  document.body.appendChild(root);
  const anchor=root.querySelector('.wof-anchor'),dot=root.querySelector('.wof-dot'),alerts=root.querySelector('.wof-alerts'),statusText=root.querySelector('.wof-status-text'),lockTip=root.querySelector('.wof-lock-tip');

  let visible=true,detail=false,focus='P1',lastMsg=null,lastRx=0,destroyed=false,lastCanvas=null,lastRect=null;
  let lockArmed=false,lastScanAt=0;
  const HOLD={P1:null,P2:null,P3:null};
  const TRACK={
    P1:{hit:null,vx:0,vy:0,pending:null},
    P2:{hit:null,vx:0,vy:0,pending:null},
    P3:{hit:null,vx:0,vy:0,pending:null}
  };
  const bc=new BroadcastChannel(CHANNEL);
  const scanCanvas=document.createElement('canvas');scanCanvas.width=LW;scanCanvas.height=LH;
  const scanCtx=scanCanvas.getContext('2d',{willReadFrequently:true});
  const mask=new Uint8Array(LW*LH),seen=new Uint8Array(LW*LH),stack=new Int32Array(LW*LH);
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const ms=v=>v==null?null:(Number.isFinite(+v)?Math.max(0,Math.round(+v/50)*50):null);
  const levelClass=l=>l>=3?'l3':l===2?'l2':l===1?'l1':'';
  const actionGlyph=a=>a==='UP'?'⬆':a==='DOWN'?'⬇':a==='AB'?'AB!':'⚠';
  const actionText=a=>a==='UP'?'上躲':a==='DOWN'?'下躲':a==='AB'?'AB':'注意';

  function bestCanvas(){
    const cs=[...document.querySelectorAll('canvas')].filter(c=>{const r=c.getBoundingClientRect();return r.width>100&&r.height>80&&getComputedStyle(c).display!=='none';});
    return cs.sort((a,b)=>{const A=a.getBoundingClientRect(),B=b.getBoundingClientRect();return B.width*B.height-A.width*A.height;})[0]||null;
  }
  function holdKey(p){
    if(!p)return '';
    if((+p.level||0)>=3)return 'ACTION|'+p.action;
    if((+p.level||0)>=2)return 'WARN|'+(p.source||'WATCH');
    return '';
  }
  function updateHold(name,p,now){
    let h=HOLD[name];
    if(p&&p.level>=2){
      const k=holdKey(p),changed=!h||h.key!==k;
      if(changed)h=HOLD[name]={key:k,p:{...p},level:p.level,startedAt:now,lastSeen:now,minUntil:now+(HOLD_MS[p.level]||1000)};
      else{h.p={...p};h.level=p.level;h.lastSeen=now;h.minUntil=Math.max(h.minUntil,now+250);}
      return h;
    }
    if(!h)return null;
    if(now>=h.minUntil&&now-h.lastSeen>RELEASE_GRACE_MS){HOLD[name]=null;return null;}
    return h;
  }
  function heldTime(h,now){
    const base=ms(h?.p?.hitMs);if(base==null)return null;
    return Math.max(0,base-Math.max(0,now-h.lastSeen));
  }

  function playerColor(name,r,g,b){
    if(name==='P1')return r>150&&r>g*1.16&&r>b*1.08;
    if(name==='P2')return b>135&&b>r*1.10&&g>62&&b>=g*.76;
    return (g>125&&g>r*1.03&&g>b*1.08)||(r>155&&g>135&&b<118);
  }
  function buildMask(data,name){
    mask.fill(0);seen.fill(0);
    for(let y=24;y<LH-10;y++)for(let x=3;x<LW-3;x++){
      const i=y*LW+x,p=i*4,r=data[p],g=data[p+1],b=data[p+2],a=data[p+3];
      if(a>180&&playerColor(name,r,g,b))mask[i]=1;
    }
  }
  function components(){
    const out=[];
    for(let y=24;y<LH-10;y++)for(let x=3;x<LW-3;x++){
      const start=y*LW+x;if(!mask[start]||seen[start])continue;
      let sp=0;stack[sp++]=start;seen[start]=1;
      let minx=x,maxx=x,miny=y,maxy=y,n=0;
      while(sp){
        const q=stack[--sp],qy=(q/LW)|0,qx=q-qy*LW;n++;
        if(qx<minx)minx=qx;if(qx>maxx)maxx=qx;if(qy<miny)miny=qy;if(qy>maxy)maxy=qy;
        const a=q-1,b=q+1,c=q-LW,d=q+LW;
        if(qx>3&&mask[a]&&!seen[a]){seen[a]=1;stack[sp++]=a;}
        if(qx<LW-4&&mask[b]&&!seen[b]){seen[b]=1;stack[sp++]=b;}
        if(qy>24&&mask[c]&&!seen[c]){seen[c]=1;stack[sp++]=c;}
        if(qy<LH-11&&mask[d]&&!seen[d]){seen[d]=1;stack[sp++]=d;}
      }
      const w=maxx-minx+1,h=maxy-miny+1,density=n/(w*h);
      if(n>=2&&n<=320&&w<=30&&h<=28&&density>=.09)out.push({minx,maxx,miny,maxy,w,h,n,cx:(minx+maxx)/2,cy:(miny+maxy)/2,density});
    }
    return out;
  }
  function textCandidates(comps){
    const out=[];
    for(const c of comps)if(c.w>=5&&c.w<=18&&c.h>=4&&c.h<=11&&c.n>=6)out.push({...c,pair:false});
    for(let i=0;i<comps.length;i++)for(let j=i+1;j<comps.length;j++){
      let a=comps[i],b=comps[j];if(a.minx>b.minx){const t=a;a=b;b=t;}
      const gap=b.minx-a.maxx-1,dy=Math.abs(a.cy-b.cy),minx=a.minx,maxx=b.maxx,miny=Math.min(a.miny,b.miny),maxy=Math.max(a.maxy,b.maxy),w=maxx-minx+1,h=maxy-miny+1,n=a.n+b.n;
      if(gap>=-1&&gap<=6&&dy<=3.5&&w>=7&&w<=24&&h>=4&&h<=12&&n>=8&&n<=150)
        out.push({minx,maxx,miny,maxy,w,h,n,cx:(minx+maxx)/2,cy:(miny+maxy)/2,pair:true});
    }
    return out;
  }
  function arrowBelow(c,comps){
    let best=null,bs=-1e9;
    for(const a of comps){
      if(a===c)continue;
      const gap=a.miny-c.maxy,dx=Math.abs(a.cx-c.cx);
      if(gap<3||gap>26||dx>10)continue;
      if(a.w<5||a.w>22||a.h<5||a.h>22||a.n<8)continue;
      const s=80-dx*5-Math.abs(gap-11)*2-Math.abs(a.h-10)*1.5;
      if(s>bs){bs=s;best=a;}
    }
    return best?{arrow:best,score:bs}:null;
  }
  function predicted(name,now){
    const tr=TRACK[name],h=tr.hit;if(!h)return null;
    const dt=clamp((now-h.at)/1000,0,.35);
    return {x:h.x+tr.vx*dt,y:h.y+tr.vy*dt};
  }
  function candidateScore(name,c,arrow,now){
    const tr=TRACK[name],prev=tr.hit,pred=predicted(name,now);
    let s=(c.pair?28:6)-Math.abs(c.h-7)*2.5-Math.abs(c.w-12)*1.2;
    if(arrow)s+=arrow.score;
    else s-=55;
    if(c.miny<34)s-=18;
    if(prev&&pred){
      const age=now-prev.at,maxD=age<220?34:age<450?52:70,d=Math.hypot(c.cx-pred.x,c.cy-pred.y);
      if(d>maxD)return -1e9;
      s+=120-d*3.0;
    }else s+=(185-c.cy)*.03;
    return s;
  }
  function detect(name){
    const c=lastCanvas||bestCanvas();if(!c||!scanCtx)return null;
    try{scanCtx.clearRect(0,0,LW,LH);scanCtx.drawImage(c,0,0,LW,LH);}catch(e){return null;}
    let img;try{img=scanCtx.getImageData(0,0,LW,LH);}catch(e){return null;}
    buildMask(img.data,name);const comps=components(),texts=textCandidates(comps),now=Date.now();
    let best=null,bs=-1e9;
    for(const t of texts){const a=arrowBelow(t,comps),s=candidateScore(name,t,a,now);if(s>bs){bs=s;best={x:t.cx,y:t.miny,box:t,arrow:a?.arrow||null,score:s,at:now,source:'native-label+arrow'};}}
    if(!best||bs<20)return null;
    return best;
  }
  function acceptHit(name,hit){
    const tr=TRACK[name],old=tr.hit;
    if(old){
      const dt=Math.max(.03,(hit.at-old.at)/1000),dx=hit.x-old.x,dy=hit.y-old.y;
      const nvx=clamp(dx/dt,-280,280),nvy=clamp(dy/dt,-380,380);
      tr.vx=tr.vx*.45+nvx*.55;tr.vy=tr.vy*.45+nvy*.55;
      hit.x=old.x+(hit.x-old.x)*.78;hit.y=old.y+(hit.y-old.y)*.78;
    }
    tr.hit=hit;tr.pending=null;
  }
  function updateTracking(nowPerf){
    if(nowPerf-lastScanAt<SCAN_MS)return;lastScanAt=nowPerf;
    const hit=detect(focus),tr=TRACK[focus],now=Date.now();
    if(hit){
      if(!tr.hit||now-tr.hit.at<TRACK_LOST_MS){acceptHit(focus,hit);return;}
      // After a long loss, require two nearby detections before relocking so jumps/overlap do not snap to clothing.
      if(tr.pending&&Math.hypot(hit.x-tr.pending.x,hit.y-tr.pending.y)<18&&now-tr.pending.at<220){acceptHit(focus,hit);return;}
      tr.pending=hit;return;
    }
    if(tr.hit){
      const age=now-tr.hit.at;
      if(age<=FREEZE_MS){
        const dt=age/1000;tr.hit.renderX=tr.hit.x+tr.vx*dt;tr.hit.renderY=tr.hit.y+tr.vy*dt;
      }else{delete tr.hit.renderX;delete tr.hit.renderY;}
    }
  }
  function positionAnchor(){
    const tr=TRACK[focus],h=tr.hit,r=lastRect;if(!h||!r)return false;
    const age=Date.now()-h.at;if(age>TRACK_LOST_MS)return false;
    const x=h.renderX??h.x,y=h.renderY??h.y,sx=r.width/LW,sy=r.height/LH;
    const px=clamp(x*sx,58,r.width-58),py=clamp((y-3)*sy,42,r.height-18);
    anchor.style.left=px+'px';anchor.style.top=py+'px';
    return true;
  }
  function fallbackAnchor(){if(!lastRect)return;anchor.style.left=(lastRect.width*.5)+'px';anchor.style.top=(lastRect.height*.58)+'px';}

  function render(msg){
    if(!msg?.players)return;lastMsg=msg;lastRx=Date.now();root.classList.remove('wof-stale');
    const now=Date.now(),p=msg.players[focus]||{},h=updateHold(focus,p,now),display=h?.p||null,tracked=positionAnchor();
    statusText.textContent=focus+(tracked?' 跟随':' 寻找人物');
    const dotLevel=Math.max(+p.level||0,+h?.level||0);
    dot.className='wof-dot '+levelClass(dotLevel);
    dot.textContent=focus+' '+(dotLevel?(dotLevel>=3?actionGlyph(display?.action||p.action):dotLevel===2?'⚠':'●'):'·');
    alerts.textContent='';if(!display||h.level<2)return;
    const box=document.createElement('div');box.className='wof-alert '+levelClass(h.level),t=heldTime(h,now),main=document.createElement('div');main.className='wof-main';
    main.textContent=h.level>=3?(actionGlyph(display.action)+' '+actionText(display.action)):'⚠ 注意';box.appendChild(main);
    const time=document.createElement('div');time.className='wof-time';time.textContent=t!=null?(t>=1000?'约 '+(t/1000).toFixed(1)+' 秒':'约 '+t+' ms'):'保持注意';box.appendChild(time);
    if(detail){const sub=document.createElement('div');sub.className='wof-sub';sub.textContent=[focus,display.source,display.family,display.type!=null?'T'+display.type:null,tracked?'label+arrow':'unlocked'].filter(Boolean).join(' · ');box.appendChild(sub);}
    const bar=document.createElement('div');bar.className='wof-bar';bar.style.width=(t==null?100:Math.max(5,Math.min(100,100*(1-t/1200))))+'%';box.appendChild(bar);alerts.appendChild(box);
  }
  bc.onmessage=e=>{const m=e.data;if(m?.schema==='wof-hud-v1'&&m.kind==='state')render(m);};

  function layout(){
    if(destroyed)return;const c=bestCanvas(),r=c?.getBoundingClientRect();lastCanvas=c||lastCanvas;
    if(r){lastRect=r;root.style.left=r.left+'px';root.style.top=r.top+'px';root.style.width=r.width+'px';root.style.height=r.height+'px';}
    else{lastRect={left:0,top:0,width:innerWidth,height:innerHeight};root.style.left='0';root.style.top='0';root.style.width='100vw';root.style.height='100vh';}
    root.classList.toggle('wof-hidden',!visible);updateTracking(performance.now());if(!positionAnchor())fallbackAnchor();
    if(Date.now()-lastRx>700){root.classList.add('wof-stale');statusText.textContent=focus+' 等待数据';alerts.textContent='';}
    requestAnimationFrame(layout);
  }
  requestAnimationFrame(layout);

  function canvasPointFromEvent(e){const r=lastRect;if(!r)return null;return{x:clamp((e.clientX-r.left)/r.width*LW,0,LW-1),y:clamp((e.clientY-r.top)/r.height*LH,0,LH-1)};}
  function lockClick(e){
    if(!lockArmed)return;const q=canvasPointFromEvent(e);if(!q)return;
    TRACK[focus]={hit:{x:q.x,y:q.y,at:Date.now(),source:'manual-seed'},vx:0,vy:0,pending:null};
    lockArmed=false;root.classList.remove('wof-locking');root.style.pointerEvents='none';
    console.log('🎯 已校准',focus,'原生浮动字样；跳跃后会继续局部跟踪，不会全屏乱锁');e.preventDefault();e.stopPropagation();
  }
  root.addEventListener('click',lockClick,true);
  function armLock(){lockArmed=true;root.classList.add('wof-locking');root.style.pointerEvents='auto';lockTip.textContent='点击游戏里浮动的 '+focus+' 字样';return true;}
  function cancelLock(){lockArmed=false;root.classList.remove('wof-locking');root.style.pointerEvents='none';return true;}
  function setFocus(name){
    if(!['P1','P2','P3'].includes(name))return focus;
    focus=name;HOLD.P1=HOLD.P2=HOLD.P3=null;cancelLock();if(lastMsg)render(lastMsg);
    console.log('🎯 WOF HUD 只显示',focus,'；自动锁定“字样+下箭头”组合');return focus;
  }
  function cycleFocus(){return setFocus(focus==='P1'?'P2':focus==='P2'?'P3':'P1');}
  function key(e){
    if(e.code==='F6'){e.preventDefault();cycleFocus();}
    else if(e.code==='F7'){e.preventDefault();armLock();}
    else if(e.code==='F8'){e.preventDefault();visible=!visible;}
    else if(e.code==='F9'){e.preventDefault();detail=!detail;if(lastMsg)render(lastMsg);}
  }
  addEventListener('keydown',key,true);

  window.WOFHUD={
    version:'hud-overlay-v6-jump-safe-label-follow',
    show(){visible=true;return true;},hide(){visible=false;return true;},toggle(){visible=!visible;return visible;},
    detail(on=!detail){detail=!!on;if(lastMsg)render(lastMsg);return detail;},
    focus:setFocus,p1(){return setFocus('P1');},p2(){return setFocus('P2');},p3(){return setFocus('P3');},cycle:cycleFocus,
    lock:armLock,cancelLock,
    relock(){TRACK[focus]={hit:null,vx:0,vy:0,pending:null};return true;},
    status(){return {visible,detail,focus,lastRx,tracking:TRACK[focus],lockArmed,lastMsg};},
    destroy(){destroyed=true;removeEventListener('keydown',key,true);try{bc.close();}catch(_){};root.removeEventListener('click',lockClick,true);root.remove();style.remove();delete window.WOFHUD;}
  };
  root.style.pointerEvents='none';
  console.log('✅ WOF HUD overlay v6 jump-safe label-follow started');
  console.log('🧲 现在锁定游戏原生“1P/2P/3P文字 + 下箭头”组合，并用速度预测跨过跳起/前跳/后跳短暂丢帧。');
  console.log('🎯 F6切玩家；如果第一次没锁准，F7后点一下游戏原生P字样。');
})();
