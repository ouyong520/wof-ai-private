import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const API=require('./gstyphoon_renderer_submit_correlation_probe.js');

function makeFake(){
  const C={
    CURRENT_PROGRAM:1,ARRAY_BUFFER:2,ELEMENT_ARRAY_BUFFER:3,ARRAY_BUFFER_BINDING:4,ELEMENT_ARRAY_BUFFER_BINDING:5,BUFFER_SIZE:6,
    MAX_VERTEX_ATTRIBS:7,VERTEX_ATTRIB_ARRAY_ENABLED:8,VERTEX_ATTRIB_ARRAY_BUFFER_BINDING:9,VERTEX_ATTRIB_ARRAY_SIZE:10,VERTEX_ATTRIB_ARRAY_TYPE:11,VERTEX_ATTRIB_ARRAY_NORMALIZED:12,VERTEX_ATTRIB_ARRAY_STRIDE:13,VERTEX_ATTRIB_ARRAY_POINTER:14,VERTEX_ATTRIB_ARRAY_DIVISOR:15,
    ACTIVE_TEXTURE:16,TEXTURE0:100,TEXTURE_2D:17,TEXTURE_CUBE_MAP:18,TEXTURE_BINDING_2D:19,VIEWPORT:20,SCISSOR_BOX:21,SCISSOR_TEST:22,LINK_STATUS:23,SHADER_TYPE:24,
    FLOAT:30,TRIANGLES:31,UNSIGNED_SHORT:32
  };
  const program={},vs={},fs={},arrayBuffer={},elementBuffer={},texture={};
  const state={program,arrayBuffer,elementBuffer,activeTexture:C.TEXTURE0,texture2D:texture,viewport:new Int32Array([0,0,768,448]),scissor:new Int32Array([2,4,760,440]),scissorEnabled:true,bufferSizes:new Map([[arrayBuffer,4096],[elementBuffer,2048]]),draws:[],uploads:[],textureUploads:[]};
  const attrib={enabled:true,buffer:arrayBuffer,size:4,type:C.FLOAT,normalized:false,stride:16,offset:32,divisor:0};
  const gl={...C,
    getParameter(p){switch(p){case C.CURRENT_PROGRAM:return state.program;case C.ARRAY_BUFFER_BINDING:return state.arrayBuffer;case C.ELEMENT_ARRAY_BUFFER_BINDING:return state.elementBuffer;case C.MAX_VERTEX_ATTRIBS:return 4;case C.ACTIVE_TEXTURE:return state.activeTexture;case C.TEXTURE_BINDING_2D:return state.texture2D;case C.VIEWPORT:return state.viewport;case C.SCISSOR_BOX:return state.scissor;default:return null;}},
    getBufferParameter(target,p){if(p!==C.BUFFER_SIZE)return null;return state.bufferSizes.get(target===C.ARRAY_BUFFER?state.arrayBuffer:state.elementBuffer)||0;},
    getVertexAttrib(i,p){if(i!==0)return p===C.VERTEX_ATTRIB_ARRAY_ENABLED?false:null;switch(p){case C.VERTEX_ATTRIB_ARRAY_ENABLED:return attrib.enabled;case C.VERTEX_ATTRIB_ARRAY_BUFFER_BINDING:return attrib.buffer;case C.VERTEX_ATTRIB_ARRAY_SIZE:return attrib.size;case C.VERTEX_ATTRIB_ARRAY_TYPE:return attrib.type;case C.VERTEX_ATTRIB_ARRAY_NORMALIZED:return attrib.normalized;case C.VERTEX_ATTRIB_ARRAY_STRIDE:return attrib.stride;case C.VERTEX_ATTRIB_ARRAY_DIVISOR:return attrib.divisor;default:return null;}},
    getVertexAttribOffset(i,p){return i===0&&p===C.VERTEX_ATTRIB_ARRAY_POINTER?attrib.offset:0;},
    isEnabled(p){return p===C.SCISSOR_TEST?state.scissorEnabled:false;},
    getAttachedShaders(p){return p===program?[vs,fs]:[];},
    getShaderSource(s){return s===vs?'attribute vec4 a; void main(){gl_Position=a;}':'precision mediump float; void main(){gl_FragColor=vec4(1.0);}';},
    getShaderParameter(s,p){if(p===C.SHADER_TYPE)return s===vs?35633:35632;return null;},
    getProgramParameter(p,q){if(p===program&&q===C.LINK_STATUS)return true;return 0;},
    bufferData(...args){state.uploads.push(['bufferData',...args]);},
    bufferSubData(...args){state.uploads.push(['bufferSubData',...args]);},
    texImage2D(...args){state.textureUploads.push(['texImage2D',...args]);},
    texSubImage2D(...args){state.textureUploads.push(['texSubImage2D',...args]);},
    activeTexture(unit){state.activeTexture=unit;},
    bindTexture(target,tex){if(target===C.TEXTURE_2D)state.texture2D=tex;},
    bindBufferRange(){},bindBufferBase(){},
    drawArrays(...args){state.draws.push(['drawArrays',...args]);return 7;},
    drawElements(...args){state.draws.push(['drawElements',...args]);return 8;}
  };
  return{gl,state,objects:{program,vs,fs,arrayBuffer,elementBuffer,texture}};
}
function binding(){return{runtimeEpoch:'runtime-epoch-0001',rendererEpoch:'renderer-epoch-0001',authorityKey:'authority-key-0001'};}
function baseline(x=120,y=80){return{classification:'UNVERIFIED_AUTO_BASELINE',rendererSourceProof:null,authorityEligibility:{p29Pass:false,p32NativeMarkerQualification:false,p36RendererSourceTrace:false,p34RetryReadiness:false,promotion:false},state:'READY',controller:{visibleFresh:true,envelopeState:'TRACKING',tracks:{P1:{state:'TRACKED',observed:true,x,y,coordinateClass:'OBSERVED_DIAGNOSTIC_PIXEL_STRUCTURE',reacquireCount:1},P2:{state:'LOST',observed:false},P3:{state:'LOST',observed:false}}}};}

