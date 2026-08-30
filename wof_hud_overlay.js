(()=>{
  'use strict';
  const CHANNEL='wof-ai-hud-v1',ROOT_ID='wof-ai-hud-root',STYLE_ID='wof-ai-hud-style';
  const HOLD_MS={2:1000,3:1600},RELEASE_GRACE_MS=320;
  const LW=384,LH=224,SCAN_MS=50,TRACK_LOST_MS=1200;
  let FIXED_Y=.30;

  try{window.WOFHUD?.destroy?.();}catch(_){}
  document.getElementById(ROOT_ID)?.remove();
  document.getElementById(STYLE_ID)?.remove();

  const style=document.createElement('style');style.id=STYLE_ID;style.textContent=`
#${ROOT_ID}{position:fixed;z-index:2147483646;pointer-events:none;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#fff;box-sizing:border-box;transform:translateZ(0)}
#${ROOT_ID} *{box-sizing:border-box}
#${ROOT_ID}.wof-hidden{display:none!important}
#${ROOT_ID} .wof-status{position:absolute;left:7px;bottom:7px;display:flex;align-items:center;gap:5px;font-size:9px;line-height:1;padding:4px 6px;border-radius:8px;background:rgba(0,0,0,.28);opacity:.58}
#${ROOT_ID} .wof-led{width:6px;height:6px;border-radius:50%;background:#5ee27d;box-shadow:0 0 6px rgba(94,226,125,.8)}
#${ROOT_ID}.wof-stale .wof-led{background:#999;box-shadow:none}
#${ROOT_ID} .wof-anchor{position:absolute;left:50%;top:30%;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;gap:5px;will-change:left}
#${ROOT_ID} .wof-dot{min-width:88px;text-align:center;padding:7px 12px;border-radius:18px;background:rgba(0,0,0,.48);font-size:17px;line-height:1;font-weight:950;opacity:.94;white-space:nowrap;border:2px solid rgba(255,255,255,.30);box-shadow:0 3px 14px rgba(0,0,0,.50),0 0 10px rgba(255,255,255,.10)}
#${ROOT_ID} .wof-dot .bigdot{display:inline-block;font-size:22px;line-height:12px;vertical-align:-2px;margin-right:5px;color:#fff;text-shadow:0 0 9px rgba(255,255,255,.95)}
#${ROOT_ID} .wof-dot.l1{color:#ffe17a;border-color:rgba(255,225,122,.72);background:rgba(55,42,0,.62);box-shadow:0 3px 14px rgba(0,0,0,.50),0 0 14px rgba(255,225,122,.35)}
#${ROOT_ID} .wof-dot.l1 .bigdot{color:#ffe17a}
#${ROOT_ID} .wof-dot.l2{color:#ffb15b;border-color:rgba(255,177,91,.84);background:rgba(65,30,0,.67);box-shadow:0 3px 14px rgba(0,0,0,.50),0 0 15px rgba(255,177,91,.45)}
#${ROOT_ID} .wof-dot.l2 .bigdot{color:#ffb15b}
#${ROOT_ID} .wof-dot.l3{color:#ff7777;border-color:rgba(255,92,92,.95);background:rgba(75,0,0,.72);box-shadow:0 3px 16px rgba(0,0,0,.55),0 0 18px rgba(255,70,70,.50)}
#${ROOT_ID} .wof-dot.l3 .bigdot{color:#ff6d6d}
#${ROOT_ID} .wof-alerts{display:flex;flex-direction:column;align-items:center;margin-bottom:6px}
#${ROOT_ID} .wof-alert{position:relative;overflow:hidden;text-align:center;backdrop-filter:blur(2px);white-space:nowrap}
#${ROOT_ID} .wof-alert.l2{min-width:124px;padding:7px 11px 9px;border-radius:11px;border:1px solid rgba(255,177,91,.78);background:rgba(30,20,4,.72);box-shadow:0 3px 14px rgba(0,0,0,.38)}
#${ROOT_ID} .wof-alert.l3{min-width:154px;padding:9px 13px 11px;border-radius:13px;border:2px solid rgba(255,92,92,.96);background:rgba(55,0,0,.80);box-shadow:0 4px 20px rgba(0,0,0,.50),0 0 17px rgba(255,70,70,.18)}
#${ROOT_ID} .wof-main{font-weight:950;line-height:1;letter-spacing:.3px}
#${ROOT_ID} .wof-alert.l2 .wof-main{font-size:19px}
#${ROOT_ID} .wof-alert.l3 .wof-main{font-size:34px}
#${ROOT_ID} .wof-time{margin-top:5px;font-size:14px;font-weight:850;opacity:.98}
#${ROOT_ID} .wof-sub{margin-top:4px;font-size:9px;opacity:.68;max-width:230px;overflow:hidden;text-overflow:ellipsis}
#${ROOT_ID} .wof-bar{position:absolute;left:0;bottom:0;height:3px;background:rgba(255,255,255,.84);transition:width .08s linear}
#${ROOT_ID}.wof-locking{pointer-events:auto;cursor:crosshair}
#${ROOT_ID} .wof-lock-tip{display:none;position:absolute;left:50%;top:12%;transform:translateX(-50%);padding:8px 12px;border-radius:10px;background:rgba(0,0,0,.78);font-size:13px;font-weight:800;white-space:nowrap}
#${ROOT_ID}.wof-locking .wof-lock-tip{display:block}
`;
  document.head.appendChild(style);

  const root=document.createElement('div');root.id=ROOT_ID;
  root.innerHTML='<div class="wof-status"><span class="wof-led"></span><span class="wof-status-text">P1 X跟随</span></div><div class="wof-lock-tip">点击游戏里浮动的 1P/2P/3P 字样</div><div class="wof-anchor"><div class="wof-alerts"></div><div class="wof-dot"><span class="bigdot">●</span><span class="label">P1</span></div></div>';
  document.body.appendChild(root);
  const anchor=root.querySelector('.wof-anchor'),dot=root.querySelector('.wof-dot'),dotLabel=root.querySelector('.label'),alerts=root.querySelector('.wof-alerts'),statusText=root.querySelector('.wof-status-text'),lockTip=root.querySelector('.wof-lock-tip');

  let visible=true,detail=false,focus='P1',lastMsg=null,lastRx=0,destroyed=false,lastCanvas=null,lastRect=null;
  let lockArmed=false,lastScanAt=0;
  const HOLD={P1:null,P2:null,P3:null};
  const TRACK={P1:{x:null,vx:0,at:0,pending:null},P2:{x:null,vx:0,at:0,pending:null},P3:{x:null,vx:0,at:0,pending:null}};
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
  function holdKey(p){if(!p)return '';if((+p.level||0)>=3)return 'ACTION|'+p.action;if((+p.level||0)>=2)return 'WARN|'+(p.source||'WATCH');return '';}
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
  function heldTime(h,now){const base=ms(h?.p?.hitMs);if(base==null)return null;return Math.max(0,base-Math.max(0,now-h.lastSeen));}

  function playerColor(name,r,g,b){
    if(name==='P1')return r>150&&r>g*1.16&&r>b*1.08;
    if(name==='P2')return b>135&&b>r*1.10&&g>62&&b>=g*.76;
    return (g>125&&g>r*1.03&&g>b*1.08)||(r>155&&g>135&&b<118);
  }
  function buildMask(data,name){
    mask.fill(0);seen.fill(0);
    for(let y=20;y<LH-8;y++)for(let x=3;x<LW-3;x++){
      const i=y*LW+x,p=i*4,r=data[p],g=data[p+1],b=data[p+2],a=data[p+3];
      if(a>180&&playerColor(name,r,g,b))mask[i]=1;
    }
  }
  function components(){
    const out=[];
    for(let y=20;y<LH-8;y++)for(let x=3;x<LW-3;x++){
      const start=y*LW+x;if(!mask[start]||seen[start])continue;
      let sp=0;stack[sp++]=start;seen[start]=1;let minx=x,maxx=x,miny=y,maxy=y,n=0;
      while(sp){
        const q=stack[--sp],qy=(q/LW)|0,qx=q-qy*LW;n++;
        if(qx<minx)minx=qx;if(qx>maxx)maxx=qx;if(qy<miny)miny=qy;if(qy>maxy)maxy=qy;
        const a=q-1,b=q+1,c=q-LW,d=q+LW;
        if(qx>3&&mask[a]&&!seen[a]){seen[a]=1;stack[sp++]=a;}
        if(qx<LW-4&&mask[b]&&!seen[b]){seen[b]=1;stack[sp++]=b;}
        if(qy>20&&mask[c]&&!seen[c]){seen[c]=1;stack[sp++]=c;}
        if(qy<LH-9&&mask[d]&&!seen[d]){seen[d]=1;stack[sp++]=d;}
      }
      const w=maxx-minx+1,h=maxy-miny+1,density=n/(w*h);
      if(n>=2&&n<=330&&w<=32&&h<=30&&density>=.08)out.push({minx,maxx,miny,maxy,w,h,n,cx:(minx+maxx)/2,cy:(miny+maxy)/2,density});
    }
    return out;
  }
  function textCandidates(comps){
    const out=[];
    for(const c of comps)if(c.w>=5&&c.w<=19&&c.h>=4&&c.h<=12&&c.n>=6)out.push({...c,pair:false});
    for(let i=0;i<comps.length;i++)for(let j=i+1;j<comps.length;j++){
      let a=comps[i],b=comps[j];if(a.minx>b.minx){const t=a;a=b;b=t;}
      const gap=b.minx-a.maxx-1,dy=Math.abs(a.cy-b.cy),minx=a.minx,maxx=b.maxx,miny=Math.min(a.miny,b.miny),maxy=Math.max(a.maxy,b.maxy),w=maxx-minx+1,h=maxy-miny+1,n=a.n+b.n;
      if(gap>=-1&&gap<=6&&dy<=4&&w>=7&&w<=25&&h>=4&&h<=13&&n>=8&&n<=160)out.push({minx,maxx,miny,maxy,w,h,n,cx:(minx+maxx)/2,cy:(miny+maxy)/2,pair:true});
    }
    return out;
  }
  function arrowBelow(c,comps){
    let best=null,bs=-1e9;
    for(const a of comps){
      if(a===c)continue;const gap=a.miny-c.maxy,dx=Math.abs(a.cx-c.cx);
      if(gap<2||gap>30||dx>12||a.w<5||a.w>24||a.h<5||a.h>24||a.n<8)continue;
      const s=90-dx*5-Math.abs(gap-12)*1.8-Math.abs(a.h-11)*1.2;
      if(s>bs){bs=s;best=a;}
    }
    return best?{arrow:best,score:bs}:null;
  }
  function predictedX(name,now){const tr=TRACK[name];if(tr.x==null)return null;return tr.x+tr.vx*clamp((now-tr.at)/1000,0,.28);}
  function detectX(name){
    const c=lastCanvas||bestCanvas();if(!c||!scanCtx)return null;
    try{scanCtx.clearRect(0,0,LW,LH);scanCtx.drawImage(c,0,0,LW,LH);}catch(e){return null;}
    let img;try{img=scanCtx.getImageData(0,0,LW,LH);}catch(e){return null;}
    buildMask(img.data,name);const comps=components(),texts=textCandidates(comps),now=Date.now(),pred=predictedX(name,now),tr=TRACK[name];
    let best=null,bs=-1e9;
    for(const t of texts){
      const a=arrowBelow(t,comps);let s=(t.pair?30:8)-Math.abs(t.h-7)*2-Math.abs(t.w-12)*1.1+(a?a.score:-60);
      if(pred!=null){const dx=Math.abs(t.cx-pred),age=now-tr.at,maxDx=age<260?34:age<650?52:76;if(dx>maxDx)continue;s+=145-dx*3.3;}
      else s+=(185-t.cy)*.02;
      if(s>bs){bs=s;best={x:t.cx,at:now,score:s,source:'native-label-x'};}
    }
    return best&&bs>=25?best:null;
  }
  function acceptX(name,hit){
    const tr=TRACK[name];
    if(tr.x!=null){const dt=Math.max(.03,(hit.at-tr.at)/1000),nvx=clamp((hit.x-tr.x)/dt,-300,300);tr.vx=tr.vx*.55+nvx*.45;hit.x=tr.x+(hit.x-tr.x)*.72;}
    tr.x=hit.x;tr.at=hit.at;tr.pending=null;
  }
  function updateTracking(nowPerf){
    if(nowPerf-lastScanAt<SCAN_MS)return;lastScanAt=nowPerf;
    const hit=detectX(focus),tr=TRACK[focus],now=Date.now();if(!hit)return;
    if(tr.x==null||now-tr.at<TRACK_LOST_MS){acceptX(focus,hit);return;}
    if(tr.pending&&Math.abs(hit.x-tr.pending.x)<15&&now-tr.pending.at<220){acceptX(focus,hit);return;}
    tr.pending=hit;
  }
  function positionAnchor(){
    const tr=TRACK[focus],r=lastRect;if(!r)return false;
    let x=predictedX(focus,Date.now());if(x==null)return false;
    if(Date.now()-tr.at>TRACK_LOST_MS)x=tr.x;
    const px=clamp(x/LW*r.width,62,r.width-62),py=clamp(FIXED_Y*r.height,70,r.height-70);
    anchor.style.left=px+'px';anchor.style.top=py+'px';return true;
  }
  function fallbackAnchor(){if(!lastRect)return;anchor.style.left=(lastRect.width*.5)+'px';anchor.style.top=(FIXED_Y*lastRect.height)+'px';}

  function render(msg){
    if(!msg?.players)return;lastMsg=msg;lastRx=Date.now();root.classList.remove('wof-stale');
    const now=Date.now(),p=msg.players[focus]||{},h=updateHold(focus,p,now),display=h?.p||null,tracked=positionAnchor();
    statusText.textContent=focus+(tracked?' X跟随':' 等待X锁定');
    const dotLevel=Math.max(+p.level||0,+h?.level||0);dot.className='wof-dot '+levelClass(dotLevel);dotLabel.textContent=focus;
    alerts.textContent='';if(!display||h.level<2)return;
    const box=document.createElement('div');box.className='wof-alert '+levelClass(h.level),t=heldTime(h,now),main=document.createElement('div');main.className='wof-main';
    main.textContent=h.level>=3?(actionGlyph(display.action)+' '+actionText(display.action)):'⚠ 注意';box.appendChild(main);
    const time=document.createElement('div');time.className='wof-time';time.textContent=t!=null?(t>=1000?'约 '+(t/1000).toFixed(1)+' 秒':'约 '+t+' ms'):'保持注意';box.appendChild(time);
    if(detail){const sub=document.createElement('div');sub.className='wof-sub';sub.textContent=[focus,display.source,display.family,display.type!=null?'T'+display.type:null,'fixedY '+Math.round(FIXED_Y*100)+'%'].filter(Boolean).join(' · ');box.appendChild(sub);}
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

  function canvasPointFromEvent(e){const r=lastRect;if(!r)return null;return{x:clamp((e.clientX-r.left)/r.width*LW,0,LW-1)};}
  function lockClick(e){
    if(!lockArmed)return;const q=canvasPointFromEvent(e);if(!q)return;
    TRACK[focus]={x:q.x,vx:0,at:Date.now(),pending:null};lockArmed=false;root.classList.remove('wof-locking');root.style.pointerEvents='none';
    console.log('🎯 已校准',focus,'的X轴；Y轴保持固定');e.preventDefault();e.stopPropagation();
  }
  root.addEventListener('click',lockClick,true);
  function armLock(){lockArmed=true;root.classList.add('wof-locking');root.style.pointerEvents='auto';lockTip.textContent='点击游戏里浮动的 '+focus+' 字样，只校准X轴';return true;}
  function cancelLock(){lockArmed=false;root.classList.remove('wof-locking');root.style.pointerEvents='none';return true;}
  function setFocus(name){
    if(!['P1','P2','P3'].includes(name))return focus;focus=name;HOLD.P1=HOLD.P2=HOLD.P3=null;cancelLock();if(lastMsg)render(lastMsg);
    console.log('🎯 只显示',focus,'；Y固定，X跟随原生P字样');return focus;
  }
  function cycleFocus(){return setFocus(focus==='P1'?'P2':focus==='P2'?'P3':'P1');}
  function setY(v){const n=+v;if(!Number.isFinite(n))return FIXED_Y;FIXED_Y=clamp(n,.12,.70);if(lastMsg)render(lastMsg);return FIXED_Y;}
  function key(e){if(e.code==='F6'){e.preventDefault();cycleFocus();}else if(e.code==='F7'){e.preventDefault();armLock();}else if(e.code==='F8'){e.preventDefault();visible=!visible;}else if(e.code==='F9'){e.preventDefault();detail=!detail;if(lastMsg)render(lastMsg);}}
  addEventListener('keydown',key,true);

  window.WOFHUD={
    version:'hud-overlay-v7-fixed-y-x-follow',
    show(){visible=true;return true;},hide(){visible=false;return true;},toggle(){visible=!visible;return visible;},
    detail(on=!detail){detail=!!on;if(lastMsg)render(lastMsg);return detail;},
    focus:setFocus,p1(){return setFocus('P1');},p2(){return setFocus('P2');},p3(){return setFocus('P3');},cycle:cycleFocus,
    y:setY,lock:armLock,cancelLock,
    relock(){TRACK[focus]={x:null,vx:0,at:0,pending:null};return true;},
    status(){return {visible,detail,focus,fixedY:FIXED_Y,lastRx,tracking:TRACK[focus],lockArmed,lastMsg};},
    destroy(){destroyed=true;removeEventListener('keydown',key,true);try{bc.close();}catch(_){};root.removeEventListener('click',lockClick,true);root.remove();style.remove();delete window.WOFHUD;}
  };
  root.style.pointerEvents='none';
  console.log('✅ WOF HUD overlay v7 fixed-Y X-follow started');
  console.log('📍 这版不再跟随Y轴：Y固定在画面30%，只让X轴跟随玩家；大圆点永久放大显示。');
  console.log('🎯 F6切P1/P2/P3；F7可点原生P字样校准X；Y位置可用 WOFHUD.y(0.25) / WOFHUD.y(0.35) 调整。');
})();
