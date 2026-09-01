import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const C=require('./wof_alpha_core.js');
const H=require('./wof_alpha_hud_model.js');

const files=n=>fs.readFileSync(new URL(n,import.meta.url),'utf8');
const base=(slot,type,target7E=0,enemyX=100,targetX=140)=>({slot,type,target7E,enemyX,targetX,state99:0,action2A:0,b2B:0,body:1,attack:0,frameEnd:1,next:2,value30:0,timer34:0,payload6C:0});
const stateFor=(id,slot=0,target7E=0,enemyX=100,targetX=140,bOverride=null)=>{
  let s;
  if(id==='T16_B4_DANGER_40')s={...base(slot,16,target7E,enemyX,targetX),state99:2,action2A:4,b2B:4,body:4856,frameEnd:0x851ae,next:0x84c44,value30:0xffff,timer34:1};
  else if(id==='T20_5136_B0_TO_B255_1250')s={...base(slot,20,target7E,enemyX,targetX),state99:2,action2A:4,b2B:bOverride??255,body:0,frameEnd:0x839c4,next:0x82b0a,value30:0x100000,timer34:20,payload6C:0};
  else if(id==='D867BA_3232_TM6_220')s={...base(slot,33,target7E,enemyX,targetX),state99:2,action2A:4,b2B:2,body:2872,frameEnd:0x867ba,next:0x85ece,value30:0x100000,timer34:6,payload6C:2784};
  else if(id==='D8811E_3232_TM6_135')s={...base(slot,34,target7E,enemyX,targetX),state99:2,action2A:4,b2B:2,body:2872,frameEnd:0x8811e,next:0x879e2,value30:0x100000,timer34:6,payload6C:2784};
  else if(id==='T18_5440_CYCLE_BODY7512_TM4_LEVEL_90')s={...base(slot,18,target7E,enemyX,targetX),state99:2,action2A:2,b2B:4,body:7512,frameEnd:0x8bbb2,next:0x8b290,value30:0x180001,timer34:4,payload6C:0};
  else if(id==='T18_5424_CYCLE_BODY7520_TM4_LEVEL_90')s={...base(slot,18,target7E,enemyX,targetX),state99:2,action2A:2,b2B:4,body:7520,frameEnd:0x8bbde,next:0x8b2a4,value30:0x180001,timer34:4,payload6C:0};
  else throw new Error(id);
  return s;
};
const expectedAttack={
  T16_B4_DANGER_40:6432,T20_5136_B0_TO_B255_1250:5136,D867BA_3232_TM6_220:3232,D8811E_3232_TM6_135:3232,
  T18_5440_CYCLE_BODY7512_TM4_LEVEL_90:5440,T18_5424_CYCLE_BODY7520_TM4_LEVEL_90:5424
};
const neutralFor=id=>{
  const s=stateFor(id);
  if(id==='T20_5136_B0_TO_B255_1250')return stateFor(id,0,0,100,140,0);
  return {...base(0,s.type),attack:0,frameEnd:0x1234,next:0x5678};
};

assert.equal(C.VERSION,'wof-alpha-core-rc2');
assert.equal(C.SCHEMA,'wof-alpha-v2');
assert.deepEqual(C.RULES.map(x=>x.id),[
  'T16_B4_DANGER_40','T20_5136_B0_TO_B255_1250','D867BA_3232_TM6_220','D8811E_3232_TM6_135',
  'T18_5440_CYCLE_BODY7512_TM4_LEVEL_90','T18_5424_CYCLE_BODY7520_TM4_LEVEL_90'
]);
assert.equal(C.RULES[0].attackSpecific,false);
assert.equal(C.RULES[0].attack,null);

// P0 identity: layout alone is never enough.
const layoutOnly={moduleOk:true,ramBase:123,ramWithinHeap:true,selfIndexes:[0,4,8]};
assert.equal(C.validateIdentityProbe(layoutOnly).ok,false);
const goodIdentity={...layoutOnly,romFingerprint:{source:'browser-wasm-rom',vectorSp:0x00FF62EE,vectorPc:0x0000754A,dispatchOffset:0x25DC,
  dispatchEntries:[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2],uniformDelta:0}};