// 1. exact draw/state capture, CPU payload identity, bounded termination, and teardown.
{
  const {gl,state}=makeFake(),root={};
  const native={drawArrays:gl.drawArrays,drawElements:gl.drawElements,bufferData:gl.bufferData,bufferSubData:gl.bufferSubData};
  const probe=API.createProbe({root,gl,captureRafFrames:false,baselineProvider:()=>baseline(),limits:{maxSubmissions:2,maxWallMs:60000,maxRawBytesPerPayload:32}});
  assert.equal(probe.start(binding()).state,'OBSERVING');
  probe.markFrame('frame-A',1.25);
  const data=new Uint16Array([0x1122,0x3344,0x5566]);
  gl.bufferData(gl.ARRAY_BUFFER,data,35040,1,1);
  gl.bufferSubData(gl.ARRAY_BUFFER,64,data,1,1);
  gl.drawArrays(gl.TRIANGLES,3,6);
  gl.drawElements(gl.TRIANGLES,12,gl.UNSIGNED_SHORT,128);
  const r=probe.result();
  assert.equal(r.schema,'wof-gstyphoon-renderer-correlation-probe-v1');
  assert.equal(r.state,'CAPTURE_READY');
  assert.equal(r.reason,'BOUNDED_SUBMISSION_LIMIT_REACHED');
  assert.equal(r.submissions.length,2);
  assert.deepEqual(r.submissions[0].draw,{method:'drawArrays',mode:gl.TRIANGLES,first:3,count:6,indexType:null,indexByteOffset:null});
  assert.equal(r.submissions[1].draw.indexByteOffset,128);
  assert.equal(r.submissions[0].program.shaderCount,2);
  assert.equal(r.submissions[0].buffers.array.sizeBytes,4096);
  assert.equal(r.submissions[0].vertexAttribs[0].offset,32);
  assert.deepEqual(r.submissions[0].viewport,[0,0,768,448]);
  assert.deepEqual(r.submissions[0].scissorBox,[2,4,760,440]);
  assert.equal(r.submissions[0].diagnosticCorrelation.classification,'UNVERIFIED_AUTO_BASELINE');
  assert.equal(r.submissions[0].diagnosticCorrelation.players.P1.x,120);
  assert.equal(r.authorityEligible,false);assert.equal(Object.hasOwn(r,'rendererSourceProof'),false);
  assert.equal(r.bufferUploads[0].payload.sourceElementOffset,1);
  assert.equal(r.bufferUploads[0].payload.sourceElementLength,1);
  assert.equal(r.bufferUploads[0].payload.totalBytes,2);
  assert.equal(r.bufferUploads[1].destinationByteOffset,64);
  assert.equal(r.bufferUploads[0].payload.hash.complete,true);
  assert.equal(r.mappingAssessment.selectionMade,false);
  assert.equal(gl.drawArrays,native.drawArrays);assert.equal(gl.drawElements,native.drawElements);assert.equal(gl.bufferData,native.bufferData);assert.equal(gl.bufferSubData,native.bufferSubData);
  assert.equal(state.draws.length,2);
}

