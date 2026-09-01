import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const C=require('./wof_alpha_core.js');
const H=require('./wof_alpha_hud_model.js');
const files=n=>fs.readFileSync(new URL(n,import.meta.url),'utf8');

const GOLD='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const ACTIVE=['T18_5440_CYCLE_BODY7512_TM4_LEVEL_90','T18_5424_CYCLE_BODY7520_TM4_LEVEL_90'];
const QUARANTINED=['T16_B4_DANGER_40','T20_5136_B0_TO_B255_1250','D867BA_3232_TM6_220','D8811E_3232_TM6_135'];
const base=(slot,type,target7E=0,enemyX=100,targetX=140)=>({slot,type,target7E,enemyX,targetX,state99:0,action2A:0,b2B:0,body:1,attack:0,frameEnd:1,next:2,value30:0,timer34:0,payload6C:0});
const stateFor=(id,slot=0,target7E=0,enemyX=100,targetX=140,bOverride=null)=>{
  if(id==='T16_B4_DANGER_40')return {...base(slot,16,target7E,enemyX,targetX),state99:2,action2A:4,b2B:4,body:4856,frameEnd:0x851ae,next:0x84c44,value30:0xffff,timer34:1};
  if(id==='T20_5136_B0_TO_B255_1250')return {...base(slot,20,target7E,enemyX,targetX),state99:2,action2A:4,b2B:bOverride??255,body:0,frameEnd:0x839c4,next:0x82b0a,value30:0x100000,timer34:20,payload6C:0};
  if(id==='D867BA_3232_TM6_220')return {...base(slot,33,target7E,enemyX,targetX),state99:2,action2A:4,b2B:2,body:2872,frameEnd:0x867ba,next:0x85ece,value30:0x100000,timer34:6,payload6C:2784};
  if(id==='D8811E_3232_TM6_135')return {...base(slot,34,target7E,enemyX,targetX),state99:2,action2A:4,b2B:2,body:2872,frameEnd:0x8811e,next:0x879e2,value30:0x100000,timer34:6,payload6C:2784};
  if(id==='T18_5440_CYCLE_BODY7512_TM4_LEVEL_90')return {...base(slot,18,target7E,enemyX,targetX),state99:2,action2A:2,b2B:4,body:7512,frameEnd:0x8bbb2,next:0x8b290,value30:0x180001,timer34:4,payload6C:0};
  if(id==='T18_5424_CYCLE_BODY7520_TM4_LEVEL_90')return {...base(slot,18,target7E,enemyX,targetX),state99:2,action2A:2,b2B:4,body:7520,frameEnd:0x8bbde,next:0x8b2a4,value30:0x180001,timer34:4,payload6C:0};
  throw new Error(id);
};
const neutral=(slot=0,type=18)=>({...base(slot,type),frameEnd:0x1234,next:0x5678});
const layout={moduleOk:true,ramBase:123,ramWithinHeap:true,selfIndexes:[0,4,8]};
const locator={source:'browser-wasm-rom',candidateCount:1,vectorSp:0x00FF62EE,vectorPc:0x0000754A,dispatchOffset:0x25DC,
  dispatchEntries:[0x06F518,0x074980,0x071B0E,0x077BC2,0x07C706],uniformDelta:0x34};
const rom=(hashStatus='accepted',sha256=GOLD)=>({source:'browser-wasm-rom',logicalBytes:0x100000,hashStatus,sha256});

assert.equal(C.VERSION,'wof-alpha-core-rc3');
assert.equal(C.SCHEMA,'wof-alpha-v2');
assert.equal(C.ROM_IDENTITY.game,'wof');
assert.equal(C.ROM_IDENTITY.description,'Warriors of Fate (World 921031)');
assert.equal(C.ROM_IDENTITY.expectedSha256,GOLD);
assert.deepEqual(C.RULES.map(r=>r.id),ACTIVE);
assert.deepEqual(C.QUARANTINED_RULES.map(r=>r.id),QUARANTINED);
assert.equal(C.FROZEN_RULES.length,6);

