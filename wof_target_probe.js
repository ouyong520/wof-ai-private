(()=>{
'use strict';
try{self.WOFTARGET?.stop?.();}catch(_){}
const M=_0x515056?.HEAPU8,R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM base unavailable');
const PLAYERS={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC},PN=['P1','P2','P3'];
const POOL=0xFFC0BC,STRIDE=0xE0,NSLOTS=20,TICK=80;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const W=v=>v/65536;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const player=name=>{const b=PLAYERS[name];if(!B(b))return null;return{name,x:W(S32(b+4)),y:W(S32(b+8)),z:W(S32(b+12))};};
const actor=slot=>{const b=POOL+slot*STRIDE;if(!B(b))return null;return{slot,base:b,type:U16(b+0x20),x:W(S32(b+4)),y:W(S32(b+8)),z:W(S32(b+12)),face:B(b+0x16),s0:B(b+0x28),s1:B(b+0x29),s2:B(b+0x2A),s3:B(b+0x2B),anim:U32(b+0x2C),timer:U16(b+0x34),vx:W(S32(b+0x40)),vy:W(S32(b+0x44)),attack:U16(b+0x70)};};

// Locate the exact wofr1 68000 execution ROM already loaded by the emulator.
const sig1Off=0x100,sig1=[0x23,0xFC,0x00,0x00,0x03,0x86,0x00,0xFF,0x00,0x08,0x60,0x00,0x00,0x82];
const sig2Off=0x426,sig2=[0x4B,0xF8,0x80,0x00,0x20,0x7C,0x00,0xFF,0x00,0x00,0x30,0x3C,0x3F,0xFF];
const matchAt=(p,s)=>{if(p<0||p+s.length>M.length)return false;for(let i=0;i<s.length;i++)if(M[p+i]!==s[i])return false;return true;};
const findRom=()=>{let p=0;while((p=M.indexOf(sig1[0],p))>=0){const base=p-sig1Off;if(base>=0&&matchAt(p,sig1)&&matchAt(base+sig2Off,sig2))return base;p++;}return -1;};
const romBase=findRom();
function romRefs(){
  if(romBase<0)return {romBase:null,refs:[]};
  const refs=[];
  for(const n of PN){const v=PLAYERS[n]>>>0,b0=(v>>>24)&255,b1=(v>>>16)&255,b2=(v>>>8)&255,b3=v&255;let hits=0;
    for(let a=0;a<0x100000-4;a++)if(M[romBase+a]===b0&&M[romBase+a+1]===b1&&M[romBase+a+2]===b2&&M[romBase+a+3]===b3){
      const s=Math.max(0,a-12),e=Math.min(0x100000,a+16),hex=Array.from(M.slice(romBase+s,romBase+e),x=>x.toString(16).padStart(2,'0').toUpperCase()).join(' ');
      refs.push({player:n,address:'0x'+v.toString(16).toUpperCase(),romOffset:'0x'+a.toString(16).toUpperCase(),context:hex});if(++hits>=40)break;
    }
  }
  return {romBase:'0x'+romBase.toString(16),refs};
}

const hist=Array.from({length:NSLOTS},()=>({last:null,dist:{},ema:{P1:0,P2:0,P3:0},target:null,confidence:0,margin:0,lastMotionAt:0,lastFocusAt:0}));
const direct32=new Map(),direct16=new Map();
let samples=0,running=true,timer=null,startedAt=Date.now(),maxLivePlayers=0;
function addDirect(map,off,name){const k=off+'|'+name;map.set(k,(map.get(k)||0)+1);}
function scanPointers(base){for(let off=0;off<=STRIDE-4;off+=2){const v=U32(base+off);for(const n of PN)if(v===PLAYERS[n])addDirect(direct32,off,n);}for(let off=0;off<=STRIDE-2;off+=2){const v=U16(base+off);for(const n of PN)if(v===(PLAYERS[n]&0xffff))addDirect(direct16,off,n);}}

function infer(slot,o,ps,now){
  const h=hist[slot],prev=h.last;let best=null,bestScore=-9,second=-9;
  if(prev){
    const mx=o.x-prev.x,my=o.y-prev.y,move=Math.hypot(mx,my);
    for(const n of PN){const p=ps[n];if(!p)continue;const dx=p.x-o.x,dy=p.y-o.y,d=Math.hypot(dx,dy),pd=h.dist[n];let instant=0;
      if(move>=0.10&&d>=1){const align=(mx*dx+my*dy)/(move*d);const gain=pd==null?0:(pd-d)/Math.max(.10,move);instant=.62*clamp(align,-1,1)+.38*clamp(gain,-1,1);h.lastMotionAt=now;}
      h.ema[n]=h.ema[n]*.80+instant*.20;h.dist[n]=d;
    }
    const live=PN.filter(n=>ps[n]);
    for(const n of live){const s=h.ema[n];if(s>bestScore){second=bestScore;bestScore=s;best=n;}else if(s>second)second=s;}
    // Solo mode: there is no competing player, so confidence means "is this enemy actually converging on P1", not identity certainty.
    let conf;
    if(live.length===1)conf=clamp((bestScore+.05)/.75,0,1);
    else{const margin=bestScore-second;conf=clamp((bestScore+.2)/1.05,0,1)*clamp((margin+.05)/.55,0,1);h.margin=margin;}
    if(best&&conf>=.35){h.target=best;h.confidence=conf;h.lastFocusAt=now;}
    else if(now-h.lastFocusAt>900){h.target=null;h.confidence=0;h.margin=0;}
  }
  h.last={x:o.x,y:o.y};return h;
}
function intentOf(o,h,now){
  if(o.attack!==0)return 'ACTIVE';
  const moving=Math.hypot(o.vx,o.vy)>=1.5 || (h.last&&now-h.lastMotionAt<240);
  if(h.target&&h.confidence>=.55&&moving)return 'APPROACH';
  if(h.target&&now-h.lastFocusAt<700)return 'FOCUS-HOLD';
  return moving?'MOVE-OTHER':'IDLE/UNKNOWN';
}

function tick(){if(!running)return;const now=Date.now(),ps=Object.fromEntries(PN.map(n=>[n,player(n)]));maxLivePlayers=Math.max(maxLivePlayers,PN.filter(n=>ps[n]).length);for(let slot=0;slot<NSLOTS;slot++){const o=actor(slot);if(!o){hist[slot]={last:null,dist:{},ema:{P1:0,P2:0,P3:0},target:null,confidence:0,margin:0,lastMotionAt:0,lastFocusAt:0};continue;}infer(slot,o,ps,now);scanPointers(o.base);}samples++;}
function live(){const now=Date.now(),rows=[];for(let slot=0;slot<NSLOTS;slot++){const o=actor(slot);if(!o)continue;const h=hist[slot];rows.push({slot,type:o.type,intent:intentOf(o,h,now),focus:h.target,confidence:+h.confidence.toFixed(2),attack:o.attack,x:+o.x.toFixed(1),y:+o.y.toFixed(1),vx:+o.vx.toFixed(1),vy:+o.vy.toFixed(1),state:[o.s0,o.s1,o.s2,o.s3].join('/'),anim:o.anim,timer:o.timer});}console.table(rows);return rows;}
function directRows(map,kind){const by=new Map();for(const [k,count] of map){const [offS,name]=k.split('|'),off=+offS;let r=by.get(off);if(!r){r={kind,offset:'0x'+off.toString(16).toUpperCase(),P1:0,P2:0,P3:0,total:0};by.set(off,r);}r[name]+=count;r.total+=count;}return [...by.values()].sort((a,b)=>b.total-a.total);}
function result(limit=24){const p32=directRows(direct32,'ptr32').slice(0,limit),p16=directRows(direct16,'ptr16').slice(0,limit),rr=romRefs();console.log('=== direct player-pointer candidates inside enemy struct ===');console.table(p32);console.table(p16);console.log('=== current enemy focus / intent (solo-compatible) ===');const l=live();console.log('=== ROM absolute player-address references ===');console.table(rr.refs.map(x=>({player:x.player,romOffset:x.romOffset,address:x.address})));return{version:'enemy-target-probe-v2-solo',running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),maxLivePlayers,romBase:rr.romBase,direct32:p32,direct16:p16,romRefs:rr.refs,live:l};}

timer=setInterval(tick,TICK);tick();
self.WOFTARGET={version:'enemy-target-probe-v2-solo',live,result,rom(){const r=romRefs();console.table(r.refs);return r;},status(){return{running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),maxLivePlayers,romBase:romBase<0?null:'0x'+romBase.toString(16)}},stop(){running=false;if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF target probe stopped');}};
console.log('✅ WOF enemy target/focus probe v2 started · solo compatible');
console.log('🎯 单打即可：让小怪出现“原地/倒地起身/追你/上下绕路/进入攻击”的过程，30~60秒后运行 WOFTARGET.result()');
})();