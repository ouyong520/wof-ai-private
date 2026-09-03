(function(root){
'use strict';
const VERSION='wof-alpha-enemy-target-labels-v1';
const PROJECTION_SCHEMA='wof-alpha-enemy-head-projection-v1';
const PROJECTION_VERDICT='IMPLEMENTATION_READY';
const SUPPORTED_ROM_SHA='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const TARGETS_BY_FIELD=Object.freeze({0:'P1',4:'P2',8:'P3'});
const TARGET_LABELS=Object.freeze({P1:'1P',P2:'2P',P3:'3P'});
const Y_MODELS=new Set(['Y-Z','Y+Z','Y']);
const AFFINE_KIND='world-camera-floor-z-affine-v2';
const DEFAULT_MARKER_MAX_AGE_MS=300,DEFAULT_PROJECTION_MAX_AGE_MS=300,DEFAULT_DRAWING_BUFFER_MAX_AGE_MS=1000;
const CAMERA_MIN=0xFF0000,CAMERA_MAX_EXCLUSIVE=0xFFBE00;
const finite=value=>Number.isFinite(value),clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
const ageMs=(nowMs,sampleAtMs)=>finite(nowMs)&&finite(sampleAtMs)?Math.max(0,nowMs-sampleAtMs):Infinity;
const confidence=value=>finite(value)&&value>=0&&value<=1?value:null;
const fail=(reason,extra={})=>({ok:false,reason,...extra});
function targetForField(target7E){if(typeof target7E!=='number'||!Number.isFinite(target7E)||!Number.isInteger(target7E)||Object.is(target7E,-0))return null;if(target7E===0)return'P1';if(target7E===4)return'P2';if(target7E===8)return'P3';return null;}
function labelForTarget(target){return TARGET_LABELS[target]||null;}
function contentRectOf(state){if(!state||!finite(state.width)||state.width<=0||!finite(state.height)||state.height<=0)return null;const rect=state.contentRect||{x:0,y:0,width:state.width,height:state.height};if(![rect.x,rect.y,rect.width,rect.height].every(finite)||rect.width<=0||rect.height<=0)return null;if(rect.x<0||rect.y<0||rect.x+rect.width>state.width||rect.y+rect.height>state.height)return null;return{x:rect.x,y:rect.y,width:rect.width,height:rect.height};}
function rangePair(v){return Array.isArray(v)&&v.length===2&&v.every(finite)&&v[0]<=v[1]?v:null;}
function validateLiveEnvelope(profile){
  const e=profile?.validationEnvelope,m=profile?.motionEnvelope,a=profile?.authorityBinding;
  if(!e||!rangePair(e.worldX)||!rangePair(e.worldY)||!rangePair(e.worldZ)||!rangePair(e.cameraRaw))return fail('INVALID_PROOF_ENVELOPE');
  if(!m||!['worldXStep','worldYStep','worldZStep','cameraRawStep'].every(k=>finite(m[k])&&m[k]>0))return fail('INVALID_MOTION_ENVELOPE');
  if(!a||typeof a.workerSessionId!=='string'||!a.workerSessionId||!Number.isInteger(a.cameraAuthorityGeneration)||a.cameraAuthorityGeneration<1||!Number.isInteger(a.p1LifecycleGeneration)||a.p1LifecycleGeneration<1)return fail('INVALID_AUTHORITY_BINDING');
  return{ok:true};
}
function validateProofProfile(profile){
  if(!profile||profile.schema!==PROJECTION_SCHEMA||profile.verdict!==PROJECTION_VERDICT)return fail('PROJECTION_UNPROVEN');
  if(typeof profile.proofId!=='string'||!profile.proofId)return fail('PROJECTION_PROOF_ID_MISSING');
  if(profile.romSha256!==SUPPORTED_ROM_SHA)return fail('PROJECTION_ROM_MISMATCH');
  if(profile.nativeWidth!==384||profile.nativeHeight!==224)return fail('INVALID_NATIVE_VIEWPORT');
  if(!Number.isInteger(profile.cameraAddress)||profile.cameraAddress<CAMERA_MIN||profile.cameraAddress>=CAMERA_MAX_EXCLUSIVE||((profile.cameraAddress-CAMERA_MIN)&1)!==0)return fail('INVALID_CAMERA_ADDRESS');
  if(profile.cameraRead!=='u16be')return fail('INVALID_CAMERA_READ');
  if(profile.cameraSign!==1&&profile.cameraSign!==-1)return fail('INVALID_CAMERA_SIGN');
  if(!finite(profile.cameraScale)||profile.cameraScale<=0)return fail('INVALID_CAMERA_SCALE');
  const affine=profile.projectionKind===AFFINE_KIND;
  if(affine){
    if(!['worldXScale','xBias','floorYScale','zScale','yBias'].every(k=>finite(profile[k])))return fail('INVALID_PROJECTION_CONSTANTS');
    const gate=validateLiveEnvelope(profile);if(!gate.ok)return gate;
  }else{
    if(!finite(profile.xBias))return fail('INVALID_PROJECTION_CONSTANTS');
    if(!Y_MODELS.has(profile.yModel))return fail('INVALID_Y_MODEL');
  }
  const offsets=profile.enemyHeadOffsetsByType;if(!offsets||typeof offsets!=='object'||Array.isArray(offsets))return fail('ENEMY_HEAD_OFFSETS_MISSING');
  const entries=Object.entries(offsets);if(!entries.length)return fail('ENEMY_HEAD_OFFSETS_MISSING');
  for(const [key,value] of entries){const type=Number(key);if(!Number.isInteger(type)||type<0||type>=47||!finite(value))return fail('INVALID_ENEMY_HEAD_OFFSET');}
  if(affine){const ev=profile.enemyHeadEvidenceByType;if(!ev||typeof ev!=='object')return fail('ENEMY_HEAD_EVIDENCE_MISSING');for(const key of Object.keys(offsets)){const x=ev[key];if(!x||!Number.isInteger(x.sampleCount)||x.sampleCount<8||!finite(x.mad)||x.mad>3.5||!Number.isInteger(x.lifecycleGeneration)||x.lifecycleGeneration<1)return fail('INVALID_ENEMY_HEAD_EVIDENCE');}}
  return{ok:true};
}
function validateProjection(projection,nowMs,maxAgeMs=DEFAULT_PROJECTION_MAX_AGE_MS){const profile=validateProofProfile(projection);if(!profile.ok)return profile;if(typeof projection.epoch!=='string'||!projection.epoch)return fail('PROJECTION_EPOCH_MISSING');const age=ageMs(nowMs,projection.sampleAt);if(age>maxAgeMs)return fail('STALE_PROJECTION',{ageMs:age});if(confidence(projection.confidence)===null)return fail('INVALID_PROJECTION_CONFIDENCE');if(!finite(projection.cameraRaw)||!finite(projection.cameraX))return fail('INVALID_CAMERA_SAMPLE');const expected=projection.cameraRaw*projection.cameraSign*projection.cameraScale;if(!finite(expected)||Math.abs(expected-projection.cameraX)>1e-9)return fail('CAMERA_SAMPLE_MISMATCH');return{ok:true,ageMs:age};}
function validateDrawingBuffer(state,nowMs,projectionEpoch,maxAgeMs=DEFAULT_DRAWING_BUFFER_MAX_AGE_MS){const rect=contentRectOf(state);if(!rect)return fail('INVALID_DRAWING_BUFFER');const age=ageMs(nowMs,state.sampleAt);if(age>maxAgeMs)return fail('STALE_DRAWING_BUFFER',{ageMs:age});if(confidence(state.confidence)===null)return fail('INVALID_DRAWING_BUFFER_CONFIDENCE');if(typeof state.epoch!=='string'||!state.epoch||typeof state.projectionEpoch!=='string'||!state.projectionEpoch)return fail('DRAWING_BUFFER_EPOCH_MISSING');if(typeof projectionEpoch!=='string'||!projectionEpoch)return fail('PROJECTION_EPOCH_MISSING');if(state.epoch!==state.projectionEpoch||state.epoch!==projectionEpoch)return fail('DRAWING_BUFFER_EPOCH_MISMATCH');return{ok:true,rect,ageMs:age};}
function within(v,r){return finite(v)&&rangePair(r)&&v>=r[0]&&v<=r[1];}
function projectMarkerNative(marker,projection){
  if(!marker||!Number.isInteger(marker.slot)||marker.slot<0||marker.slot>=20)return fail('INVALID_MARKER_SLOT');
  const expectedTarget=targetForField(marker.target7E);if(!expectedTarget||marker.target!==expectedTarget)return fail('INVALID_TARGET');const label=labelForTarget(expectedTarget);if(!label)return fail('INVALID_TARGET');
  if(![marker.enemyX,marker.enemyY,marker.enemyZ].every(finite))return fail('INVALID_ENEMY_XYZ');
  if(typeof marker.epoch!=='string'||!marker.epoch||marker.projectionEpoch!==projection.epoch||marker.epoch!==projection.epoch)return fail('EPOCH_MISMATCH');
  const headOffset=projection.enemyHeadOffsetsByType?.[String(marker.type)];if(!finite(headOffset))return fail('UNSUPPORTED_ENEMY_TYPE');
  let anchorXNative,anchorYNative;
  if(projection.projectionKind===AFFINE_KIND){
    const e=projection.validationEnvelope;if(!within(marker.enemyX,e.worldX)||!within(marker.enemyY,e.worldY)||!within(marker.enemyZ,e.worldZ)||!within(projection.cameraRaw,e.cameraRaw))return fail('PROJECTION_OUTSIDE_PROOF_ENVELOPE');
    anchorXNative=(marker.enemyX-projection.cameraX)*projection.worldXScale+projection.xBias;
    anchorYNative=marker.enemyY*projection.floorYScale+marker.enemyZ*projection.zScale+projection.yBias+headOffset;
  }else{
    let baseY;if(projection.yModel==='Y-Z')baseY=marker.enemyY-marker.enemyZ;else if(projection.yModel==='Y+Z')baseY=marker.enemyY+marker.enemyZ;else baseY=marker.enemyY;
    anchorXNative=marker.enemyX-projection.cameraX+projection.xBias;anchorYNative=baseY+headOffset;
  }
  if(![anchorXNative,anchorYNative].every(finite))return fail('PROJECTION_NONFINITE');
  if(anchorXNative<0||anchorXNative>=projection.nativeWidth||anchorYNative<0||anchorYNative>=projection.nativeHeight)return fail('PROJECTION_OUT_OF_BOUNDS');
  return{ok:true,anchorXNative,anchorYNative,label,target:expectedTarget};
}
function buildPlan({markers=[],projection,drawingBufferState,nowMs,markerMaxAgeMs=DEFAULT_MARKER_MAX_AGE_MS,projectionMaxAgeMs=DEFAULT_PROJECTION_MAX_AGE_MS,drawingBufferMaxAgeMs=DEFAULT_DRAWING_BUFFER_MAX_AGE_MS,labelWidth=30,labelHeight=18}={}){
  const now=finite(nowMs)?nowMs:Date.now(),p=validateProjection(projection,now,projectionMaxAgeMs),d=validateDrawingBuffer(drawingBufferState,now,projection?.epoch,drawingBufferMaxAgeMs),labels=[],suppressed=[];
  if(!p.ok||!d.ok){const reason=!p.ok?p.reason:d.reason;for(const marker of Array.isArray(markers)?markers:[])suppressed.push({slot:marker?.slot??null,reason});return{coordinateSpace:'webgl-drawing-buffer',labels,suppressed,reason,mappingKey:null};}
  const rect=d.rect,mappingKey=[drawingBufferState.width,drawingBufferState.height,rect.x,rect.y,rect.width,rect.height,drawingBufferState.mappingVersion??'',drawingBufferState.fullscreen?'fs':'win',projection.proofId,projection.epoch].join(':');
  for(const marker of Array.isArray(markers)?markers:[]){const markerAge=ageMs(now,marker?.sampleAt);if(markerAge>markerMaxAgeMs){suppressed.push({slot:marker?.slot??null,reason:'STALE_MARKER'});continue;}if(confidence(marker?.confidence)===null){suppressed.push({slot:marker?.slot??null,reason:'INVALID_MARKER_CONFIDENCE'});continue;}const native=projectMarkerNative(marker,projection);if(!native.ok){suppressed.push({slot:marker?.slot??null,reason:native.reason});continue;}const xDb=rect.x+native.anchorXNative/projection.nativeWidth*rect.width,yDb=rect.y+native.anchorYNative/projection.nativeHeight*rect.height;if(![xDb,yDb].every(finite)){suppressed.push({slot:marker.slot,reason:'DRAWING_BUFFER_PROJECTION_NONFINITE'});continue;}if(xDb<rect.x||xDb>=rect.x+rect.width||yDb<rect.y||yDb>=rect.y+rect.height){suppressed.push({slot:marker.slot,reason:'DRAWING_BUFFER_ANCHOR_OUT_OF_BOUNDS'});continue;}const width=Math.min(labelWidth,rect.width),height=Math.min(labelHeight,rect.height),drawRectDb={x:clamp(xDb-width/2,rect.x,rect.x+Math.max(0,rect.width-width)),y:clamp(yDb-height/2,rect.y,rect.y+Math.max(0,rect.height-height)),width,height};labels.push({slot:marker.slot,sourceId:marker.sourceId||('enemy-slot-'+marker.slot),target:native.target,label:native.label,anchorDb:{x:xDb,y:yDb},drawRectDb,mappingKey,proofId:projection.proofId,epoch:projection.epoch});}
  return{coordinateSpace:'webgl-drawing-buffer',labels,suppressed,reason:null,mappingKey};
}
const api={VERSION,PROJECTION_SCHEMA,PROJECTION_VERDICT,SUPPORTED_ROM_SHA,TARGETS_BY_FIELD,TARGET_LABELS,AFFINE_KIND,DEFAULT_MARKER_MAX_AGE_MS,DEFAULT_PROJECTION_MAX_AGE_MS,targetForField,labelForTarget,contentRectOf,validateProofProfile,validateProjection,projectMarkerNative,buildPlan};
if(typeof module!=='undefined'&&module.exports)module.exports=api;root.WOFAlphaEnemyTargetLabels=api;
})(typeof self!=='undefined'?self:globalThis);
