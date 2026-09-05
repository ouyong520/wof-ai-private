(function(root,factory){
'use strict';
const api=factory();
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaPlayerHeadWarning=api;
})(typeof self!=='undefined'?self:globalThis,function(){
'use strict';

const VERSION='wof-alpha-player-head-warning-v1';
const GEOMETRY_VERSION='wof-alpha-player-head-geometry-v2';
const CANONICAL_GEOMETRY_VERSION='wof-alpha-player-danger-canonical-anchor-v1';
const CANONICAL_ANCHOR_SCHEMA='wof-render-object-anchor-v1';
const CANONICAL_NATIVE_WIDTH=384;
const CANONICAL_NATIVE_HEIGHT=224;
const PROFILE_SCHEMA='wof-alpha-player-head-projection-v2';
const PROJECTION_KIND='world-camera-y-sign-z-head-clearance-v2';
const Y_MODELS=new Set(['Y-Z','Y+Z','Y']);
const PLAYERS=Object.freeze(['P1','P2','P3']);
const PLAYER_SET=new Set(PLAYERS);
const EPOCH_RE=/^[0-9a-f]{32}$/;
const MAX_PLAYER_AGE_MS=80;
const MAX_PROJECTION_AGE_MS=80;
const MAX_DRAWING_BUFFER_AGE_MS=250;
const DEFAULT_CANONICAL_ANCHOR_MAX_AGE_MS=80;
const DEFAULT_BOX_WIDTH=84;
const DEFAULT_BOX_HEIGHT=26;

const finite=Number.isFinite;
const confidenceValue=value=>finite(value)&&value>=0&&value<=1?value:null;
const ageMs=(now,sample)=>finite(now)&&finite(sample)?Math.max(0,now-sample):Infinity;
const validEpoch=value=>typeof value==='string'&&EPOCH_RE.test(value);

function contentRectOf(state){
  if(!state||!finite(state.width)||state.width<=0||!finite(state.height)||state.height<=0)return null;
  const rect=state.contentRect||{x:0,y:0,width:state.width,height:state.height};
  if(![rect.x,rect.y,rect.width,rect.height].every(finite)||rect.width<=0||rect.height<=0)return null;
  if(rect.x<0||rect.y<0||rect.x+rect.width>state.width||rect.y+rect.height>state.height)return null;
  return{x:rect.x,y:rect.y,width:rect.width,height:rect.height};
}

function validateBounds(bounds,nativeWidth,nativeHeight){
  if(!bounds||![bounds.minX,bounds.maxX,bounds.minY,bounds.maxY].every(finite))return false;
  if(bounds.minX<0||bounds.minY<0||bounds.maxX>nativeWidth||bounds.maxY>nativeHeight)return false;
  return bounds.minX<=bounds.maxX&&bounds.minY<=bounds.maxY;
}

function validateProofProfile(profile){
  const reasons=[];
  if(!profile||profile.schema!==PROFILE_SCHEMA)reasons.push('PROFILE_SCHEMA_MISMATCH');
  if(profile?.status!=='PROVED')reasons.push('PROFILE_NOT_PROVED');
  if(typeof profile?.proofId!=='string'||profile.proofId.length<8)reasons.push('PROOF_ID_MISSING');
  if(typeof profile?.projectionVersion!=='string'||profile.projectionVersion.length<8)reasons.push('PROJECTION_VERSION_MISSING');
  if(profile?.projectionKind!==PROJECTION_KIND)reasons.push('PROJECTION_KIND_UNSUPPORTED');
  if(!finite(profile?.nativeWidth)||profile.nativeWidth<=0||!finite(profile?.nativeHeight)||profile.nativeHeight<=0)reasons.push('INVALID_NATIVE_VIEWPORT');
  if(!Number.isInteger(profile?.cameraAddress)||profile.cameraAddress<0xFF0000||profile.cameraAddress>0xFFFFFF)reasons.push('INVALID_CAMERA_ADDRESS');
  if(profile?.cameraSign!==1&&profile?.cameraSign!==-1)reasons.push('INVALID_CAMERA_SIGN');
  for(const key of ['cameraScale','worldXScale','xBias','yBias','headClearanceNative']){
    if(!finite(profile?.[key]))reasons.push('INVALID_'+key.toUpperCase());
  }
  if(profile?.yAxisSign!==1&&profile?.yAxisSign!==-1)reasons.push('INVALID_Y_AXIS_SIGN');
  if(!Y_MODELS.has(profile?.yModel))reasons.push('INVALID_Y_MODEL');
  if(Object.prototype.hasOwnProperty.call(profile||{},'floorYScale')||Object.prototype.hasOwnProperty.call(profile||{},'zScale'))reasons.push('LEGACY_FREEFORM_Y_SCALES_UNSUPPORTED');
  if(finite(profile?.headClearanceNative)&&profile.headClearanceNative<0)reasons.push('INVALID_HEAD_CLEARANCE');
  if(finite(profile?.nativeWidth)&&finite(profile?.nativeHeight)&&!validateBounds(profile?.validationBounds,profile.nativeWidth,profile.nativeHeight)){
    reasons.push('INVALID_VALIDATION_BOUNDS');
  }
  return{ok:reasons.length===0,reasons,reason:reasons[0]||null};
}

function buildProjectionSnapshot(profile,{cameraRaw,epoch,sampleAt}={}){
  const valid=validateProofProfile(profile);
  if(!valid.ok)return{ok:false,reason:valid.reason,reasons:valid.reasons,projection:null};
  if(!Number.isInteger(cameraRaw)||cameraRaw<0||cameraRaw>0xFFFF)return{ok:false,reason:'INVALID_CAMERA_SAMPLE',reasons:['INVALID_CAMERA_SAMPLE'],projection:null};
  if(!validEpoch(epoch))return{ok:false,reason:'INVALID_RUNTIME_EPOCH',reasons:['INVALID_RUNTIME_EPOCH'],projection:null};
  if(!finite(sampleAt))return{ok:false,reason:'INVALID_SAMPLE_TIME',reasons:['INVALID_SAMPLE_TIME'],projection:null};
  const cameraX=cameraRaw*profile.cameraSign*profile.cameraScale;
  if(!finite(cameraX))return{ok:false,reason:'INVALID_CAMERA_SAMPLE',reasons:['INVALID_CAMERA_SAMPLE'],projection:null};
  const projection=Object.freeze({
    schema:PROFILE_SCHEMA,
    status:'PROVED',
    proofId:profile.proofId,
    version:profile.projectionVersion,
    projectionKind:PROJECTION_KIND,
    source:profile.source||'proved-browser-profile',
    epoch,
    projectionEpoch:epoch,
    sampleAt,
    confidence:1,
    nativeWidth:profile.nativeWidth,
    nativeHeight:profile.nativeHeight,
    cameraRaw,
    cameraX,
    worldXScale:profile.worldXScale,
    xBias:profile.xBias,
    yAxisSign:profile.yAxisSign,
    yModel:profile.yModel,
    yBias:profile.yBias,
    headClearanceNative:profile.headClearanceNative,
    validationBounds:{...profile.validationBounds}
  });
  return{ok:true,reason:null,reasons:[],projection};
}

function validProjectionState(projection){
  if(!projection||projection.schema!==PROFILE_SCHEMA||projection.status!=='PROVED'||projection.projectionKind!==PROJECTION_KIND)return false;
  if(typeof projection.proofId!=='string'||projection.proofId.length<8||typeof projection.version!=='string'||projection.version.length<8)return false;
  if(![projection.nativeWidth,projection.nativeHeight,projection.cameraX,projection.worldXScale,projection.xBias,projection.yBias,projection.headClearanceNative].every(finite))return false;
  if(projection.yAxisSign!==1&&projection.yAxisSign!==-1)return false;
  if(!Y_MODELS.has(projection.yModel))return false;
  if(projection.nativeWidth<=0||projection.nativeHeight<=0||projection.headClearanceNative<0)return false;
  return validateBounds(projection.validationBounds,projection.nativeWidth,projection.nativeHeight);
}

function baseYForModel(playerState,yModel){
  if(yModel==='Y-Z')return playerState.y-playerState.z;
  if(yModel==='Y+Z')return playerState.y+playerState.z;
  return playerState.y;
}

function projectNative(playerState,projection){
  const bodyXNative=(playerState.x-projection.cameraX)*projection.worldXScale+projection.xBias;
  const baseY=baseYForModel(playerState,projection.yModel);
  const bodyYNative=projection.yAxisSign*baseY+projection.yBias;
  const anchorXNative=bodyXNative;
  const anchorYNative=bodyYNative-projection.headClearanceNative;
  return{bodyXNative,bodyYNative,anchorXNative,anchorYNative,baseY,yModel:projection.yModel,yAxisSign:projection.yAxisSign,headClearanceNative:projection.headClearanceNative,confidence:1};
}

function failAnchor(player,reason,metadata={}){
  return{ok:false,player,reason,xDb:null,yDb:null,bodyXDb:null,bodyYDb:null,confidence:0,
    ageMs:metadata.ageMs??Infinity,sampleAt:metadata.sampleAt??null,mappingKey:metadata.mappingKey??null};
}

function resolveAnchor({player,playerState,projection,drawingBufferState,nowMs,warningEpoch,warningSampleAt}){
  if(!PLAYER_SET.has(player))return failAnchor(player,'INVALID_PLAYER');
  if(typeof warningSampleAt!=='number'||!finite(warningSampleAt))return failAnchor(player,'INVALID_WARNING_SAMPLE_TIME');
  if(!playerState||playerState.present!==true)return failAnchor(player,'PLAYER_ABSENT');
  if(![playerState.x,playerState.y,playerState.z].every(finite))return failAnchor(player,'INVALID_PLAYER_XYZ');
  const pAge=ageMs(nowMs,playerState.sampleAt);
  if(pAge>MAX_PLAYER_AGE_MS)return failAnchor(player,'STALE_PLAYER',{ageMs:pAge,sampleAt:playerState.sampleAt});
  if(confidenceValue(playerState.confidence)===null)return failAnchor(player,'INVALID_PLAYER_CONFIDENCE');
  if(!validProjectionState(projection))return failAnchor(player,'INVALID_PROJECTION_STATE');
  const projAge=ageMs(nowMs,projection.sampleAt);
  if(projAge>MAX_PROJECTION_AGE_MS)return failAnchor(player,'STALE_PROJECTION',{ageMs:projAge,sampleAt:projection.sampleAt});
  if(confidenceValue(projection.confidence)===null)return failAnchor(player,'INVALID_PROJECTION_CONFIDENCE');

  const rect=contentRectOf(drawingBufferState);
  if(!rect)return failAnchor(player,'INVALID_DRAWING_BUFFER');
  const dbAge=ageMs(nowMs,drawingBufferState.sampleAt);
  if(dbAge>MAX_DRAWING_BUFFER_AGE_MS)return failAnchor(player,'STALE_DRAWING_BUFFER',{ageMs:dbAge,sampleAt:drawingBufferState.sampleAt});
  if(confidenceValue(drawingBufferState.confidence)===null)return failAnchor(player,'INVALID_DRAWING_BUFFER_CONFIDENCE');

  const epochs=[
    warningEpoch,
    playerState.epoch,
    playerState.projectionEpoch,
    projection.epoch,
    projection.projectionEpoch,
    drawingBufferState.epoch,
    drawingBufferState.projectionEpoch
  ];
  if(!epochs.every(validEpoch))return failAnchor(player,'INVALID_EPOCH');
  if(epochs.some(value=>value!==epochs[0]))return failAnchor(player,'EPOCH_MISMATCH');

  if(playerState.sampleAt<warningSampleAt){
    return failAnchor(player,'SPATIAL_BEFORE_WARNING_SAMPLE');
  }
  if(projection.sampleAt<warningSampleAt){
    return failAnchor(player,'PROJECTION_BEFORE_WARNING_SAMPLE');
  }

  let projected;
  try{projected=projectNative(playerState,projection);}catch(_){return failAnchor(player,'PROJECTION_ERROR');}
  if(!projected||![projected.anchorXNative,projected.anchorYNative,projected.bodyXNative,projected.bodyYNative].every(finite)){
    return failAnchor(player,'PROJECTION_NONFINITE');
  }
  if(confidenceValue(projected.confidence)===null)return failAnchor(player,'INVALID_PROJECTED_CONFIDENCE');

  const nativeWidth=projection.nativeWidth,nativeHeight=projection.nativeHeight,bounds=projection.validationBounds;
  const anchorOutside=projected.anchorXNative<0||projected.anchorXNative>=nativeWidth||projected.anchorYNative<0||projected.anchorYNative>=nativeHeight;
  const bodyOutside=projected.bodyXNative<bounds.minX||projected.bodyXNative>bounds.maxX||projected.bodyYNative<bounds.minY||projected.bodyYNative>bounds.maxY;
  if(anchorOutside||bodyOutside)return failAnchor(player,'PROJECTION_OUT_OF_BOUNDS');

  const sx=rect.width/nativeWidth,sy=rect.height/nativeHeight;
  const xDb=rect.x+projected.anchorXNative*sx,yDb=rect.y+projected.anchorYNative*sy;
  const bodyXDb=rect.x+projected.bodyXNative*sx,bodyYDb=rect.y+projected.bodyYNative*sy;
  if(![xDb,yDb,bodyXDb,bodyYDb].every(finite))return failAnchor(player,'DRAWING_BUFFER_PROJECTION_NONFINITE');

  const mappingKey=[
    drawingBufferState.width,drawingBufferState.height,rect.x,rect.y,rect.width,rect.height,
    drawingBufferState.mappingVersion??'',drawingBufferState.fullscreen?'fs':'win',projection.version
  ].join(':');
  return{ok:true,player,reason:null,xDb,yDb,bodyXDb,bodyYDb,
    yModel:projected.yModel,yAxisSign:projected.yAxisSign,headClearanceNative:projected.headClearanceNative,
    confidence:Math.min(playerState.confidence,projection.confidence,drawingBufferState.confidence,projected.confidence),
    ageMs:Math.max(pAge,projAge,dbAge),sampleAt:Math.min(playerState.sampleAt,projection.sampleAt,drawingBufferState.sampleAt),
    mappingKey};
}

function validAuthorityBinding(binding){
  return!!binding&&typeof binding.authorityKey==='string'&&binding.authorityKey.length>0&&
    typeof binding.runtimeEpoch==='string'&&binding.runtimeEpoch.length>=16&&
    typeof binding.rendererEpoch==='string'&&binding.rendererEpoch.length>=16;
}

function canonicalSampleOf(value){
  if(value&&typeof value==='object'&&value.canonicalAnchor&&typeof value.canonicalAnchor==='object'){
    return{anchor:value.canonicalAnchor,sampleAt:value.sampleAt};
  }
  return{anchor:value,sampleAt:value?.sampleAt};
}

function failCanonicalAnchor(player,reason,metadata={}){
  return{ok:false,player,reason,xDb:null,yDb:null,confidence:0,generation:metadata.generation??null,
    ageMs:metadata.ageMs??Infinity,sampleAt:metadata.sampleAt??null,mappingKey:metadata.mappingKey??null};
}

function resolveCanonicalAnchor({
  player,anchorSample,expectedGeneration,authorityBinding,drawingBufferState,nowMs,warningSampleAt,
  anchorMaxAgeMs=DEFAULT_CANONICAL_ANCHOR_MAX_AGE_MS
}={}){
  if(!PLAYER_SET.has(player))return failCanonicalAnchor(player,'INVALID_PLAYER');
  if(typeof warningSampleAt!=='number'||!finite(warningSampleAt))return failCanonicalAnchor(player,'INVALID_WARNING_SAMPLE_TIME');
  if(!Number.isInteger(expectedGeneration)||expectedGeneration<0)return failCanonicalAnchor(player,'EXPECTED_GENERATION_MISSING');
  if(!validAuthorityBinding(authorityBinding))return failCanonicalAnchor(player,'CANONICAL_AUTHORITY_INVALID',{generation:expectedGeneration});

  const sample=canonicalSampleOf(anchorSample);
  const anchor=sample.anchor;
  if(!anchor||typeof anchor!=='object')return failCanonicalAnchor(player,'CANONICAL_ANCHOR_MISSING',{generation:expectedGeneration});
  if(anchor.schema!==CANONICAL_ANCHOR_SCHEMA)return failCanonicalAnchor(player,'CANONICAL_ANCHOR_SCHEMA_MISMATCH',{generation:expectedGeneration});
  if(anchor.state!=='READY'){
    const reason=typeof anchor.reason==='string'&&anchor.reason?anchor.reason:'CANONICAL_ANCHOR_SUPPRESSED';
    return failCanonicalAnchor(player,reason,{generation:expectedGeneration,sampleAt:sample.sampleAt});
  }
  if(anchor.actor!==player)return failCanonicalAnchor(player,'CANONICAL_ACTOR_MISMATCH',{generation:expectedGeneration,sampleAt:sample.sampleAt});
  if(anchor.generation!==expectedGeneration)return failCanonicalAnchor(player,'CANONICAL_GENERATION_MISMATCH',{generation:expectedGeneration,sampleAt:sample.sampleAt});
  if(anchor.nativeWidth!==CANONICAL_NATIVE_WIDTH||anchor.nativeHeight!==CANONICAL_NATIVE_HEIGHT){
    return failCanonicalAnchor(player,'CANONICAL_NATIVE_SIZE_MISMATCH',{generation:expectedGeneration,sampleAt:sample.sampleAt});
  }
  if(anchor.readOnly!==true||anchor.ramWrites!==0||anchor.inputInjection!==false){
    return failCanonicalAnchor(player,'CANONICAL_SAFETY_INVALID',{generation:expectedGeneration,sampleAt:sample.sampleAt});
  }
  if(anchor.unsafe===true)return failCanonicalAnchor(player,'CANONICAL_ANCHOR_UNSAFE',{generation:expectedGeneration,sampleAt:sample.sampleAt});
  if(anchor.ambiguous===true||anchor.association?.ambiguous===true){
    return failCanonicalAnchor(player,'CANONICAL_ANCHOR_AMBIGUOUS',{generation:expectedGeneration,sampleAt:sample.sampleAt});
  }
  if(anchor.proven===false||anchor.sourceProven===false||anchor.rendererSource?.proven===false||
    (anchor.association&&anchor.association.proven!==true)){
    return failCanonicalAnchor(player,'CANONICAL_ANCHOR_UNPROVEN',{generation:expectedGeneration,sampleAt:sample.sampleAt});
  }
  if(anchor.authorityKey!==authorityBinding.authorityKey||
    anchor.runtimeEpoch!==authorityBinding.runtimeEpoch||
    anchor.rendererEpoch!==authorityBinding.rendererEpoch){
    return failCanonicalAnchor(player,'CANONICAL_AUTHORITY_EPOCH_MISMATCH',{generation:expectedGeneration,sampleAt:sample.sampleAt});
  }

  if(!finite(sample.sampleAt))return failCanonicalAnchor(player,'CANONICAL_SAMPLE_TIME_MISSING',{generation:expectedGeneration});
  const anchorAge=ageMs(nowMs,sample.sampleAt);
  if(anchorAge>anchorMaxAgeMs){
    return failCanonicalAnchor(player,'STALE_CANONICAL_ANCHOR',{generation:expectedGeneration,ageMs:anchorAge,sampleAt:sample.sampleAt});
  }
  if(sample.sampleAt<warningSampleAt){
    return failCanonicalAnchor(player,'CANONICAL_ANCHOR_BEFORE_WARNING_SAMPLE',{generation:expectedGeneration,ageMs:anchorAge,sampleAt:sample.sampleAt});
  }

  const native=anchor.anchor;
  if(!native||![native.x,native.y].every(finite)){
    return failCanonicalAnchor(player,'CANONICAL_NATIVE_ANCHOR_INVALID',{generation:expectedGeneration,ageMs:anchorAge,sampleAt:sample.sampleAt});
  }
  if(native.x<0||native.x>CANONICAL_NATIVE_WIDTH||native.y<0||native.y>CANONICAL_NATIVE_HEIGHT){
    return failCanonicalAnchor(player,'CANONICAL_NATIVE_ANCHOR_OUT_OF_BOUNDS',{generation:expectedGeneration,ageMs:anchorAge,sampleAt:sample.sampleAt});
  }

  const rect=contentRectOf(drawingBufferState);
  if(!rect)return failCanonicalAnchor(player,'INVALID_DRAWING_BUFFER',{generation:expectedGeneration,ageMs:anchorAge,sampleAt:sample.sampleAt});
  const dbAge=ageMs(nowMs,drawingBufferState?.sampleAt);
  if(dbAge>MAX_DRAWING_BUFFER_AGE_MS){
    return failCanonicalAnchor(player,'STALE_DRAWING_BUFFER',{generation:expectedGeneration,ageMs:Math.max(anchorAge,dbAge),sampleAt:sample.sampleAt});
  }
  if(confidenceValue(drawingBufferState?.confidence)===null){
    return failCanonicalAnchor(player,'INVALID_DRAWING_BUFFER_CONFIDENCE',{generation:expectedGeneration,ageMs:Math.max(anchorAge,dbAge),sampleAt:sample.sampleAt});
  }
  if(Object.prototype.hasOwnProperty.call(drawingBufferState||{},'runtimeEpoch')&&drawingBufferState.runtimeEpoch!==authorityBinding.runtimeEpoch){
    return failCanonicalAnchor(player,'DRAWING_BUFFER_RUNTIME_EPOCH_MISMATCH',{generation:expectedGeneration,ageMs:Math.max(anchorAge,dbAge),sampleAt:sample.sampleAt});
  }
  if(Object.prototype.hasOwnProperty.call(drawingBufferState||{},'rendererEpoch')&&drawingBufferState.rendererEpoch!==authorityBinding.rendererEpoch){
    return failCanonicalAnchor(player,'DRAWING_BUFFER_RENDERER_EPOCH_MISMATCH',{generation:expectedGeneration,ageMs:Math.max(anchorAge,dbAge),sampleAt:sample.sampleAt});
  }

  const xDb=rect.x+native.x/CANONICAL_NATIVE_WIDTH*rect.width;
  const yDb=rect.y+native.y/CANONICAL_NATIVE_HEIGHT*rect.height;
  if(![xDb,yDb].every(finite)){
    return failCanonicalAnchor(player,'DRAWING_BUFFER_CANONICAL_MAP_NONFINITE',{generation:expectedGeneration,ageMs:Math.max(anchorAge,dbAge),sampleAt:sample.sampleAt});
  }
  const mappingKey=[
    drawingBufferState.width,drawingBufferState.height,rect.x,rect.y,rect.width,rect.height,
    drawingBufferState.mappingVersion??'',drawingBufferState.fullscreen?'fs':'win',
    authorityBinding.authorityKey,authorityBinding.runtimeEpoch,authorityBinding.rendererEpoch
  ].join(':');
  return{
    ok:true,player,reason:null,generation:expectedGeneration,xDb,yDb,
    nativeX:native.x,nativeY:native.y,nativeWidth:CANONICAL_NATIVE_WIDTH,nativeHeight:CANONICAL_NATIVE_HEIGHT,
    authorityKey:authorityBinding.authorityKey,runtimeEpoch:authorityBinding.runtimeEpoch,rendererEpoch:authorityBinding.rendererEpoch,
    confidence:drawingBufferState.confidence,ageMs:Math.max(anchorAge,dbAge),sampleAt:Math.min(sample.sampleAt,drawingBufferState.sampleAt),
    mappingKey,source:'canonical-render-object-anchor'
  };
}

function buildCanonicalPlan({
  warnings,canonicalAnchors,playerGenerations,authorityBinding,drawingBufferState,nowMs,warningSampleAt,
  anchorMaxAgeMs=DEFAULT_CANONICAL_ANCHOR_MAX_AGE_MS,boxWidth=DEFAULT_BOX_WIDTH,boxHeight=DEFAULT_BOX_HEIGHT
}={}){
  const now=finite(nowMs)?nowMs:Date.now();
  const {groups,invalid}=warningGroups(warnings);
  const anchored=[],suppressed=[];
  for(const warning of invalid){
    suppressed.push({player:null,warning,warnings:[warning],warningCount:1,reason:'INVALID_TARGET'});
  }
  for(const player of PLAYERS){
    const rows=groups.get(player);
    if(!rows.length)continue;
    const anchor=resolveCanonicalAnchor({
      player,anchorSample:canonicalAnchors?.[player],expectedGeneration:playerGenerations?.[player],
      authorityBinding,drawingBufferState,nowMs:now,warningSampleAt,anchorMaxAgeMs
    });
    if(!anchor.ok){
      suppressed.push({player,warnings:rows,warning:rows[0],warningCount:rows.length,reason:anchor.reason});
      continue;
    }
    const rect=contentRectOf(drawingBufferState);
    const width=finite(boxWidth)&&boxWidth>0?Math.min(boxWidth,rect.width):Math.min(DEFAULT_BOX_WIDTH,rect.width);
    const height=finite(boxHeight)&&boxHeight>0?Math.min(boxHeight,rect.height):Math.min(DEFAULT_BOX_HEIGHT,rect.height);
    const x=Math.min(rect.x+rect.width-width,Math.max(rect.x,anchor.xDb-width/2));
    const y=Math.min(rect.y+rect.height-height,Math.max(rect.y,anchor.yDb-height/2));
    if(![x,y,width,height].every(finite)){
      suppressed.push({player,warnings:rows,warning:rows[0],warningCount:rows.length,reason:'INVALID_DRAW_RECT'});
      continue;
    }
    anchored.push({player,warnings:rows,warning:rows[0],warningCount:rows.length,anchor,drawRectDb:{x,y,width,height}});
  }
  return{
    mode:'canonical-render-anchor',coordinateSpace:'webgl-drawing-buffer',anchored,fixed:[],suppressed,
    holdMs:0,smoothing:false,fallback:'NONE',maxCanonicalAnchorAgeMs:anchorMaxAgeMs,maxDrawingBufferAgeMs:MAX_DRAWING_BUFFER_AGE_MS
  };
}

function warningGroups(warnings){
  const groups=new Map(PLAYERS.map(player=>[player,[]]));
  const invalid=[];
  for(const warning of Array.isArray(warnings)?warnings:[]){
    if(!warning)continue;
    if(!PLAYER_SET.has(warning.target)){invalid.push(warning);continue;}
    groups.get(warning.target).push(warning);
  }
  return{groups,invalid};
}

function buildPlan({warnings,players,projection,drawingBufferState,nowMs,warningEpoch,warningSampleAt,boxWidth=DEFAULT_BOX_WIDTH,boxHeight=DEFAULT_BOX_HEIGHT}={}){
  const now=finite(nowMs)?nowMs:Date.now();
  const {groups,invalid}=warningGroups(warnings);
  const anchored=[],fixed=[];
  for(const warning of invalid)fixed.push({player:null,warning,warnings:[warning],warningCount:1,reason:'INVALID_TARGET'});
  for(const player of PLAYERS){
    const rows=groups.get(player);
    if(!rows.length)continue;
    const anchor=resolveAnchor({player,playerState:players?.[player],projection,drawingBufferState,nowMs:now,warningEpoch,warningSampleAt});
    if(!anchor.ok){
      fixed.push({player,warnings:rows,warning:rows[0],warningCount:rows.length,reason:anchor.reason});
      continue;
    }
    const rect=contentRectOf(drawingBufferState);
    if(!rect){
      fixed.push({player,warnings:rows,warning:rows[0],warningCount:rows.length,reason:'INVALID_DRAWING_BUFFER'});
      continue;
    }
    const width=finite(boxWidth)&&boxWidth>0?boxWidth:DEFAULT_BOX_WIDTH;
    const height=finite(boxHeight)&&boxHeight>0?boxHeight:DEFAULT_BOX_HEIGHT;
    const x=Math.min(rect.x+rect.width-width,Math.max(rect.x,anchor.xDb-width/2));
    const y=Math.min(rect.y+rect.height-height,Math.max(rect.y,anchor.yDb-height/2));
    if(![x,y,width,height].every(finite)){
      fixed.push({player,warnings:rows,warning:rows[0],warningCount:rows.length,reason:'INVALID_DRAW_RECT'});
      continue;
    }
    anchored.push({player,warnings:rows,warning:rows[0],warningCount:rows.length,anchor,drawRectDb:{x,y,width,height}});
  }
  return{anchored,fixed,holdMs:0,smoothing:false,maxPlayerAgeMs:MAX_PLAYER_AGE_MS,maxProjectionAgeMs:MAX_PROJECTION_AGE_MS};
}

return{
  VERSION,GEOMETRY_VERSION,CANONICAL_GEOMETRY_VERSION,CANONICAL_ANCHOR_SCHEMA,CANONICAL_NATIVE_WIDTH,CANONICAL_NATIVE_HEIGHT,
  PROFILE_SCHEMA,PROJECTION_KIND,Y_MODELS,PLAYERS,MAX_PLAYER_AGE_MS,MAX_PROJECTION_AGE_MS,MAX_DRAWING_BUFFER_AGE_MS,DEFAULT_CANONICAL_ANCHOR_MAX_AGE_MS,
  validateProofProfile,buildProjectionSnapshot,resolveAnchor,validAuthorityBinding,resolveCanonicalAnchor,buildCanonicalPlan,buildPlan
};
});