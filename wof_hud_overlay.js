(()=>{
  'use strict';
  const CHANNEL='wof-ai-hud-v1',ROOT_ID='wof-ai-hud-root',STYLE_ID='wof-ai-hud-style';
  const HOLD_MS={1:1000,2:1200,3:1700},RELEASE_GRACE_MS=380;
  const LOGICAL_W=384,LEFT_BAND=.16,RIGHT_BAND=.84;
  let FIXED_Y=.28;

  try{window.WOFHUD?.destroy?.();}catch(_){}
  document.getElementById(ROOT_ID)?.remove();
  document.getElementById(STYLE_ID)?.remove();

  const style=document.createElement('style');style.id=STYLE_ID;style.textContent=`
#${ROOT_ID}{position:fixed;inset:0;z-index:2147483646;pointer-events:none;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#fff;box-sizing:border-box}
#${ROOT_ID} *{box-sizing:border-box}
#${ROOT_ID}.wof-hidden{display:none!important}
#${ROOT_ID} .wof-anchor{position:absolute;left:50%;top:28%;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;gap:7px;will-change:left}
#${ROOT_ID} .wof-point{min-width:118px;padding:9px 15px;border-radius:24px;background:rgba(0,0,0,.68);border:3px solid rgba(255,255,255,.78);box-shadow:0 4px 18px rgba(0,0,0,.60);text-align:center;font-weight:950;font-size:20px;line-height:1;white-space:nowrap;color:#fff}
#${ROOT_ID} .wof-point .bigdot{display:inline-block;font-size:36px;line-height:15px;vertical-align:-5px;margin-right:7px;color:#fff;text-shadow:0 0 10px rgba(255,255,255,.75)}
#${ROOT_ID} .wof-alert{position:relative;min-width:150px;text-align:center;border-radius:14px;padding:10px 15px 12px;backdrop-filter:blur(2px);box-shadow:0 4px 20px rgba(0,0,0,.52);overflow:hidden;white-space:nowrap;background:rgba(0,0,0,.78);border:2px solid rgba(255,255,255,.90);color:#fff}
#${ROOT_ID} .wof-alert.l3{min-width:190px;padding:12px 18px 14px;border-width:3px}
#${ROOT_ID} .wof-main{font-weight:1000;line-height:1;color:#fff}
#${ROOT_ID} .wof-alert.l1 .wof-main,#${ROOT_ID} .wof-alert.l2 .wof-main{font-size:27px}
#${ROOT_ID} .wof-alert.l3 .wof-main{font-size:44px}
#${ROOT_ID} .wof-time{margin-top:7px;font-size:16px;font-weight:900;opacity:.98;color:#fff}
#${ROOT_ID} .wof-sub{margin-top:5px;font-size:10px;opacity:.72;max-width:250px;overflow:hidden;text-overflow:ellipsis;color:#fff}
#${ROOT_ID} .wof-bar{position:absolute;left:0;bottom:0;height:4px;background:rgba(255,255,255,.90)}
#${ROOT_ID} .wof-status{position:absolute;left:8px;bottom:8px;padding:5px 8px;border-radius:9px;background:rgba(0,0,0,.44);font-size:10px;opacity:.72;color:#fff}
#${ROOT_ID}.wof-calibrating{pointer-events:auto;cursor:crosshair;background:rgba(0,0,0,.05)}
#${ROOT_ID} .wof-cal-tip{display:none;position:absolute;left:50%;top:9%;transform:translateX(-50%);padding:10px 15px;border-radius:11px;background:rgba(0,0,0,.88);font-size:15px;font-weight:900;white-space:nowrap;color:#fff;border:1px solid rgba(255,255,255,.65)}
#${ROOT_ID}.wof-calibrating .wof-cal-tip{display:block}
`;
  document.head.appendChild(style);

  const root=document.createElement('div');root.id=ROOT_ID;
  root.innerHTML='<div class="wof-cal-tip">点击你的人物，或人物头顶原生P字样，只校准X轴</div><div class="wof-anchor"><div class="wof-alerts"></div><div class="wof-point"><span class="bigdot">●</span><span class="label">P1</span></div></div><div class="wof-status">P1 · 固定Y / RAM-X</div>';
  document.body.appendChild(root);
  const anchor=root.querySelector('.wof-anchor'),alerts=root.querySelector('.wof-alerts'),point=root.querySelector('.wof-point'),label=root.querySelector('.label'),status=root.querySelector('.wof-status'),calTip=root.querySelector('.wof-cal-tip');

  let visible=true,detail=false,focus='P1',lastMsg=null,lastRx=0,destroyed=false,calibrating=false;
  const HOLD={P1:null,P2:null,P3:null};
  const XSTATE={P1:null,P2:null,P3:null};
  const bc=new BroadcastChannel(CHANNEL);
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const finite=v=>Number.isFinite(+v)?+v:null;
  const roundMs=v=>v==null?null:(Number.isFinite(+v)?Math.max(0,Math.round(+v/50)*50):null);
  const ratioKey=n=>'wof-hud-xratio-'+n;

  function glyph(a){
    return a==='UP'?'⬆':a==='DOWN'?'⬇':a==='LEFT'?'⬅':a==='RIGHT'?'➡':a==='AB'?'AB!':'⚠';
  }
  function actionText(a){
    return a==='UP'?'上':a==='DOWN'?'下':a==='LEFT'?'左':a==='RIGHT'?'右':a==='AB'?'AB':'注意';
  }
  function savedRatio(name){
    try{const v=+localStorage.getItem(ratioKey(name));return Number.isFinite(v)&&v>.05&&v<.95?v:null;}catch(_){return null;}
  }
  function saveRatio(name,r){try{localStorage.setItem(ratioKey(name),String(r));}catch(_){}}
  function holdKey(p){
    if(!p||(+p.level||0)<1)return '';
    if((+p.level||0)>=3)return 'ACTION|'+p.action;
    return 'WARN|'+(p.source||'WATCH')+'|L'+p.level;
  }
  function updateHold(name,p,now){
    let h=HOLD[name];
    if(p&&(+p.level||0)>=1){
      const level=+p.level||1,k=holdKey(p),changed=!h||h.key!==k;
      if(changed)h=HOLD[name]={key:k,p:{...p},level,startedAt:now,lastSeen:now,minUntil:now+(HOLD_MS[level]||1000)};
      else{h.p={...p};h.level=level;h.lastSeen=now;h.minUntil=Math.max(h.minUntil,now+240);}
      return h;
    }
    if(!h)return null;
    if(now>=h.minUntil&&now-h.lastSeen>RELEASE_GRACE_MS){HOLD[name]=null;return null;}
    return h;
  }
  function heldTime(h,now){
    const base=roundMs(h?.p?.hitMs);if(base==null)return null;
    return Math.max(0,base-Math.max(0,now-h.lastSeen));
  }

  function ensureX(name,p){
    const wx=finite(p?.x),W=innerWidth;if(wx==null)return null;
    let s=XSTATE[name];
    if(!s){
      const saved=savedRatio(name),ratio=saved??.50;
      s=XSTATE[name]={screenX:ratio*W,lastWorldX:wx,calibrated:saved!=null,ratio};
    }
    return s;
  }
  function updateX(name,p){
    const wx=finite(p?.x),W=innerWidth,s=ensureX(name,p);if(!s||wx==null)return W*.5;
    let dw=wx-s.lastWorldX;s.lastWorldX=wx;
    if(Math.abs(dw)>70)dw=0;
    const scale=W/LOGICAL_W;
    let next=s.screenX+dw*scale;
    const lo=W*LEFT_BAND,hi=W*RIGHT_BAND;
    next=clamp(next,lo,hi);
    s.screenX=s.screenX+(next-s.screenX)*.88;
    s.ratio=s.screenX/W;
    return s.screenX;
  }
  function positionAnchor(p){
    const x=updateX(focus,p);anchor.style.left=clamp(x,75,innerWidth-75)+'px';anchor.style.top=(FIXED_Y*innerHeight)+'px';
  }

  function render(msg){
    if(!msg?.players)return;lastMsg=msg;lastRx=Date.now();
    const now=Date.now(),p=msg.players[focus]||{},h=updateHold(focus,p,now),display=h?.p||null;
    positionAnchor(p);label.textContent=focus;point.className='wof-point';
    alerts.textContent='';
    const xs=XSTATE[focus];status.textContent=focus+' · 固定Y '+Math.round(FIXED_Y*100)+'% · '+(xs?.calibrated?'X已校准':'F7校准X');
    if(!display||!h||h.level<1)return;

    const box=document.createElement('div');box.className='wof-alert '+(h.level>=3?'l3':h.level===2?'l2':'l1');
    const main=document.createElement('div');main.className='wof-main';
    if(h.level>=3){
      main.textContent=glyph(display.action)+' '+actionText(display.action);
    }else{
      main.textContent='⚠ 注意';
    }
    box.appendChild(main);

    const t=heldTime(h,now),time=document.createElement('div');time.className='wof-time';
    if(h.level>=3){
      time.textContent=t!=null?(t>=1000?'约 '+(t/1000).toFixed(1)+' 秒':'约 '+t+' ms'):'立即';
    }else{
      time.textContent=t!=null?(t>=1000?'约 '+(t/1000).toFixed(1)+' 秒':'约 '+t+' ms'):'保持注意';
    }
    box.appendChild(time);

    if(detail){
      const sub=document.createElement('div');sub.className='wof-sub';
      sub.textContent=[focus,display.source,display.family,display.type!=null?'T'+display.type:null].filter(Boolean).join(' · ');box.appendChild(sub);
    }
    const bar=document.createElement('div');bar.className='wof-bar';bar.style.width=(t==null?100:Math.max(6,Math.min(100,100*(1-t/1200))))+'%';box.appendChild(bar);
    alerts.appendChild(box);
  }
  bc.onmessage=e=>{const m=e.data;if(m?.schema==='wof-hud-v1'&&m.kind==='state')render(m);};

  function armCal(){calibrating=true;root.classList.add('wof-calibrating');root.style.pointerEvents='auto';calTip.textContent='点击 '+focus+' 人物或头顶原生'+focus+'字样，只校准X轴';return true;}
  function cancelCal(){calibrating=false;root.classList.remove('wof-calibrating');root.style.pointerEvents='none';return true;}
  function calibrateAt(clientX){
    const p=lastMsg?.players?.[focus],wx=finite(p?.x);if(wx==null)return false;
    const W=innerWidth,x=clamp(clientX,75,W-75),ratio=x/W;
    XSTATE[focus]={screenX:x,lastWorldX:wx,calibrated:true,ratio};saveRatio(focus,ratio);cancelCal();
    if(lastMsg)render(lastMsg);console.log('🎯 '+focus+' X轴已校准',Math.round(ratio*100)+'%');return true;
  }
  function click(e){if(!calibrating)return;if(calibrateAt(e.clientX)){e.preventDefault();e.stopPropagation();}}
  root.addEventListener('click',click,true);

  function setFocus(name){
    if(!['P1','P2','P3'].includes(name))return focus;
    focus=name;HOLD.P1=HOLD.P2=HOLD.P3=null;cancelCal();
    const p=lastMsg?.players?.[focus],wx=finite(p?.x),ratio=savedRatio(focus);
    XSTATE[focus]=wx!=null?{screenX:(ratio??.5)*innerWidth,lastWorldX:wx,calibrated:ratio!=null,ratio:ratio??.5}:null;
    if(lastMsg)render(lastMsg);console.log('🎯 HUD 只显示',focus);return focus;
  }
  function cycle(){return setFocus(focus==='P1'?'P2':focus==='P2'?'P3':'P1');}
  function key(e){
    if(e.code==='F6'){e.preventDefault();cycle();}
    else if(e.code==='F7'){e.preventDefault();armCal();}
    else if(e.code==='F8'){e.preventDefault();visible=!visible;root.classList.toggle('wof-hidden',!visible);}
    else if(e.code==='F9'){e.preventDefault();detail=!detail;if(lastMsg)render(lastMsg);}
  }
  addEventListener('keydown',key,true);

  function layout(){
    if(destroyed)return;root.classList.toggle('wof-hidden',!visible);anchor.style.top=(FIXED_Y*innerHeight)+'px';
    if(lastMsg)positionAnchor(lastMsg.players?.[focus]||{});
    requestAnimationFrame(layout);
  }
  requestAnimationFrame(layout);

  window.WOFHUD={
    version:'hud-overlay-v9-monochrome-text-directions',
    show(){visible=true;return true;},hide(){visible=false;return true;},toggle(){visible=!visible;return visible;},
    detail(on=!detail){detail=!!on;if(lastMsg)render(lastMsg);return detail;},
    focus:setFocus,p1(){return setFocus('P1');},p2(){return setFocus('P2');},p3(){return setFocus('P3');},cycle,
    y(v){if(v==null)return FIXED_Y;FIXED_Y=clamp(+v||.28,.10,.70);if(lastMsg)render(lastMsg);return FIXED_Y;},
    calibrate:armCal,
    resetX(){try{localStorage.removeItem(ratioKey(focus));}catch(_){};XSTATE[focus]=null;if(lastMsg)render(lastMsg);return true;},
    status(){return {visible,detail,focus,fixedY:FIXED_Y,x:XSTATE[focus],lastRx,lastMsg,hold:HOLD[focus]};},
    destroy(){destroyed=true;removeEventListener('keydown',key,true);root.removeEventListener('click',click,true);try{bc.close();}catch(_){};root.remove();style.remove();delete window.WOFHUD;}
  };
  root.style.pointerEvents='none';
  console.log('✅ WOF HUD overlay v9 monochrome text directions started');
  console.log('⚠ 不再用颜色表达危险等级：普通风险统一显示“注意”，动作只看箭头/文字。');
  console.log('↕↔ 支持 ↑上 / ↓下 / ←左 / →右 / AB 显示；当前预测核心若只输出上下，则绝不乱猜左右。');
  console.log('🎯 F7点人物校准X；Y固定。F6切P1/P2/P3。');
})();
