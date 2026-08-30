(async()=>{
'use strict';
const M=_0x515056?.HEAPU8,R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM base unavailable');
const POOL=0xFFC0BC,STRIDE=0xE0,SLOTS=20,P=[0xFFBE1C,0xFFBEFC,0xFFBFDC],SCR=0xFF81FA;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const H=(v,n=4)=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(n,'0');
const bump=(m,k)=>m.set(k,(m.get(k)||0)+1);
const top=(m,n=6)=>[...m.entries()].sort((a,b)=>b[1]-a[1]).slice(0,n).map(([v,c])=>({v:H(Number(v)&0xffff),c}));
const st=Array.from({length:SLOTS},(_,i)=>({slot:i,base:POOL+i*STRIDE,n:0,active:0,v7c:new Map(),v7e:new Map(),types:new Map(),valid:0,ffff:0,eq:0,nearN:0,nearMatch:0}));
const scr=new Map(); let samples=0;
const t0=performance.now();
function snap(){
  const pp=P.map(a=>({a,x:S32(a+4)/65536,y:S32(a+8)/65536}));
  const sv=U16(SCR); bump(scr,sv);
  for(const s of st){
    const a=s.base,type=B(a+0x20),v7c=U16(a+0x7C),v7e=U16(a+0x7E),x=S32(a+4)/65536,y=S32(a+8)/65536;
    s.n++; bump(s.types,type); bump(s.v7c,v7c); bump(s.v7e,v7e);
    if(type!==0 || x!==0 || y!==0) s.active++;
    if(v7c===v7e)s.eq++;
    if(v7e===0xffff)s.ffff++;
    if(v7e===0||v7e===4||v7e===8){
      s.valid++;
      const sel=v7e===0?0:v7e===4?1:2;
      let ni=0,bd=Infinity;
      for(let i=0;i<3;i++){const dx=x-pp[i].x,dy=y-pp[i].y,d=dx*dx+dy*dy;if(d<bd){bd=d;ni=i;}}
      s.nearN++; if(sel===ni)s.nearMatch++;
    }
  }
  samples++;
}
const timer=setInterval(snap,20); snap();
await new Promise(r=>setTimeout(r,6000)); clearInterval(timer);
const rows=st.map(s=>({
  slot:s.slot,base:H(s.base,6),samples:s.n,activeLike:s.active,
  typeTop:top(s.types,3),v7cTop:top(s.v7c,5),v7eTop:top(s.v7e,5),
  valid048:s.valid,valid048Pct:+(s.valid/s.n).toFixed(3),ffff:s.ffff,ffffPct:+(s.ffff/s.n).toFixed(3),
  eq7c7ePct:+(s.eq/s.n).toFixed(3),nearestMatchPct:s.nearN?+(s.nearMatch/s.nearN).toFixed(3):0
})).sort((a,b)=>(b.activeLike-a.activeLike)||(b.valid048-a.valid048));
const liveRows=rows.filter(r=>r.activeLike>samples*0.15).slice(0,20);
const evidence=liveRows.filter(r=>r.valid048>0);
const scrDecoded=top(scr,12).map(x=>({...x,player:x.v==='0xBE1C'?'P1':x.v==='0xBEFC'?'P2':x.v==='0xBFDC'?'P3':''}));
const verdict={durationMs:Math.round(performance.now()-t0),samples,liveLikeSlots:liveRows.length,slotsWith048:evidence.length,allLiveMostly048:evidence.length?evidence.every(r=>r.valid048Pct>=0.8):false,scratchPlayerHits:[...scr.entries()].filter(([v])=>v===0xBE1C||v===0xBEFC||v===0xBFDC).reduce((a,[,c])=>a+c,0),scratchTop:scrDecoded.slice(0,4)};
const out={version:'wof-player-selector-7e-runtime-probe-v1',verdict,rows:liveRows,scratch:scrDecoded};
self.__WOF_PLAYER_SELECTOR_7E_RUNTIME=out;
console.log('=== DYNAMIC PLAYER SELECTOR 7E VERDICT ===');console.table([verdict]);
console.log('=== DYNAMIC PLAYER SELECTOR 7E ROWS ===');console.table(liveRows.map(r=>({slot:r.slot,base:r.base,activeLike:r.activeLike,valid048:r.valid048,valid048Pct:r.valid048Pct,ffffPct:r.ffffPct,eq7c7ePct:r.eq7c7ePct,nearestMatchPct:r.nearestMatchPct,v7eTop:r.v7eTop.map(x=>x.v+':'+x.c).join(' ')})));
console.log('=== DYNAMIC PLAYER SELECTOR 7E JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_PLAYER_SELECTOR_7E_RUNTIME_ERROR',e);throw e;});