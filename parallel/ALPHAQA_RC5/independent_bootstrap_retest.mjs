import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const src=fs.readFileSync(path.resolve(here,'../../product/alpha/wof_alpha_bootstrap.user.js'),'utf8');

assert(!/window\.Worker\s*=/.test(src),'RC5 must not assign window.Worker');
assert(!/(?:new\s+Blob\s*\(|createObjectURL\s*\(|importScripts\s*\()/.test(src),'RC5 must not contain Blob/ObjectURL/importScripts Worker wrapping');

function run({bcThrows=false,cryptoThrows=false,surface=false}={}){
  const calls={worker:[],fetch:0,blob:0,url:0,timers:0};
  function NativeWorker(url,options){this.url=url;this.options=options;calls.worker.push({url,options});}
  const channels=[];
  class BC{
    constructor(name){if(bcThrows)throw new Error('bc blocked');this.name=name;channels.push(this);}
    close(){}
  }
  const window={
    Worker:NativeWorker,
    addEventListener(){},
    I_GF1TC:surface?{}:null,
    I_fdC8Q:surface?{drawArrays(){}}:null
  };
  const crypto={
    getRandomValues(a){
      if(cryptoThrows)throw new Error('rng blocked');
      for(let i=0;i<a.length;i++)a[i]=i+1;
      return a;
    }
  };
  const context={
    window,crypto,BroadcastChannel:BC,Date,Uint8Array,
    fetch:async()=>{calls.fetch++;return {ok:true,async text(){return '';}};},
    setTimeout(){calls.timers++;return 1;},clearTimeout(){},
    Blob:class{constructor(){calls.blob++;}},
    URL:{createObjectURL(){calls.url++;return 'blob:x';}},
    console:{log(){},warn(){}}
  };
  assert.doesNotThrow(()=>vm.runInNewContext(src,context,{filename:'wof_alpha_bootstrap.user.js'}));
  return{window,NativeWorker,channels,calls};
}

{
  const x=run();
  assert.strictEqual(x.window.Worker,x.NativeWorker,'native Worker identity must remain exact');
  assert.equal(x.calls.worker.length,0,'bootstrap must create zero game Workers');
  assert.equal(x.calls.fetch,0,'no HUD/loader fetch before detector pairing');
  assert.equal(x.calls.blob,0,'no Blob creation');
  assert.equal(x.calls.url,0,'no ObjectURL creation');
  assert.equal(x.window.__WOF_ALPHA_BOOTSTRAP_RC5.attachState,'WAITING_EXTERNAL_TRANSPORT');
  assert.equal(x.window.__WOF_ALPHA_BOOTSTRAP_RC5.gameWorkerUntouched,true);
  assert.match(x.window.__WOF_ALPHA_BOOTSTRAP_RC5.session,/^[0-9a-f]{32}$/);

  const options={type:'module',name:'gstyphoon',credentials:'include'};
  const url='https://game.invalid/gstyphoon.js';
  const w=new x.window.Worker(url,options);
  assert.equal(w.url,url,'game Worker URL must pass through unchanged');
  assert.strictEqual(w.options,options,'game Worker options object must pass through unchanged');
}

{
  const x=run({bcThrows:true});
  assert.strictEqual(x.window.Worker,x.NativeWorker,'BroadcastChannel failure must leave Worker untouched');
  assert.equal(x.window.__WOF_ALPHA_BOOTSTRAP_RC5.attachState,'DISABLED');
  assert.equal(x.calls.worker.length,0);
  assert.equal(x.calls.fetch,0);
  assert.equal(x.calls.blob,0);
  assert.equal(x.calls.url,0);
}

{
  const x=run({cryptoThrows:true});
  assert.strictEqual(x.window.Worker,x.NativeWorker,'secure-random failure must leave Worker untouched');
  assert.equal(x.window.__WOF_ALPHA_BOOTSTRAP_RC5.attachState,'DISABLED');
  assert.equal(x.calls.worker.length,0);
  assert.equal(x.calls.fetch,0);
  assert.equal(x.calls.blob,0);
  assert.equal(x.calls.url,0);
}

{
  const x=run({surface:true});
  const state=x.window.__WOF_ALPHA_BOOTSTRAP_RC5;
  const bc=x.channels[0];
  bc.onmessage({data:{schema:'wof-alpha-v2',session:'ffffffffffffffffffffffffffffffff',kind:'state'}});
  await Promise.resolve();
  assert.equal(x.calls.fetch,0,'foreign-session state must not pair or start HUD');
  bc.onmessage({data:{schema:'wof-alpha-v2',session:state.session,kind:'state'}});
  await new Promise(r=>setImmediate(r));
  assert.equal(state.attachState,'PAIRED');
  assert.equal(x.calls.fetch,1,'only a valid paired state may start HUD loader');
}

console.log(JSON.stringify({
  tests:'PASS',
  bootstrapWorkerIdentityPreserved:true,
  gameWorkerUrlAndOptionsUnchanged:true,
  noPrePairHudFetch:true,
  noBlobOrObjectUrl:true,
  broadcastChannelFailureGameplayFailOpen:true,
  secureRandomFailureGameplayFailOpen:true,
  sessionIsolationBeforeHudAttach:true
},null,2));
