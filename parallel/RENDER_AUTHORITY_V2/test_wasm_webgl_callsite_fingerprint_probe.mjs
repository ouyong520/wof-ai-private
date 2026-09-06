import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const API=require('./wasm_webgl_callsite_fingerprint_probe.js');

function binding(){return{runtimeEpoch:'runtime-epoch-p46-0001',rendererEpoch:'renderer-epoch-p46-0001',authorityKey:'authority-key-p46-0001'};}
function makeFake(){
  const C={ARRAY_BUFFER:1,ELEMENT_ARRAY_BUFFER:2,ARRAY_BUFFER_BINDING:3,ELEMENT_ARRAY_BUFFER_BINDING:4,TRIANGLES:5,UNSIGNED_SHORT:6,FLOAT:7};
  const state={arrayBuffer:null,elementBuffer:null,draws:[],bufferCalls:[],attribCalls:[]};
  const gl={...C,
    getParameter(p){if(p===C.ARRAY_BUFFER_BINDING)return state.arrayBuffer;if(p===C.ELEMENT_ARRAY_BUFFER_BINDING)return state.elementBuffer;return null;},
    bindBuffer(target,buffer){if(target===C.ARRAY_BUFFER)state.arrayBuffer=buffer;if(target===C.ELEMENT_ARRAY_BUFFER)state.elementBuffer=buffer;state.bufferCalls.push(['bindBuffer',target,buffer]);},
    bindBufferBase(target,index,buffer){state.bufferCalls.push(['bindBufferBase',target,index,buffer]);},
    bindBufferRange(target,index,buffer,offset,size){state.bufferCalls.push(['bindBufferRange',target,index,buffer,offset,size]);},
    bufferData(...args){state.bufferCalls.push(['bufferData',...args]);},
    bufferSubData(...args){state.bufferCalls.push(['bufferSubData',...args]);},
    vertexAttribPointer(...args){state.attribCalls.push(['vertexAttribPointer',...args]);},
    vertexAttribIPointer(...args){state.attribCalls.push(['vertexAttribIPointer',...args]);},
    enableVertexAttribArray(...args){state.attribCalls.push(['enableVertexAttribArray',...args]);},
    disableVertexAttribArray(...args){state.attribCalls.push(['disableVertexAttribArray',...args]);},
    vertexAttribDivisor(...args){state.attribCalls.push(['vertexAttribDivisor',...args]);},
    drawArrays(...args){state.draws.push(['drawArrays',...args]);return 11;},
    drawElements(...args){state.draws.push(['drawElements',...args]);return 12;}
  };
  return{gl,state};
}
function providerFor(map){return meta=>map[meta.method]||map.default||'';}
const chromeWasmStack=`Error: P46_CALLSITE\n    at p46WrappedWebGLBoundary (probe.js:300:20)\n    at _glDrawArrays (gstyphoon.js:220:17)\n    at renderObject (wasm://wasm/9e91:wasm-function[417]:0x1a2b)\n    at mainLoop (gstyphoon.js:900:3)`;

// 1. Raw stack, normalized fingerprint, exact browser-exposed wasm fields, JS caller, Module/asm identity and draw sequence.
{
  const {gl}=makeFake();const root={Module:{asm:{}}};
  const probe=API.createProbe({root,gl,stackProvider:providerFor({drawArrays:chromeWasmStack}),limits:{maxWallMs:60000,maxDrawSubmissions:8}});
  assert.equal(probe.start(binding()).state,'OBSERVING');
  gl.drawArrays(gl.TRIANGLES,0,6);gl.drawArrays(gl.TRIANGLES,6,6);probe.stop('SYNTHETIC_DONE');
  const r=probe.result();
  assert.equal(r.schema,'wof-wasm-webgl-callsite-fingerprint-probe-v1');
  assert.equal(r.draws.length,2);assert.equal(r.draws[0].drawSubmissionSequence,1);assert.equal(r.draws[1].drawSubmissionSequence,2);
  assert.equal(r.draws[0].callsite.rawStackStatus,'AVAILABLE');assert.match(r.draws[0].callsite.rawStack,/wasm-function\[417\]/);
  assert.equal(r.draws[0].callsite.normalizedCallsiteFingerprint.status,'AVAILABLE');
  assert.equal(r.draws[0].callsite.normalizedCallsiteFingerprint.value,r.draws[1].callsite.normalizedCallsiteFingerprint.value);
  assert.deepEqual(r.draws[0].callsite.wasm.functionIndices,[417]);
  assert.deepEqual(r.draws[0].callsite.wasm.functionNames,['renderObject']);
  assert.deepEqual(r.draws[0].callsite.wasm.offsets,['0x1a2b']);
  assert.equal(r.draws[0].callsite.jsWrapperOrImport.immediateJsCaller.functionName,'_glDrawArrays');
  assert.equal(r.draws[0].callsite.jsWrapperOrImport.semanticRole,'UNRESOLVED');
  assert.equal(r.moduleSurfaceAtStart.Module.status,'AVAILABLE');assert.equal(r.moduleSurfaceAtStart.ModuleAsm.status,'AVAILABLE');assert.equal(r.moduleSurfaceAtStart.relationship,'DISTINCT_OBJECTS');
  assert.deepEqual(r.draws[0].binding,binding());assert.equal(r.mappingAssessment.selectionMade,false);assert.equal(r.authorityEligible,false);
}

