(()=>{
'use strict';
try{self.WOFTARGETXY?.stop?.();}catch(_){}
const MOD=_0x515056,M=MOD?.HEAPU8,R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM unavailable');
const PLAYERS=[{name:'P1',base:0xFFBE1C},{name:'P2',base:0xFFBEFC},{name:'P3',base:0xFFBFDC}],POOL=0xFFC0BC,STRIDE=0xE0,N=20,TICK=40,DURATION=42000;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0,U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S16=a=>{const v=U16(a);return v&0x8000?v-0x10000:v;},S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;},F=v=>v/65536;
const hx=v=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(4,'0'),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const player=p=>B(p.base)?{name:p.name,base:p.base,x:F(S32(p.base+4)),y:F(S32(p.base+8)),z:F(S32(p.base+12))}:null;
const actor=i=>{const b=POOL+i*STRIDE;if(!B(b))return null;return{slot:i,base:b,type:U16(b+0x20),x:F(S32(b+4)),y:F(S32(b+8)),z:F(S32(b+12))};};
const OFFS=[];for(let off=0x10;off<=STRIDE-8;off+=2)OFFS.push(off);
const formats=[
 {kind:'xy16',read:(b,o)=>({x:S16(b+o),y:S16(b+o+2)})},
 {kind:'xy16-gap4',read:(b,o)=>({x:S16(b+o),y:S16(b+o+4)})},
 {kind:'xy32',read:(b,o)=>({x:F(S32(b+o)),y:F(S32(b+o+4))})}
];
const mk=()=>({samples:0,valid:0,motionN:0,towardSum:0,towardWins:0,selfNear:0,playerNear:0,player:{P1:0,P2:0,P3:0},switches:0,postN:0,postToward:0});
const stats=Object.fromEntries(formats.map(f=>[f.kind,OFFS.map(()=>mk())]));
const H=Array.from({length:N},()=>({last:null,lastNear:Object.fromEntries(formats.map(f=>[f.kind,Array(OFFS.length).fill(null)])),lastSwitch:Object.fromEntries(formats.map(f=>[f.kind,Array(OFFS.length).fill(0)]))}));
let running=true,timer=null,finishTimer=null,samples=0,started=Date.now();
function validPoint(p){return Number.isFinite(p.x)&&Number.isFinite(p.y)&&Math.abs(p.x)<8192&&Math.abs(p.y)<8192&&!(Math.abs(p.x)<.001&&Math.abs(p.y)<.001);}
function motionToward(prev,o,p){if(!prev)return null;const mx=o.x-prev.x,my=o.y-prev.y,m=Math.hypot(mx,my);if(m<.05)return null;const dx=p.x-o.x,dy=p.y-o.y,d=Math.hypot(dx,dy);if(d<.5)return null;const align=(mx*dx+my*dy)/(m*d),prevD=Math.hypot(p.x-prev.x,p.y-prev.y),gain=(prevD-d)/Math.max(.05,m);return .72*clamp(align,-1,1)+.28*clamp(gain,-1,1);}
function nearestPlayer(p,ps){let best=null,bd=1e9;for(const x of ps){const d=Math.hypot(p.x-x.x,p.y-x.y);if(d<bd){bd=d;best=x;}}return best&&bd<=96?{name:best.name,d:bd}:null;}
function tick(){if(!running)return;const ps=PLAYERS.map(player).filter(Boolean),now=Date.now();
 for(let i=0;i<N;i++){
  const o=actor(i),h=H[i];if(!o){H[i]={last:null,lastNear:Object.fromEntries(formats.map(f=>[f.kind,Array(OFFS.length).fill(null)])),lastSwitch:Object.fromEntries(formats.map(f=>[f.kind,Array(OFFS.length).fill(0)]))};continue;}
  for(const f of formats){const arr=stats[f.kind],lastNear=h.lastNear[f.kind],lastSwitch=h.lastSwitch[f.kind];
   for(let oi=0;oi<OFFS.length;oi++){
    const off=OFFS[oi],r=arr[oi],p=f.read(o.base,off);r.samples++;if(!validPoint(p))continue;r.valid++;
    const selfD=Math.hypot(p.x-o.x,p.y-o.y);if(selfD<=3)r.selfNear++;
    const near=nearestPlayer(p,ps);if(near){r.playerNear++;r.player[near.name]++;}
    const prevName=lastNear[oi];if(near?.name&&prevName&&near.name!==prevName){r.switches++;lastSwitch[oi]=now;}lastNear[oi]=near?.name||null;
    const mt=motionToward(h.last,o,p);if(mt!=null){r.motionN++;r.towardSum+=mt;if(mt>.05)r.towardWins++;if(now-lastSwitch[oi]<=800&&lastSwitch[oi]){r.postN++;r.postToward+=mt;}}
   }
  }
  h.last={x:o.x,y:o.y};
 }
 samples++;
}
const rate=(a,b)=>b?a/b:0;
function rank(kind){const arr=stats[kind],rows=[];for(let i=0;i<arr.length;i++){const r=arr[i];if(r.valid<40||r.motionN<20)continue;const validity=rate(r.valid,r.samples),meanToward=rate(r.towardSum,r.motionN),winRate=rate(r.towardWins,r.motionN),selfRate=rate(r.selfNear,r.valid),playerNearRate=rate(r.playerNear,r.valid),coverage=Object.values(r.player).filter(n=>n>=8).length,post=rate(r.postToward,r.postN);
  if(selfRate>.75)continue;
  const score=meanToward*3+Math.max(0,winRate-.5)*2+Math.min(.8,playerNearRate)*.8+Math.max(-.5,post)*1.8+Math.min(r.switches,24)*.02+coverage*.12-validity<.05?0:0;
  const fixedScore=meanToward*3+Math.max(0,winRate-.5)*2+Math.min(.8,playerNearRate)*.8+Math.max(-.5,post)*1.8+Math.min(r.switches,24)*.02+coverage*.12-selfRate*2;
  rows.push({offset:hx(OFFS[i]),kind,validity:+validity.toFixed(3),motionN:r.motionN,meanToward:+meanToward.toFixed(3),winRate:+winRate.toFixed(3),selfRate:+selfRate.toFixed(3),playerNearRate:+playerNearRate.toFixed(3),switches:r.switches,postN:r.postN,postSwitchToward:+post.toFixed(3),P1:r.player.P1,P2:r.player.P2,P3:r.player.P3,score:+fixedScore.toFixed(3)});
 }
 return rows.sort((a,b)=>b.score-a.score);
}
function finish(){if(!running)return self.__WOF_TARGET_XY_V3;running=false;if(timer)clearInterval(timer);if(finishTimer)clearTimeout(finishTimer);
 const all=[];for(const f of formats){const rows=rank(f.kind);console.log('=== TARGET XY '+f.kind.toUpperCase()+' CANDIDATES ===');console.table(rows.slice(0,24));all.push(...rows);}
 all.sort((a,b)=>b.score-a.score);const best=all[0];const verdict={seconds:+((Date.now()-started)/1000).toFixed(1),samples,livePlayers:PLAYERS.map(player).filter(Boolean).map(p=>p.name).join(','),candidates:all.length,topKind:best?.kind||'',topOffset:best?.offset||'',topScore:best?.score??'',topMeanToward:best?.meanToward??'',topWinRate:best?.winRate??'',topPlayerNearRate:best?.playerNearRate??'',topSwitches:best?.switches??'',topPostSwitchToward:best?.postSwitchToward??'',topSelfRate:best?.selfRate??''};
 console.log('=== TARGET XY VERDICT V3 ===');console.table([verdict]);
 if(best&&best.meanToward>.12&&best.winRate>.58&&best.selfRate<.3)console.log('🎯 高置信 target/action XY：该字段能预测怪的后续运动，下一步反查 topOffset 的 ROM 写入点。');else if(best&&best.meanToward>.05)console.warn('⚠️ 有弱到中等 XY 运动证据；下一步对 top 3 offset 做 target-switch 专项验证。');else console.warn('⚠️ enemy struct 内未找到能预测运动的稳定 XY；下一步转抓 action-state 切换瞬间的字段变化/写入时序。');
 const out={version:'wof-target-xy-v3',verdict,rows:all};self.__WOF_TARGET_XY_V3=out;return out;
}
timer=setInterval(tick,TICK);tick();finishTimer=setTimeout(finish,DURATION);self.WOFTARGETXY={version:'wof-target-xy-v3',finish,stop(){if(!running)return;running=false;if(timer)clearInterval(timer);if(finishTimer)clearTimeout(finishTimer);console.log('⛔ target XY probe stopped');},status(){return{running,seconds:+((Date.now()-started)/1000).toFixed(1),samples}}};
console.log('✅ WOF target XY probe v3 started · 42s auto-report');
console.log('期间让怪多走动、切换追击/攻击对象；42 秒后自动输出 TARGET XY VERDICT V3');
})();