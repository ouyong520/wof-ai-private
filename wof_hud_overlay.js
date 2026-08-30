(()=>{
  'use strict';
  const CHANNEL='wof-ai-hud-v1',ROOT_ID='wof-ai-hud-root',STYLE_ID='wof-ai-hud-style';
  const HOLD_MS={2:1000,3:1600},RELEASE_GRACE_MS=320;
  try{window.WOFHUD?.destroy?.();}catch(_){}
  document.getElementById(ROOT_ID)?.remove();
  document.getElementById(STYLE_ID)?.remove();

  const style=document.createElement('style');style.id=STYLE_ID;style.textContent=`
#${ROOT_ID}{position:fixed;z-index:2147483646;pointer-events:none;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#fff;box-sizing:border-box;transform:translateZ(0)}
#${ROOT_ID} *{box-sizing:border-box}
#${ROOT_ID}.wof-hidden{display:none!important}
#${ROOT_ID} .wof-status{position:absolute;left:8px;bottom:8px;display:flex;align-items:center;gap:5px;font-size:10px;line-height:1;padding:5px 7px;border-radius:9px;background:rgba(0,0,0,.30);opacity:.7}
#${ROOT_ID} .wof-led{width:6px;height:6px;border-radius:50%;background:#5ee27d;box-shadow:0 0 6px rgba(94,226,125,.8)}
#${ROOT_ID}.wof-stale .wof-led{background:#999;box-shadow:none}
#${ROOT_ID} .wof-dot{position:absolute;left:50%;bottom:10px;transform:translateX(-50%);min-width:84px;text-align:center;padding:5px 10px;border-radius:13px;background:rgba(0,0,0,.24);font-size:12px;font-weight:800;opacity:.45;white-space:nowrap}
#${ROOT_ID} .wof-dot.l1{opacity:.9;color:#ffe17a}
#${ROOT_ID} .wof-dot.l2{opacity:1;color:#ffb15b;text-shadow:0 0 6px rgba(255,177,91,.7)}
#${ROOT_ID} .wof-dot.l3{opacity:1;color:#ff7474;text-shadow:0 0 8px rgba(255,90,90,.95)}
#${ROOT_ID} .wof-alerts{position:absolute;left:50%;top:64%;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;width:min(94%,720px)}
#${ROOT_ID} .wof-alert{position:relative;overflow:hidden;max-width:100%;text-align:center;backdrop-filter:blur(3px)}
#${ROOT_ID} .wof-alert.l2{min-width:230px;padding:10px 18px 12px;border-radius:14px;border:2px solid rgba(255,177,91,.65);background:rgba(30,20,4,.68);box-shadow:0 4px 18px rgba(0,0,0,.35)}
#${ROOT_ID} .wof-alert.l3{min-width:310px;padding:15px 24px 17px;border-radius:18px;border:3px solid rgba(255,92,92,.92);background:rgba(55,0,0,.74);box-shadow:0 5px 28px rgba(0,0,0,.48),0 0 22px rgba(255,70,70,.18)}
#${ROOT_ID} .wof-main{font-weight:950;line-height:1;letter-spacing:.4px;white-space:nowrap}
#${ROOT_ID} .wof-alert.l2 .wof-main{font-size:clamp(22px,3.2vw,30px)}
#${ROOT_ID} .wof-alert.l3 .wof-main{font-size:clamp(40px,6vw,60px)}
#${ROOT_ID} .wof-time{margin-top:8px;font-size:clamp(15px,2vw,22px);font-weight:850;opacity:.95}
#${ROOT_ID} .wof-sub{margin-top:5px;font-size:11px;opacity:.7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#${ROOT_ID} .wof-bar{position:absolute;left:0;bottom:0;height:4px;background:rgba(255,255,255,.82);transition:width .08s linear}
`;
  document.head.appendChild(style);

  const root=document.createElement('div');root.id=ROOT_ID;
  root.innerHTML='<div class="wof-status"><span class="wof-led"></span><span class="wof-status-text">P1 HUD</span></div><div class="wof-dot">P1 ○</div><div class="wof-alerts"></div>';
  document.body.appendChild(root);
  const dot=root.querySelector('.wof-dot'),alerts=root.querySelector('.wof-alerts'),statusText=root.querySelector('.wof-status-text');

  let visible=true,detail=false,focus='P1',lastMsg=null,lastRx=0,destroyed=false;
  const HOLD={P1:null,P2:null,P3:null};
  const bc=new BroadcastChannel(CHANNEL);
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
      if(changed){
        h=HOLD[name]={key:k,p:{...p},level:p.level,startedAt:now,lastSeen:now,minUntil:now+(HOLD_MS[p.level]||1000)};
      }else{
        h.p={...p};h.level=p.level;h.lastSeen=now;h.minUntil=Math.max(h.minUntil,now+250);
      }
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
  function render(msg){
    if(!msg?.players)return;lastMsg=msg;lastRx=Date.now();root.classList.remove('wof-stale');statusText.textContent=focus+' HUD';
    const now=Date.now(),p=msg.players[focus]||{},h=updateHold(focus,p,now),display=h?.p||null;
    const dotLevel=Math.max(+p.level||0,+h?.level||0);
    dot.className='wof-dot '+levelClass(dotLevel);
    dot.textContent=focus+' '+(dotLevel?(dotLevel>=3?actionGlyph(display?.action||p.action):dotLevel===2?'⚠':'●'):'○');
    alerts.textContent='';
    if(!display||h.level<2)return;

    const box=document.createElement('div');box.className='wof-alert '+levelClass(h.level);
    const t=heldTime(h,now),main=document.createElement('div');main.className='wof-main';
    main.textContent=h.level>=3?(actionGlyph(display.action)+'  '+actionText(display.action)):'⚠  '+focus+' 注意';
    box.appendChild(main);

    const time=document.createElement('div');time.className='wof-time';
    time.textContent=t!=null?('约 '+(t>=1000?(t/1000).toFixed(1)+' 秒':t+' ms')):'保持注意';box.appendChild(time);

    if(detail){
      const sub=document.createElement('div');sub.className='wof-sub';
      sub.textContent=[display.source,display.family,display.type!=null?'T'+display.type:null,display.slot!=null?'slot'+display.slot:null,display.hp!=null?'HP'+display.hp:null].filter(Boolean).join(' · ');box.appendChild(sub);
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
    if(r){root.style.left=r.left+'px';root.style.top=r.top+'px';root.style.width=r.width+'px';root.style.height=r.height+'px';}
    else{root.style.left='0';root.style.top='0';root.style.width='100vw';root.style.height='100vh';}
    root.classList.toggle('wof-hidden',!visible);
    if(Date.now()-lastRx>700){root.classList.add('wof-stale');statusText.textContent=focus+' HUD 等待数据';alerts.textContent='';}
    requestAnimationFrame(layout);
  }
  requestAnimationFrame(layout);

  function setFocus(name){
    if(!['P1','P2','P3'].includes(name))return focus;
    focus=name;HOLD.P1=HOLD.P2=HOLD.P3=null;
    if(lastMsg)render(lastMsg);
    console.log('🎯 WOF HUD 只显示',focus);
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
    version:'hud-overlay-v3-single-player',
    show(){visible=true;return true;},hide(){visible=false;return true;},toggle(){visible=!visible;return visible;},
    detail(on=!detail){detail=!!on;if(lastMsg)render(lastMsg);return detail;},
    focus:setFocus,p1(){return setFocus('P1');},p2(){return setFocus('P2');},p3(){return setFocus('P3');},cycle:cycleFocus,
    status(){return {visible,detail,focus,lastRx,lastMsg,hold:HOLD[focus]};},
    destroy(){destroyed=true;removeEventListener('keydown',key,true);try{bc.close();}catch(_){};root.remove();style.remove();delete window.WOFHUD;}
  };
  console.log('✅ WOF HUD overlay v3 single-player started');
  console.log('🎯 默认只显示P1；F6切换 P1→P2→P3；F8显示/隐藏；F9详情。');
  console.log("也可以在top Console输入 WOFHUD.p1() / WOFHUD.p2() / WOFHUD.p3()");
})();
