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
globalThis.__WOF_ALPHA_CONFIG={release:'wof-alpha-rc3',session:'1234567890abcdef',channel:'selfcheck'};
globalThis.__WOF_ALPHA_TRANSPORT_V1={version:'wof-alpha-safe-transport-v1',matches(){return true;}};
globalThis.WOFAlphaHudModel={summarizeWarnings(rows){const r=Array.isArray(rows)?rows:[];return{count:r.length,lines:r.map(x=>x.target||'?'),groups:{}};}};
globalThis.WOFAlphaEnemyTargetLabels={buildPlan(){return{labels:[],suppressed:[]};}};
globalThis.WOFAlphaPlayerHeadWarning={MAX_PLAYER_AGE_MS:300,buildPlan(){return{anchored:[],fixed:[],suppressed:[]};}};
let normalizeCalls=0,planCalls=0;
globalThis.WOFAlphaCanonicalAnchorEnvelope={DEFAULT_MAX_AGE_MS:300,
  validateAuthorityBinding(b){if(!b||!b.authorityKey||!b.runtimeEpoch||!b.rendererEpoch)return{ok:false,reason:'BAD'};return{ok:true,value:{authorityKey:b.authorityKey,runtimeEpoch:b.runtimeEpoch,rendererEpoch:b.rendererEpoch,worldSha256:b.worldSha256??null}};},
  normalizeEnvelope({records,authorityBinding}){normalizeCalls++;return{ok:true,schema:'wof-alpha-canonical-anchor-envelope-v1',authority:{...authorityBinding,worldSha256:authorityBinding.worldSha256??null},records:records||[],ready:records||[],suppressed:[]};},
  toEnemyAnchorArray(env){return(env.records||[]).filter(x=>x.kind==='enemy').map(x=>({slot:Number(x.actor.split('-').pop()),actor:x.actor,generation:x.generation,sampleAt:x.sampleAt,canonicalAnchor:x.canonicalAnchor}));},
  toPlayerAnchorSamples(env){const out={};for(const x of env.records||[])if(x.kind==='player')out[x.actor]={canonicalAnchor:x.canonicalAnchor,sampleAt:x.sampleAt};return out;}
};
globalThis.WOFAlphaCanonicalOverlayPlan={buildCanonicalPlan(args){planCalls++;
  const enemy=args.enemy.markers.length&&args.enemy.canonicalAnchors.length?[{label:'1P',drawRectDb:{x:50,y:50,width:30,height:18}}]:[];
  const player=args.player.warnings.length&&args.player.canonicalAnchors.P1?[{player:'P1',drawRectDb:{x:80,y:70,width:84,height:26}}]:[];
  return{mode:'canonical-render-anchor',coordinateSpace:'webgl-drawing-buffer',fallback:'NONE',state:'READY',reason:null,
    drawIntents:[...enemy.map(payload=>({kind:'enemy-target-label',payload})),...player.map(payload=>({kind:'player-danger-warning',payload}))],enemyTargetLabels:enemy,playerDangerWarnings:player,
    suppression:{enemy:[],player:[],global:[]},diagnostics:{emitted:{enemyTargetLabels:enemy.length,playerDangerWarnings:player.length,total:enemy.length+player.length}}};
}};
let bcInstance=null;globalThis.BroadcastChannel=class{constructor(){bcInstance=this;}close(){}};
require('./wof_alpha_hud.js');
const hud=globalThis.WOFALPHAHUD;assert.ok(hud);
const now=Date.now();const binding={authorityKey:'authority-1',runtimeEpoch:'runtime-epoch-0001',rendererEpoch:'renderer-epoch-01'};
hud.bindCanonicalOverlayAuthority(binding);
bcInstance.onmessage({data:{schema:'wof-alpha-v2',session:'1234567890abcdef',kind:'state',sampleAt:now-5,runtimeEpoch:binding.runtimeEpoch,warnings:[{target:'P1'}]}});
bcInstance.onmessage({data:{schema:'wof-alpha-v2',session:'1234567890abcdef',kind:'enemy-target-markers',markers:[{slot:0,target7E:0,target:'P1',sampleAt:now-5,confidence:1}]}});
const payload={schema:'wof-alpha-canonical-anchor-runtime-envelope-input-v1',authorityBinding:binding,records:[
  {kind:'enemy',actor:'enemy-slot-0',generation:7,sampleAt:now,canonicalAnchor:{state:'READY'}},
  {kind:'player',actor:'P1',generation:3,sampleAt:now,canonicalAnchor:{state:'READY'}}
]};
let st=hud.ingestCanonicalAnchorEnvelope(payload);assert.equal(st.bound,true);assert.equal(st.state,'READY');assert.equal(st.fallback,'NONE');assert.equal(st.emittedEnemyLabelCount,1);assert.equal(st.emittedPlayerDangerCount,1);
const before=hud.status();gl.drawArrays(gl.TRIANGLES,0,3);const after=hud.status();assert.ok(after.enemyTargetLabels.drawCount>before.enemyTargetLabels.drawCount);assert.ok(after.playerHeadWarning.drawCount>before.playerHeadWarning.drawCount);
assert.ok(normalizeCalls>=2);assert.ok(planCalls>=2);
st=hud.ingestCanonicalAnchorEnvelope({...payload,authorityBinding:{...binding,rendererEpoch:'renderer-epoch-02'}});assert.equal(st.state,'SUPPRESSED');assert.equal(st.fallback,'NONE');assert.equal(st.emittedEnemyLabelCount,0);assert.equal(st.emittedPlayerDangerCount,0);
const labelsBefore=hud.status().enemyTargetLabels.drawCount,warningsBefore=hud.status().playerHeadWarning.drawCount;gl.drawArrays(gl.TRIANGLES,0,3);assert.equal(hud.status().enemyTargetLabels.drawCount,labelsBefore);assert.equal(hud.status().playerHeadWarning.drawCount,warningsBefore);
hud.setFixedDrawSmokeEnabled(true);gl.drawArrays(gl.TRIANGLES,0,3);assert.ok(hud.fixedDrawSmokeStatus().drawCount>0);
console.log('maintained HUD canonical overlay self-check PASS');