assert.equal(C.validateIdentityProbe(goodIdentity).ok,true);
assert.equal(C.validateIdentityProbe({...goodIdentity,romFingerprint:{...goodIdentity.romFingerprint,dispatchEntries:[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D3]}}).ok,false);

// P0 session transport: same schema but foreign nonce is rejected.
const session='0123456789abcdef0123456789abcdef';
assert.equal(C.transportAccepts({schema:C.SCHEMA,session},session),true);
assert.equal(C.transportAccepts({schema:C.SCHEMA,session:'ffffffffffffffffffffffffffffffff'},session),false);

// All six frozen rules can signal and resolve in canonical exact-predicate fixtures.
for(const r of C.RULES){
  const e=C.createEngine();let t=0;
  if(r.id==='T20_5136_B0_TO_B255_1250'){
    e.step([stateFor(r.id,0,0,100,140,0)],t+=10);
    const st=e.step([stateFor(r.id)],t+=10);assert.equal(st.warnings.length,1,r.id+' signal');
  }else if(r.trigger==='entry'){
    e.step([neutralFor(r.id)],t+=10);
    const st=e.step([stateFor(r.id)],t+=10);assert.equal(st.warnings.length,1,r.id+' signal');
  }else{
    const st=e.step([stateFor(r.id)],t+=10);assert.equal(st.warnings.length,1,r.id+' signal');
  }
  e.step([{...stateFor(r.id),attack:expectedAttack[r.id]}],t+=10);
  assert.equal(e.diagnostics().stats[r.id].resolved,1,r.id+' resolved');
}

// Explicitly excluded BODY4728 T18 candidate remains silent.
{
  const e=C.createEngine();
  const x={...base(0,18),state99:2,action2A:4,b2B:2,body:4728,attack:0,frameEnd:0x8a000,next:0x8a100,value30:0x180001,timer34:1,payload6C:0};
  assert.equal(e.step([x],10).warnings.length,0);
}

// T16 remains danger-only even when the eventual ACTIVE is A4840.
{
  const e=C.createEngine();e.step([neutralFor('T16_B4_DANGER_40')],0);
  const w=e.step([stateFor('T16_B4_DANGER_40')],10).warnings[0];
  assert.equal(w.attackSpecific,false);assert.equal(w.attack,null);
  e.step([{...stateFor('T16_B4_DANGER_40'),attack:4840}],20);
  assert.equal(e.diagnostics().stats.T16_B4_DANGER_40.attackDistribution['4840'],1);
}

// Live retarget + side recompute, UNKNOWN selector silent.
{
  const e=C.createEngine(),id='T18_5440_CYCLE_BODY7512_TM4_LEVEL_90';
  let w=e.step([stateFor(id,0,0,100,140)],10).warnings[0];
  assert.equal(w.target,'P1');assert.equal(w.threatSide,'LEFT');
  w=e.step([stateFor(id,0,8,180,100)],20).warnings[0];
  assert.equal(w.target,'P3');assert.equal(w.threatSide,'RIGHT');
  assert.equal(e.step([stateFor(id,0,6,100,140)],30).warnings.length,0);
}

// P1 same-type/same-slot replacement cannot inherit an armed watch.
{
  const e=C.createEngine(),id='T20_5136_B0_TO_B255_1250';
  e.step([stateFor(id,0,0,100,140,0)],0);
  assert.equal(e.step([stateFor(id)],10).warnings.length,1);
  const replacement={...base(0,20),state99:0,action2A:0,b2B:0,body:1234,frameEnd:0x1111,next:0x2222,value30:0,timer34:0,payload6C:0};
  assert.equal(e.step([replacement],20).warnings.length,0);
  e.step([{...replacement,attack:5136}],30);
  const st=e.diagnostics().stats[id];
  assert.equal(st.resolved,0);assert.equal(st.episodeDriftClears,1);
}

// Slot disappearance/type replacement still clears.
{
  const id='T18_5440_CYCLE_BODY7512_TM4_LEVEL_90',e=C.createEngine();
  e.step([stateFor(id)],0);assert.equal(e.step([],10).warnings.length,0);
  e.step([stateFor(id)],20);assert.equal(e.step([{...base(0,17),frameEnd:1,next:2}],30).warnings.length,0);
}

