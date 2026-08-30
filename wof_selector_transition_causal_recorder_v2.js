(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const validTarget=v=>v===0||v===4||v===8;
const tname=v=>v===0?'P1':v===4?'P2':v===8?'P3':'INVALID';
const h=(v,n=2)=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(n,'0');
const r3=v=>Math.round(v*1000)/1000;

let proof=self.__WOF_SELECTOR_END_TO_END;
if(!proof?.verdict?.endToEndStructuralProof) proof=await load('wof_selector_end_to_end_proof.js');
if(!proof?.verdict?.endToEndStructuralProof){
  const out={version:'wof-selector-transition-causal-recorder-v2',readOnly:true,started:false,reason:'END_TO_END_STRUCTURAL_PROOF_NOT_TRUE'};
  self.__WOF_SELECTOR_TRANSITION_CAUSAL_V2=out; console.log('=== SELECTOR TRANSITION CAUSAL V2 JSON ===');console.log(JSON.stringify(out,null,2)); return out;
}

const MOD=_0x515056,M=MOD?.HEAPU8,R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM base unavailable');
const POOL=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PADDR=[0xFFBE1C,0xFFBEFC,0xFFBFDC];
const SAMPLE_MS=16,RING_MS=700,POST_MS=300,MAX_RUN_MS=45000,TARGET_CASES=3,WARM_MS=500;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const blob=a=>{const x=new Uint8Array(STRIDE);for(let i=0;i<STRIDE;i++)x[i]=B(a+i);return x;};

function ent(a,enemy=false){
  const xRaw=S32(a+4),yRaw=S32(a+8),o={xRaw,yRaw,x:xRaw/65536,y:yRaw/65536,bytes:blob(a)};
  if(enemy){Object.assign(o,{type:U16(a+0x20),target:U16(a+0x7E),state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),b72:B(a+0x72),w02:U16(a+2),w3E:U16(a+0x3E),w40:U16(a+0x40),w42:U16(a+0x42)});}
  return o;
}
function snap(slot,seq,t0){
  const e=ent(POOL+slot*STRIDE,true),p=PADDR.map(a=>ent(a,false));
  const d=p.map(x=>{const dx=(x.xRaw-e.xRaw)/65536,dy=(x.yRaw-e.yRaw)/65536;return{dx,dy,d2:dx*dx+dy*dy};});
  let nearest=0;for(let i=1;i<3;i++)if(d[i].d2<d[nearest].d2)nearest=i;
  return{seq,t:performance.now()-t0,e,p,d,nearest};
}
async function chooseSlot(preferred){
  if(Number.isInteger(preferred)&&preferred>=0&&preferred<SLOTS){const a=POOL+preferred*STRIDE,t=U16(a+0x7E),type=U16(a+0x20),active=S32(a+4)!==0||S32(a+8)!==0||type!==0;if(validTarget(t)&&active)return{slot:preferred,source:'previous-v1'};}
  const st=Array.from({length:SLOTS},(_,slot)=>({slot,n:0,v:0,a:0,type:0,target:0})),t0=performance.now();
  while(performance.now()-t0<WARM_MS){for(const s of st){const a=POOL+s.slot*STRIDE,t=U16(a+0x7E),type=U16(a+0x20),active=S32(a+4)!==0||S32(a+8)!==0||type!==0;s.n++;if(validTarget(t))s.v++;if(active)s.a++;s.type=type;s.target=t;}await sleep(25);}
  const rows=st.map(s=>({...s,validPct:s.v/s.n,activePct:s.a/s.n,score:(s.v/s.n)*1000+(s.a/s.n)*250})).sort((a,b)=>b.score-a.score);
  const best=rows.find(x=>x.validPct>=.8&&x.activePct>=.5);return{slot:best?.slot??null,source:'auto',candidates:rows.slice(0,6).map(x=>({slot:x.slot,validPct:+x.validPct.toFixed(2),activePct:+x.activePct.toFixed(2),type:x.type,target:x.target}))};
}
function valueEvent(samples,t0,get,name){const ev=[];for(let i=1;i<samples.length;i++){const a=get(samples[i-1]),b=get(samples[i]);if(a!==b)ev.push({r:Math.round(samples[i].t-t0),field:name,from:a,to:b});}return ev;}
function byteEvents(samples,t0,getBytes,lo=-300,hi=300){
  const map=new Map();
  for(let i=1;i<samples.length;i++){
    const r=Math.round(samples[i].t-t0);if(r<lo||r>hi)continue;const a=getBytes(samples[i-1]),b=getBytes(samples[i]);
    for(let off=0;off<STRIDE;off++)if(a[off]!==b[off]){let x=map.get(off);if(!x){x={off,events:[]};map.set(off,x);}x.events.push({r,from:a[off],to:b[off]});}
  }
  return[...map.values()];
}
function summarizeRole(events){
  return events.map(x=>{const lead=x.events.filter(e=>e.r<0),at=x.events.filter(e=>e.r===0),after=x.events.filter(e=>e.r>0);const closest=x.events.slice().sort((a,b)=>Math.abs(a.r)-Math.abs(b.r))[0];return{off:'+0x'+x.off.toString(16).toUpperCase().padStart(2,'0'),n:x.events.length,leadR:lead.length?lead[lead.length-1].r:null,at:at.length?at[0]:null,afterR:after.length?after[0].r:null,closestR:closest?.r??null,closestFrom:closest?.from,closestTo:closest?.to};}).sort((a,b)=>Math.abs(a.closestR??9999)-Math.abs(b.closestR??9999)||a.n-b.n);
}
function trimRole(rows,mode,limit){
  let a=rows;
  if(mode==='lead')a=rows.filter(x=>x.leadR!==null&&x.leadR>=-250).sort((x,y)=>Math.abs(x.leadR)-Math.abs(y.leadR)||x.n-y.n);
  if(mode==='at')a=rows.filter(x=>x.at).sort((x,y)=>x.n-y.n);
  if(mode==='after')a=rows.filter(x=>x.afterR!==null&&x.afterR<=250).sort((x,y)=>x.afterR-y.afterR||x.n-y.n);
  return a.slice(0,limit);
}
function coreEvents(s,t0){
  const defs=[['target',x=>tname(x.e.target)],['state99',x=>x.e.state99],['action2A',x=>x.e.action2A],['b2B',x=>x.e.b2B],['b72',x=>x.e.b72],['w02',x=>x.e.w02],['w3E',x=>x.e.w3E],['w40',x=>x.e.w40],['w42',x=>x.e.w42],['nearest',x=>'P'+(x.nearest+1)]];
  return defs.flatMap(([n,g])=>valueEvent(s,t0,g,n)).filter(x=>x.r>=-300&&x.r<=300).sort((a,b)=>a.r-b.r);
}
function addAgg(map,rows,key){for(const r of rows){const off=r.off;let x=map.get(off);if(!x){x={off,newLead:0,newAt:0,oldLead:0,oldAt:0,otherLead:0,otherAt:0,leadRs:[]};map.set(off,x);}if(key==='new'){if(r.leadR!==null&&r.leadR>=-250){x.newLead++;x.leadRs.push(r.leadR);}if(r.at)x.newAt++;}else if(key==='old'){if(r.leadR!==null&&r.leadR>=-250)x.oldLead++;if(r.at)x.oldAt++;}else{if(r.leadR!==null&&r.leadR>=-250)x.otherLead++;if(r.at)x.otherAt++;}}}
function finishCase(cap,tr){
  const oi=tr.from>>>2,ni=tr.to>>>2,others=[0,1,2].filter(i=>i!==oi&&i!==ni),at=cap.reduce((a,b)=>Math.abs(b.t-tr.t)<Math.abs(a.t-tr.t)?b:a,cap[0]);
  const er=summarizeRole(byteEvents(cap,tr.t,s=>s.e.bytes));
  const roles=[0,1,2].map(i=>summarizeRole(byteEvents(cap,tr.t,s=>s.p[i].bytes)));
  return{
    transition:{from:tname(tr.from),to:tname(tr.to),seq:tr.seq},
    at:{state99:at.e.state99,action2A:at.e.action2A,b2B:at.e.b2B,b72:at.e.b72,nearest:'P'+(at.nearest+1),d2:at.d.map(x=>Math.round(x.d2)),dx:at.d.map(x=>r3(x.dx)),dy:at.d.map(x=>r3(x.dy))},
    coreEvents:coreEvents(cap,tr.t),
    enemyLead:trimRole(er,'lead',12),enemyAt:trimRole(er,'at',16),enemyAfter:trimRole(er,'after',10),
    newTargetPlayer:{player:'P'+(ni+1),lead:trimRole(roles[ni],'lead',18),at:trimRole(roles[ni],'at',12),after:trimRole(roles[ni],'after',10)},
    oldTargetPlayer:{player:'P'+(oi+1),lead:trimRole(roles[oi],'lead',12),at:trimRole(roles[oi],'at',10)},
    otherPlayers:others.map(i=>({player:'P'+(i+1),lead:trimRole(roles[i],'lead',8),at:trimRole(roles[i],'at',8)})),
    _roles:roles
  };
}