// 2. No WebAssembly frame produces explicit NOT_AVAILABLE instead of a guessed function/index/offset.
{
  const {gl}=makeFake();const root={Module:{asm:{}}};
  const stack=`Error\n at p46WrappedWebGLBoundary (probe.js:1:1)\n at _glDrawElements (gstyphoon.js:311:9)\n at mainLoop (gstyphoon.js:900:3)`;
  const probe=API.createProbe({root,gl,stackProvider:providerFor({drawElements:stack}),limits:{maxWallMs:60000}});probe.start(binding());gl.drawElements(gl.TRIANGLES,4,gl.UNSIGNED_SHORT,64);probe.stop();
  const wasm=probe.result().draws[0].callsite.wasm;
  assert.equal(wasm.status,'NOT_AVAILABLE');assert.deepEqual(wasm.functionIndices,['NOT_AVAILABLE']);assert.deepEqual(wasm.functionNames,['NOT_AVAILABLE']);assert.deepEqual(wasm.offsets,['NOT_AVAILABLE']);
}

// 3. A browser-exposed wasm frame without index/name/offset remains UNRESOLVED; nothing is invented.
{
  const {gl}=makeFake();const root={Module:{asm:{}}};
  const stack=`Error\n at p46WrappedWebGLBoundary (probe.js:1:1)\n at wasm://wasm/abcdef`;
  const probe=API.createProbe({root,gl,stackProvider:providerFor({drawArrays:stack}),limits:{maxWallMs:60000}});probe.start(binding());gl.drawArrays(gl.TRIANGLES,0,3);probe.stop();
  const wasm=probe.result().draws[0].callsite.wasm;
  assert.equal(wasm.status,'AVAILABLE');assert.equal(wasm.functionIndexStatus,'UNRESOLVED');assert.equal(wasm.functionNameStatus,'UNRESOLVED');assert.equal(wasm.offsetStatus,'UNRESOLVED');
  assert.deepEqual(wasm.functionIndices,['UNRESOLVED']);assert.deepEqual(wasm.offsets,['UNRESOLVED']);
}

// 4. Buffer uploads and vertex setup associate to a later draw only through exact object/attrib state identity; unrelated buffers are excluded.
{
  const {gl}=makeFake();const root={Module:{asm:{}}};const b1={},b2={},unrelated={};
  const stacks={default:`Error\n at p46WrappedWebGLBoundary (probe.js:1:1)\n at jsWrapper (gstyphoon.js:50:2)`};
  const probe=API.createProbe({root,gl,stackProvider:providerFor(stacks),limits:{maxWallMs:60000,maxEvents:64}});probe.start(binding());
  gl.bindBuffer(gl.ARRAY_BUFFER,b1);gl.bufferData(gl.ARRAY_BUFFER,new Uint8Array([1,2,3]),35040);gl.vertexAttribPointer(0,2,gl.FLOAT,false,8,0);gl.enableVertexAttribArray(0);
  gl.bindBuffer(gl.ARRAY_BUFFER,unrelated);gl.bufferData(gl.ARRAY_BUFFER,new Uint8Array([9,9]),35040);gl.bindBuffer(gl.ARRAY_BUFFER,b1);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,b2);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array([0,1,2]),35040);
  gl.drawElements(gl.TRIANGLES,3,gl.UNSIGNED_SHORT,0);probe.stop();
  const draw=probe.result().draws[0];
  assert.equal(draw.exactAssociations.arrayBufferUploads.length,1);assert.equal(draw.exactAssociations.elementArrayBufferUploads.length,1);
  assert.equal(draw.exactAssociations.arrayBufferUploads[0].bufferId,draw.buffers.arrayBufferId);
  assert.equal(draw.exactAssociations.elementArrayBufferUploads[0].bufferId,draw.buffers.elementArrayBufferId);
  assert.equal(draw.exactAssociations.vertexAttribSetups.length,1);assert.equal(draw.exactAssociations.vertexAttribSetups[0].bufferId,draw.buffers.arrayBufferId);
  assert.equal(draw.exactAssociations.associationRule,'EXACT_OBJECT_OR_ATTRIB_STATE_IDENTITY_ONLY');assert.equal(draw.exactAssociations.semanticSelectionMade,false);
}

