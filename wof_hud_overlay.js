(()=>{
  'use strict';
  const CHANNEL='wof-ai-hud-v1',ROOT_ID='wof-ai-hud-root',STYLE_ID='wof-ai-hud-style';
  try{window.WOFHUD?.destroy?.();}catch(_){}
  document.getElementById(ROOT_ID)?.remove();
  document.getElementById(STYLE_ID)?.remove();

  const style=document.createElement('style');style.id=STYLE_ID;style.textContent=`
#${ROOT_ID}{position:fixed;z-index:2147483646;pointer-events:none;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#fff;box-sizing:border-box;transform:translateZ(0)}
#${ROOT_ID} *{box-sizing:border-box}
#${ROOT_ID} .wof-status{position:absolute;left:8px;top:7px;display:flex;align-items:center;gap:5px;font-size:10px;line-height:1;padding:4px 6px;border-radius:8px;background:rgba(0,0,0,.35);opacity:.8;backdrop-filter:blur(2px)}
#${ROOT_ID} .wof-led{width:6px;height:6px;border-radius:50%;background:#5ee27d;box-shadow:0 0 6px rgba(94,226,125,.8)}
#${ROOT_ID}.wof-stale .wof-led{background:#999;box-shadow:none}
#${ROOT_ID} .wof-dots{position:absolute;left:50%;top:8px;transform:translateX(-50%);display:flex;gap:8px;padding:3px 7px;border-radius:10px;background:rgba(0,0,0,.26);font-size:11px;line-height:1;white-space:nowrap}
#${ROOT_ID} .wof-dot{opacity:.35;min-width:30px;text-align:center;font-weight:700;letter-spacing:.2px}
#${ROOT_ID} .wof-dot.l1{opacity:.8;color:#ffe17a}
#${ROOT_ID} .wof-dot.l2{opacity:1;color:#ffb15b;text-shadow:0 0 6px rgba(255,177,91,.65)}
#${ROOT_ID} .wof-dot.l3{opacity:1;color:#ff6b6b;text-shadow:0 0 8px rgba(255,107,107,.9)}
#${ROOT_ID} .wof-alerts{position:absolute;left:50%;top:30px;transform:translateX(-50%);display:flex;flex-direction:column;gap:5px;align-items:center;width:min(86%,560px)}
#${ROOT_ID} .wof-alert{position:relative;overflow:hidden;min-width:150px;max-width:100%;padding:6px 10px 7px;border-radius:10px;background:rgba(0,0,0,.54);box-shadow:0 2px 12px rgba(0,0,0,.28);backdrop-filter:blur(3px);text-align:center}
#${ROOT_ID} .wof-alert.l2{border:1px solid rgba(255,177,91,.5)}
#${ROOT_ID} .wof-alert.l3{border:1px solid rgba(255,107,107,.75);background:rgba(50,0,0,.64)}
#${ROOT_ID} .wof-main{font-size:clamp(16px,3.2vw,27px);font-weight:900;line-height:1.05;letter-spacing:.2px;white-space:nowrap}
#${ROOT_ID} .wof-sub{margin-top:3px;font-size:10px;opacity:.72;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#${ROOT_ID} .wof-bar{position:absolute;left:0;bottom:0;height:2px;background:rgba(255,255,255,.75);transition:width .04s linear}
#${ROOT_ID} .wof-hidden{display:none!important}
`;
  document.head.appendChild(style);

  const root=document.createElement('div');root.id=ROOT_ID;
  root.innerHTML='<div class="wof-status"><span class="wof-led"></span><span class="wof-status-text">WOF HUD</span></div><div class="wof-dots"></div><div class="wof-alerts"></div>';
  document.body.appendChild(root);
  const dots=root.querySelector('.wof-dots'),alerts=root.querySelector('.wof-alerts'),statusText=root.querySelector('.wof-status-text');

  let visible=true,detail=false,focus=null,lastMsg=null,lastRx=0,destroyed=false;
  const bc=new BroadcastChannel(CHANNEL);
  const glyph=p=>p.action==='UP'?'⬆':p.action==='DOWN'?'⬇':p.action==='AB'?'AB!':p.level>=2?'⚠':'●';
  const ms=v=>Number.isFinite(+v)?Math.max(0,Math.round(+v/10)*10):null;
  const levelClass=l=>l>=3?'l3':l===2?'l2':l===1?'l1':'';
  function selected(name){return !focus||focus===name;}
  function render(msg){
    if(!msg?.players)return;lastMsg=msg;lastRx=Date.now();root.classList.remove('wof-stale');statusText.textContent='WOF HUD';
    dots.textContent='';alerts.textContent='';
    for(const name of ['P1','P2','P3']){
      const p=msg.players[name]||{},dot=document.createElement('div');dot.className='wof-dot '+levelClass(selected(name)?p.level:0);
      dot.textContent=name+' '+(selected(name)&&p.level?glyph(p):'○');dots.appendChild(dot);
      if(!selected(name)||p.level<2)continue;
      const box=document.createElement('div');box.className='wof-alert '+levelClass(p.level);
      const t=ms(p.hitMs),main=document.createElement('div');main.className='wof-main';
      main.textContent=name+' '+glyph(p)+(t!=null?'  '+t+'ms':'');box.appendChild(main);
      if(detail){const sub=document.createElement('div');sub.className='wof-sub';sub.textContent=[p.source,p.family,p.type!=null?'T'+p.type:null,p.slot!=null?'slot'+p.slot:null,p.hp!=null?'HP'+p.hp:null].filter(Boolean).join(' · ');box.appendChild(sub);}
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
    version:'hud-overlay-v1',
    show(){visible=true;return true;},hide(){visible=false;return true;},toggle(){visible=!visible;return visible;},
    detail(on=!detail){detail=!!on;if(lastMsg)render(lastMsg);return detail;},
    focus(name=null){focus=['P1','P2','P3'].includes(name)?name:null;if(lastMsg)render(lastMsg);return focus;},
    all(){focus=null;if(lastMsg)render(lastMsg);return true;},
    status(){return {visible,detail,focus,lastRx,lastMsg};},
    destroy(){destroyed=true;removeEventListener('keydown',key,true);try{bc.close();}catch(_){};root.remove();style.remove();delete window.WOFHUD;}
  };
  console.log('✅ WOF HUD overlay v1 started | F8 显示/隐藏 | F9 详情');
  console.log('🟡 L1只在顶部小点提示；🟠 L2显示警告；🔴 L3显示UP/DOWN/AB。只提示，不控制玩家。');
})();