// P1 multi-threat HUD model retains every target/side group; no warning[0] special case.
{
  const e=C.createEngine();
  const st=e.step([
    stateFor('T18_5440_CYCLE_BODY7512_TM4_LEVEL_90',0,0,100,140),
    stateFor('T18_5424_CYCLE_BODY7520_TM4_LEVEL_90',1,4,180,100)
  ],10);
  assert.equal(st.warnings.length,2);
  const model=H.summarizeWarnings(st.warnings);
  assert.equal(model.count,2);assert.equal(model.groupCount,2);
  assert(model.lines.some(x=>x.includes('P1')&&x.includes('左侧')));
  assert(model.lines.some(x=>x.includes('P2')&&x.includes('右侧')));
}

// Canonical WOF-051 aggregate reconstruction stays 143/143.
const counts={
  T16_B4_DANGER_40:98,T20_5136_B0_TO_B255_1250:5,D867BA_3232_TM6_220:10,D8811E_3232_TM6_135:22,
  T18_5440_CYCLE_BODY7512_TM4_LEVEL_90:4,T18_5424_CYCLE_BODY7520_TM4_LEVEL_90:4
};
let totalSignals=0,totalResolved=0;
for(const [id,n] of Object.entries(counts)){
  const e=C.createEngine();let t=0;
  for(let i=0;i<n;i++){
    const s=stateFor(id),activeAttack=id==='T16_B4_DANGER_40'&&i===0?4840:expectedAttack[id];
    if(id==='T20_5136_B0_TO_B255_1250'){
      e.step([stateFor(id,0,0,100,140,0)],t+=10);e.step([s],t+=10);
    }else if(C.RULES.find(r=>r.id===id).trigger==='entry'){
      e.step([neutralFor(id)],t+=10);e.step([s],t+=10);
    }else e.step([s],t+=10);
    e.step([{...s,attack:activeAttack}],t+=10);
  }
  const st=e.diagnostics().stats[id];assert.equal(st.signals,n,id+' aggregate signals');assert.equal(st.resolved,n,id+' aggregate resolved');
  totalSignals+=st.signals;totalResolved+=st.resolved;
}
assert.equal(totalSignals,143);assert.equal(totalResolved,143);

// Static release safety / blocker guards.
const loader=files('wof_alpha_loader.js'),hud=files('wof_alpha_hud.js'),boot=files('wof_alpha_bootstrap.user.js'),readme=files('README.md');
for(const [name,src] of [['loader',loader],['core',files('wof_alpha_core.js')]]){
  assert(!/HEAPU(?:8|16|32|S8|S16|S32)\s*\[[^\]]+\]\s*=/.test(src),name+' must not write HEAP');
  assert(!/(dispatchEvent|KeyboardEvent|MouseEvent|\.click\s*\()/.test(src),name+' must not inject input');
}
assert(!/warnings\?\.\[0\]|warnings\s*\[\s*0\s*\]/.test(hud),'HUD must not special-case first warning');
assert(/legacy\.dispose/.test(hud),'legacy research HUD must be disposed');
assert(/m\.session===SESSION/.test(hud),'HUD must enforce session nonce');
assert(/@run-at\s+document-start/.test(boot)&&/window\.Worker=AlphaWorker/.test(boot)&&/gstyphoon/.test(boot),'normal-user bootstrap must intercept target Worker at document start');
assert(!/live\s+`gstyphoon\.js`\s+Worker console/i.test(readme),'README must not require live Worker console');
assert(/snapshot|snapGL/.test(hud)&&/restoreGL/.test(hud),'HUD must preserve GL state');

console.log(JSON.stringify({
  artifact:'wof-alpha-rc2',tests:'PASS',productionFixtureSignals:143,productionFixtureResolved:143,hardMissEquivalent:0,
  blockers:{positiveRomIdentity:true,sameTypeReplacementClears:true,multiThreatAggregate:true,normalUserBootstrap:true,sessionBoundTransport:true,legacyHudDisposed:true}
},null,2));
