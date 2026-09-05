import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);

globalThis.window=globalThis;globalThis.self=globalThis;
const ctx2d={clearRect(){},fillRect(){},strokeRect(){},fillText(){},set fillStyle(v){},set strokeStyle(v){},set lineWidth(v){},set textBaseline(v){},set textAlign(v){},set font(v){}};
const makeCanvas=()=>({width:768,height:448,getContext(){return ctx2d;},getBoundingClientRect(){return{width:768,height:448};}});
globalThis.document={fullscreenElement:null,getElementById(){return globalThis.I_GF1TC;},createElement(){return makeCanvas();}};
class MockGL{drawArrays(){this.nativeCalls=(this.nativeCalls||0)+1;}}
globalThis.WebGLRenderingContext=MockGL;
const gl=new MockGL();
Object.assign(gl,{drawingBufferWidth:768,drawingBufferHeight:448,
  ACTIVE_TEXTURE:1,TEXTURE_BINDING_2D:2,CURRENT_PROGRAM:3,ARRAY_BUFFER_BINDING:4,VIEWPORT:5,BLEND:6,DEPTH_TEST:7,CULL_FACE:8,SCISSOR_TEST:9,
  BLEND_SRC_RGB:10,BLEND_DST_RGB:11,BLEND_SRC_ALPHA:12,BLEND_DST_ALPHA:13,BLEND_EQUATION_RGB:14,BLEND_EQUATION_ALPHA:15,COLOR_WRITEMASK:16,
  UNPACK_FLIP_Y_WEBGL:17,UNPACK_PREMULTIPLY_ALPHA_WEBGL:18,VERTEX_ATTRIB_ARRAY_ENABLED:19,VERTEX_ATTRIB_ARRAY_BUFFER_BINDING:20,VERTEX_ATTRIB_ARRAY_SIZE:21,
  VERTEX_ATTRIB_ARRAY_TYPE:22,VERTEX_ATTRIB_ARRAY_NORMALIZED:23,VERTEX_ATTRIB_ARRAY_STRIDE:24,VERTEX_ATTRIB_ARRAY_POINTER:25,TEXTURE0:26,
  VERTEX_SHADER:27,FRAGMENT_SHADER:28,COMPILE_STATUS:29,LINK_STATUS:30,TEXTURE_2D:31,TEXTURE_MIN_FILTER:32,TEXTURE_MAG_FILTER:33,LINEAR:34,
  TEXTURE_WRAP_S:35,TEXTURE_WRAP_T:36,CLAMP_TO_EDGE:37,RGBA:38,UNSIGNED_BYTE:39,TRIANGLES:40,STREAM_DRAW:41,FLOAT:42,SRC_ALPHA:43,ONE_MINUS_SRC_ALPHA:44,
  createShader(){return{};},shaderSource(){},compileShader(){},getShaderParameter(){return true;},getShaderInfoLog(){return'';},deleteShader(){},createProgram(){return{};},
  attachShader(){},bindAttribLocation(){},linkProgram(){},getProgramParameter(){return true;},getProgramInfoLog(){return'';},deleteProgram(){},getUniformLocation(){return{};},
  createBuffer(){return{};},createTexture(){return{};},deleteTexture(){},deleteBuffer(){},activeTexture(){},bindTexture(){},pixelStorei(){},texParameteri(){},texImage2D(){},
  viewport(){},disable(){},enable(){},blendFunc(){},blendFuncSeparate(){},blendEquationSeparate(){},colorMask(){},useProgram(){},bindBuffer(){},bufferData(){},enableVertexAttribArray(){},
  disableVertexAttribArray(){},vertexAttribPointer(){},uniform1i(){},isEnabled(){return false;},getVertexAttrib(){return 0;},getVertexAttribOffset(){return 0;},
  getParameter(key){if(key===this.VIEWPORT)return[0,0,768,448];if(key===this.COLOR_WRITEMASK)return[true,true,true,true];if(key===this.ACTIVE_TEXTURE)return this.TEXTURE0;return 0;}
});
globalThis.I_GF1TC=makeCanvas();globalThis.I_fdC8Q=gl;
globalThis.__WOF_ALPHA_CONFIG={release:'wof-alpha-rc3',session:'1234567890abcdef',channel:'p18-selfcheck'};
globalThis.__WOF_ALPHA_TRANSPORT_V1={version:'wof-alpha-safe-transport-v1',matches(){return true;}};
globalThis.WOFAlphaHudModel={summarizeWarnings(rows){const r=Array.isArray(rows)?rows:[];return{count:r.length,lines:r.map(x=>x.target||'?'),groups:{}};}};
globalThis.WOFAlphaEnemyTargetLabels={buildPlan(){return{labels:[],suppressed:[]};}};
globalThis.WOFAlphaPlayerHeadWarning={MAX_PLAYER_AGE_MS:300,buildPlan(){return{anchored:[],fixed:[],suppressed:[]};}};
globalThis.WOFAlphaCanonicalAnchorEnvelope={DEFAULT_MAX_AGE_MS:300,
  validateAuthorityBinding(b){if(!b||!b.authorityKey||!b.runtimeEpoch||!b.rendererEpoch)return{ok:false,reason:'BAD'};return{ok:true,value:{authorityKey:b.authorityKey,runtimeEpoch:b.runtimeEpoch,rendererEpoch:b.rendererEpoch,worldSha256:b.worldSha256??null}};},
  normalizeEnvelope({records,authorityBinding}){return{ok:true,schema:'wof-alpha-canonical-anchor-envelope-v1',authority:{...authorityBinding,worldSha256:authorityBinding.worldSha256??null},records:records||[],ready:records||[],suppressed:[]};},
  toEnemyAnchorArray(env){return(env.records||[]).filter(x=>x.kind==='enemy').map(x=>({slot:Number(x.actor.split('-').pop()),actor:x.actor,generation:x.generation,sampleAt:x.sampleAt,canonicalAnchor:x.canonicalAnchor}));},
  toPlayerAnchorSamples(env){const out={};for(const x of env.records||[])if(x.kind==='player')out[x.actor]={canonicalAnchor:x.canonicalAnchor,sampleAt:x.sampleAt};return out;}
};
globalThis.WOFAlphaCanonicalOverlayPlan={buildCanonicalPlan(args){
  const b=args.canonicalAuthority;
  const enemy=args.enemy.markers.length&&args.enemy.canonicalAnchors.length?[{
    label:'1P',target:'P1',actor:'enemy-slot-0',generation:7,sourceId:'enemy-slot-0',anchorNative:{x:25,y:30},
    drawRectDb:{x:50,y:50,width:30,height:18},mappingKey:'enemy-map',authorityKey:b.authorityKey,runtimeEpoch:b.runtimeEpoch,rendererEpoch:b.rendererEpoch
  }]:[];
  const player=args.player.warnings.length&&args.player.canonicalAnchors.P1?[{
    player:'P1',warning:{target:'P1',kind:'danger'},warningCount:1,
    anchor:{player:'P1',generation:3,nativeX:40,nativeY:35,mappingKey:'player-map',authorityKey:b.authorityKey,runtimeEpoch:b.runtimeEpoch,rendererEpoch:b.rendererEpoch},
    drawRectDb:{x:80,y:70,width:84,height:26}
  }]:[];
  return{mode:'canonical-render-anchor',coordinateSpace:'webgl-drawing-buffer',fallback:'NONE',state:'READY',reason:null,
    drawIntents:[...enemy.map(payload=>({kind:'enemy-target-label',payload})),...player.map(payload=>({kind:'player-danger-warning',payload}))],enemyTargetLabels:enemy,playerDangerWarnings:player,
    suppression:{enemy:[],player:[],global:[]},diagnostics:{emitted:{enemyTargetLabels:enemy.length,playerDangerWarnings:player.length,total:enemy.length+player.length}}};
}};
let bcInstance=null;globalThis.BroadcastChannel=class{constructor(){bcInstance=this;}close(){}};
require('./wof_alpha_hud.js');
const hud=globalThis.WOFALPHAHUD;assert.ok(hud);assert.equal(typeof hud.canonicalDrawEvidence,'function');
assert.equal(typeof hud.bindP1HeadTrackerAuthority,'function');assert.equal(typeof hud.setFixedDrawSmokeEnabled,'function');
const binding={authorityKey:'authority-1',runtimeEpoch:'runtime-epoch-0001',rendererEpoch:'renderer-epoch-01',worldSha256:'a'.repeat(64)};
const newBinding={authorityKey:'authority-2',runtimeEpoch:'runtime-epoch-0002',rendererEpoch:'renderer-epoch-02',worldSha256:'b'.repeat(64)};
const now=Date.now();
const payloadFor=(b)=>({schema:'wof-alpha-canonical-anchor-runtime-envelope-input-v1',sequence:11,authorityBinding:b,records:[
  {kind:'enemy',actor:'enemy-slot-0',generation:7,sampleAt:now,canonicalAnchor:{state:'READY'}},
  {kind:'player',actor:'P1',generation:3,sampleAt:now,canonicalAnchor:{state:'READY'}}
]});
function feedInputs(b){
  bcInstance.onmessage({data:{schema:'wof-alpha-v2',session:'1234567890abcdef',kind:'state',sampleAt:now-5,runtimeEpoch:b.runtimeEpoch,warnings:[{target:'P1',kind:'danger'}]}});
  bcInstance.onmessage({data:{schema:'wof-alpha-v2',session:'1234567890abcdef',kind:'enemy-target-markers',markers:[{slot:0,target7E:0,target:'P1',sampleAt:now-5,confidence:1}]}});
}

