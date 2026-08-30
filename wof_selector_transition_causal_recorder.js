(async()=>{
'use strict';

const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const validTarget=v=>v===0||v===4||v===8;
const targetName=v=>v===0?'P1':v===4?'P2':v===8?'P3':'INVALID';
const hx=(v,n=2)=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(n,'0');
const round3=v=>Math.round(v*1000)/1000;
const sign=v=>v<0?-1:v>0?1:0;

async function ensureStructuralGate(){
  let p=self.__WOF_SELECTOR_END_TO_END;
  if(!p||!p.verdict||p.verdict.endToEndStructuralProof!==true) p=await load('wof_selector_end_to_end_proof.js');
  const ok=!!(p&&p.verdict&&p.verdict.endToEndStructuralProof===true);
  return {ok,proof:p&&p.verdict?p.verdict:null};
}

const gate=await ensureStructuralGate();
if(!gate.ok){
  const out={version:'wof-selector-transition-causal-recorder-v1',readOnly:true,started:false,reason:'END_TO_END_STRUCTURAL_PROOF_NOT_TRUE',structuralProof:gate.proof};
  self.__WOF_SELECTOR_TRANSITION_CAUSAL=out;
  console.log('=== SELECTOR TRANSITION CAUSAL JSON ===');
  console.log(JSON.stringify(out,null,2));
  return out;
}

const MOD=_0x515056;
const M=MOD?.HEAPU8;
const R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM base unavailable');

const POOL=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLAYERS=[0xFFBE1C,0xFFBEFC,0xFFBFDC];
const SAMPLE_MS=16,PRE_MS=1500,POST_MS=1500,MAX_WAIT_MS=25000,WARMUP_MS=600,WARMUP_STEP_MS=30;

const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const bytes=a=>{const u=new Uint8Array(STRIDE);for(let i=0;i<STRIDE;i++)u[i]=B(a+i);return u;};

function readEntity(a,isEnemy=false){
  const xRaw=S32(a+4),yRaw=S32(a+8);
  const o={addr:a,xRaw,yRaw,x:xRaw/65536,y:yRaw/65536,bytes:bytes(a)};
  if(isEnemy){
    o.type=U16(a+0x20);
    o.target=U16(a+0x7E);
    o.state99=B(a+0x99);
    o.action2A=B(a+0x2A);
    o.actionWord=U16(a+0x2A);
    o.w02=U16(a+0x02);
    o.b2B=B(a+0x2B);
    o.b1F=B(a+0x1F);
    o.w3E=U16(a+0x3E);
    o.w40=U16(a+0x40);
    o.w42=U16(a+0x42);
    o.b72=B(a+0x72);
  }else{
    o.selfIndex=U16(a+0x7C);
  }
  return o;
}

function warmRow(slot){
  const a=POOL+slot*STRIDE;
  const xRaw=S32(a+4),yRaw=S32(a+8),target=U16(a+0x7E),type=U16(a+0x20);
  return {slot,a,target,type,xRaw,yRaw,valid:validTarget(target),active:(xRaw!==0||yRaw!==0||type!==0)};
}

async function chooseSlot(forcedSlot){
  if(Number.isInteger(forcedSlot)&&forcedSlot>=0&&forcedSlot<SLOTS){
    const r=warmRow(forcedSlot);
    return {slot:forcedSlot,forced:true,candidates:[{slot:r.slot,validPct:r.valid?1:0,activePct:r.active?1:0,type:r.type,target:r.target,score:999999}]};
  }
  const st=Array.from({length:SLOTS},(_,slot)=>({slot,n:0,valid:0,active:0,plausibleType:0,lastType:0,lastTarget:0}));
  const t0=performance.now();
  while(performance.now()-t0<WARMUP_MS){
    for(const s of st){
      const r=warmRow(s.slot);s.n++;if(r.valid)s.valid++;if(r.active)s.active++;if(r.type<47)s.plausibleType++;s.lastType=r.type;s.lastTarget=r.target;
    }
    await sleep(WARMUP_STEP_MS);
  }
  const rows=st.map(s=>{
    const validPct=s.n?s.valid/s.n:0,activePct=s.n?s.active/s.n:0,typePct=s.n?s.plausibleType/s.n:0;
    const score=validPct*1000+activePct*250+typePct*25;
    return {slot:s.slot,validPct:+validPct.toFixed(3),activePct:+activePct.toFixed(3),typePct:+typePct.toFixed(3),type:s.lastType,target:s.lastTarget,score:+score.toFixed(1)};
  }).sort((a,b)=>b.score-a.score);
  const best=rows.find(r=>r.validPct>=0.8&&r.activePct>=0.4)||rows.find(r=>r.validPct>=0.8)||null;
  return {slot:best?best.slot:null,forced:false,candidates:rows.slice(0,8)};
}

function snap(slot,seq,t0){
  const e=readEntity(POOL+slot*STRIDE,true);
  const p=PLAYERS.map(a=>readEntity(a,false));
  const d=p.map(x=>{
    const dxRaw=x.xRaw-e.xRaw,dyRaw=x.yRaw-e.yRaw;
    const dx=dxRaw/65536,dy=dyRaw/65536;
    return {dxRaw,dyRaw,dx,dy,d2:dx*dx+dy*dy};
  });
  let nearest=0;
  for(let i=1;i<3;i++)if(d[i].d2<d[nearest].d2)nearest=i;
  return {seq,t:performance.now()-t0,e,p,d,nearest};
}

function coreRow(s,tTransition){
  const rel=Math.round(s.t-tTransition);
  return {
    r:rel,q:s.seq,tg:s.e.target,tgn:targetName(s.e.target),st:s.e.state99,ac:s.e.action2A,aw:s.e.actionWord,tp:s.e.type,
    ex:round3(s.e.x),ey:round3(s.e.y),
    pDx:s.d.map(x=>round3(x.dx)),pDy:s.d.map(x=>round3(x.dy)),pD2:s.d.map(x=>Math.round(x.d2)),nearest:'P'+(s.nearest+1),
    w02:s.e.w02,b2b:s.e.b2B,b1f:s.e.b1F,w3e:s.e.w3E,w40:s.e.w40,w42:s.e.w42,b72:s.e.b72
  };
}

function coreEvents(samples,tTransition){
  const ev=[];
  const fields=[
    ['target',s=>s.e.target],['state99',s=>s.e.state99],['action2A',s=>s.e.action2A],['actionWord',s=>s.e.actionWord],
    ['w02',s=>s.e.w02],['b2B',s=>s.e.b2B],['b1F',s=>s.e.b1F],['w3E',s=>s.e.w3E],['w40',s=>s.e.w40],['w42',s=>s.e.w42],['b72',s=>s.e.b72],
    ['nearest',s=>s.nearest]
  ];
  for(let i=1;i<samples.length;i++){
    for(const [name,get] of fields){
      const a=get(samples[i-1]),b=get(samples[i]);
      if(a!==b)ev.push({r:Math.round(samples[i].t-tTransition),field:name,from:name==='target'?targetName(a):name==='nearest'?'P'+(a+1):a,to:name==='target'?targetName(b):name==='nearest'?'P'+(b+1):b});
    }
    for(let p=0;p<3;p++){
      const sx0=sign(samples[i-1].d[p].dx),sx1=sign(samples[i].d[p].dx),sy0=sign(samples[i-1].d[p].dy),sy1=sign(samples[i].d[p].dy);
      if(sx0!==sx1)ev.push({r:Math.round(samples[i].t-tTransition),field:'P'+(p+1)+'.dxSign',from:sx0,to:sx1});
      if(sy0!==sy1)ev.push({r:Math.round(samples[i].t-tTransition),field:'P'+(p+1)+'.dySign',from:sy0,to:sy1});
    }
  }
  return ev.sort((a,b)=>a.r-b.r);
}

function summarizeByteChanges(samples,tTransition,getBytes,exclude,limit=96){
  const out=[];
  for(let off=0;off<STRIDE;off++){
    if(exclude&&exclude(off))continue;
    let count=0,firstRel=null,closestRel=null,closestAbs=Infinity,lastFrom=null,lastTo=null;
    for(let i=1;i<samples.length;i++){
      const a=getBytes(samples[i-1])[off],b=getBytes(samples[i])[off];
      if(a===b)continue;
      count++;
      const rel=Math.round(samples[i].t-tTransition),ar=Math.abs(rel);
      if(firstRel===null)firstRel=rel;
      if(ar<closestAbs){closestAbs=ar;closestRel=rel;lastFrom=a;lastTo=b;}
    }
    if(count)out.push({off:'+0x'+off.toString(16).toUpperCase().padStart(2,'0'),changes:count,firstR:firstRel,closestR:closestRel,nearFrom:lastFrom,nearTo:lastTo});
  }
  out.sort((a,b)=>Math.abs(a.closestR)-Math.abs(b.closestR)||a.changes-b.changes||a.off.localeCompare(b.off));
  return out.slice(0,limit);
}

function knownEnemyOffset(off){
  if(off>=0x04&&off<=0x0B)return true;
  return off===0x20||off===0x21||off===0x2A||off===0x2B||off===0x3E||off===0x3F||off===0x40||off===0x41||off===0x42||off===0x43||off===0x72||off===0x7E||off===0x7F||off===0x99;
}
function knownPlayerOffset(off){return (off>=0x04&&off<=0x0B)||off===0x7C||off===0x7D;}

async function run(opts={}){
  if(self.__WOF_SELECTOR_TRANSITION_RUNNING)throw new Error('transition recorder already running');
  self.__WOF_SELECTOR_TRANSITION_RUNNING=true;
  try{
    const pick=await chooseSlot(opts.slot);
    if(pick.slot===null){
      const out={version:'wof-selector-transition-causal-recorder-v1',readOnly:true,started:false,reason:'NO_VALID_ENEMY_SLOT_TO_LOCK',structuralProof:true,slotCandidates:pick.candidates};
      self.__WOF_SELECTOR_TRANSITION_CAUSAL=out;
      console.log('=== SELECTOR TRANSITION CAUSAL JSON ===');console.log(JSON.stringify(out,null,2));
      return out;
    }

    const slot=pick.slot,t0=performance.now();
    let seq=0,lastValid=null,transition=null,capture=null;
    const pre=[];
    while(true){
      const s=snap(slot,seq++,t0);
      if(!transition){
        pre.push(s);
        while(pre.length&&s.t-pre[0].t>PRE_MS)pre.shift();
        if(validTarget(s.e.target)){
          if(lastValid&&lastValid.target!==s.e.target){
            transition={t:s.t,seq:s.seq,from:lastValid.target,to:s.e.target,fromName:targetName(lastValid.target),toName:targetName(s.e.target),invalidGapMs:Math.round(s.t-lastValid.t)};
            capture=pre.slice();
          }
          lastValid={target:s.e.target,t:s.t,seq:s.seq};
        }
      }else{
        capture.push(s);
      }

      if(transition&&s.t-transition.t>=POST_MS)break;
      if(!transition&&s.t>=MAX_WAIT_MS)break;
      await sleep(SAMPLE_MS);
    }

    if(!transition){
      const tail=pre.length?pre[pre.length-1]:null;
      const out={
        version:'wof-selector-transition-causal-recorder-v1',readOnly:true,started:true,structuralProof:true,transitionFound:false,
        lockedSlot:slot,lockedBase:hx(POOL+slot*STRIDE,6),slotSelection:pick.candidates,
        samples:seq,lastTarget:tail?targetName(tail.e.target):null,lastState99:tail?tail.e.state99:null,lastAction2A:tail?tail.e.action2A:null
      };
      self.__WOF_SELECTOR_TRANSITION_CAUSAL=out;
      console.log('=== SELECTOR TRANSITION CAUSAL JSON ===');console.log(JSON.stringify(out,null,2));
      return out;
    }

    const oldIdx=transition.from>>>2,newIdx=transition.to>>>2;
    const timeline=capture.map(s=>coreRow(s,transition.t));
    const events=coreEvents(capture,transition.t);
    const enemyCandidates=summarizeByteChanges(capture,transition.t,s=>s.e.bytes,knownEnemyOffset,96);
    const oldPlayerCandidates=summarizeByteChanges(capture,transition.t,s=>s.p[oldIdx].bytes,knownPlayerOffset,64);
    const newPlayerCandidates=summarizeByteChanges(capture,transition.t,s=>s.p[newIdx].bytes,knownPlayerOffset,64);
    const at=capture.reduce((best,s)=>Math.abs(s.t-transition.t)<Math.abs(best.t-transition.t)?s:best,capture[0]);
    const before=[...capture].reverse().find(s=>s.t<transition.t)||capture[0];
    const after=capture.find(s=>s.t>transition.t)||capture[capture.length-1];

    const out={
      version:'wof-selector-transition-causal-recorder-v1',readOnly:true,ramWrites:0,structuralProof:true,transitionFound:true,
      config:{sampleMs:SAMPLE_MS,preMs:PRE_MS,postMs:POST_MS,maxWaitMs:MAX_WAIT_MS,enemyStride:STRIDE},
      lockedSlot:slot,lockedBase:hx(POOL+slot*STRIDE,6),slotSelection:pick.candidates,
      transition:{...transition,oldPlayer:targetName(transition.from),newPlayer:targetName(transition.to)},
      boundary:{
        before:{r:Math.round(before.t-transition.t),target:targetName(before.e.target),state99:before.e.state99,action2A:before.e.action2A,nearest:'P'+(before.nearest+1)},
        at:{r:Math.round(at.t-transition.t),target:targetName(at.e.target),state99:at.e.state99,action2A:at.e.action2A,nearest:'P'+(at.nearest+1)},
        after:{r:Math.round(after.t-transition.t),target:targetName(after.e.target),state99:after.e.state99,action2A:after.e.action2A,nearest:'P'+(after.nearest+1)}
      },
      knownStructuralRoute:{state99:0,action2A:2,targetRoutine:'0x010EC6',runtimeD0Observed:false,note:'D0=24 -> 0x25C8 is structural proof only; this recorder does not hook CPU registers.'},
      events,
      enemyUnknownByteCandidates:enemyCandidates,
      oldTargetPlayerUnknownByteCandidates:oldPlayerCandidates,
      newTargetPlayerUnknownByteCandidates:newPlayerCandidates,
      timeline
    };
    self.__WOF_SELECTOR_TRANSITION_CAUSAL=out;
    console.log('=== SELECTOR TRANSITION CAUSAL VERDICT ===');
    console.table([{slot,from:transition.fromName,to:transition.toName,samples:capture.length,events:events.length,enemyCandidates:enemyCandidates.length,readOnly:true}]);
    console.log('=== SELECTOR TRANSITION CAUSAL JSON ===');
    console.log(JSON.stringify(out,null,2));
    return out;
  } finally {
    self.__WOF_SELECTOR_TRANSITION_RUNNING=false;
  }
}

self.WOFTRANS={run,version:'wof-selector-transition-causal-recorder-v1'};
return await run({});
})().catch(e=>{self.__WOF_SELECTOR_TRANSITION_RUNNING=false;console.error('WOF_SELECTOR_TRANSITION_CAUSAL_ERROR',e);throw e;});