// 2. texture/range observation stays diagnostic and exact to observed hook calls.
{
  const {gl}=makeFake(),root={};const probe=API.createProbe({root,gl,captureRafFrames:false,baselineProvider:()=>baseline(),limits:{maxSubmissions:5,maxWallMs:60000}});probe.start(binding());
  const t2={};gl.activeTexture(gl.TEXTURE0+1);gl.bindTexture(gl.TEXTURE_2D,t2);gl.bindBufferRange(35345,2,{},96,512);gl.texSubImage2D(gl.TEXTURE_2D,0,0,0,1,1,6408,5121,new Uint8Array([1,2,3,4]));gl.drawArrays(gl.TRIANGLES,0,3);probe.stop();const r=probe.result();
  assert.equal(r.textureUploads.length,1);assert.equal(r.textureUploads[0].payload.totalBytes,4);assert.equal(r.submissions[0].buffers.ranges[0].offset,96);assert.equal(r.submissions[0].buffers.ranges[0].size,512);assert.equal(r.submissions[0].textures.semanticBankIdentityAvailable,false);
}

// 3. stale/mixed authority binding rejects further correlation and restores hooks.
{
  const {gl}=makeFake(),root={};let current=binding();const native=gl.drawArrays;const probe=API.createProbe({root,gl,captureRafFrames:false,bindingProvider:()=>current,baselineProvider:()=>baseline(),limits:{maxSubmissions:10,maxWallMs:60000}});probe.start(binding());gl.drawArrays(gl.TRIANGLES,0,3);current={...current,rendererEpoch:'renderer-epoch-STALE'};gl.drawArrays(gl.TRIANGLES,0,3);const r=probe.result();
  assert.equal(r.state,'REJECTED');assert.equal(r.reason,'STALE_OR_MIXED_AUTHORITY_BINDING');assert.equal(r.submissions.length,1);assert.equal(gl.drawArrays,native);
}

// 4. ambiguity is preserved: multiple exact renderer-state groups are never ranked/selected.
{
  const {gl,state}=makeFake(),root={};const probe=API.createProbe({root,gl,captureRafFrames:false,baselineProvider:()=>baseline(),limits:{maxSubmissions:10,maxWallMs:60000}});probe.start(binding());gl.drawArrays(gl.TRIANGLES,0,3);state.program={};gl.drawArrays(gl.TRIANGLES,0,3);probe.stop();const r=probe.result();
  assert.equal(r.submissionGroups.length,2);assert.equal(r.mappingAssessment.selectionMade,false);assert.equal(r.mappingAssessment.selectedGroup,null);assert.equal(r.mappingAssessment.ambiguityPreserved,true);assert.equal(r.mappingAssessment.status,'DIAGNOSTIC_ONLY_NO_AUTHORITY_SELECTION');
}

// 5. baseline authority impersonation is rejected as correlation input, not converted into proof.
{
  const {gl}=makeFake(),root={};const bad=baseline();bad.rendererSourceProof={fake:true};const probe=API.createProbe({root,gl,captureRafFrames:false,baselineProvider:()=>bad,limits:{maxSubmissions:1,maxWallMs:60000}});probe.start(binding());gl.drawArrays(gl.TRIANGLES,0,3);const r=probe.result();
  assert.equal(r.submissions[0].diagnosticCorrelation.accepted,false);assert.equal(r.submissions[0].diagnosticCorrelation.reason,'BASELINE_PROOF_BOUNDARY_VIOLATION');assert.equal(Object.hasOwn(r,'rendererSourceProof'),false);assert.equal(r.authorityEligible,false);
  const forbiddenA='__WOF_'+'NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__';const forbiddenB='WOFNativeMarkerRenderer'+'SubmitSourceV1';assert.equal(root[forbiddenA],undefined);assert.equal(root[forbiddenB],undefined);
}

// 6. explicit stop tears down all instrumentation deterministically.
{
  const {gl}=makeFake(),root={requestAnimationFrame(cb){cb(5);return 1;}};const before={draw:gl.drawArrays,raf:root.requestAnimationFrame};const probe=API.createProbe({root,gl,baselineProvider:()=>baseline(),limits:{maxWallMs:60000}});probe.start(binding());probe.stop('SYNTHETIC_DONE');assert.equal(gl.drawArrays,before.draw);assert.equal(root.requestAnimationFrame,before.raf);assert.deepEqual(probe.result().teardown.conflicts,[]);
}

console.log('P42 renderer correlation probe self-check: 6/6 PASS');
