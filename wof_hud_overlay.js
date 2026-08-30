(()=>{
  'use strict';
  const CHANNEL='wof-ai-hud-v1',ROOT_ID='wof-ai-hud-root',STYLE_ID='wof-ai-hud-style';
  const HOLD_MS={2:520,3:900},RELEASE_GRACE_MS=180;
  try{window.WOFHUD?.destroy?.();}catch(_){}
  document.getElementById(ROOT_ID)?.remove();
  document.getElementById(STYLE_ID)?.remove();

  const style=document.createElement('style');style.id=STYLE_ID;style.textContent=`
#${ROOT_ID}{position:fixed;z-index:2147483646;pointer-events:none;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#fff;box-sizing:border-box;transform:translateZ(0)}
#${ROOT_ID} *{box-sizing:border-box}
#${ROOT_ID}.wof-hidden{display:none!important}
#${ROOT_ID} .wof-status{position:absolute;left:8px;bottom:8px;display:flex;align-items:center;gap:5px;font-size:9px;line-height:1;padding:4px 6px;border-radius:8px;background:rgba(0,0,0,.28);opacity:.58;backdrop-filter:blur(2px)}
#${ROOT_ID} .wof-led{width:6px;height:6px;border-radius:50%;background:#5ee27d;box-shadow:0 0 6px rgba(94,226,125,.8)}
#${ROOT_ID}.wof-stale .wof-led{background:#999;box-shadow:none}
#${ROOT_ID} .wof-dots{position:absolute;left:50%;bottom:10px;transform:translateX(-50%);display:flex;gap:10px;padding:4px 9px;border-radius:12px;background:rgba(0,0,0,.22);font-size:11px;line-height:1;white-space:nowrap;opacity:.78}
#${ROOT_ID} .wof-dot{opacity:.28;min-width:34px;text-align:center;font-weight:750;letter-spacing:.2px}
#${ROOT_ID} .wof-dot.l1{opacity:.85;color:#ffe17a}
#${ROOT_ID} .wof-dot.l2{opacity:1;color:#ffb15b;text-shadow:0 0 6px rgba(255,177,91,.7)}
#${ROOT_ID} .wof-dot.l3{opacity:1;color:#ff7474;text-shadow:0 0 8px rgba(255,90,90,.95)}
#${ROOT_ID} .wof-alerts{position:absolute;left:50%;top:61%;transform:translate(-50%,-50%);display:flex;flex-direction:column;gap:8px;align-items:center;width:min(92%,660px)}
#${ROOT_ID} .wof-alert{position:relative;overflow:hidden;max-width:100%;text-align:center;backdrop-filter:blur(3px);animation:wof-in .10s ease-out}
#${ROOT_ID} .wof-alert.l2{min-width:170px;padding:7px 13px 8px;border-radius:12px;border:1px solid rgba(255,177,91,.55);background:rgba(25,18,4,.58);box-shadow:0 3px 15px rgba(0,0,0,.30)}
#${ROOT_ID} .wof-alert.l3{min-width:240px;padding:10px 18px 12px;border-radius:15px;border:2px solid rgba(255,92,92,.88);background:rgba(52,0,0,.68);box-shadow:0 4px 22px rgba(0,0,0,.42),0 0 18px rgba(255,70,70,.16)}
#${ROOT_ID} .wof-main{font-weight:950;line-height:1;letter-spacing:.3px;white-space:nowrap}
#${ROOT_ID} .wof-alert.l2 .wof-main{font-size:clamp(17px,2.6vw,24px)}
#${ROOT_ID} .wof-alert.l3 .wof-main{font-size:clamp(30px,5.2vw,46px)}
#${ROOT_ID} .wof-time{margin-top:4px;font-size:clamp(12px,1.8vw,18px);font-weight:800;opacity:.92}
#${ROOT_ID} .wof-sub{margin-top:4px;font-size:10px;opacity:.66;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#${ROOT_ID} .wof-bar{position:absolute;left:0;bottom:0;height:3px;background:rgba(255,255,255,.78);transition:width .04s linear}
@keyframes wof-in{from{transform:scale(.94);opacity:.55}to{transform:scale(1);opacity:1}}
`;
  document.head.appendChild(style);

  const root=document.createElement('div');root.id=ROOT_ID;
  root.innerHTML='<div class="wof-status"><span class="wof-led"></span><span class="wof-status-text">WOF HUD</span></div><div class="wof-dots"></div><div class="wof-alerts"></div>';
  document.body.appendChild(root);
  const dots=root.querySelector('.wof-dots'),alerts=root.querySelector('.wof-alerts'),statusText=root.querySelector('.wof-status-text');

  let visible=true,detail=false,focus=null,lastMsg=null,lastRx=0,destroyed=false;
  const HOLD={P1:null,P2:null,P3:null};
  const bc=new BroadcastChannel(CHANNEL);
  const ms=v=>v==null?null:(Number.isFinite(+v)?Math.max(0,Math.round(+v/10)*10):null);
  const levelClass=l=>l>=3?'l3':l===2?'l2':l===1?'l1':'';
  const actionGlyph=a=>a==='UP'?'⬆':a==='DOWN'?'⬇':a==='AB'?'AB!':'⚠';
  const actionText=a=>a==='UP'?'上躲':a==='DOWN'?'下躲':a==='AB'?'AB':'注意';
  function selected(name){return !focus||focus===name;}
  function keyOf(p){return [p.level,p.action,p.source,p.family,p.type,p.slot].join('|');}
  function updateHold(name,p,now){
    let h=HOLD[name];
    if(p&&p.level>=2){
      const k=keyOf(p),changed=!h||h.key!==k;
      if(changed){
        h=HOLD[name]={key:k,p:{...p},level:p.level,startedAt:now,lastSeen:now,minUntil:now+(HOLD_MS[p.level]||520)};
      }else{
        h.p={...p};h.level=p.level;h.lastSeen=now;
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
    if(!msg?.players)return;lastMsg=msg;lastRx=Date.now();root.classList.remove('wof-stale');statusText.textContent='WOF HUD';
    const now=Date.now();dots.textContent='';alerts.textContent='';
    for(const name of ['P1','P2','P3']){
      const p=msg.players[name]||{},h=updateHold(name,selected(name)?p:null,now),display=h?.p||null;
      const dotLevel=selected(name)?Math.max(+p.level||0,+h?.level||0):0;
      const dot=document.createElement('div');dot.className='wof-dot '+levelClass(dotLevel);
      dot.textContent=name+' '+(dotLevel?(dotLevel>=3?actionGlyph(display?.action||p.action):dotLevel===2?'⚠':'●'):'○');dots.appendChild(dot);
      if(!selected(name)||!display||h.level<2)continue;

      const box=document.createElement('div');box.className='wof-alert '+levelClass(h.level);
      const t=heldTime(h,now),main=document.createElement('div');main.className='wof-main';
      if(h.level>=3)main.textContent=actionGlyph(display.action)+'  '+actionText(display.action);
      else main.textContent='⚠  '+name+' 注意';
      box.appendChild(main);

      const time=document.createElement('div');time.className='wof-time';
      time.textContent=name+(t!=null?' · '+Math.round(t/10)*10+'ms':'');box.appendChild(time);

      if(detail){
        const sub=document.createElement('div');sub.className='wof-sub';
        sub.textContent=[display.source,display.family,display.type!=null?'T'+display.type:null,display.slot!=null?'slot'+display.slot:null,display.hp!=null?'HP'+display.hp:null].filter(Boolean).join(' · ');box.appendChild(sub);
      }
      const bar=document.createElement('div');bar.className='wof-bar';const w=t==null?100:Math.max(4,Math.min(100,100*(1-t/1000)));bar.style.width=w+'%';box.appendChild(bar);
      alerts.appendChild(box);
    }
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
    if(Date.now()-lastRx>700){root.classList.add('wof-stale');statusText.textContent='WOF HUD 等待数据';alerts.textContent='';}
    requestAnimationFrame(layout);
  }
  requestAnimationFrame(layout);

  function key(e){
    if(e.code==='F8'){e.preventDefault();visible=!visible;}
    else if(e.code==='F9'){e.preventDefault();detail=!detail;if(lastMsg)render(lastMsg);}
  }
  addEventListener('keydown',key,true);

  window.WOFHUD={
    version:'hud-overlay-v2-sticky',
    show(){visible=true;return true;},hide(){visible=false;return true;},toggle(){visible=!visible;return visible;},
    detail(on=!detail){detail=!!on;if(lastMsg)render(lastMsg);return detail;},
    focus(name=null){focus=['P1','P2','P3'].includes(name)?name:null;if(lastMsg)render(lastMsg);return focus;},
    all(){focus=null;if(lastMsg)render(lastMsg);return true;},
    status(){return {visible,detail,focus,lastRx,lastMsg,hold:{...HOLD}};},
    destroy(){destroyed=true;removeEventListener('keydown',key,true);try{bc.close();}catch(_){};root.remove();style.remove();delete window.WOFHUD;}
  };
  console.log('✅ WOF HUD overlay v2 sticky started | F8 显示/隐藏 | F9 详情');
  console.log('🟡 L1移到底部小点；🟠 L2在战斗区短停留；🔴 L3在战斗区至少停留900ms。只提示，不控制玩家。');
})();
