(()=>{
'use strict';
try{self.WOFTARGET?.stop?.();}catch(_){}
const M=_0x515056?.HEAPU8,R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM base unavailable');
const P1=0xFFBE1C,POOL=0xFFC0BC,STRIDE=0xE0,N=20,TICK=40;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const S16=a=>{const v=U16(a);return v&0x8000?v-0x10000:v;};
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const W=v=>v/65536,clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const hx=v=>'0x'+(v&0xffff).toString(16).toUpperCase().padStart(4,'0');
function p1(){return B(P1)?{x:W(S32(P1+4)),y:W(S32(P1+8)),hp:B(P1+0x83)}:null;}
function actor(slot){const b=POOL+slot*STRIDE;if(!B(b))return null;return{slot,base:b,type:U16(b+0x20),x:W(S32(b+4)),y:W(S32(b+8)),attack:U16(b+0x70)};}
const lowObj=new Map([[P1&0xffff,{kind:'P1',slot:-1}]]);for(let i=0;i<N;i++)lowObj.set((POOL+i*STRIDE)&0xffff,{kind:'ENEMY',slot:i});
const H=Array.from({length:N},()=>({last:null,dist:null,ema:0,lastMoveAt:0,lastFocusAt:0,target:false}));
const PH=['APPROACH','ACTIVE','HOLD','IDLE'];
const word=Array.from({length:STRIDE/2},()=>({phase:Object.fromEntries(PH.map(p=>[p,{n:0,p1:0,enemy:0,other:0}])),changes:0,last:Array(N).fill(null)}));
const pair32=Array.from({length:STRIDE-7},()=>({phase:Object.fromEntries(PH.map(p=>[p,[0,0]]))}));
const pair16=Array.from({length:STRIDE-3},()=>({phase:Object.fromEntries(PH.map(p=>[p,[0,0]]))}));
let running=true,timer=null,samples=0,startedAt=Date.now();
function infer(slot,o,p,now){const h=H[slot];if(!p){h.target=false;h.last={x:o.x,y:o.y};return h;}const d=Math.hypot(p.x-o.x,p.y-o.y);if(h.last){const mx=o.x-h.last.x,my=o.y-h.last.y,m=Math.hypot(mx,my);let q=0;if(m>=.08&&d>=1){const dx=p.x-o.x,dy=p.y-o.y;const align=(mx*dx+my*dy)/(m*d),gain=h.dist==null?0:(h.dist-d)/Math.max(.08,m);q=.65*clamp(align,-1,1)+.35*clamp(gain,-1,1);h.lastMoveAt=now;}h.ema=h.ema*.82+q*.18;}h.dist=d;h.last={x:o.x,y:o.y};if(h.ema>=.28){h.target=true;h.lastFocusAt=now;}else if(now-h.lastFocusAt>800)h.target=false;return h;}
function phase(o,h,now){if(o.attack)return'ACTIVE';const mv=now-h.lastMoveAt<180;if(h.target&&mv)return'APPROACH';if(h.target&&now-h.lastFocusAt<650)return'HOLD';return'IDLE';}
function near(a,b,t=3){return Number.isFinite(a)&&Math.abs(a-b)<=t;}
function tick(){if(!running)return;const now=Date.now(),p=p1();for(let slot=0;slot<N;slot++){const o=actor(slot);if(!o){H[slot]={last:null,dist:null,ema:0,lastMoveAt:0,lastFocusAt:0,target:false};continue;}const h=infer(slot,o,p,now),ph=phase(o,h,now),b=o.base;
  for(let off=0;off<=STRIDE-2;off+=2){const s=word[off>>1],v=U16(b+off),r=s.phase[ph];r.n++;const obj=lowObj.get(v);if(obj?.kind==='P1')r.p1++;else if(obj?.kind==='ENEMY')r.enemy++;else r.other++;const prev=s.last[slot];if(prev!==null&&prev!==v)s.changes++;s.last[slot]=v;}
  if(p){for(let off=0;off<=STRIDE-8;off+=2){const r=pair32[off].phase[ph];r[1]++;const x=W(S32(b+off)),y=W(S32(b+off+4));if(near(x,p.x,4)&&near(y,p.y,4))r[0]++;}
    for(let off=0;off<=STRIDE-4;off+=2){const r=pair16[off].phase[ph];r[1]++;const x=S16(b+off),y=S16(b+off+2);if(near(x,p.x,4)&&near(y,p.y,4))r[0]++;}}
}samples++;}
const pct=(a,b)=>b?+(a/b).toFixed(3):0;
function handles(){const rows=[];for(let i=0;i<word.length;i++){const off=i*2,s=word[i],a=s.phase.APPROACH,ac=s.phase.ACTIVE,h=s.phase.HOLD,id=s.phase.IDLE;const ar=pct(a.p1,a.n),acr=pct(ac.p1,ac.n),hr=pct(h.p1,h.n),ir=pct(id.p1,id.n),enemyA=pct(a.enemy,a.n);if(a.p1+ac.p1+h.p1<3)continue;const score=ar*4+acr*2+hr*1.5-ir*1.5-enemyA*3;rows.push({offset:'0x'+off.toString(16).toUpperCase(),approachP1:ar,activeP1:acr,holdP1:hr,idleP1:ir,approachEnemy:enemyA,changes:s.changes,score:+score.toFixed(3)});}rows.sort((a,b)=>b.score-a.score);console.table(rows.slice(0,20));return rows.slice(0,40);}
function coords32(){const rows=[];for(let off=0;off<pair32.length;off+=2){if(off===4||off===8)continue;const s=pair32[off].phase,a=pct(...s.APPROACH),ac=pct(...s.ACTIVE),h=pct(...s.HOLD),id=pct(...s.IDLE);if(s.APPROACH[0]+s.ACTIVE[0]+s.HOLD[0]<3)continue;const score=a*4+ac*2+h*1.5-id*2;rows.push({offset:'0x'+off.toString(16).toUpperCase(),approachXY:a,activeXY:ac,holdXY:h,idleXY:id,score:+score.toFixed(3)});}rows.sort((a,b)=>b.score-a.score);console.table(rows.slice(0,20));return rows.slice(0,40);}
function coords16(){const rows=[];for(let off=0;off<pair16.length;off+=2){const s=pair16[off].phase,a=pct(...s.APPROACH),ac=pct(...s.ACTIVE),h=pct(...s.HOLD),id=pct(...s.IDLE);if(s.APPROACH[0]+s.ACTIVE[0]+s.HOLD[0]<3)continue;const score=a*4+ac*2+h*1.5-id*2;rows.push({offset:'0x'+off.toString(16).toUpperCase(),approachXY:a,activeXY:ac,holdXY:h,idleXY:id,score:+score.toFixed(3)});}rows.sort((a,b)=>b.score-a.score);console.table(rows.slice(0,20));return rows.slice(0,40);}
function live(){const now=Date.now(),p=p1(),rows=[];for(let slot=0;slot<N;slot++){const o=actor(slot);if(!o)continue;const h=H[slot],ph=phase(o,h,now);rows.push({slot,type:o.type,phase:ph,focusMotion:h.target,score:+h.ema.toFixed(2),attack:o.attack,dx:p?+(o.x-p.x).toFixed(1):null,dy:p?+(o.y-p.y).toFixed(1):null,o3A:hx(U16(o.base+0x3A)),o68:hx(U16(o.base+0x68)),o6A:hx(U16(o.base+0x6A)),o86:hx(U16(o.base+0x86))});}console.table(rows);return rows;}
function result(){console.log('=== 16-bit object-handle candidates ===');const h=handles();console.log('=== target XY candidates: 32-bit 16.16 pairs ===');const c32=coords32();console.log('=== target XY candidates: 16-bit integer pairs ===');const c16=coords16();console.log('=== current enemies ===');const l=live();return{version:'enemy-target-probe-v5-handle-coord',running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),handles:h,coord32:c32,coord16:c16,live:l};}
timer=setInterval(tick,TICK);tick();
self.WOFTARGET={version:'enemy-target-probe-v5-handle-coord',result,handles,coords32,coords16,live,status(){return{running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1)}},stop(){running=false;if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF target probe stopped');}};
console.log('✅ WOF target probe v5 started · handle + target-coordinate scan');
console.log('🎯 单打30~60秒：让怪出现原地、追你、上下绕路、近身停顿、攻击，然后 WOFTARGET.result()');
})();