(function(root){
'use strict';

const VERSION='wof-alpha-canonical-anchor-envelope-v1';
const SOURCE_SCHEMA='wof-render-object-anchor-v1';
const NATIVE_WIDTH=384;
const NATIVE_HEIGHT=224;
const DEFAULT_MAX_AGE_MS=300;
const MAX_RECORDS=23;
const PLAYER_SET=new Set(['P1','P2','P3']);
const ENEMY_ACTOR_RE=/^enemy-slot-(?:[0-9]|1[0-9])$/;
const STATES=new Set(['READY','SUPPRESSED']);

const finite=value=>Number.isFinite(value);
const own=(value,key)=>Object.prototype.hasOwnProperty.call(value,key);
const fail=(reason,detail={})=>({ok:false,reason,...detail});

function validEpoch(value){return typeof value==='string'&&value.length>=16;}
function validWorldSha(value){return typeof value==='string'&&/^[0-9a-f]{64}$/.test(value);}
function validPoint(value){return !!value&&typeof value==='object'&&finite(value.x)&&finite(value.y);}

function validateAuthorityBinding(binding){
  if(!binding||typeof binding!=='object')return fail('AUTHORITY_BINDING_MISSING');
  if(typeof binding.authorityKey!=='string'||binding.authorityKey.length===0)return fail('AUTHORITY_KEY_INVALID');
  if(!validEpoch(binding.runtimeEpoch))return fail('RUNTIME_EPOCH_INVALID');
  if(!validEpoch(binding.rendererEpoch))return fail('RENDERER_EPOCH_INVALID');
  if(own(binding,'worldSha256')&&binding.worldSha256!==null&&!validWorldSha(binding.worldSha256))return fail('WORLD_IDENTITY_INVALID');
  return{ok:true,value:{
    authorityKey:binding.authorityKey,
    runtimeEpoch:binding.runtimeEpoch,
    rendererEpoch:binding.rendererEpoch,
    worldSha256:binding.worldSha256??null
  }};
}

function validateIdentity(record){
  if(!record||typeof record!=='object')return fail('RECORD_INVALID');
  if(record.kind!=='player'&&record.kind!=='enemy')return fail('KIND_INVALID');
  if(typeof record.actor!=='string'||record.actor.length===0)return fail('ACTOR_INVALID');
  if(record.kind==='player'&&!PLAYER_SET.has(record.actor))return fail('PLAYER_ACTOR_INVALID');
  if(record.kind==='enemy'){
    if(!ENEMY_ACTOR_RE.test(record.actor))return fail('ENEMY_ACTOR_INVALID');
    const slot=Number(record.actor.slice('enemy-slot-'.length));
    if(own(record,'slot')&&record.slot!==slot)return fail('ENEMY_SLOT_ACTOR_MISMATCH');
  }
  if(!Number.isInteger(record.generation)||record.generation<0)return fail('GENERATION_INVALID');
  return{ok:true};
}

function validateSampleTime(sampleAt,nowMs,maxAgeMs){
  if(!finite(sampleAt))return fail('SAMPLE_TIME_INVALID');
  if(!finite(nowMs))return fail('NOW_INVALID');
  if(!finite(maxAgeMs)||maxAgeMs<0)return fail('MAX_AGE_INVALID');
  if(sampleAt>nowMs)return fail('FUTURE_SAMPLE_INVALID',{sampleAt,nowMs});
  const ageMs=nowMs-sampleAt;
  if(ageMs>maxAgeMs)return fail('STALE_SAMPLE',{ageMs,maxAgeMs});
  return{ok:true,ageMs};
}

function recordBindingValue(record,source,key){
  const values=[];
  if(own(record,key)&&record[key]!=null)values.push(record[key]);
  if(own(source,key)&&source[key]!=null)values.push(source[key]);
  return values;
}

function validateBindingConsistency(record,source,binding){
  for(const key of ['authorityKey','runtimeEpoch','rendererEpoch']){
    for(const value of recordBindingValue(record,source,key)){
      if(value!==binding[key])return fail('MIXED_AUTHORITY_BINDING',{field:key});
    }
  }
  const worldValues=[];
  if(binding.worldSha256!=null)worldValues.push(binding.worldSha256);
  if(own(record,'worldSha256')&&record.worldSha256!=null)worldValues.push(record.worldSha256);
  if(own(source,'worldSha256')&&source.worldSha256!=null)worldValues.push(source.worldSha256);
  for(const value of worldValues){if(!validWorldSha(value))return fail('WORLD_IDENTITY_INVALID');}
  if(new Set(worldValues).size>1)return fail('MIXED_WORLD_IDENTITY');
  return{ok:true,worldSha256:worldValues[0]??null};
}

function validateSafety(source){
  if(source.readOnly!==true||source.ramWrites!==0||source.inputInjection!==false)return fail('UNSAFE_SOURCE');
  if(source.unsafe===true)return fail('UNSAFE_SOURCE');
  return{ok:true};
}

function hasSuppressedFallback(record,source){
  const candidates=[
    source.anchor,source.renderAnchor,source.position,source.fallbackAnchor,source.legacyAnchor,
    record.renderAnchor,record.anchor,record.position,record.fallbackAnchor,record.legacyAnchor
  ];
  return candidates.some(validPoint);
}

function normalizedCanonicalAnchor(source,binding,record){
  const base={
    schema:SOURCE_SCHEMA,
    state:source.state,
    nativeWidth:NATIVE_WIDTH,
    nativeHeight:NATIVE_HEIGHT,
    readOnly:true,
    ramWrites:0,
    inputInjection:false
  };
  if(source.state==='SUPPRESSED')return{...base,reason:source.reason};
  return{
    ...base,
    actor:record.actor,
    generation:record.generation,
    anchor:{x:source.anchor.x,y:source.anchor.y},
    authorityKey:binding.authorityKey,
    runtimeEpoch:binding.runtimeEpoch,
    rendererEpoch:binding.rendererEpoch,
    ...(record.worldSha256?{worldSha256:record.worldSha256}:{})
  };
}

function normalizeRecord(record,binding,nowMs,maxAgeMs){
  const identity=validateIdentity(record);if(!identity.ok)return identity;
  const source=record.canonicalAnchor;
  if(!source||typeof source!=='object')return fail('CANONICAL_ANCHOR_MISSING');
  if(source.schema!==SOURCE_SCHEMA)return fail('SOURCE_SCHEMA_INVALID');
  if(!STATES.has(source.state))return fail('SOURCE_STATE_INVALID');
  if(source.nativeWidth!==NATIVE_WIDTH||source.nativeHeight!==NATIVE_HEIGHT)return fail('NATIVE_COORDINATE_CONTRACT_MISMATCH');
  const safety=validateSafety(source);if(!safety.ok)return safety;
  const timing=validateSampleTime(record.sampleAt,nowMs,maxAgeMs);if(!timing.ok)return timing;
  if(own(source,'sampleAt')&&source.sampleAt!==record.sampleAt)return fail('SAMPLE_TIME_MISMATCH');

  const consistency=validateBindingConsistency(record,source,binding);if(!consistency.ok)return consistency;
  if(own(record,'worldSha256')&&record.worldSha256!=null&&!validWorldSha(record.worldSha256))return fail('WORLD_IDENTITY_INVALID');

  if(source.state==='READY'){
    if(!own(source,'authorityKey')||!own(source,'runtimeEpoch')||!own(source,'rendererEpoch'))return fail('READY_AUTHORITY_BINDING_MISSING');
    if(source.actor!==record.actor)return fail('ACTOR_MISMATCH');
    if(source.generation!==record.generation)return fail('GENERATION_MISMATCH');
    if(!validPoint(source.anchor))return fail('READY_ANCHOR_INVALID');
    if(source.anchor.x<0||source.anchor.x>NATIVE_WIDTH||source.anchor.y<0||source.anchor.y>NATIVE_HEIGHT)return fail('READY_ANCHOR_OUT_OF_BOUNDS');
  }else{
    if(typeof source.reason!=='string'||source.reason.length===0)return fail('SUPPRESSION_REASON_INVALID');
    if(hasSuppressedFallback(record,source))return fail('SUPPRESSED_FALLBACK_POSITION_FORBIDDEN');
    if(own(source,'actor')&&source.actor!==record.actor)return fail('ACTOR_MISMATCH');
    if(own(source,'generation')&&source.generation!==record.generation)return fail('GENERATION_MISMATCH');
  }

  const worldSha256=consistency.worldSha256;
  const canonicalAnchor=normalizedCanonicalAnchor(source,binding,{...record,worldSha256});
  const normalized={
    kind:record.kind,
    actor:record.actor,
    ...(record.kind==='enemy'?{slot:Number(record.actor.slice('enemy-slot-'.length))}:{}),
    generation:record.generation,
    status:source.state,
    renderAnchor:source.state==='READY'?{x:source.anchor.x,y:source.anchor.y}:null,
    suppressionReason:source.state==='SUPPRESSED'?source.reason:null,
    nativeWidth:NATIVE_WIDTH,
    nativeHeight:NATIVE_HEIGHT,
    authorityKey:binding.authorityKey,
    runtimeEpoch:binding.runtimeEpoch,
    rendererEpoch:binding.rendererEpoch,
    worldSha256,
    sampleAt:record.sampleAt,
    ageMs:timing.ageMs,
    readOnly:true,
    ramWrites:0,
    inputInjection:false,
    sourceSchema:SOURCE_SCHEMA,
    canonicalAnchor
  };
  return{ok:true,value:normalized};
}

function emptyFailure(reason,detail={}){
  return{
    ok:false,
    schema:VERSION,
    reason,
    nativeWidth:NATIVE_WIDTH,
    nativeHeight:NATIVE_HEIGHT,
    authority:null,
    records:[],
    ready:[],
    suppressed:[],
    ...detail
  };
}

function normalizeEnvelope({records=[],authorityBinding,nowMs,maxAgeMs=DEFAULT_MAX_AGE_MS}={}){
  const authority=validateAuthorityBinding(authorityBinding);
  if(!authority.ok)return emptyFailure(authority.reason);
  if(!Array.isArray(records))return emptyFailure('RECORDS_INVALID');
  if(records.length>MAX_RECORDS)return emptyFailure('RECORD_LIMIT_EXCEEDED',{maxRecords:MAX_RECORDS});
  const now=finite(nowMs)?nowMs:Date.now();
  const normalized=[];
  const seen=new Set();
  let worldSha256=authority.value.worldSha256;

  for(let index=0;index<records.length;index+=1){
    const record=records[index];
    const identity=validateIdentity(record);
    if(!identity.ok)return emptyFailure(identity.reason,{recordIndex:index});
    const identityKey=record.actor+'#'+record.generation;
    if(seen.has(identityKey))return emptyFailure('DUPLICATE_ACTOR_GENERATION',{recordIndex:index,identityKey});
    seen.add(identityKey);

    const result=normalizeRecord(record,authority.value,now,maxAgeMs);
    if(!result.ok)return emptyFailure(result.reason,{recordIndex:index,...('field'in result?{field:result.field}:{}),...('ageMs'in result?{ageMs:result.ageMs}:{})});
    const recordWorld=result.value.worldSha256;
    if(recordWorld!=null){
      if(worldSha256!=null&&recordWorld!==worldSha256)return emptyFailure('MIXED_WORLD_IDENTITY',{recordIndex:index});
      worldSha256=recordWorld;
    }
    normalized.push(result.value);
  }

  const finalAuthority={...authority.value,worldSha256};
  const recordsOut=normalized.map(record=>Object.freeze({...record}));
  const ready=recordsOut.filter(record=>record.status==='READY');
  const suppressed=recordsOut.filter(record=>record.status==='SUPPRESSED');
  return{
    ok:true,
    schema:VERSION,
    reason:null,
    nativeWidth:NATIVE_WIDTH,
    nativeHeight:NATIVE_HEIGHT,
    authority:finalAuthority,
    records:recordsOut,
    ready,
    suppressed
  };
}

function readyByActor(envelope){
  if(!envelope||envelope.ok!==true||envelope.schema!==VERSION)return{};
  const out={};
  for(const record of envelope.ready||[]){out[record.actor]=record;}
  return out;
}

function toPlayerAnchorSamples(envelope){
  if(!envelope||envelope.ok!==true||envelope.schema!==VERSION)return{};
  const out={};
  for(const record of envelope.records||[]){
    if(record.kind!=='player')continue;
    out[record.actor]={canonicalAnchor:record.canonicalAnchor,sampleAt:record.sampleAt};
  }
  return out;
}

function toEnemyAnchorArray(envelope){
  if(!envelope||envelope.ok!==true||envelope.schema!==VERSION)return[];
  return(envelope.records||[]).filter(record=>record.kind==='enemy').map(record=>({
    slot:record.slot,
    actor:record.actor,
    generation:record.generation,
    sampleAt:record.sampleAt,
    canonicalAnchor:record.canonicalAnchor
  }));
}

const api={
  VERSION,SOURCE_SCHEMA,NATIVE_WIDTH,NATIVE_HEIGHT,DEFAULT_MAX_AGE_MS,MAX_RECORDS,
  validateAuthorityBinding,normalizeEnvelope,readyByActor,toPlayerAnchorSamples,toEnemyAnchorArray
};
if(typeof module!=='undefined'&&module.exports)module.exports=api;
root.WOFAlphaCanonicalAnchorEnvelope=api;
})(typeof self!=='undefined'?self:globalThis);
