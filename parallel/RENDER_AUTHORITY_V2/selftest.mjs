import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const source = fs.readFileSync(new URL('./wof_render_authority_capture_worker.js', import.meta.url), 'utf8');
let now = 1000;
let tick = null;
const heap = new Uint8Array(0x400000);
const heap32 = new Uint32Array(heap.buffer);
heap32[0x2e39e4 >>> 2] = 0x300000;
for (let i=0;i<16;i++) {
  const p=0x1000+i*8;
  heap[p]=0; heap[p+1]=40+i; heap[p+2]=0; heap[p+3]=50+i;
  heap[p+4]=0x12; heap[p+5]=i+1; heap[p+6]=0; heap[p+7]=1;
}
const context = {
  Uint8Array, Uint32Array, ArrayBuffer, Map, Math, JSON,
  Date: {now:()=>now},
  setInterval:(fn)=>{tick=fn;return 1;}, clearInterval:()=>{},
  _0x515056:{HEAPU8:heap,HEAPU32:heap32},
};
context.globalThis=context;
vm.createContext(context);
vm.runInContext(source, context);
const api=context.WOFRENDERAUTHV2;
assert.equal(api.status().overlayEnabled,false);
const regions=api._test.topStructuralRegions(heap,0,0x4000,4);
assert.ok(regions.length>0);
assert.ok(regions.every(x=>x.authority==='UNVERIFIED_CANDIDATE_ONLY'));
const decoded=api._test.decodeEntries(heap,0x1000,false,2);
assert.equal(decoded[0].x9,40);
assert.equal(decoded[0].y9,50);
assert.throws(()=>api.start({worldSha256:'wrong',runtimeEpoch:'0123456789abcdef',rendererEpoch:'fedcba9876543210',authorityKey:'a'}));
assert.throws(()=>api.start({worldSha256:'5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62',runtimeEpoch:'0123456789abcdef',authorityKey:'authority-v2'}));
const status=api.start({worldSha256:'5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62',runtimeEpoch:'0123456789abcdef',rendererEpoch:'fedcba9876543210',authorityKey:'authority-v2'});
assert.equal(status.state,'MEASURING');
assert.equal(status.rendererEpoch,'fedcba9876543210');
assert.equal(status.rendererSourceQualification,'UNVERIFIED_CANDIDATE_ONLY');
assert.equal(status.canonicalNativeContract.accepted,false);
for (let i=0;i<5;i++){ now += 500; tick(); }
assert.ok(api.status().candidateTimelineFrames>0);
now += 31000; tick();
const result=api.result();
assert.equal(result.captureComplete,true);
assert.equal(result.resultVerdict,'BOUNDED_CAPTURE_READY_FOR_RENDER_AUTHORITY_ANALYSIS');
assert.equal(result.guessedConstantsAccepted,false);
assert.equal(result.authorityKey,'authority-v2');
assert.equal(result.rendererEpoch,'fedcba9876543210');
assert.ok(result.candidateTimeline.length>0);
assert.ok(result.candidateTimeline.every(f=>f.regions.every(r=>r.authority==='UNVERIFIED_CANDIDATE_ONLY')));
console.log('render-authority-v2 selftest PASS');
