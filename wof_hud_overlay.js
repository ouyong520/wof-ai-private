(()=>{
  'use strict';
  const CHANNEL='wof-ai-hud-v1',ROOT_ID='wof-ai-hud-root',STYLE_ID='wof-ai-hud-style';
  const HOLD_MS={1:1100,2:1300,3:1800},RELEASE_GRACE_MS=420;
  let POS_X=.50,POS_Y=.18;

  try{window.WOFHUD?.destroy?.();}catch(_){}
  document.getElementById(ROOT_ID)?.remove();document.getElementById(STYLE_ID)?.remove();

  const style=document.createElement('style');style.id=STYLE_ID;style.textContent=`
#${ROOT_ID}{position:fixed;inset:0;z-index:2147483646;pointer-events:none;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#fff}
#${ROOT_ID} *{box-sizing:border-box}
#${ROOT_ID}.wof-hidden{display:none!important}
#${ROOT_ID} .wof-anchor{position:absolute;left:50%;top:18%;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;gap:8px}
#${ROOT_ID} .wof-point{min-width:128px;padding:10px 16px;border-radius:24px;background:rgba(0,0,0,.72);border:3px solid rgba(255,255,255,.86);box-shadow:0 4px 20px rgba(0,0,0,.65);text-align:center;font-weight:1000;font-size:21px;line-height:1;white-space:nowrap;color:#fff}
#${ROOT_ID} .wof-point .bigdot{display:inline-block;font-size:38px;line-height:14px;vertical-align:-5px;margin-right:8px;color:#fff;text-shadow:0 0 11px rgba(255,255,255,.9)}
#${ROOT_ID} .wof-alert{position:relative;min-width:220px;text-align:center;border-radius:15px;padding:11px 16px 13px;background:rgba(0,0,0,.84);border:3px solid rgba(255,255,255,.94);box-shadow:0 5px 22px rgba(0,0,0,.60);overflow:hidden;white-space:nowrap;color:#fff}
#${ROOT_ID} .wof-main{font-size:31px;font-weight:1000;line-height:1;color:#fff}
#${ROOT_ID} .wof-alert.l3 .wof-main{font-size:43px}
#${ROOT_ID} .wof-threat{margin-top:7px;font-size:21px;font-weight:950;color:#fff}
#${ROOT_ID} .wof-time{margin-top:6px;font-size:15px;font-weight:900;opacity:.96;color:#fff}
#${ROOT_ID} .wof-sub{margin-top:5px;font-size:10px;opacity:.74;max-width:290px;overflow:hidden;text-overflow:ellipsis;color:#fff}
#${ROOT_ID} .wof-bar{position:absolute;left:0;bottom:0;height:4px;background:#fff}
#${ROOT_ID} .wof-status{position:absolute;padding:6px 9px;border-radius:9px;background:rgba(0,0,0,.52);font-size:10px;opacity:.78;color:#fff}
#${ROOT_ID}.wof-placing{pointer-events:auto;cursor:crosshair;background:rgba(0,0,0,.03)}
#${ROOT_ID} .wof-place-tip{display:none;position:absolute;left:50%;top:8%;transform:translateX(-50%);padding:10px 15px;border-radius:11px;background:rgba(0,0,0,.90);font-size:15px;font-weight:900;white-space:nowrap;border:1px solid rgba(255,255,255,.7)}
#${ROOT_ID}.wof-placing .wof-place-tip{display:block}
`;
  document.head.appendChild(style);

  const root=document.createElement('div');root.id=ROOT_ID;
  root.innerHTML='<div class="wof-place-tip">只可点击游戏画面内部固定HUD</div><div class="wof-anchor"><div class="wof-alerts"></div><div class="wof-point"><span class="bigdot">●</span><span class="label">P1</span></div></div><div class="wof-status">P1 · 游戏画面固定HUD</div>';
  document.body.appendChild(root);
  const anchor=root.querySelector('.wof-anchor'),alerts=root.querySelector('.wof-alerts'),label=root.querySelector('.label'),status=root.querySelector('.wof-status'),placeTip=root.querySelector('.wof-place-tip');

  let visible=true,detail=false,focus='P1',lastMsg=null,lastRx=0,destroyed=false,placing=false,lastGameRect=null;
  const HOLD={P1:null,P2:null,P3:null};
  const bc=new BroadcastChannel(CHANNEL);
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const roundMs=v=>v==null?null:(Number.isFinite(+v)?Math.max(0,Math.round(+v/50)*50):null);
  const glyph=a=>a==='UP'?'↑':a==='DOWN'?'↓':a==='LEFT'?'←':a==='RIGHT'?'→':a==='AB'?'AB':'⚠';
  const actionText=a=>a==='UP'?'上躲':a==='DOWN'?'下躲':a==='LEFT'?'左躲':a==='RIGHT'?'右躲':a==='AB'?'AB':'注意';

  function gameRect(){
    const cs=[...document.querySelectorAll('canvas')].map(c=>({c,r:c.getBoundingClientRect(),s:getComputedStyle(c)})).filter(o=>o.r.width>200&&o.r.height>150&&o.s.display!=='none'&&o.s.visibility!=='hidden');
    if(cs.length){cs.sort((a,b)=>b.r.width*b.r.height-a.r.width*a.r.height);lastGameRect=cs[0].r;return lastGameRect;}
    // Fallback for pages where the emulator uses a wrapper instead of a visible canvas.
    const els=[...document.querySelectorAll('video,iframe,[class*=game],[id*=game],[class*=emulator],[id*=emulator]')]
      .map(e=>({e,r:e.getBoundingClientRect()})).filter(o=>o.r.width>300&&o.r.height>200);
    if(els.length){els.sort((a,b)=>b.r.width*b.r.height-a.r.width*a.r.height);lastGameRect=els[0].r;return lastGameRect;}
    return lastGameRect||{left:0,top:0,width:innerWidth,height:innerHeight,right:innerWidth,bottom:innerHeight};
  }
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
  function position(){
    const r=gameRect();
    const x=r.left+POS_X*r.width,y=r.top+POS_Y*r.height;
    anchor.style.left=clamp(x,r.left+90,r.right-90)+'px';anchor.style.top=clamp(y,r.top+70,r.bottom-70)+'px';
    status.style.left=(r.left+8)+'px';status.style.top=(r.bottom-30)+'px';
    placeTip.style.left=(r.left+r.width/2)+'px';placeTip.style.top=(r.top+Math.max(25,r.height*.07))+'px';
  }

  function render(msg){
    if(!msg?.players)return;lastMsg=msg;lastRx=Date.now();
    const now=Date.now(),p=msg.players[focus]||{},h=updateHold(focus,p,now),display=h?.p||null;
    label.textContent=focus;position();alerts.textContent='';
    status.textContent=focus+' · 游戏画面固定 '+Math.round(POS_X*100)+'% / '+Math.round(POS_Y*100)+'%';
    if(!display||!h||h.level<1)return;

    const box=document.createElement('div');box.className='wof-alert '+(h.level>=3?'l3':'l1');
    const main=document.createElement('div');main.className='wof-main';
    main.textContent=h.level>=3?(glyph(display.action)+' '+actionText(display.action)):'⚠ 注意';box.appendChild(main);
    const threat=document.createElement('div');threat.className='wof-threat';threat.textContent=sideText(display);box.appendChild(threat);
    const t=heldTime(h,now),time=document.createElement('div');time.className='wof-time';
    time.textContent=t!=null?(t>=1000?'约 '+(t/1000).toFixed(1)+' 秒':'约 '+t+' ms'):(h.level>=3?'立即':'保持注意');box.appendChild(time);
    if(detail){const sub=document.createElement('div');sub.className='wof-sub';sub.textContent=[focus,display.source,display.family,display.type!=null?'T'+display.type:null,display.slot!=null?'slot '+display.slot:null].filter(Boolean).join(' · ');box.appendChild(sub);}
    const bar=document.createElement('div');bar.className='wof-bar';bar.style.width=(t==null?100:Math.max(6,Math.min(100,100*(1-t/1200))))+'%';box.appendChild(bar);alerts.appendChild(box);
  }
  bc.onmessage=e=>{const m=e.data;if(m?.schema==='wof-hud-v1'&&m.kind==='state')render(m);};

  function armPlace(){placing=true;root.classList.add('wof-placing');root.style.pointerEvents='auto';return true;}
  function cancelPlace(){placing=false;root.classList.remove('wof-placing');root.style.pointerEvents='none';return true;}
  function click(e){
    if(!placing)return;const r=gameRect();
    if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom){console.log('⚠ 请点击游戏画面内部');return;}
    POS_X=clamp((e.clientX-r.left)/r.width,.08,.92);POS_Y=clamp((e.clientY-r.top)/r.height,.08,.78);cancelPlace();position();
    console.log('🎯 HUD已固定在游戏画面',Math.round(POS_X*100)+'%',Math.round(POS_Y*100)+'%');e.preventDefault();e.stopPropagation();
  }
  root.addEventListener('click',click,true);

  function setFocus(name){if(!['P1','P2','P3'].includes(name))return focus;focus=name;HOLD.P1=HOLD.P2=HOLD.P3=null;if(lastMsg)render(lastMsg);return focus;}
  function cycle(){return setFocus(focus==='P1'?'P2':focus==='P2'?'P3':'P1');}
  function key(e){
    if(e.code==='F6'){e.preventDefault();cycle();}
    else if(e.code==='F7'){e.preventDefault();armPlace();}
    else if(e.code==='F8'){e.preventDefault();visible=!visible;root.classList.toggle('wof-hidden',!visible);}
    else if(e.code==='F9'){e.preventDefault();detail=!detail;if(lastMsg)render(lastMsg);}
  }
  addEventListener('keydown',key,true);
  function layout(){if(destroyed)return;root.classList.toggle('wof-hidden',!visible);position();requestAnimationFrame(layout);}requestAnimationFrame(layout);

  window.WOFHUD={
    version:'hud-overlay-v11-canvas-fixed-front-back',show(){visible=true;return true;},hide(){visible=false;return true;},toggle(){visible=!visible;return visible;},
    detail(on=!detail){detail=!!on;if(lastMsg)render(lastMsg);return detail;},focus:setFocus,p1(){return setFocus('P1');},p2(){return setFocus('P2');},p3(){return setFocus('P3');},cycle,
    place:armPlace,pos(x,y){if(x!=null)POS_X=clamp(+x,.08,.92);if(y!=null)POS_Y=clamp(+y,.08,.78);position();return{x:POS_X,y:POS_Y};},
    gameRect(){const r=gameRect();return{left:r.left,top:r.top,width:r.width,height:r.height,right:r.right,bottom:r.bottom};},
    status(){return{visible,detail,focus,pos:{x:POS_X,y:POS_Y},gameRect:this.gameRect(),lastRx,lastMsg,hold:HOLD[focus]};},
    destroy(){destroyed=true;removeEventListener('keydown',key,true);root.removeEventListener('click',click,true);try{bc.close();}catch(_){};root.remove();style.remove();delete window.WOFHUD;}
  };
  root.style.pointerEvents='none';
  console.log('✅ WOF HUD overlay v11 canvas-fixed + front/back threat started');
  console.log('📌 HUD现在严格绑定游戏画面矩形，不再跑到右侧聊天/功能栏。F7也只能在游戏画面内放置。');
  console.log('⚠ 提示继续显示：注意 + 前方怪/后方怪 + 左侧/右侧；真正需要躲时显示↑/↓/AB。');
})();