// C1 identity gate: only exact 1 MiB CPU-logical SHA-256 can accept.
assert.equal(C.validateIdentityProbe({...layout,romLocator:locator,romIdentity:rom()}).ok,true,'exact supported digest accepts');
assert.match(C.validateIdentityProbe({...layout,romLocator:locator,romIdentity:rom()}).signature,/^wof-world-921031-maincpu-sha256-v1:/);
assert.equal(C.validateIdentityProbe(layout).ok,false,'layout only rejects');
assert.equal(C.validateIdentityProbe({...layout,romLocator:locator}).ok,false,'layout+vector+dispatch without full digest rejects');
assert.equal(C.validateIdentityProbe({...layout,romLocator:locator,romIdentity:rom('pending','')}).ok,false,'pending hash rejects');
assert.equal(C.validateIdentityProbe({...layout,romLocator:locator,romIdentity:rom('error','')}).ok,false,'hash error rejects');
assert.equal(C.validateIdentityProbe({...layout,romLocator:locator,romIdentity:rom('accepted','0'.repeat(64))}).ok,false,'old/other/wrong digest rejects');
assert.equal(C.validateIdentityProbe({...layout,romLocator:locator,romIdentity:rom('accepted',GOLD.slice(0,-1)+'3')}).ok,false,'one-digit mutation rejects');
assert.equal(C.validateIdentityProbe({...layout,romLocator:locator,romIdentity:rom('accepted','xyz')}).ok,false,'malformed digest rejects');
assert.equal(C.validateIdentityProbe({...layout,romLocator:{...locator,candidateCount:2},romIdentity:rom()}).ok,false,'ambiguous locator rejects');
assert.equal(C.validateIdentityProbe({...layout,romLocator:{...locator,candidateCount:0,dispatchEntries:null},romIdentity:rom()}).ok,false,'missing locator rejects');

// Session isolation remains enforced.
const session='0123456789abcdef0123456789abcdef';
assert.equal(C.transportAccepts({schema:C.SCHEMA,session},session),true);
assert.equal(C.transportAccepts({schema:C.SCHEMA,session:'ffffffffffffffffffffffffffffffff'},session),false);

// C2: history/edge rules are production-quarantined, so cross-episode edges cannot warn.
{
  const e=C.createEngine();
  e.step([stateFor('T20_5136_B0_TO_B255_1250',0,0,100,140,0)],0);
  assert.equal(e.step([stateFor('T20_5136_B0_TO_B255_1250')],10).warnings.length,0,'hidden same-type false T20 edge silent');
  assert.equal(e.step([{...stateFor('T20_5136_B0_TO_B255_1250'),attack:5136}],20).warnings.length,0,'history watch cannot resolve on replacement');
}
for(const id of ['T16_B4_DANGER_40','D867BA_3232_TM6_220','D8811E_3232_TM6_135']){
  const e=C.createEngine();
  e.step([neutral(0,stateFor(id).type)],0);
  assert.equal(e.step([stateFor(id)],10).warnings.length,0,id+' is quarantined from user-facing production');
}

// F5/F6 are stateless hold-only current-level warnings.
for(const id of ACTIVE){
  const e=C.createEngine();
  let s=e.step([stateFor(id)],10);
  assert.equal(s.warnings.length,1,id+' current match shows');
  const w=s.warnings[0];
  assert.equal(w.publication,'hold-only-current-level');
  assert.equal(w.evidence,'fresh-current-sample');
  assert.equal('ageMs' in w,false,'no inherited age');
  assert.equal('watchId' in w,false,'no inherited watch id');
  assert.equal('atMs' in w,false,'no inherited arm timestamp');
  assert.equal(s=e.step([neutral(0,18)],20).warnings.length,0,id+' first current nonmatch clears immediately');
  s=e.step([stateFor(id,0,8,180,100)],30);
  assert.equal(s.warnings.length,1,id+' matching replacement is fresh current evidence');
  assert.equal(s.warnings[0].target,'P3');
  assert.equal(s.warnings[0].threatSide,'RIGHT');
}

// Same-type replacement neutral never inherits old warning; matching replacement is independent current evidence.
{
  const id=ACTIVE[0],e=C.createEngine();
  assert.equal(e.step([stateFor(id)],0).warnings.length,1);
  assert.equal(e.step([neutral(0,18)],10).warnings.length,0);
  const s=e.step([stateFor(id,0,4,50,90)],20);
  assert.equal(s.warnings.length,1);assert.equal(s.warnings[0].target,'P2');assert.equal(s.warnings[0].evidence,'fresh-current-sample');
}

// Cross-slot / simultaneous same-type warnings stay per-slot and all are retained.
{
  const e=C.createEngine(),id=ACTIVE[0];
  const s=e.step([stateFor(id,0,0,100,140),stateFor(id,1,4,180,100)],10);
  assert.equal(s.warnings.length,2);
  assert.deepEqual(s.warnings.map(w=>w.slot).sort((a,b)=>a-b),[0,1]);
}

