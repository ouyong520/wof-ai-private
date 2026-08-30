(()=>{
'use strict';
try{self.WOFTARGET?.stop?.();}catch(_){}
const M=_0x515056?.HEAPU8,R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM base unavailable');
const PLAYERS={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC},PN=['P1','P2','P3'];
const POOL=0xFFC0BC,STRIDE=0xE0,NSLOTS=20,TICK=40;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const W=v=>v/65536;
const hex=(v,n=8)=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(n,'0');
const norm24=v=>v&0xFFFFFF;
const ptrName=v=>PN.find(n=>norm24(v)===PLAYERS[n])||'';
function player(n){const b=PLAYERS[n];return B(b)?{name:n,x:W(S32(b+4)),y:W(S32(b+8)),hp:B(b+0x83)}:null;}
function actor(slot){const b=POOL+slot*STRIDE;if(!B(b))return null;return{slot,base:b,type:U16(b+0x20),x:W(S32(b+4)),y:W(S32(b+8)),attack:U16(b+0x70)};}

const PTR=Array.from({length:STRIDE-3},()=>({samples:0,P1:0,P2:0,P3:0,other:0,changes:0,last:Array(NSLOTS).fill(null),phase:{APPROACH:[0,0],ACTIVE:[0,0],HOLD:[0,0],IDLE:[0,0]}}));
const H=Array.from({length:NSLOTS},()=>({last:null,dist:null,ema:0,lastMoveAt:0,lastFocusAt:0,target:false}));
const EVENTS=[];let running=true,timer=null,samples=0,startedAt=Date.now(),maxLivePlayers=0;
function infer(slot,o,p1,now){const h=H[slot];if(!p1){h.target=false;h.last={x:o.x,y:o.y};return h;}const d=Math.hypot(p1.x-o.x,p1.y-o.y);if(h.last){const mx=o.x-h.last.x,my=o.y-h.last.y,move=Math.hypot(mx,my);let q=0;if(move>=.08&&d>=1){const dx=p1.x-o.x,dy=p1.y-o.y;const align=(mx*dx+my*dy)/(move*d),gain=h.dist==null?0:(h.dist-d)/Math.max(.08,move);q=.65*Math.max(-1,Math.min(1,align))+.35*Math.max(-1,Math.min(1,gain));h.lastMoveAt=now;}h.ema=h.ema*.82+q*.18;}h.dist=d;h.last={x:o.x,y:o.y};if(h.ema>=.28){h.target=true;h.lastFocusAt=now;}else if(now-h.lastFocusAt>800)h.target=false;return h;}
function phase(o,h,now){if(o.attack)return'ACTIVE';const moving=now-h.lastMoveAt<180;if(h.target&&moving)return'APPROACH';if(h.target&&now-h.lastFocusAt<650)return'HOLD';return'IDLE';}
function bump(off,slot,v,ph){const s=PTR[off],n=ptrName(v);s.samples++;if(n)s[n]++;else s.other++;if(s.phase[ph]){s.phase[ph][1]++;if(n==='P1')s.phase[ph][0]++;}const prev=s.last[slot];if(prev!==null&&prev!==v){s.changes++;if((n||ptrName(prev))&&EVENTS.length<400)EVENTS.push({t:+((Date.now()-startedAt)/1000).toFixed(2),slot,offset:'0x'+off.toString(16).toUpperCase(),from:hex(prev),to:hex(v),fromPlayer:ptrName(prev),toPlayer:n,phase:ph});}s.last[slot]=v;}
function tick(){if(!running)return;const now=Date.now(),p1=player('P1'),live=PN.filter(n=>player(n));maxLivePlayers=Math.max(maxLivePlayers,live.length);for(let slot=0;slot<NSLOTS;slot++){const o=actor(slot);if(!o){H[slot]={last:null,dist:null,ema:0,lastMoveAt:0,lastFocusAt:0,target:false};continue;}const h=infer(slot,o,p1,now),ph=phase(o,h,now);for(let off=0;off<=STRIDE-4;off+=2)bump(off,slot,U32(o.base+off),ph);}samples++;}
const pct=(a,b)=>b?+(a/b).toFixed(3):null;
function summary(){const rows=[];for(let off=0;off<=STRIDE-4;off+=2){const s=PTR[off],hits=s.P1+s.P2+s.P3;if(!hits)continue;const a=pct(s.phase.APPROACH[0],s.phase.APPROACH[1]),ac=pct(s.phase.ACTIVE[0],s.phase.ACTIVE[1]),h=pct(s.phase.HOLD[0],s.phase.HOLD[1]),i=pct(s.phase.IDLE[0],s.phase.IDLE[1]);const bad=s.P2+s.P3;let score=(a||0)*3+(ac||0)*2+(h||0)-(bad/Math.max(1,hits))*5;rows.push({offset:'0x'+off.toString(16).toUpperCase(),samples:s.samples,P1:s.P1,P2:s.P2,P3:s.P3,other:s.other,approachP1:a,activeP1:ac,holdP1:h,idleP1:i,changes:s.changes,score:+score.toFixed(3)});}rows.sort((a,b)=>b.score-a.score||b.P1-a.P1);console.table(rows);return rows;}
function live(){const now=Date.now(),p1=player('P1'),rows=[];for(let slot=0;slot<NSLOTS;slot++){const o=actor(slot);if(!o)continue;const h=H[slot],ph=phase(o,h,now),p38=U32(o.base+0x38),p68=U32(o.base+0x68);rows.push({slot,type:o.type,phase:ph,focusMotion:h.target,score:+h.ema.toFixed(2),attack:o.attack,dx:p1?+(o.x-p1.x).toFixed(1):null,dy:p1?+(o.y-p1.y).toFixed(1):null,p38:hex(p38),p38Player:ptrName(p38),p68:hex(p68),p68Player:ptrName(p68)});}console.table(rows);return rows;}
function result(){console.log('=== normalized 24-bit player pointer candidates ===');const s=summary();console.log('=== current enemies / suspected pointers ===');const l=live();console.log('=== player-pointer transitions ===');console.table(EVENTS.slice(-60));return{version:'enemy-target-probe-v4-pointer24',running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),maxLivePlayers,summary:s,live:l,events:EVENTS.slice(-100)};}
timer=setInterval(tick,TICK);tick();
self.WOFTARGET={version:'enemy-target-probe-v4-pointer24',result,summary,live,events(){console.table(EVENTS.slice(-100));return EVENTS.slice(-100);},status(){return{running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),maxLivePlayers}},stop(){running=false;if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF target probe stopped');}};
console.log('✅ WOF target probe v4 started · normalized 24-bit pointers');
console.log('🎯 单打即可，重点验证 enemy+0x38 是否直接保存 0x00FFBE1C(P1)。玩20~40秒后 WOFTARGET.result()');
})();