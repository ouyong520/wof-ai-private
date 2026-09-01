import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createRequire} from 'node:module';

const require=createRequire(import.meta.url);
const here=path.dirname(fileURLToPath(import.meta.url));
const alpha=path.resolve(here,'../../product/alpha');
const read=name=>fs.readFileSync(path.join(alpha,name),'utf8');

const core=require(path.join(alpha,'wof_alpha_core.js'));
const hudModel=require(path.join(alpha,'wof_alpha_hud_model.js'));
const loader=read('wof_alpha_loader.js');
const hud=read('wof_alpha_hud.js');
const bootstrap=read('wof_alpha_bootstrap.user.js');
const manifest=JSON.parse(read('rules_manifest.json'));

const GOLD='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const SESSION='0123456789abcdef0123456789abcdef';
const results=[];
function test(name,fn){try{fn();results.push({name,ok:true});}catch(e){results.push({name,ok:false,error:String(e?.stack||e)});}}

function goodProbe(sha256=GOLD,hashStatus='accepted'){
  return {
    moduleOk:true,
    ramBase:0x100000,
    ramWithinHeap:true,
    selfIndexes:[0,4,8],
    romLocator:{
      source:'browser-wasm-rom',candidateCount:1,selectedHeapBase:0x200000,swap16:false,
      vectorSp:core.ROM_IDENTITY.vectorSp,vectorPc:core.ROM_IDENTITY.vectorPc,
      dispatchOffset:core.ROM_IDENTITY.dispatchOffset,
      dispatchEntries:core.ROM_IDENTITY.dispatchEntries.slice(),uniformDelta:0
    },
    romIdentity:{source:'browser-wasm-rom',logicalBytes:0x100000,hashStatus,sha256}
  };
}

function t18(body=7512,overrides={}){
  const is7512=body===7512;
  return {slot:3,type:18,target7E:0,state99:2,action2A:2,b2B:4,body,attack:0,
    frameEnd:is7512?0x8BBB2:0x8BBDE,next:is7512?0x8B290:0x8B2A4,value30:0x180001,timer34:4,payload6C:0,
    enemyX:120,targetX:200,...overrides};
}

// Q1: exact identity, fail closed.
test('identity accepts exact full golden digest',()=>assert.equal(core.validateIdentityProbe(goodProbe()).ok,true));
test('identity rejects one-nibble digest mutation',()=>assert.equal(core.validateIdentityProbe(goodProbe(GOLD.slice(0,-1)+'3')).ok,false));
test('identity rejects pending digest',()=>assert.equal(core.validateIdentityProbe(goodProbe('', 'pending')).ok,false));
test('identity rejects malformed digest',()=>assert.equal(core.validateIdentityProbe(goodProbe('1234')).ok,false));
test('identity rejects hash error',()=>assert.equal(core.validateIdentityProbe(goodProbe('', 'error')).ok,false));
test('identity rejects sparse locator without digest',()=>{const p=goodProbe();delete p.romIdentity;assert.equal(core.validateIdentityProbe(p).ok,false);});

// Q2/Q3: current-only T18, no inherited warnings.
test('exactly two production rules',()=>assert.equal(core.RULES.length,2));
test('four quarantined frozen rules',()=>assert.equal(core.QUARANTINED_RULES.length,4));
test('F1-F4 absent from production RULES',()=>assert.deepEqual(core.RULES.map(x=>x.id).sort(),[
  'T18_5424_CYCLE_BODY7520_TM4_LEVEL_90','T18_5440_CYCLE_BODY7512_TM4_LEVEL_90'].sort()));
test('matching T18 warns as current evidence',()=>{const e=core.createEngine();const s=e.step([t18()],1);assert.equal(s.warnings.length,1);assert.equal(s.warnings[0].evidence,'fresh-current-sample');});
test('T18 clears on first current nonmatch',()=>{const e=core.createEngine();assert.equal(e.step([t18()],1).warnings.length,1);assert.equal(e.step([t18(7512,{timer34:5})],2).warnings.length,0);});
test('same-slot same-type ACTIVE replacement does not inherit',()=>{const e=core.createEngine();assert.equal(e.step([t18()],1).warnings.length,1);const replacement=t18(7512,{attack:5440,state99:3,action2A:8,b2B:9,body:7000,timer34:0});assert.equal(e.step([replacement],2).warnings.length,0);});
test('cross-episode neutral gap does not inherit',()=>{const e=core.createEngine();assert.equal(e.step([t18()],1).warnings.length,1);assert.equal(e.step([],2).warnings.length,0);assert.equal(e.step([t18(7512,{timer34:0})],3).warnings.length,0);});
test('fresh matching replacement may warn without history',()=>{const e=core.createEngine();e.step([t18(7512,{timer34:0})],1);const s=e.step([t18()],2);assert.equal(s.warnings.length,1);assert.equal(s.warnings[0].publication,'hold-only-current-level');});
test('UNKNOWN target stays silent',()=>{const e=core.createEngine();assert.equal(e.step([t18(7512,{target7E:2})],1).warnings.length,0);});