// UNKNOWN target stays silent and reset clears immediately.
{
  const e=C.createEngine(),id=ACTIVE[0];
  assert.equal(e.step([stateFor(id,0,6,100,140)],10).warnings.length,0);
  assert.equal(e.step([stateFor(id)],20).warnings.length,1);e.reset();assert.equal(e.state(21).warnings.length,0);
}

// Explicitly excluded BODY4728 candidate remains silent.
{
  const e=C.createEngine();
  const x={...base(0,18),state99:2,action2A:4,b2B:2,body:4728,attack:0,frameEnd:0x8a000,next:0x8a100,value30:0x180001,timer34:1,payload6C:0};
  assert.equal(e.step([x],10).warnings.length,0);
}

// Preserved RC2 HUD aggregation remains correct for simultaneous current-level warnings.
{
  const e=C.createEngine(),id=ACTIVE[0];
  const s=e.step([stateFor(id,0,0,100,140),stateFor(id,1,4,180,100)],10);
  const model=H.summarizeWarnings(s.warnings);
  assert.equal(model.count,2);assert.equal(model.groupCount,2);
}

// Static release guards for the new authoritative hash path and preserved RC2 packaging/safety.
const loader=files('wof_alpha_loader.js'),core=files('wof_alpha_core.js'),hud=files('wof_alpha_hud.js'),boot=files('wof_alpha_bootstrap.user.js'),readme=files('README.md');
const manifest=JSON.parse(files('rules_manifest.json'));
assert(loader.includes("const RELEASE='wof-alpha-rc3'"));
assert(loader.includes("C.VERSION!=='wof-alpha-core-rc3'"));
assert(loader.includes("self.crypto.subtle.digest('SHA-256',logical)"),'loader must hash full logical program');
assert(loader.includes('identityPromise'),'identity hash result must be cached once per startup');
assert(loader.includes('logical=new Uint8Array(n)'),'loader must normalize the full logical program before hashing');
assert(core.includes(GOLD),'golden 921031 SHA-256 must be bound in core');
assert(!/wofr1|921002/.test(core+loader+readme),'stale 921002 identity label must not remain in RC3 active code/docs');
assert(/@run-at\s+document-start/.test(boot)&&/window\.Worker=AlphaWorker/.test(boot)&&/gstyphoon/.test(boot),'normal-user bootstrap must still intercept target Worker at document start');
assert(/legacy\.dispose/.test(hud),'legacy research HUD must still be disposed');
assert(/m\.session===SESSION/.test(hud),'HUD must still enforce session nonce');
assert(!/warnings\?\.\[0\]|warnings\s*\[\s*0\s*\]/.test(hud),'HUD must not special-case only warning[0]');
assert(/snapshot|snapGL/.test(hud)&&/restoreGL/.test(hud),'HUD must preserve GL state');
assert.equal(manifest.artifactVersion,'wof-alpha-rc3');
assert.equal(manifest.supportedIdentity.fullCpuLogicalSha256,GOLD);
assert.deepEqual(manifest.activeProductionRules.map(r=>r.id),ACTIVE);
assert.deepEqual(manifest.quarantinedFrozenCandidates.map(r=>r.id),QUARANTINED);
for(const [name,src] of [['loader',loader],['core',core]]){
  assert(!/(?:HEAPU(?:8|16|32)|\bM)\s*\[[^\]]+\]\s*(?:=|\+=|-=|\*=|\/=|\+\+|--)/.test(src),name+' must not write game heap');
  assert(!/(dispatchEvent|KeyboardEvent|MouseEvent|\.click\s*\()/.test(src),name+' must not inject input');
}

console.log(JSON.stringify({
  artifact:'wof-alpha-rc3',tests:'PASS',supportedIdentity:'wof / World 921031',goldenSha256:GOLD,
  productionRules:ACTIVE,quarantinedRules:QUARANTINED,
  blockers:{exactFullSha256Gate:true,hashPendingFailClosed:true,hashErrorFailClosed:true,sparseFingerprintNotAuthoritative:true,
    historyRulesQuarantined:true,currentLevelHoldOnly:true,sameTypeReplacementNoInheritance:true,sessionBoundTransportPreserved:true,readOnly:true,inputInjection:false}
},null,2));