// 5. Stale runtime/renderer/authority binding rejects new evidence while leaving the actual GL call untouched and restoring hooks.
{
  const {gl,state}=makeFake();const root={Module:{asm:{}}};let current=binding();const native=gl.drawArrays;
  const probe=API.createProbe({root,gl,bindingProvider:()=>current,stackProvider:providerFor({drawArrays:chromeWasmStack}),limits:{maxWallMs:60000}});probe.start(binding());gl.drawArrays(gl.TRIANGLES,0,3);current={...current,rendererEpoch:'renderer-epoch-stale'};gl.drawArrays(gl.TRIANGLES,3,3);
  const r=probe.result();assert.equal(r.state,'REJECTED');assert.equal(r.reason,'STALE_OR_MIXED_AUTHORITY_BINDING');assert.equal(r.draws.length,1);assert.equal(state.draws.length,2);assert.equal(gl.drawArrays,native);assert.equal(r.teardown.complete,true);
}

// 6. Module/Module.asm identity drift is rejected instead of mixing call-site evidence across runtime surfaces.
{
  const {gl,state}=makeFake();const root={Module:{asm:{}}};const native=gl.drawArrays;
  const probe=API.createProbe({root,gl,stackProvider:providerFor({drawArrays:chromeWasmStack}),limits:{maxWallMs:60000}});probe.start(binding());gl.drawArrays(gl.TRIANGLES,0,3);root.Module={asm:{}};gl.drawArrays(gl.TRIANGLES,3,3);
  const r=probe.result();assert.equal(r.state,'REJECTED');assert.equal(r.reason,'MODULE_OR_ASM_IDENTITY_CHANGED');assert.equal(r.draws.length,1);assert.equal(state.draws.length,2);assert.equal(gl.drawArrays,native);assert.equal(r.moduleSurfaceAtStart.relationship,'DISTINCT_OBJECTS');
}

// 7. Bounds and proof boundary: limit seals deterministically and no forbidden authority surface/property is created.
{
  const {gl}=makeFake();const root={Module:{asm:{}}};const native=gl.drawArrays;
  const probe=API.createProbe({root,gl,stackProvider:providerFor({drawArrays:chromeWasmStack}),limits:{maxWallMs:60000,maxDrawSubmissions:1}});probe.start(binding());gl.drawArrays(gl.TRIANGLES,0,3);const r=probe.result();
  assert.equal(r.state,'CAPTURE_READY');assert.equal(r.reason,'BOUNDED_DRAW_LIMIT_REACHED');assert.equal(gl.drawArrays,native);assert.equal(r.teardown.complete,true);
  assert.equal(Object.hasOwn(r,'rendererSourceProof'),false);assert.equal(r.proofBoundary.nativeMarkerRendererSource,false);assert.equal(r.proofBoundary.rendererAuthorityProof,false);assert.equal(r.proofBoundary.p29Pass,false);assert.equal(r.proofBoundary.p32Qualification,false);
  assert.equal(root.__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__,undefined);assert.equal(root.WOFNativeMarkerRendererSubmitSourceV1,undefined);
  assert.equal(r.mappingAssessment.guessedWasmSymbol,false);assert.equal(r.mappingAssessment.guessedWasmOffset,false);assert.equal(r.mappingAssessment.orderOnlySelection,false);assert.equal(r.mappingAssessment.timingOnlySelection,false);
}

console.log('P46 WASM/WebGL call-site fingerprint probe self-check: 7/7 PASS');