hud.bindCanonicalOverlayAuthority(binding);feedInputs(binding);
let st=hud.ingestCanonicalAnchorEnvelope(payloadFor(binding));assert.equal(st.state,'READY');
let evidence=hud.canonicalDrawEvidence();assert.equal(evidence.entryCount,0);assert.equal(evidence.reason,'HUD_INGEST_ACCEPTED_WAITING_FOR_DRAW');assert.equal(evidence.visibleProof,'NOT_PROVEN');
gl.drawArrays(gl.TRIANGLES,0,3);
evidence=hud.canonicalDrawEvidence();assert.equal(evidence.evidenceState,'CANONICAL_DRAW_ACKNOWLEDGED');assert.equal(evidence.entryCount,2);assert.equal(evidence.entries[0].kind,'enemy-target-label');assert.equal(evidence.entries[1].kind,'player-danger-warning');
assert.deepEqual([evidence.entries[0].nativeX,evidence.entries[0].nativeY],[25,30]);assert.deepEqual([evidence.entries[1].nativeX,evidence.entries[1].nativeY],[40,35]);
for(const row of evidence.entries){assert.equal(row.completed,true);assert.equal(row.visibleProof,'NOT_PROVEN');assert.equal(row.authority.rendererEpoch,binding.rendererEpoch);assert.equal(row.screenshotAuthority,false);assert.equal(row.worldProjectionAuthority,false);}
const oldGeneration=evidence.evidenceGeneration;
hud.bindCanonicalOverlayAuthority(newBinding);evidence=hud.canonicalDrawEvidence();assert.equal(evidence.entryCount,0);assert.ok(evidence.evidenceGeneration>oldGeneration);assert.equal(evidence.authority.authorityKey,newBinding.authorityKey);
feedInputs(newBinding);st=hud.ingestCanonicalAnchorEnvelope({...payloadFor(newBinding),authorityBinding:{...newBinding,rendererEpoch:'renderer-epoch-bad'}});assert.equal(st.state,'SUPPRESSED');
gl.drawArrays(gl.TRIANGLES,0,3);evidence=hud.canonicalDrawEvidence();assert.equal(evidence.entryCount,0);
hud.ingestCanonicalAnchorEnvelope(payloadFor(newBinding));
for(let i=0;i<70;i++)gl.drawArrays(gl.TRIANGLES,0,3);
evidence=hud.canonicalDrawEvidence();assert.equal(evidence.entryCount,128);assert.equal(evidence.maxEntries,128);assert.ok(evidence.entries[0].sequence<evidence.entries.at(-1).sequence);assert.ok(evidence.entries.every(row=>row.evidenceGeneration===evidence.evidenceGeneration));
hud.clearCanonicalOverlayAuthority('SELF_CHECK_REVOKE');evidence=hud.canonicalDrawEvidence();assert.equal(evidence.bound,false);assert.equal(evidence.entryCount,0);
hud.setFixedDrawSmokeEnabled(true);gl.drawArrays(gl.TRIANGLES,0,3);assert.ok(hud.fixedDrawSmokeStatus().drawCount>0);assert.equal(hud.canonicalDrawEvidence().entryCount,0);hud.setFixedDrawSmokeEnabled(false);
const directBinding={authorityKey:'direct-p1',runtimeEpoch:'direct-runtime-0001'};hud.bindP1HeadTrackerAuthority(directBinding);hud.setP1HeadTracker({...directBinding,visible:true,x:200,y:140});gl.drawArrays(gl.TRIANGLES,0,3);assert.equal(hud.canonicalDrawEvidence().entryCount,0);
console.log('maintained HUD canonical draw evidence self-check PASS');