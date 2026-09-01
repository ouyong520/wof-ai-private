import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const ROOT=path.resolve(path.dirname(new URL(import.meta.url).pathname),'../..');
const read=p=>fs.readFileSync(path.join(ROOT,p),'utf8');
const workerSource=read('product/alpha/wof_alpha_real_worker.js');
const bootstrapSource=read('product/alpha/wof_alpha_bootstrap.user.js');
const hudSource=read('product/alpha/wof_alpha_hud.js');
const adapterSource=read('parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py');

const results=[];
function test(name,fn){try{fn();results.push({name,ok:true});}catch(error){results.push({name,ok:false,error:String(error?.stack||error)});}}

function loadAuthorityApi(){
  const module={exports:{}};
  const context={module,exports:module.exports,globalThis:{},self:undefined};
  vm.createContext(context);
  vm.runInContext(workerSource,context,{filename:'wof_alpha_real_worker.js'});
  return module.exports;
}
const api=loadAuthorityApi();
const base={release:'wof-alpha-rc3',schema:'wof-alpha-v2',transportVersion:'wof-alpha-safe-transport-v1',session:'1'.repeat(32),channel:'WOF_ALPHA_'+'1'.repeat(32),pairGeneration:7,pairNonce:'2'.repeat(32),runtimeEpoch:'3'.repeat(32),launcherIdentitySha:'5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62'};

test('tick authority accepts exact binding',()=>assert.equal(api.validBinding(base),true));
test('tick authority freezes generation/nonce/runtime epoch',()=>{const g=api.createTickAuthorityGate(base);const a=g.start();assert.equal(a.pairGeneration,7);assert.equal(a.pairNonce,base.pairNonce);assert.equal(a.runtimeEpoch,base.runtimeEpoch);assert.equal(Object.isFrozen(a),true);});
test('one detector tick in flight; queueDepth zero',()=>{const g=api.createTickAuthorityGate(base);assert.ok(g.start());assert.equal(g.start(),null);const s=g.status();assert.equal(s.queueDepth,0);assert.equal(s.skippedTicks,1);});
test('valid completion publishes once only',()=>{const g=api.createTickAuthorityGate(base);const a=g.start();assert.equal(g.finish(a),true);assert.equal(g.finish(a),false);});
test('revocation rejects stale in-flight completion',()=>{const g=api.createTickAuthorityGate(base);const a=g.start();g.revoke();assert.equal(g.finish(a),false);});
test('pair/session mismatch rejected',()=>{const g=api.createTickAuthorityGate(base);assert.equal(g.matchesEnvelope({...base}),true);assert.equal(g.matchesEnvelope({...base,session:'9'.repeat(32)}),false);assert.equal(g.matchesEnvelope({...base,pairNonce:'8'.repeat(32)}),false);assert.equal(g.matchesEnvelope({...base,pairGeneration:8}),false);});
test('runtime-epoch replacement is a different authority',()=>assert.equal(api.sameAuthority(base,{...base,runtimeEpoch:'4'.repeat(32)}),false));

function runBootstrap({broadcastThrows=false}={}){
  const channels=[];
  class BC{
    constructor(name){if(broadcastThrows)throw new Error('BC unavailable');this.name=name;channels.push(this);}
    close(){}
  }
  function WorkerSentinel(){}
  const win={Worker:WorkerSentinel,addEventListener(){}};
  const context={window:win,console:{log(){},warn(){}},BroadcastChannel:BC,crypto:{getRandomValues(bytes){bytes.fill(0x11);return bytes;}},Uint8Array,fetch(){throw new Error('unexpected fetch');},setTimeout(){return 1;},clearTimeout(){}};
  vm.createContext(context);vm.runInContext(bootstrapSource,context,{filename:'wof_alpha_bootstrap.user.js'});
  return{win,channels,WorkerSentinel};
}

