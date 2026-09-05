(function(root){
'use strict';
const VERSION='wof-alpha-enemy-target-labels-v1';
const GEOMETRY_VERSION='wof-alpha-enemy-head-geometry-v2';
const PROJECTION_SCHEMA='wof-alpha-enemy-head-projection-v2';
const PROJECTION_VERDICT='IMPLEMENTATION_READY';
const PROJECTION_KIND='world-camera-y-sign-z-head-clearance-v2';
const CANONICAL_ANCHOR_SCHEMA='wof-render-object-anchor-v1';
const CANONICAL_PLAN_VERSION='wof-alpha-enemy-target-labels-canonical-anchor-v1';
const SUPPORTED_ROM_SHA='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const TARGETS_BY_FIELD=Object.freeze({0:'P1',4:'P2',8:'P3'});
const TARGET_LABELS=Object.freeze({P1:'1P',P2:'2P',P3:'3P'});
const Y_MODELS=new Set(['Y-Z','Y+Z','Y']);
const NATIVE_WIDTH=384,NATIVE_HEIGHT=224;
const DEFAULT_MARKER_MAX_AGE_MS=300;
const DEFAULT_PROJECTION_MAX_AGE_MS=300;
const DEFAULT_CANONICAL_ANCHOR_MAX_AGE_MS=300;
const DEFAULT_DRAWING_BUFFER_MAX_AGE_MS=1000;
const CAMERA_MIN=0xFF0000,CAMERA_MAX_EXCLUSIVE=0xFFBE00;

const finite=value=>Number.isFinite(value);
const clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
const ageMs=(nowMs,sampleAtMs)=>finite(nowMs)&&finite(sampleAtMs)?Math.max(0,nowMs-sampleAtMs):Infinity;
const confidence=value=>finite(value)&&value>=0&&value<=1?value:null;

function targetForField(target7E){
  if(typeof target7E!=='number'||!Number.isFinite(target7E)||!Number.isInteger(target7E)||Object.is(target7E,-0))return null;
  if(target7E===0)return'P1';
  if(target7E===4)return'P2';
  if(target7E===8)return'P3';
  return null;
}
function labelForTarget(target){return TARGET_LABELS[target]||null;}
function contentRectOf(state){
  if(!state||!finite(state.width)||state.width<=0||!finite(state.height)||state.height<=0)return null;
  const rect=state.contentRect||{x:0,y:0,width:state.width,height:state.height};
  if(![rect.x,rect.y,rect.width,rect.height].every(finite)||rect.width<=0||rect.height<=0)return null;
  if(rect.x<0||rect.y<0||rect.x+rect.width>state.width||rect.y+rect.height>state.height)return null;
  return{x:rect.x,y:rect.y,width:rect.width,height:rect.height};
}
function fail(reason,extra={}){return{ok:false,reason,...extra};}
function validateProofProfile(profile){
  if(!profile||profile.schema!==PROJECTION_SCHEMA||profile.verdict!==PROJECTION_VERDICT)return fail('PROJECTION_UNPROVEN');
  if(profile.projectionKind!==PROJECTION_KIND)return fail('INVALID_PROJECTION_KIND');
  if(typeof profile.proofId!=='string'||!profile.proofId)return fail('PROJECTION_PROOF_ID_MISSING');
  if(profile.romSha256!==SUPPORTED_ROM_SHA)return fail('PROJECTION_ROM_MISMATCH');
  if(profile.nativeWidth!==384||profile.nativeHeight!==224)return fail('INVALID_NATIVE_VIEWPORT');
  if(!Number.isInteger(profile.cameraAddress)||profile.cameraAddress<CAMERA_MIN||profile.cameraAddress>=CAMERA_MAX_EXCLUSIVE||((profile.cameraAddress-CAMERA_MIN)&1)!==0)return fail('INVALID_CAMERA_ADDRESS');
  if(profile.cameraRead!=='u16be')return fail('INVALID_CAMERA_READ');
  if(profile.cameraSign!==1&&profile.cameraSign!==-1)return fail('INVALID_CAMERA_SIGN');
  if(!finite(profile.cameraScale)||profile.cameraScale<=0)return fail('INVALID_CAMERA_SCALE');
  if(!finite(profile.xBias)||!finite(profile.yBias))return fail('INVALID_PROJECTION_CONSTANTS');
  if(profile.yAxisSign!==1&&profile.yAxisSign!==-1)return fail('INVALID_Y_AXIS_SIGN');
  if(!Y_MODELS.has(profile.yModel))return fail('INVALID_Y_MODEL');
  if(Object.prototype.hasOwnProperty.call(profile,'enemyHeadOffsetsByType'))return fail('LEGACY_ENEMY_HEAD_OFFSETS_UNSUPPORTED');
  const clearances=profile.enemyHeadClearanceByType;
  if(!clearances||typeof clearances!=='object'||Array.isArray(clearances))return fail('ENEMY_HEAD_CLEARANCE_MISSING');
  const entries=Object.entries(clearances);if(!entries.length)return fail('ENEMY_HEAD_CLEARANCE_MISSING');
  for(const [key,value] of entries){const type=Number(key);if(!Number.isInteger(type)||type<0||type>=47||!finite(value)||value<0)return fail('INVALID_ENEMY_HEAD_CLEARANCE');}
  return{ok:true};
}
function validateProjection(projection,nowMs,maxAgeMs=DEFAULT_PROJECTION_MAX_AGE_MS){
  const profile=validateProofProfile(projection);if(!profile.ok)return profile;
  if(typeof projection.epoch!=='string'||!projection.epoch)return fail('PROJECTION_EPOCH_MISSING');
  const age=ageMs(nowMs,projection.sampleAt);
  if(age>maxAgeMs)return fail('STALE_PROJECTION',{ageMs:age});
  if(confidence(projection.confidence)===null)return fail('INVALID_PROJECTION_CONFIDENCE');
  if(!finite(projection.cameraRaw)||!finite(projection.cameraX))return fail('INVALID_CAMERA_SAMPLE');
  const expected=projection.cameraRaw*projection.cameraSign*projection.cameraScale;
  if(!finite(expected)||Math.abs(expected-projection.cameraX)>1e-9)return fail('CAMERA_SAMPLE_MISMATCH');
  return{ok:true,ageMs:age};
}
function validateDrawingBuffer(state,nowMs,projectionEpoch,maxAgeMs=DEFAULT_DRAWING_BUFFER_MAX_AGE_MS){
  const rect=contentRectOf(state);if(!rect)return fail('INVALID_DRAWING_BUFFER');
  const age=ageMs(nowMs,state.sampleAt);if(age>maxAgeMs)return fail('STALE_DRAWING_BUFFER',{ageMs:age});
  if(confidence(state.confidence)===null)return fail('INVALID_DRAWING_BUFFER_CONFIDENCE');
  if(typeof state.epoch!=='string'||!state.epoch||typeof state.projectionEpoch!=='string'||!state.projectionEpoch)return fail('DRAWING_BUFFER_EPOCH_MISSING');
  if(typeof projectionEpoch!=='string'||!projectionEpoch)return fail('PROJECTION_EPOCH_MISSING');
  if(state.epoch!==state.projectionEpoch||state.epoch!==projectionEpoch)return fail('DRAWING_BUFFER_EPOCH_MISMATCH');
  return{ok:true,rect,ageMs:age};
}
function baseYForModel(marker,yModel){
  if(yModel==='Y-Z')return marker.enemyY-marker.enemyZ;
  if(yModel==='Y+Z')return marker.enemyY+marker.enemyZ;
  return marker.enemyY;
}
function projectMarkerNative(marker,projection){
  if(!marker||!Number.isInteger(marker.slot)||marker.slot<0||marker.slot>=20)return fail('INVALID_MARKER_SLOT');
  const expectedTarget=targetForField(marker.target7E);
  if(!expectedTarget||marker.target!==expectedTarget)return fail('INVALID_TARGET');
  const label=labelForTarget(expectedTarget);if(!label)return fail('INVALID_TARGET');
  if(![marker.enemyX,marker.enemyY,marker.enemyZ].every(finite))return fail('INVALID_ENEMY_XYZ');
  if(typeof marker.epoch!=='string'||!marker.epoch||marker.projectionEpoch!==projection.epoch||marker.epoch!==projection.epoch)return fail('EPOCH_MISMATCH');
  const baseY=baseYForModel(marker,projection.yModel);
  const bodyYNative=projection.yAxisSign*baseY+projection.yBias;
  const anchorXNative=marker.enemyX-projection.cameraX+projection.xBias;
  const headClearanceNative=projection.enemyHeadClearanceByType?.[String(marker.type)];
  if(!finite(headClearanceNative)||headClearanceNative<0)return fail('UNSUPPORTED_ENEMY_TYPE');
  const anchorYNative=bodyYNative-headClearanceNative;
  if(![anchorXNative,bodyYNative,anchorYNative].every(finite))return fail('PROJECTION_NONFINITE');
  if(anchorXNative<0||anchorXNative>=projection.nativeWidth||anchorYNative<0||anchorYNative>=projection.nativeHeight)return fail('PROJECTION_OUT_OF_BOUNDS');
  return{ok:true,anchorXNative,anchorYNative,bodyYNative,headClearanceNative,label,target:expectedTarget};
}
function buildPlan({markers=[],projection,drawingBufferState,nowMs,markerMaxAgeMs=DEFAULT_MARKER_MAX_AGE_MS,projectionMaxAgeMs=DEFAULT_PROJECTION_MAX_AGE_MS,drawingBufferMaxAgeMs=DEFAULT_DRAWING_BUFFER_MAX_AGE_MS,labelWidth=30,labelHeight=18}={}){
  const now=finite(nowMs)?nowMs:Date.now();
  const p=validateProjection(projection,now,projectionMaxAgeMs);
  const d=validateDrawingBuffer(drawingBufferState,now,projection?.epoch,drawingBufferMaxAgeMs);
  const labels=[],suppressed=[];
  if(!p.ok||!d.ok){
    const reason=!p.ok?p.reason:d.reason;
    for(const marker of Array.isArray(markers)?markers:[])suppressed.push({slot:marker?.slot??null,reason});
    return{coordinateSpace:'webgl-drawing-buffer',labels,suppressed,reason,mappingKey:null};
  }
  const rect=d.rect;
  const mappingKey=[drawingBufferState.width,drawingBufferState.height,rect.x,rect.y,rect.width,rect.height,drawingBufferState.mappingVersion??'',drawingBufferState.fullscreen?'fs':'win',projection.proofId,projection.epoch].join(':');
  for(const marker of Array.isArray(markers)?markers:[]){
    const markerAge=ageMs(now,marker?.sampleAt);
    if(markerAge>markerMaxAgeMs){suppressed.push({slot:marker?.slot??null,reason:'STALE_MARKER'});continue;}
    if(confidence(marker?.confidence)===null){suppressed.push({slot:marker?.slot??null,reason:'INVALID_MARKER_CONFIDENCE'});continue;}
    const native=projectMarkerNative(marker,projection);
    if(!native.ok){suppressed.push({slot:marker?.slot??null,reason:native.reason});continue;}
    const xDb=rect.x+native.anchorXNative/projection.nativeWidth*rect.width;
    const yDb=rect.y+native.anchorYNative/projection.nativeHeight*rect.height;
    if(![xDb,yDb].every(finite)){suppressed.push({slot:marker.slot,reason:'DRAWING_BUFFER_PROJECTION_NONFINITE'});continue;}
    if(xDb<rect.x||xDb>=rect.x+rect.width||yDb<rect.y||yDb>=rect.y+rect.height){suppressed.push({slot:marker.slot,reason:'DRAWING_BUFFER_ANCHOR_OUT_OF_BOUNDS'});continue;}
    const width=Math.min(labelWidth,rect.width),height=Math.min(labelHeight,rect.height);
    const drawRectDb={
      x:clamp(xDb-width/2,rect.x,rect.x+Math.max(0,rect.width-width)),
      y:clamp(yDb-height/2,rect.y,rect.y+Math.max(0,rect.height-height)),
      width,height
    };
    labels.push({slot:marker.slot,sourceId:marker.sourceId||('enemy-slot-'+marker.slot),target:native.target,label:native.label,anchorDb:{x:xDb,y:yDb},bodyYNative:native.bodyYNative,headClearanceNative:native.headClearanceNative,drawRectDb,mappingKey,proofId:projection.proofId,epoch:projection.epoch});
  }
  return{coordinateSpace:'webgl-drawing-buffer',labels,suppressed,reason:null,mappingKey};
}

function validateCanonicalAuthority(authority){
  if(!authority||typeof authority!=='object')return fail('CANONICAL_AUTHORITY_MISSING');
  if(typeof authority.authorityKey!=='string'||!authority.authorityKey)return fail('CANONICAL_AUTHORITY_KEY_MISSING');
  if(typeof authority.runtimeEpoch!=='string'||authority.runtimeEpoch.length<16)return fail('CANONICAL_RUNTIME_EPOCH_INVALID');
  if(typeof authority.rendererEpoch!=='string'||authority.rendererEpoch.length<16)return fail('CANONICAL_RENDERER_EPOCH_INVALID');
  return{ok:true};
}
function validateCanonicalDrawingBuffer(state,nowMs,runtimeEpoch,maxAgeMs=DEFAULT_DRAWING_BUFFER_MAX_AGE_MS){
  const rect=contentRectOf(state);if(!rect)return fail('INVALID_DRAWING_BUFFER');
  const age=ageMs(nowMs,state.sampleAt);if(age>maxAgeMs)return fail('STALE_DRAWING_BUFFER',{ageMs:age});
  if(confidence(state.confidence)===null)return fail('INVALID_DRAWING_BUFFER_CONFIDENCE');
  if(typeof runtimeEpoch!=='string'||!runtimeEpoch)return fail('CANONICAL_RUNTIME_EPOCH_INVALID');
  if(typeof state.epoch!=='string'||!state.epoch)return fail('DRAWING_BUFFER_EPOCH_MISSING');
  if(state.epoch!==runtimeEpoch)return fail('DRAWING_BUFFER_RUNTIME_EPOCH_MISMATCH');
  if(Object.prototype.hasOwnProperty.call(state,'runtimeEpoch')&&state.runtimeEpoch!==runtimeEpoch)return fail('DRAWING_BUFFER_RUNTIME_EPOCH_MISMATCH');
  return{ok:true,rect,ageMs:age};
}
function validateCanonicalMarker(marker,nowMs,maxAgeMs=DEFAULT_MARKER_MAX_AGE_MS){
  if(!marker||!Number.isInteger(marker.slot)||marker.slot<0||marker.slot>=20)return fail('INVALID_MARKER_SLOT');
  const target=targetForField(marker.target7E);
  if(!target||marker.target!==target)return fail('INVALID_TARGET');
  const label=labelForTarget(target);if(!label)return fail('INVALID_TARGET');
  const age=ageMs(nowMs,marker.sampleAt);if(age>maxAgeMs)return fail('STALE_MARKER',{ageMs:age});
  if(confidence(marker.confidence)===null)return fail('INVALID_MARKER_CONFIDENCE');
  if(!Number.isInteger(marker.generation)||marker.generation<0)return fail('MARKER_GENERATION_MISSING');
  const actor=typeof marker.actor==='string'&&marker.actor?marker.actor:('enemy-slot-'+marker.slot);
  return{ok:true,target,label,actor,generation:marker.generation,ageMs:age};
}
function unwrapCanonicalAnchor(value){
  if(value&&typeof value==='object'&&value.value&&typeof value.value==='object')return value.value;
  if(value&&typeof value==='object'&&value.canonicalAnchor&&typeof value.canonicalAnchor==='object')return value.canonicalAnchor;
  return value;
}
function canonicalAnchorForMarker(canonicalAnchors,marker){
  if(Array.isArray(canonicalAnchors)){
    const matches=[];
    for(const entry of canonicalAnchors){
      if(!entry||typeof entry!=='object')continue;
      const candidate=unwrapCanonicalAnchor(entry);
      const slot=Number.isInteger(entry.slot)?entry.slot:(Number.isInteger(candidate?.slot)?candidate.slot:null);
      if(slot===marker.slot)matches.push(candidate);
    }
    if(matches.length>1)return fail('CANONICAL_ANCHOR_AMBIGUOUS');
    if(matches.length===1)return{ok:true,anchor:matches[0]};
    return fail('CANONICAL_ANCHOR_MISSING');
  }
  if(!canonicalAnchors||typeof canonicalAnchors!=='object')return fail('CANONICAL_ANCHOR_MISSING');
  const generationKey=marker.slot+':'+marker.generation;
  const raw=Object.prototype.hasOwnProperty.call(canonicalAnchors,generationKey)?canonicalAnchors[generationKey]:canonicalAnchors[String(marker.slot)];
  if(Array.isArray(raw))return raw.length===1?{ok:true,anchor:unwrapCanonicalAnchor(raw[0])}:fail(raw.length?'CANONICAL_ANCHOR_AMBIGUOUS':'CANONICAL_ANCHOR_MISSING');
  if(!raw)return fail('CANONICAL_ANCHOR_MISSING');
  return{ok:true,anchor:unwrapCanonicalAnchor(raw)};
}
function validateCanonicalAnchor(anchor,markerInfo,authority,nowMs,maxAgeMs=DEFAULT_CANONICAL_ANCHOR_MAX_AGE_MS){
  if(!anchor||typeof anchor!=='object')return fail('CANONICAL_ANCHOR_MISSING');
  if(anchor.schema!==CANONICAL_ANCHOR_SCHEMA)return fail('CANONICAL_ANCHOR_SCHEMA_INVALID');
  if(anchor.state!=='READY')return fail(anchor.state==='SUPPRESSED'?'CANONICAL_ANCHOR_SUPPRESSED':'CANONICAL_ANCHOR_NOT_READY',{sourceReason:anchor.reason||null});
  if(anchor.unsafe===true||anchor.readOnly!==true||anchor.ramWrites!==0||anchor.inputInjection!==false)return fail('CANONICAL_ANCHOR_UNSAFE');
  if(anchor.ambiguous===true||anchor.association?.ambiguous===true)return fail('CANONICAL_ANCHOR_AMBIGUOUS');
  if(anchor.proven===false||anchor.sourceProven===false||anchor.rendererSourceProven===false||anchor.association?.proven===false)return fail('CANONICAL_ANCHOR_UNPROVEN');
  if(anchor.actor!==markerInfo.actor)return fail('CANONICAL_ACTOR_MISMATCH');
  if(anchor.generation!==markerInfo.generation)return fail('CANONICAL_GENERATION_MISMATCH');
  if(anchor.nativeWidth!==NATIVE_WIDTH||anchor.nativeHeight!==NATIVE_HEIGHT)return fail('CANONICAL_NATIVE_SIZE_MISMATCH');
  if(anchor.authorityKey!==authority.authorityKey||anchor.runtimeEpoch!==authority.runtimeEpoch||anchor.rendererEpoch!==authority.rendererEpoch)return fail('CANONICAL_AUTHORITY_EPOCH_MISMATCH');
  if(Object.prototype.hasOwnProperty.call(anchor,'sampleAt')){
    const age=ageMs(nowMs,anchor.sampleAt);if(age>maxAgeMs)return fail('STALE_CANONICAL_ANCHOR',{ageMs:age});
  }
  const point=anchor.anchor;
  if(!point||![point.x,point.y].every(finite))return fail('CANONICAL_ANCHOR_POINT_INVALID');
  if(point.x<0||point.x>=NATIVE_WIDTH||point.y<0||point.y>=NATIVE_HEIGHT)return fail('CANONICAL_ANCHOR_OUT_OF_BOUNDS');
  return{ok:true,anchorXNative:point.x,anchorYNative:point.y,actor:anchor.actor,generation:anchor.generation};
}
function buildCanonicalPlan({markers=[],canonicalAnchors={},canonicalAuthority,drawingBufferState,nowMs,markerMaxAgeMs=DEFAULT_MARKER_MAX_AGE_MS,canonicalAnchorMaxAgeMs=DEFAULT_CANONICAL_ANCHOR_MAX_AGE_MS,drawingBufferMaxAgeMs=DEFAULT_DRAWING_BUFFER_MAX_AGE_MS,labelWidth=30,labelHeight=18}={}){
  const now=finite(nowMs)?nowMs:Date.now();
  const a=validateCanonicalAuthority(canonicalAuthority);
  const d=validateCanonicalDrawingBuffer(drawingBufferState,now,canonicalAuthority?.runtimeEpoch,drawingBufferMaxAgeMs);
  const labels=[],suppressed=[];
  if(!a.ok||!d.ok){
    const reason=!a.ok?a.reason:d.reason;
    for(const marker of Array.isArray(markers)?markers:[])suppressed.push({slot:marker?.slot??null,reason});
    return{mode:'canonical-render-anchor',coordinateSpace:'webgl-drawing-buffer',labels,suppressed,reason,mappingKey:null};
  }
  const rect=d.rect;
  const mappingKey=[drawingBufferState.width,drawingBufferState.height,rect.x,rect.y,rect.width,rect.height,drawingBufferState.mappingVersion??'',drawingBufferState.fullscreen?'fs':'win','canonical',canonicalAuthority.authorityKey,canonicalAuthority.runtimeEpoch,canonicalAuthority.rendererEpoch].join(':');
  for(const marker of Array.isArray(markers)?markers:[]){
    const m=validateCanonicalMarker(marker,now,markerMaxAgeMs);
    if(!m.ok){suppressed.push({slot:marker?.slot??null,reason:m.reason});continue;}
    const found=canonicalAnchorForMarker(canonicalAnchors,marker);
    if(!found.ok){suppressed.push({slot:marker.slot,reason:found.reason});continue;}
    const native=validateCanonicalAnchor(found.anchor,m,canonicalAuthority,now,canonicalAnchorMaxAgeMs);
    if(!native.ok){suppressed.push({slot:marker.slot,reason:native.reason,sourceReason:native.sourceReason??null});continue;}
    const xDb=rect.x+native.anchorXNative/NATIVE_WIDTH*rect.width;
    const yDb=rect.y+native.anchorYNative/NATIVE_HEIGHT*rect.height;
    if(![xDb,yDb].every(finite)){suppressed.push({slot:marker.slot,reason:'DRAWING_BUFFER_CANONICAL_MAP_NONFINITE'});continue;}
    if(xDb<rect.x||xDb>=rect.x+rect.width||yDb<rect.y||yDb>=rect.y+rect.height){suppressed.push({slot:marker.slot,reason:'DRAWING_BUFFER_ANCHOR_OUT_OF_BOUNDS'});continue;}
    const width=Math.min(labelWidth,rect.width),height=Math.min(labelHeight,rect.height);
    const drawRectDb={
      x:clamp(xDb-width/2,rect.x,rect.x+Math.max(0,rect.width-width)),
      y:clamp(yDb-height/2,rect.y,rect.y+Math.max(0,rect.height-height)),
      width,height
    };
    labels.push({slot:marker.slot,sourceId:marker.sourceId||('enemy-slot-'+marker.slot),actor:native.actor,generation:native.generation,target:m.target,label:m.label,
      anchorNative:{x:native.anchorXNative,y:native.anchorYNative},anchorDb:{x:xDb,y:yDb},drawRectDb,mappingKey,canonicalAnchorSchema:CANONICAL_ANCHOR_SCHEMA,
      authorityKey:canonicalAuthority.authorityKey,runtimeEpoch:canonicalAuthority.runtimeEpoch,rendererEpoch:canonicalAuthority.rendererEpoch});
  }
  return{mode:'canonical-render-anchor',coordinateSpace:'webgl-drawing-buffer',labels,suppressed,reason:null,mappingKey};
}

const api={VERSION,GEOMETRY_VERSION,PROJECTION_SCHEMA,PROJECTION_VERDICT,PROJECTION_KIND,CANONICAL_ANCHOR_SCHEMA,CANONICAL_PLAN_VERSION,SUPPORTED_ROM_SHA,TARGETS_BY_FIELD,TARGET_LABELS,DEFAULT_MARKER_MAX_AGE_MS,DEFAULT_PROJECTION_MAX_AGE_MS,DEFAULT_CANONICAL_ANCHOR_MAX_AGE_MS,targetForField,labelForTarget,contentRectOf,validateProofProfile,validateProjection,projectMarkerNative,buildPlan,validateCanonicalAuthority,validateCanonicalDrawingBuffer,validateCanonicalMarker,validateCanonicalAnchor,buildCanonicalPlan};
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaEnemyTargetLabels=api;
})(typeof self!=='undefined'?self:globalThis);