// HUD aggregation.
test('HUD preserves simultaneous warnings',()=>{const m=hudModel.summarizeWarnings([
  {target:'P1',threatSide:'LEFT',attackSpecific:false},
  {target:'P1',threatSide:'LEFT',attackSpecific:true,attack:5424},
  {target:'P2',threatSide:'RIGHT',attackSpecific:true,attack:5440}
]);assert.equal(m.count,3);assert.equal(m.groupCount,2);assert.equal(m.groups.find(g=>g.target==='P1').count,2);});

// Packaging/session/bootstrap/static safety.
test('manifest exposes two production and four quarantined',()=>{assert.equal(manifest.activeProductionRules.length,2);assert.equal(manifest.quarantinedFrozenCandidates.length,4);});
test('bootstrap is document-start',()=>assert.match(bootstrap,/@run-at\s+document-start/));
test('bootstrap uses crypto random 16-byte session',()=>{assert.match(bootstrap,/new Uint8Array\(16\)/);assert.match(bootstrap,/crypto\.getRandomValues/);});
test('HUD enforces schema and session',()=>assert.match(hud,/m\.schema===SCHEMA&&m\.session===SESSION/));
test('loader exposes read-only zero-write no-input status',()=>{assert.match(loader,/readOnly:true,ramWrites:0,inputInjection:false/);});

// ALPHAQA-RC3-001: exact current source pattern and deterministic user-visible consequence.
test('P1 source precondition: runtime exception posts diag after engine reset',()=>{assert.match(loader,/running=false;engine\.reset\(\);post\('diag'/);});
test('P1 source precondition: diag handler does not invalidate lastMsg or lastRx',()=>{
  const m=hud.match(/else if\(m\.kind==='diag'\)\{([^}]*)\}/);
  assert.ok(m,'diag handler not found');assert.doesNotMatch(m[1],/lastMsg\s*=\s*null/);assert.doesNotMatch(m[1],/lastRx\s*=\s*0/);
});
test('P1 source precondition: fresh warning branch precedes diagnostic branch',()=>{
  assert.ok(hud.indexOf('if(fresh){')<hud.indexOf('if(lastDiag&&'));
});
test('P1 reproduction: warning remains visible immediately after runtime diag',()=>{
  const STALE_MS=1500;let lastMsg=null,lastRx=0,lastDiag=null;
  const on=(m,now)=>{if(!(m&&m.schema==='wof-alpha-v2'&&m.session===SESSION))return;if(m.kind==='state'){lastMsg=m;lastRx=now;lastDiag=null;}else if(m.kind==='diag'){lastDiag={at:now,reason:m.reason};}};
  const visible=now=>{const fresh=!!lastRx&&now-lastRx<=STALE_MS;if(fresh&&Array.isArray(lastMsg?.warnings)&&lastMsg.warnings.length)return 'WARNING';if(lastDiag&&now-lastDiag.at<5000)return 'DIAG';return 'NONE';};
  on({schema:'wof-alpha-v2',session:SESSION,kind:'state',warnings:[{ruleId:'T18_5440_CYCLE_BODY7512_TM4_LEVEL_90'}]},1000);
  on({schema:'wof-alpha-v2',session:SESSION,kind:'diag',reason:'runtime exception'},1001);
  assert.equal(visible(1002),'WARNING');
  assert.equal(visible(2499),'WARNING');
  assert.equal(visible(2501),'DIAG');
});

const failed=results.filter(x=>!x.ok);
const blockerReproduced=results.find(x=>x.name.startsWith('P1 reproduction'))?.ok===true;
const out={version:'alphaqa-rc3-independent-v1',verdict:blockerReproduced?'BLOCKED_P1':'INDETERMINATE',blocker:'ALPHAQA-RC3-001',tests:results.length,failedTests:failed.length,results};
console.log(JSON.stringify(out,null,2));
if(failed.length)process.exitCode=1;