async function run(opts={}){
  if(self.__WOF_SELECTOR_TRANSITION_V2_RUNNING)throw new Error('v2 recorder already running');self.__WOF_SELECTOR_TRANSITION_V2_RUNNING=true;
  try{
    const preferred=Number.isInteger(opts.slot)?opts.slot:self.__WOF_SELECTOR_TRANSITION_CAUSAL?.lockedSlot;
    const pick=await chooseSlot(preferred);if(pick.slot===null){const out={version:'wof-selector-transition-causal-recorder-v2',readOnly:true,started:false,reason:'NO_VALID_SLOT',slotSelection:pick};self.__WOF_SELECTOR_TRANSITION_CAUSAL_V2=out;console.log('=== SELECTOR TRANSITION CAUSAL V2 JSON ===');console.log(JSON.stringify(out,null,2));return out;}
    const slot=pick.slot,t0=performance.now(),ring=[],cases=[];let seq=0,lastValid=null,active=null;
    while(performance.now()-t0<MAX_RUN_MS&&cases.length<TARGET_CASES){
      const s=snap(slot,seq++,t0);ring.push(s);while(ring.length&&s.t-ring[0].t>RING_MS)ring.shift();
      if(active){active.cap.push(s);if(s.t-active.tr.t>=POST_MS){const c=finishCase(active.cap,active.tr);cases.push(c);active=null;}}
      if(validTarget(s.e.target)){
        if(!active&&lastValid&&lastValid.target!==s.e.target){active={tr:{from:lastValid.target,to:s.e.target,t:s.t,seq:s.seq},cap:ring.slice()};}
        lastValid={target:s.e.target,t:s.t,seq:s.seq};
      }
      await sleep(SAMPLE_MS);
    }
    if(active&&cases.length<TARGET_CASES&&active.cap.length>2)cases.push(finishCase(active.cap,active.tr));
    const agg=new Map();let actionResetSameFrame=0,state99ChangedSameFrame=0,nearestNewTarget=0;
    for(const c of cases){const ni=['P1','P2','P3'].indexOf(c.newTargetPlayer.player),oi=['P1','P2','P3'].indexOf(c.oldTargetPlayer.player);addAgg(agg,c._roles[ni],'new');addAgg(agg,c._roles[oi],'old');for(let i=0;i<3;i++)if(i!==ni&&i!==oi)addAgg(agg,c._roles[i],'other');if(c.coreEvents.some(e=>e.r===0&&e.field==='action2A'))actionResetSameFrame++;if(c.coreEvents.some(e=>e.r===0&&e.field==='state99'))state99ChangedSameFrame++;if(c.at.nearest===c.newTargetPlayer.player)nearestNewTarget++;delete c._roles;}
    const rank=[...agg.values()].map(x=>({...x,medianLeadR:x.leadRs.length?x.leadRs.slice().sort((a,b)=>a-b)[Math.floor(x.leadRs.length/2)]:null})).sort((a,b)=>(b.newLead-a.newLead)||(a.oldLead-b.oldLead)||(a.otherLead-b.otherLead)||(Math.abs(a.medianLeadR??9999)-Math.abs(b.medianLeadR??9999))).slice(0,30);
    const out={version:'wof-selector-transition-causal-recorder-v2',readOnly:true,ramWrites:0,structuralProof:true,lockedSlot:slot,lockedBase:h(POOL+slot*STRIDE,6),slotSelection:pick,casesCaptured:cases.length,summary:{action2AChangedSameFrame:actionResetSameFrame,state99ChangedSameFrame,nearestEqualsNewTarget:nearestNewTarget},newTargetLeadRank:rank,cases};
    self.__WOF_SELECTOR_TRANSITION_CAUSAL_V2=out;console.log('=== SELECTOR TRANSITION CAUSAL V2 VERDICT ===');console.table([{slot,cases:cases.length,action2AChangedSameFrame:actionResetSameFrame,state99ChangedSameFrame,nearestEqualsNewTarget:nearestNewTarget}]);console.log('=== SELECTOR TRANSITION CAUSAL V2 JSON ===');console.log(JSON.stringify(out,null,2));return out;
  }finally{self.__WOF_SELECTOR_TRANSITION_V2_RUNNING=false;}
}
self.WOFTRANS2={run,version:'wof-selector-transition-causal-recorder-v2'};
return await run({});
})().catch(e=>{self.__WOF_SELECTOR_TRANSITION_V2_RUNNING=false;console.error('WOF_SELECTOR_TRANSITION_CAUSAL_V2_ERROR',e);throw e;});