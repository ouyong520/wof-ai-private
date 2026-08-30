(()=>{
'use strict';
try{self.WOFTARGET?.stop?.();}catch(_){}
const M=_0x515056?.HEAPU8,R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM base unavailable');
const PLAYERS={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC},PN=['P1','P2','P3'];
const LOW=Object.fromEntries(PN.map(n=>[n,PLAYERS[n]&0xffff]));
const LOWNAME=new Map(PN.map(n=>[LOW[n],n]));
const POOL=0xFFC0BC,STRIDE=0xE0,NSLOTS=20,TICK=50;
const CAND=[0x3A,0x68,0x6A,0x86];
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const W=v=>v/65536;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function player(n){const b=PLAYERS[n];if(!B(b))return null;return{name:n,x:W(S32(b+4)),y:W(S32(b+8)),z:W(S32(b+12)),hp:B(b+0x83)};}
function actor(slot){const b=POOL+slot*STRIDE;if(!B(b))return null;return{slot,base:b,type:U16(b+0x20),x:W(S32(b+4)),y:W(S32(b+8)),z:W(S32(b+12)),face:B(b+0x16),s0:B(b+0x28),s1:B(b+0x29),s2:B(b+0x2A),s3:B(b+0x2B),anim:U32(b+0x2C),timer:U16(b+0x34),vx:W(S32(b+0x40)),vy:W(S32(b+0x44)),attack:U16(b+0x70)};}

const H=Array.from({length:NSLOTS},()=>({last:null,dist:null,ema:0,lastMoveAt:0,lastFocusAt:0,target:false}));
const ST=Object.fromEntries(CAND.map(off=>[off,{samples:0,p1:0,p2:0,p3:0,other:0,p1Live:0,p1Absent:0,p2Inactive:0,p3Inactive:0,approach:0,approachP1:0,active:0,activeP1:0,hold:0,holdP1:0,idle:0,idleP1:0,changes:0,lastBySlot:Array(NSLOTS).fill(null)}]));
const EVENTS=[];
let running=true,timer=null,samples=0,startedAt=Date.now(),maxLivePlayers=0;

function inferP1(slot,o,p1,now){const h=H[slot];if(!p1){h.last={x:o.x,y:o.y};h.dist=null;h.ema*=.8;h.target=false;return h;}
  const d=Math.hypot(p1.x-o.x,p1.y-o.y);if(h.last){const mx=o.x-h.last.x,my=o.y-h.last.y,move=Math.hypot(mx,my);let instant=0;if(move>=.08&&d>=1){const dx=p1.x-o.x,dy=p1.y-o.y;const align=(mx*dx+my*dy)/(move*d);const gain=h.dist==null?0:(h.dist-d)/Math.max(.08,move);instant=.65*clamp(align,-1,1)+.35*clamp(gain,-1,1);h.lastMoveAt=now;}h.ema=h.ema*.82+instant*.18;}
  h.dist=d;h.last={x:o.x,y:o.y};if(h.ema>=.28){h.target=true;h.lastFocusAt=now;}else if(now-h.lastFocusAt>800)h.target=false;return h;}
function phase(o,h,now){if(o.attack)return'ACTIVE';const moving=Math.hypot(o.vx,o.vy)>=1.2||now-h.lastMoveAt<180;if(h.target&&moving)return'APPROACH';if(h.target&&now-h.lastFocusAt<650)return'HOLD';return moving?'MOVE-OTHER':'IDLE';}
function bump(off,slot,val,ph,live){const s=ST[off],name=LOWNAME.get(val);s.samples++;if(name)s[name.toLowerCase()]++;else s.other++;
  if(name==='P1'){if(live.P1)s.p1Live++;else s.p1Absent++;}if(name==='P2'&&!live.P2)s.p2Inactive++;if(name==='P3'&&!live.P3)s.p3Inactive++;
  if(ph==='APPROACH'){s.approach++;if(name==='P1')s.approachP1++;}else if(ph==='ACTIVE'){s.active++;if(name==='P1')s.activeP1++;}else if(ph==='HOLD'){s.hold++;if(name==='P1')s.holdP1++;}else if(ph==='IDLE'){s.idle++;if(name==='P1')s.idleP1++;}
  const prev=s.lastBySlot[slot];if(prev!==null&&prev!==val){s.changes++;if(EVENTS.length<300)EVENTS.push({t:+((Date.now()-startedAt)/1000).toFixed(2),slot,offset:'0x'+off.toString(16).toUpperCase(),from:'0x'+prev.toString(16).toUpperCase(),to:'0x'+val.toString(16).toUpperCase(),toPlayer:name||'',phase:ph});}s.lastBySlot[slot]=val;}
function tick(){if(!running)return;const now=Date.now(),ps=Object.fromEntries(PN.map(n=>[n,player(n)])),live=Object.fromEntries(PN.map(n=>[n,!!ps[n]]));maxLivePlayers=Math.max(maxLivePlayers,PN.filter(n=>live[n]).length);
  for(let slot=0;slot<NSLOTS;slot++){const o=actor(slot);if(!o){H[slot]={last:null,dist:null,ema:0,lastMoveAt:0,lastFocusAt:0,target:false};continue;}const h=inferP1(slot,o,ps.P1,now),ph=phase(o,h,now);for(const off of CAND)bump(off,slot,U16(o.base+off),ph,live);}samples++;}
function pct(a,b){return b?+(a/b).toFixed(3):null;}
function summary(){const rows=CAND.map(off=>{const s=ST[off];const bad=s.p2Inactive+s.p3Inactive+s.p1Absent;const approach=pct(s.approachP1,s.approach),active=pct(s.activeP1,s.active),hold=pct(s.holdP1,s.hold),idle=pct(s.idleP1,s.idle);let score=0;score+=(approach??0)*3+(active??0)*2+(hold??0)*1;score-=pct(bad,s.samples)*4;score-=Math.max(0,(idle??0)-.35)*1.5;return{offset:'0x'+off.toString(16).toUpperCase(),samples:s.samples,P1:s.p1,P2:s.p2,P3:s.p3,other:s.other,approachP1:approach,activeP1:active,holdP1:hold,idleP1:idle,inactiveRefs:bad,changes:s.changes,score:+score.toFixed(3)};}).sort((a,b)=>b.score-a.score);console.table(rows);return rows;}
function live(){const now=Date.now(),p1=player('P1'),rows=[];for(let slot=0;slot<NSLOTS;slot++){const o=actor(slot);if(!o)continue;const h=H[slot],ph=phase(o,h,now);const r={slot,type:o.type,phase:ph,focusP1:h.target,focusScore:+h.ema.toFixed(2),attack:o.attack,x:+o.x.toFixed(1),y:+o.y.toFixed(1),dx:p1?+(o.x-p1.x).toFixed(1):null,dy:p1?+(o.y-p1.y).toFixed(1):null};for(const off of CAND){const v=U16(o.base+off),n=LOWNAME.get(v);r['o'+off.toString(16).toUpperCase()]=n||('0x'+v.toString(16).toUpperCase());}rows.push(r);}console.table(rows);return rows;}
function result(){console.log('=== focus offset validation ===');const sum=summary();console.log('=== current enemies ===');const l=live();console.log('=== latest candidate transitions ===');console.table(EVENTS.slice(-40));return{version:'enemy-target-probe-v3-focus-offsets',running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),maxLivePlayers,summary:sum,live:l,events:EVENTS.slice(-80)};}
timer=setInterval(tick,TICK);tick();
self.WOFTARGET={version:'enemy-target-probe-v3-focus-offsets',result,summary,live,events(){console.table(EVENTS.slice(-80));return EVENTS.slice(-80);},status(){return{running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),maxLivePlayers}},stop(){running=false;if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF target probe stopped');}};
console.log('✅ WOF target probe v3 started · solo focus-offset validation');
console.log('🎯 单打 30~60 秒：让怪经历倒地/起身/追你/上下绕路/近身停顿/攻击，然后运行 WOFTARGET.result()');
})();