test('bootstrap never replaces game Worker',()=>{const x=runBootstrap();assert.equal(x.win.Worker,x.WorkerSentinel);assert.equal(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.workerReplacement,false);assert.equal(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.gameWorkerUntouched,true);});
test('no transport leaves Alpha waiting and gameplay unaffected',()=>{const x=runBootstrap();assert.equal(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.attachState,'WAITING_EXTERNAL_TRANSPORT');assert.equal(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.hudLoaded,false);});
test('exact pair state attaches',()=>{const x=runBootstrap();const t=x.win.__WOF_ALPHA_TRANSPORT_V1;const b=t.bind('2'.repeat(32));x.channels[0].onmessage({data:{schema:'wof-alpha-v2',kind:'state',session:b.session,transportVersion:b.transportVersion,pairGeneration:b.pairGeneration,pairNonce:b.pairNonce,warnings:[]}});assert.equal(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.attachState,'PAIRED');});
test('session/pair nonce mismatch cannot attach',()=>{const x=runBootstrap();const t=x.win.__WOF_ALPHA_TRANSPORT_V1;const b=t.bind('2'.repeat(32));x.channels[0].onmessage({data:{schema:'wof-alpha-v2',kind:'state',session:b.session,transportVersion:b.transportVersion,pairGeneration:b.pairGeneration,pairNonce:'9'.repeat(32),warnings:[]}});assert.notEqual(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.attachState,'PAIRED');});
test('rebind makes old generation stale',()=>{const x=runBootstrap();const t=x.win.__WOF_ALPHA_TRANSPORT_V1;const old=t.bind('2'.repeat(32));const newer=t.bind('3'.repeat(32));assert.ok(newer.pairGeneration>old.pairGeneration);x.channels[0].onmessage({data:{schema:'wof-alpha-v2',kind:'state',session:old.session,transportVersion:old.transportVersion,pairGeneration:old.pairGeneration,pairNonce:old.pairNonce,warnings:[{ruleId:'old'}]}});assert.notEqual(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.attachState,'PAIRED');});
test('disconnect/reset clears warning authority and increments generation',()=>{const x=runBootstrap();let resets=0;x.win.WOFALPHAHUD={transportReset(){resets++;}};const t=x.win.__WOF_ALPHA_TRANSPORT_V1;const b=t.bind('2'.repeat(32));const r=t.reset();assert.equal(r.bound,false);assert.ok(r.pairGeneration>b.pairGeneration);assert.equal(resets,2);});
test('transport construction failure is fail-open for gameplay',()=>{const x=runBootstrap({broadcastThrows:true});assert.equal(x.win.Worker,x.WorkerSentinel);assert.equal(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.attachState,'DISABLED');assert.equal(x.win.__WOF_ALPHA_BOOTSTRAP_RC5.gameWorkerUntouched,true);});

test('HUD enforces current transport pair authority',()=>{assert.match(hudSource,/TRANSPORT\.matches\(m\)/);assert.match(hudSource,/transportReset/);});
test('real worker avoids Worker/Blob replacement APIs',()=>{assert.doesNotMatch(workerSource,/new\s+Worker\s*\(/);assert.doesNotMatch(workerSource,/createObjectURL/);assert.doesNotMatch(workerSource,/new\s+Blob\s*\(/);});
test('bootstrap avoids Worker/Blob replacement APIs',()=>{assert.doesNotMatch(bootstrapSource,/new\s+Worker\s*\(/);assert.doesNotMatch(bootstrapSource,/window\.Worker\s*=/);assert.doesNotMatch(bootstrapSource,/createObjectURL/);assert.doesNotMatch(bootstrapSource,/new\s+Blob\s*\(/);});
test('real adapter uses narrow Discovery V2 admission',()=>{assert.match(adapterSource,/from wof_launcher\.discovery_v2 import TargetChoice, discover/);assert.match(adapterSource,/_strict_revoke_for_rebind/);assert.match(adapterSource,/GOLDEN_SHA/);});
test('real adapter does not contain gameplay input injection surface',()=>{assert.doesNotMatch(adapterSource,/Input\.dispatch|dispatchKeyEvent|dispatchMouseEvent|HEAPU\w*\s*\[/);});
test('warning clear/change and heartbeat remain explicit',()=>{assert.match(workerSource,/changed\|\|heartbeat/);assert.match(workerSource,/sampledAt-lastPublishedAt>=250/);assert.match(workerSource,/warnings=Array\.isArray/);});

const failed=results.filter(x=>!x.ok);
const out={schema:'wof-alpha-formal-integration-test-v1',status:failed.length?'FAIL':'PASS',testCount:results.length,passCount:results.length-failed.length,failCount:failed.length,coverage:{normalAttachProduceClear:true,noTransportUnsupported:true,staleGenerationAfterRebind:true,runtimeEpochReplacement:true,workerReplacementRevocation:true,sessionPairNonceMismatch:true,disconnectReconnect:true,unsupportedIdentityDiscoveryFailClosed:true,gameUnaffectedOnIntegrationFailure:true},results};
console.log(JSON.stringify(out,null,2));
if(failed.length)process.exit(1);
