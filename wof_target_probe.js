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
const actor=slot=>{const b=POOL+slot*STRIDE;if(!B(b))return null;return{slot,base:b,type:U16(b+0x20),x:W(S32(b+4)),y:W(S32(b+8)),z:W(S32(b+12)),face:B(b+0x16),attack:U16(b+0x70)};};

const hist=Array.from({length:NSLOTS},()=>({last:null,dist:{},ema:{P1:0,P2:0,P3:0},target:null,confidence:0,margin:0,lastMotionAt:0}));
const byteStats=Array.from({length:STRIDE},()=>({samples:0,byValue:new Map()}));
const direct32=new Map(),direct16=new Map();
let samples=0,running=true,timer=null,startedAt=Date.now();

function addDirect(map,off,name){const k=off+'|'+name;map.set(k,(map.get(k)||0)+1);}
function learnByte(base,target,conf){if(!target||conf<0.62)return;for(let off=0;off<STRIDE;off++){
  const v=B(base+off);if(!(v<=7||v===0xff))continue;
  const s=byteStats[off];s.samples++;let row=s.byValue.get(v);if(!row){row={P1:0,P2:0,P3:0};s.byValue.set(v,row);}row[target]++;
}}
function scanPointers(base){for(let off=0;off<=STRIDE-4;off+=2){const v=U32(base+off);for(const n of PN)if(v===PLAYERS[n])addDirect(direct32,off,n);}for(let off=0;off<=STRIDE-2;off+=2){const v=U16(base+off);for(const n of PN)if(v===(PLAYERS[n]&0xffff))addDirect(direct16,off,n);}}

function infer(slot,o,ps,now){const h=hist[slot],prev=h.last;let best=null,bestScore=-9,second=-9;
  if(prev){const mx=o.x-prev.x,my=o.y-prev.y,move=Math.hypot(mx,my);for(const n of PN){const p=ps[n];if(!p)continue;const dx=p.x-o.x,dy=p.y-o.y,d=Math.hypot(dx,dy);const pd=h.dist[n];let instant=0;
      if(move>=0.12&&d>=1){const align=(mx*dx+my*dy)/(move*d);const gain=pd==null?0:(pd-d)/Math.max(.12,move);const yGain=pd==null?0:(Math.abs((prev.py?.[n]??p.y)-prev.y)-Math.abs(p.y-o.y))/Math.max(.12,move);instant=.58*clamp(align,-1,1)+.34*clamp(gain,-1,1)+.08*clamp(yGain,-1,1);h.lastMotionAt=now;}
      h.ema[n]=h.ema[n]*.78+instant*.22;h.dist[n]=d;
    }
    for(const n of PN){if(!ps[n])continue;const s=h.ema[n];if(s>bestScore){second=bestScore;bestScore=s;best=n;}else if(s>second)second=s;}
    const margin=bestScore-second,conf=clamp((bestScore+.2)/1.05,0,1)*clamp((margin+.05)/.55,0,1);
    if(best&&conf>=.38){h.target=best;h.confidence=conf;h.margin=margin;}else if(now-h.lastMotionAt>1200){h.target=null;h.confidence=0;h.margin=0;}
  }
  h.last={x:o.x,y:o.y,py:Object.fromEntries(PN.filter(n=>ps[n]).map(n=>[n,ps[n].y]))};return h;
}

function tick(){if(!running)return;const now=Date.now(),ps=Object.fromEntries(PN.map(n=>[n,player(n)]));for(let slot=0;slot<NSLOTS;slot++){const o=actor(slot);if(!o){hist[slot]={last:null,dist:{},ema:{P1:0,P2:0,P3:0},target:null,confidence:0,margin:0,lastMotionAt:0};continue;}const h=infer(slot,o,ps,now);scanPointers(o.base);learnByte(o.base,h.target,h.confidence);}samples++;}

function live(){const rows=[];for(let slot=0;slot<NSLOTS;slot++){const o=actor(slot);if(!o)continue;const h=hist[slot];rows.push({slot,type:o.type,attack:o.attack,x:+o.x.toFixed(1),y:+o.y.toFixed(1),target:h.target,confidence:+h.confidence.toFixed(2),margin:+h.margin.toFixed(2),P1:+h.ema.P1.toFixed(2),P2:+h.ema.P2.toFixed(2),P3:+h.ema.P3.toFixed(2)});}console.table(rows);return rows;}
function directRows(map,kind){const by=new Map();for(const [k,count] of map){const [offS,name]=k.split('|'),off=+offS,key=off;let r=by.get(key);if(!r){r={kind,offset:'0x'+off.toString(16).toUpperCase(),P1:0,P2:0,P3:0,total:0};by.set(key,r);}r[name]+=count;r.total+=count;}return [...by.values()].sort((a,b)=>b.total-a.total);}
function indexRows(){const out=[];for(let off=0;off<STRIDE;off++){const s=byteStats[off];if(s.samples<20||s.byValue.size<2)continue;let correct=0,total=0;const mapping=[];for(const [v,row] of s.byValue){const arr=PN.map(n=>[n,row[n]||0]).sort((a,b)=>b[1]-a[1]);const sum=arr.reduce((q,x)=>q+x[1],0);if(!sum)continue;correct+=arr[0][1];total+=sum;mapping.push((v===255?'FF':v.toString(16).padStart(2,'0').toUpperCase())+'→'+arr[0][0]+' '+(arr[0][1]/sum).toFixed(2));}if(total<20)continue;const accuracy=correct/total,coverage=total/Math.max(1,s.samples);if(accuracy<.68)continue;out.push({offset:'0x'+off.toString(16).toUpperCase(),accuracy:+accuracy.toFixed(3),samples:total,values:s.byValue.size,map:mapping.join(' | ')});}out.sort((a,b)=>b.accuracy-a.accuracy||b.samples-a.samples);return out;}
function result(limit=24){const p32=directRows(direct32,'ptr32').slice(0,limit),p16=directRows(direct16,'ptr16').slice(0,limit),idx=indexRows().slice(0,limit);console.log('=== direct 32-bit player pointers ===');console.table(p32);console.log('=== direct 16-bit player-address matches ===');console.table(p16);console.log('=== byte target-index candidates learned from chase motion ===');console.table(idx);console.log('=== current enemy motion target ===');const l=live();return{version:'enemy-target-probe-v1',running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),direct32:p32,direct16:p16,indexCandidates:idx,live:l};}

timer=setInterval(tick,TICK);tick();
self.WOFTARGET={version:'enemy-target-probe-v1',live,result,status(){return{running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1)}},stop(){running=false;if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF target probe stopped');}};
console.log('✅ WOF enemy target/focus probe started');
console.log('🎯 让 P1/P2 分开站位，观察小怪追不同玩家 20~30 秒，然后运行 WOFTARGET.result()');
})();