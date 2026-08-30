(()=>{
  'use strict';
  const CHANNEL='wof-ai-hud-v1',ROOT_ID='wof-ai-hud-root',STYLE_ID='wof-ai-hud-style';
  const HOLD_MS={2:1000,3:1600},RELEASE_GRACE_MS=320;
  const LOGICAL_W=384,LOGICAL_H=224,HEAD_OFFSET=48;
  try{window.WOFHUD?.destroy?.();}catch(_){}
  document.getElementById(ROOT_ID)?.remove();
  document.getElementById(STYLE_ID)?.remove();

  const style=document.createElement('style');style.id=STYLE_ID;style.textContent=`
#${ROOT_ID}{position:fixed;z-index:2147483646;pointer-events:none;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#fff;box-sizing:border-box;transform:translateZ(0)}
#${ROOT_ID} *{box-sizing:border-box}
#${ROOT_ID}.wof-hidden{display:none!important}
#${ROOT_ID} .wof-status{position:absolute;left:7px;bottom:7px;display:flex;align-items:center;gap:5px;font-size:9px;line-height:1;padding:4px 6px;border-radius:8px;background:rgba(0,0,0,.26);opacity:.58}
#${ROOT_ID} .wof-led{width:6px;height:6px;border-radius:50%;background:#5ee27d;box-shadow:0 0 6px rgba(94,226,125,.8)}
#${ROOT_ID}.wof-stale .wof-led{background:#999;box-shadow:none}
#${ROOT_ID} .wof-anchor{position:absolute;left:50%;top:55%;transform:translate(-50%,-100%);display:flex;flex-direction:column;align-items:center;gap:5px;will-change:left,top}
#${ROOT_ID} .wof-dot{min-width:48px;text-align:center;padding:3px 7px;border-radius:11px;background:rgba(0,0,0,.20);font-size:10px;font-weight:850;opacity:.30;white-space:nowrap;box-shadow:0 1px 5px rgba(0,0,0,.24)}
#${ROOT_ID} .wof-dot.l1{opacity:.90;color:#ffe17a;background:rgba(45,35,0,.40)}
#${ROOT_ID} .wof-dot.l2{opacity:1;color:#ffb15b;background:rgba(50,25,0,.50);text-shadow:0 0 5px rgba(255,177,91,.7)}
#${ROOT_ID} .wof-dot.l3{opacity:1;color:#ff7777;background:rgba(65,0,0,.54);text-shadow:0 0 7px rgba(255,90,90,.95)}
#${ROOT_ID} .wof-alerts{display:flex;flex-direction:column;align-items:center}
#${ROOT_ID} .wof-alert{position:relative;overflow:hidden;text-align:center;backdrop-filter:blur(2px);white-space:nowrap}
#${ROOT_ID} .wof-alert.l2{min-width:120px;padding:6px 10px 8px;border-radius:11px;border:1px solid rgba(255,177,91,.70);background:rgba(30,20,4,.66);box-shadow:0 3px 13px rgba(0,0,0,.34)}
#${ROOT_ID} .wof-alert.l3{min-width:150px;padding:8px 12px 10px;border-radius:13px;border:2px solid rgba(255,92,92,.94);background:rgba(55,0,0,.74);box-shadow:0 4px 18px rgba(0,0,0,.46),0 0 15px rgba(255,70,70,.16)}
#${ROOT_ID} .wof-main{font-weight:950;line-height:1;letter-spacing:.3px}
#${ROOT_ID} .wof-alert.l2 .wof-main{font-size:18px}
#${ROOT_ID} .wof-alert.l3 .wof-main{font-size:32px}
#${ROOT_ID} .wof-time{margin-top:4px;font-size:13px;font-weight:850;opacity:.96}
#${ROOT_ID} .wof-sub{margin-top:4px;font-size:9px;opacity:.68;max-width:220px;overflow:hidden;text-overflow:ellipsis}
#${ROOT_ID} .wof-bar{position:absolute;left:0;bottom:0;height:3px;background:rgba(255,255,255,.84);transition:width .08s linear}
`;
  document.head.appendChild(style);

  const root=document.createElement('div');root.id=ROOT_ID;
  root.innerHTML='<div class="wof-status"><span class="wof-led"></span><span class="wof-status-text">P1 HUD</span></div><div class="wof-anchor"><div class="wof-alerts"></div><div class="wof-dot">P1 ○</div></div>';
  document.body.appendChild(root);
  const anchor=root.querySelector('.wof-anchor'),dot=root.querySelector('.wof-dot'),alerts=root.querySelector('.wof-alerts'),statusText=root.querySelector('.wof-status-text');

  let visible=true,detail=false,focus='P1',lastMsg=null,lastRx=0,destroyed=false;
  let manualDX=0,manualDY=0,lastCanvasRect=null;
  const HOLD={P1:null,P2:null,P3:null};
  const POS={
    P1:{sx:null,sy:null,lastX:null,lastY:null,lastZ:null,mode:'init'},
    P2:{sx:null,sy:null,lastX:null,lastY:null,lastZ:null,mode:'init'},
    P3:{sx:null,sy:null,lastX:null,lastY:null,lastZ:null,mode:'init'}
  };
  const bc=new BroadcastChannel(CHANNEL);
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const finite=v=>Number.isFinite(+v)?+v:null;
  const ms=v=>v==null?null:(Number.isFinite(+v)?Math.max(0,Math.round(+v/50)*50):null);
  const levelClass=l=>l>=3?'l3':l===2?'l2':l===1?'l1':'';
  const actionGlyph=a=>a==='UP'?'⬆':a==='DOWN'?'⬇':a==='AB'?'AB!':'⚠';
  const actionText=a=>a==='UP'?'上躲':a==='DOWN'?'下躲':a==='AB'?'AB':'注意';

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

  // Head-follow projection. WOF exposes actor world X/Y/Z but not the browser-side camera scroll.
  // If X/Y are already screen-like, use them directly. Otherwise model the normal CPS beat-em-up
  // camera dead-zone: the selected actor moves inside the center band and camera scrolling absorbs
  // further world-X motion. This keeps the marker close to the player instead of fixed at screen top.
  function projectPlayer(name,p){
    const s=POS[name],x=finite(p?.x),y=finite(p?.y),z=finite(p?.z)||0;
    if(x==null||y==null)return {x:.5,y:.56,mode:'fallback'};

    let sx,sy,mode='adaptive';
    const xScreenLike=x>=-24&&x<=LOGICAL_W+24;
    if(xScreenLike){
      sx=clamp(x,22,LOGICAL_W-22);mode='direct-x';
    }else{
      if(s.sx==null||s.lastX==null||Math.abs(x-s.lastX)>90)sx=LOGICAL_W*.50;
      else{
        const dx=x-s.lastX;
        sx=clamp(s.sx+dx,LOGICAL_W*.22,LOGICAL_W*.78);
      }
    }

    const yScreenLike=y>=20&&y<=LOGICAL_H+36;
    if(yScreenLike){
      sy=clamp(y-z-HEAD_OFFSET,28,LOGICAL_H-30);mode+=(mode?'|':'')+'direct-y';
    }else{
      if(s.sy==null||s.lastY==null||Math.abs(y-s.lastY)>60)sy=LOGICAL_H*.57;
      else sy=clamp(s.sy+(y-s.lastY)-(z-(s.lastZ||0)),30,LOGICAL_H-30);
    }

    // Gentle smoothing prevents 40ms RAM jitter, while still following real movement.
    s.sx=s.sx==null?sx:s.sx+(sx-s.sx)*.48;
    s.sy=s.sy==null?sy:s.sy+(sy-s.sy)*.48;
    s.lastX=x;s.lastY=y;s.lastZ=z;s.mode=mode;
    return {x:s.sx/LOGICAL_W,y:s.sy/LOGICAL_H,mode};
  }
  function positionAnchor(p){
    const q=projectPlayer(focus,p),r=lastCanvasRect;
    if(!r)return q;
    const padX=Math.min(90,r.width*.13),padY=Math.min(74,r.height*.22);
    const px=clamp(q.x*r.width+manualDX,padX,r.width-padX);
    const py=clamp(q.y*r.height+manualDY,padY,r.height-18);
    anchor.style.left=px+'px';anchor.style.top=py+'px';
    anchor.dataset.mode=q.mode;
    return q;
  }

  function render(msg){
    if(!msg?.players)return;lastMsg=msg;lastRx=Date.now();root.classList.remove('wof-stale');statusText.textContent=focus+' HUD';
    const now=Date.now(),p=msg.players[focus]||{},h=updateHold(focus,p,now),display=h?.p||null;
    positionAnchor(p);
    const dotLevel=Math.max(+p.level||0,+h?.level||0);
    dot.className='wof-dot '+levelClass(dotLevel);
    dot.textContent=focus+' '+(dotLevel?(dotLevel>=3?actionGlyph(display?.action||p.action):dotLevel===2?'⚠':'●'):'·');
    alerts.textContent='';
    if(!display||h.level<2)return;

    const box=document.createElement('div');box.className='wof-alert '+levelClass(h.level);
    const t=heldTime(h,now),main=document.createElement('div');main.className='wof-main';
    main.textContent=h.level>=3?(actionGlyph(display.action)+' '+actionText(display.action)):'⚠ 注意';
    box.appendChild(main);
    const time=document.createElement('div');time.className='wof-time';
    time.textContent=t!=null?(t>=1000?'约 '+(t/1000).toFixed(1)+' 秒':'约 '+t+' ms'):'保持注意';box.appendChild(time);
    if(detail){
      const sub=document.createElement('div');sub.className='wof-sub';
      sub.textContent=[focus,display.source,display.family,display.type!=null?'T'+display.type:null,'pos:'+POS[focus].mode].filter(Boolean).join(' · ');box.appendChild(sub);
    }
    const bar=document.createElement('div');bar.className='wof-bar';const w=t==null?100:Math.max(5,Math.min(100,100*(1-t/1200)));bar.style.width=w+'%';box.appendChild(bar);
    alerts.appendChild(box);
  }
  bc.onmessage=e=>{const m=e.data;if(m?.schema==='wof-hud-v1'&&m.kind==='state')render(m);};

  function bestCanvas(){
    const cs=[...document.querySelectorAll('canvas')].filter(c=>{const r=c.getBoundingClientRect();return r.width>100&&r.height>80&&getComputedStyle(c).display!=='none';});
    return cs.sort((a,b)=>{const A=a.getBoundingClientRect(),B=b.getBoundingClientRect();return B.width*B.height-A.width*A.height;})[0]||null;
  }
  function layout(){
    if(destroyed)return;const c=bestCanvas(),r=c?.getBoundingClientRect();
    if(r){lastCanvasRect=r;root.style.left=r.left+'px';root.style.top=r.top+'px';root.style.width=r.width+'px';root.style.height=r.height+'px';}
    else{lastCanvasRect={left:0,top:0,width:innerWidth,height:innerHeight};root.style.left='0';root.style.top='0';root.style.width='100vw';root.style.height='100vh';}
    root.classList.toggle('wof-hidden',!visible);
    if(lastMsg)positionAnchor(lastMsg.players?.[focus]||{});
    if(Date.now()-lastRx>700){root.classList.add('wof-stale');statusText.textContent=focus+' HUD 等待数据';alerts.textContent='';}
    requestAnimationFrame(layout);
  }
  requestAnimationFrame(layout);

  function resetPos(name=focus){POS[name]={sx:null,sy:null,lastX:null,lastY:null,lastZ:null,mode:'init'};}
  function setFocus(name){
    if(!['P1','P2','P3'].includes(name))return focus;
    focus=name;HOLD.P1=HOLD.P2=HOLD.P3=null;manualDX=manualDY=0;resetPos(name);
    if(lastMsg)render(lastMsg);
    console.log('🎯 WOF HUD 只显示',focus,'并跟随该玩家头顶');
    return focus;
  }
  function cycleFocus(){return setFocus(focus==='P1'?'P2':focus==='P2'?'P3':'P1');}
  function key(e){
    if(e.code==='F6'){e.preventDefault();cycleFocus();}
    else if(e.code==='F8'){e.preventDefault();visible=!visible;}
    else if(e.code==='F9'){e.preventDefault();detail=!detail;if(lastMsg)render(lastMsg);}
  }
  addEventListener('keydown',key,true);

  window.WOFHUD={
    version:'hud-overlay-v4-head-follow',
    show(){visible=true;return true;},hide(){visible=false;return true;},toggle(){visible=!visible;return visible;},
    detail(on=!detail){detail=!!on;if(lastMsg)render(lastMsg);return detail;},
    focus:setFocus,p1(){return setFocus('P1');},p2(){return setFocus('P2');},p3(){return setFocus('P3');},cycle:cycleFocus,
    nudge(dx=0,dy=0){manualDX+=+dx||0;manualDY+=+dy||0;if(lastMsg)render(lastMsg);return {dx:manualDX,dy:manualDY};},
    resetPosition(){manualDX=manualDY=0;resetPos();if(lastMsg)render(lastMsg);return true;},
    status(){return {visible,detail,focus,lastRx,lastMsg,hold:HOLD[focus],position:{...POS[focus]},nudge:{dx:manualDX,dy:manualDY}};},
    destroy(){destroyed=true;removeEventListener('keydown',key,true);try{bc.close();}catch(_){};root.remove();style.remove();delete window.WOFHUD;}
  };
  console.log('✅ WOF HUD overlay v4 head-follow started');
  console.log('🎯 默认P1；F6切换P1/P2/P3；提示跟随所选玩家头顶；F8隐藏；F9详情。');
  console.log("位置若差一点可临时微调：WOFHUD.nudge(左右像素, 上下像素)，例如 WOFHUD.nudge(0,-20)");
})();
