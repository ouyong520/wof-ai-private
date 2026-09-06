'use strict';
(function(factory){
  const API=factory();
  if(typeof globalThis!=='undefined')globalThis.WOFGStyphoonRendererCorrelationProbeP42=API;
  if(typeof module!=='undefined'&&module.exports)module.exports=API;
})(function(){
  const SCHEMA='wof-gstyphoon-renderer-correlation-probe-v1';
  const CLASSIFICATION='UNVERIFIED_AUTO_BASELINE';
  const SAFETY=Object.freeze({readOnly:true,ramWrites:0,inputInjection:false,ownerSelectionRequired:false,manualSeedRequired:false,promotion:false,alphaLiveMoved:false});
  const DEFAULT_LIMITS=Object.freeze({maxWallMs:15000,maxSubmissions:256,maxBufferUploads:128,maxTextureUploads:64,maxRawBytesPerPayload:2048,maxHashBytesPerPayload:1048576,maxVertexAttribs:16,maxTextureUnits:16,maxShaderSourceBytes:262144});

  const finite=v=>Number.isFinite(v);
  const nonempty=v=>typeof v==='string'&&v.trim().length>0;
  const clone=v=>{if(v==null)return v;try{if(typeof structuredClone==='function')return structuredClone(v);}catch(_){}return JSON.parse(JSON.stringify(v));};
  const bindingValid=b=>!!b&&nonempty(b.runtimeEpoch)&&nonempty(b.rendererEpoch)&&nonempty(b.authorityKey);
  const sameBinding=(a,b)=>bindingValid(a)&&bindingValid(b)&&a.runtimeEpoch===b.runtimeEpoch&&a.rendererEpoch===b.rendererEpoch&&a.authorityKey===b.authorityKey;
  const byteHex=bytes=>Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
  function fnv1a64(bytes,maxBytes){
    const limit=Math.min(bytes.byteLength,maxBytes);
    let h=14695981039346656037n;
    for(let i=0;i<limit;i++){h^=BigInt(bytes[i]);h=BigInt.asUintN(64,h*1099511628211n);}
    return{algorithm:'FNV1A64',value:h.toString(16).padStart(16,'0'),hashedBytes:limit,complete:limit===bytes.byteLength};
  }
  function stringBytes(s,max){
    const text=String(s||'');
    let bytes;
    try{bytes=new TextEncoder().encode(text);}catch(_){bytes=Uint8Array.from(Array.from(text,c=>c.charCodeAt(0)&255));}
    if(bytes.byteLength<=max)return bytes;
    return bytes.subarray(0,max);
  }
  function payloadView(data,srcOffset,srcLength){
    if(data==null)return null;
    let buffer,baseOffset,byteLength,bpe=1,kind;
    if(ArrayBuffer.isView(data)){
      buffer=data.buffer;baseOffset=data.byteOffset;byteLength=data.byteLength;bpe=Number(data.BYTES_PER_ELEMENT)||1;kind=data.constructor?.name||'ArrayBufferView';
    }else if(data instanceof ArrayBuffer){buffer=data;baseOffset=0;byteLength=data.byteLength;kind='ArrayBuffer';}
    else return null;
    const totalElements=Math.floor(byteLength/bpe);
    const elementOffset=Number.isInteger(srcOffset)&&srcOffset>=0?srcOffset:0;
    const available=Math.max(0,totalElements-elementOffset);
    const elementLength=Number.isInteger(srcLength)&&srcLength>=0?Math.min(srcLength,available):available;
    const start=baseOffset+elementOffset*bpe;
    const bytes=new Uint8Array(buffer,start,elementLength*bpe);
    return{bytes,kind,bytesPerElement:bpe,sourceByteOffset:start,sourceElementOffset:elementOffset,sourceElementLength:elementLength};
  }
  function summarizePayload(data,srcOffset,srcLength,limits){
    const view=payloadView(data,srcOffset,srcLength);if(!view)return null;
    const bytes=view.bytes,cap=Math.min(bytes.byteLength,limits.maxRawBytesPerPayload),head=Math.ceil(cap/2),tail=Math.floor(cap/2);
    const raw=bytes.byteLength<=cap?{mode:'FULL',hex:byteHex(bytes),capturedBytes:bytes.byteLength}:{mode:'HEAD_TAIL',headHex:byteHex(bytes.subarray(0,head)),tailHex:byteHex(bytes.subarray(bytes.byteLength-tail)),capturedBytes:cap};
    return{sourceType:view.kind,bytesPerElement:view.bytesPerElement,sourceByteOffset:view.sourceByteOffset,sourceElementOffset:view.sourceElementOffset,sourceElementLength:view.sourceElementLength,totalBytes:bytes.byteLength,hash:fnv1a64(bytes,limits.maxHashBytesPerPayload),raw,truncated:bytes.byteLength>cap};
  }
  function normalizedLimits(input={}){
    const out={};for(const [k,v] of Object.entries(DEFAULT_LIMITS)){const n=Number(input[k]);out[k]=finite(n)&&n>0?Math.max(1,Math.floor(n)):v;}return out;
  }
  function baselineFromStatus(status){
    const base={available:false,accepted:false,classification:CLASSIFICATION,authorityEligible:false,reason:'BASELINE_UNAVAILABLE',players:{}};
    if(!status||typeof status!=='object')return base;
    if(status.classification!==CLASSIFICATION)return{...base,available:true,reason:'BASELINE_CLASSIFICATION_INVALID'};
    if(status.rendererSourceProof!==null)return{...base,available:true,reason:'BASELINE_PROOF_BOUNDARY_VIOLATION'};
    const a=status.authorityEligibility;
    if(a&&(a.p29Pass!==false||a.p32NativeMarkerQualification!==false||a.p36RendererSourceTrace!==false||a.p34RetryReadiness!==false||a.promotion!==false))return{...base,available:true,reason:'BASELINE_AUTHORITY_BOUNDARY_VIOLATION'};
    const tracks=status.controller?.tracks||{};const players={};
    for(const p of ['P1','P2','P3']){
      const t=tracks[p];
      if(t&&t.state==='TRACKED'&&t.observed===true&&finite(t.x)&&finite(t.y))players[p]={x:t.x,y:t.y,state:t.state,observed:true,coordinateClass:t.coordinateClass||null,reacquireCount:Number(t.reacquireCount||0)};
    }
    const ambiguous=status.controller?.envelopeState==='AMBIGUOUS'||Object.values(tracks).some(t=>t?.state==='AMBIGUOUS');
    const stale=status.controller?.visibleFresh===false||status.state==='STALE_OR_UNAVAILABLE';
    return{...base,available:true,accepted:!ambiguous&&!stale,reason:ambiguous?'BASELINE_AMBIGUOUS_DIAGNOSTIC_ONLY':stale?'BASELINE_STALE_DIAGNOSTIC_ONLY':null,visibleFresh:status.controller?.visibleFresh===true,envelopeState:status.controller?.envelopeState||null,players};
  }

  function createProbe(options={}){
    const root=options.root||(typeof globalThis!=='undefined'?globalThis:null),gl=options.gl||root?.I_fdC8Q;
    if(!root||!gl)throw new Error('P42 browser/WebGL diagnostic environment missing');
    const limits=normalizedLimits(options.limits||{}),baselineProvider=typeof options.baselineProvider==='function'?options.baselineProvider:(now=>{try{return root.WOFALPHAAUTOBASELINEHUD?.status?.(now)||null;}catch(_){return null;}}),bindingProvider=typeof options.bindingProvider==='function'?options.bindingProvider:null,frameProvider=typeof options.frameProvider==='function'?options.frameProvider:null;
    let state='IDLE',terminal=false,reason='NOT_STARTED',binding=null,startedAt=null,endedAt=null,timer=null,submissionSequence=0,frameSequence=0,lastRafTimestamp=null,lastFrameIdentity=null,teardownConflicts=[],installed=false;
    const submissions=[],bufferUploads=[],textureUploads=[],rangeBindings=new Map(),objectIds=new WeakMap(),shaderIds=new WeakMap(),programIds=new WeakMap(),bufferIds=new WeakMap(),textureIds=new WeakMap();
    const originals=new Map(),wrappers=new Map();let nextObject=1,nextShader=1,nextProgram=1,nextBuffer=1,nextTexture=1;
    const textureShadow=new Map();let activeTextureShadow=safeGetParameter(gl.ACTIVE_TEXTURE);

    function idFor(map,obj,prefix,next){if(obj==null)return null;if((typeof obj!=='object'&&typeof obj!=='function'))return`${prefix}:primitive:${String(obj)}`;let id=map.get(obj);if(!id){id=`${prefix}${next()}`;map.set(obj,id);}return id;}
    const objectId=o=>idFor(objectIds,o,'O',()=>nextObject++),shaderId=o=>idFor(shaderIds,o,'S',()=>nextShader++),programId=o=>idFor(programIds,o,'P',()=>nextProgram++),bufferId=o=>idFor(bufferIds,o,'B',()=>nextBuffer++),textureId=o=>idFor(textureIds,o,'T',()=>nextTexture++);
    function safe(fn,fallback=null){try{return fn();}catch(_){return fallback;}}
    function safeGetParameter(p){return p==null?null:safe(()=>gl.getParameter(p),null);}
    function verifyBinding(){
      if(!bindingProvider)return true;
      const current=safe(()=>bindingProvider(),null);
      if(!sameBinding(current,binding)){reject('STALE_OR_MIXED_AUTHORITY_BINDING');return false;}
      return true;
    }
    function reject(code){if(terminal)return;state='REJECTED';reason=code;terminal=true;endedAt=Date.now();teardown();}
    function seal(code='BOUNDED_CAPTURE_COMPLETE'){if(terminal)return;state=submissions.length?'CAPTURE_READY':'CAPTURE_EMPTY';reason=code;terminal=true;endedAt=Date.now();teardown();}
    function currentFrame(){
      if(frameProvider){const v=safe(()=>frameProvider(),null);if(v!=null)lastFrameIdentity=v;}
      return{frameSequence,frameIdentity:lastFrameIdentity,frameSource:frameProvider?'EXPLICIT_PROVIDER':(lastRafTimestamp!==null?'REQUEST_ANIMATION_FRAME_TIMESTAMP':'UNAVAILABLE'),rafTimestamp:lastRafTimestamp};
    }
    function shaderSnapshot(shader){
      if(!shader)return null;const source=safe(()=>gl.getShaderSource(shader),'')||'',fullBytes=stringBytes(source,Number.MAX_SAFE_INTEGER),storedBytes=fullBytes.byteLength<=limits.maxShaderSourceBytes?fullBytes:fullBytes.subarray(0,limits.maxShaderSourceBytes),truncated=storedBytes.byteLength<fullBytes.byteLength;return{id:shaderId(shader),type:safe(()=>gl.getShaderParameter(shader,gl.SHADER_TYPE),null),sourceBytes:fullBytes.byteLength,sourceTruncated:truncated,sourceText:truncated?null:source,sourcePrefix:truncated?source.slice(0,4096):null,sourceHash:fnv1a64(fullBytes,limits.maxShaderSourceBytes)};
    }
    function programSnapshot(program){
      if(!program)return null;const attached=safe(()=>gl.getAttachedShaders(program),[])||[],shaders=attached.map(shaderSnapshot).filter(Boolean);const keyInput=shaders.map(s=>`${s.type}:${s.sourceHash.value}`).sort().join('|');const keyBytes=stringBytes(keyInput,65536);return{id:programId(program),linked:safe(()=>!!gl.getProgramParameter(program,gl.LINK_STATUS),null),shaderCount:shaders.length,shaders,shaderSetHash:fnv1a64(keyBytes,keyBytes.byteLength)};
    }
    function bufferBinding(target,bindingEnum){
      const obj=safeGetParameter(bindingEnum);let size=null;if(obj&&gl.BUFFER_SIZE!=null)size=safe(()=>gl.getBufferParameter(target,gl.BUFFER_SIZE),null);return{bufferId:bufferId(obj),sizeBytes:finite(size)?size:null};
    }
    function attribDescriptors(){
      const max=Math.min(limits.maxVertexAttribs,Number(safeGetParameter(gl.MAX_VERTEX_ATTRIBS))||limits.maxVertexAttribs),rows=[];
      for(let i=0;i<max;i++){
        const enabled=safe(()=>!!gl.getVertexAttrib(i,gl.VERTEX_ATTRIB_ARRAY_ENABLED),false),buf=safe(()=>gl.getVertexAttrib(i,gl.VERTEX_ATTRIB_ARRAY_BUFFER_BINDING),null);
        if(!enabled&&!buf)continue;
        rows.push({index:i,enabled,bufferId:bufferId(buf),size:safe(()=>gl.getVertexAttrib(i,gl.VERTEX_ATTRIB_ARRAY_SIZE),null),type:safe(()=>gl.getVertexAttrib(i,gl.VERTEX_ATTRIB_ARRAY_TYPE),null),normalized:safe(()=>!!gl.getVertexAttrib(i,gl.VERTEX_ATTRIB_ARRAY_NORMALIZED),null),stride:safe(()=>gl.getVertexAttrib(i,gl.VERTEX_ATTRIB_ARRAY_STRIDE),null),offset:safe(()=>gl.getVertexAttribOffset(i,gl.VERTEX_ATTRIB_ARRAY_POINTER),null),divisor:gl.VERTEX_ATTRIB_ARRAY_DIVISOR!=null?safe(()=>gl.getVertexAttrib(i,gl.VERTEX_ATTRIB_ARRAY_DIVISOR),null):null});
      }return rows;
    }
    function textureBindings(){
      const active=safeGetParameter(gl.ACTIVE_TEXTURE),direct2d=safeGetParameter(gl.TEXTURE_BINDING_2D);if(active!=null&&direct2d!=null){const row=textureShadow.get(active)||{};textureShadow.set(active,{...row,texture2D:textureId(direct2d)});}
      return{activeTexture:active,activeTexture2D:textureId(direct2d),coverage:'ACTIVE_UNIT_PLUS_POST_INSTALL_BIND_CALLS',observedUnits:[...textureShadow.entries()].slice(0,limits.maxTextureUnits).map(([unit,row])=>({unit,texture2D:row.texture2D||null,textureCube:row.textureCube||null,texture3D:row.texture3D||null,texture2DArray:row.texture2DArray||null,bankSemantic:null})),semanticBankIdentityAvailable:false};
    }
    function baselineSnapshot(now){return baselineFromStatus(safe(()=>baselineProvider(now),null));}
    function groupKeyFor(row){
      const material={method:row.draw.method,mode:row.draw.mode,program:row.program?.shaderSetHash?.value||row.program?.id||null,arrayBuffer:row.buffers.array.bufferId,elementArrayBuffer:row.buffers.element.bufferId,attribs:row.vertexAttribs.map(a=>[a.index,a.bufferId,a.size,a.type,a.normalized,a.stride,a.offset,a.divisor]),textures:row.textures.observedUnits.map(t=>[t.unit,t.texture2D,t.textureCube,t.texture3D,t.texture2DArray])};
      const bytes=stringBytes(JSON.stringify(material),262144);return'G-'+fnv1a64(bytes,bytes.byteLength).value;
    }
    function captureSubmission(method,args){
      if(terminal||!verifyBinding())return;
      const now=Date.now(),frame=currentFrame(),program=safeGetParameter(gl.CURRENT_PROGRAM),row={at:now,submissionSequence:++submissionSequence,...frame,binding:{...binding},draw:method==='drawArrays'?{method,mode:args[0],first:args[1],count:args[2],indexType:null,indexByteOffset:null}:{method,mode:args[0],count:args[1],indexType:args[2],indexByteOffset:args[3]},program:programSnapshot(program),buffers:{array:bufferBinding(gl.ARRAY_BUFFER,gl.ARRAY_BUFFER_BINDING),element:bufferBinding(gl.ELEMENT_ARRAY_BUFFER,gl.ELEMENT_ARRAY_BUFFER_BINDING),ranges:[...rangeBindings.values()].map(clone)},vertexAttribs:attribDescriptors(),textures:textureBindings(),viewport:Array.from(safeGetParameter(gl.VIEWPORT)||[]),scissorBox:Array.from(safeGetParameter(gl.SCISSOR_BOX)||[]),scissorEnabled:gl.SCISSOR_TEST!=null?safe(()=>!!gl.isEnabled(gl.SCISSOR_TEST),null):null,diagnosticCorrelation:baselineSnapshot(now),authorityEligible:false};
      row.groupKey=groupKeyFor(row);submissions.push(row);if(submissions.length>=limits.maxSubmissions)seal('BOUNDED_SUBMISSION_LIMIT_REACHED');
    }
    function captureBufferUpload(method,args){
      if(terminal||bufferUploads.length>=limits.maxBufferUploads||!verifyBinding())return;
      const target=args[0],bound=target===gl.ARRAY_BUFFER?safeGetParameter(gl.ARRAY_BUFFER_BINDING):target===gl.ELEMENT_ARRAY_BUFFER?safeGetParameter(gl.ELEMENT_ARRAY_BUFFER_BINDING):null;
      let data=null,dstByteOffset=null,usage=null,srcOffset=null,srcLength=null;
      if(method==='bufferData'){data=args[1];usage=args[2];srcOffset=args[3];srcLength=args[4];}
      else{dstByteOffset=args[1];data=args[2];srcOffset=args[3];srcLength=args[4];}
      bufferUploads.push({at:Date.now(),method,target,bufferId:bufferId(bound),usage:usage??null,destinationByteOffset:dstByteOffset,payload:summarizePayload(data,srcOffset,srcLength,limits),binding:{...binding},authorityEligible:false});
    }
    function captureTextureUpload(method,args){
      if(terminal||textureUploads.length>=limits.maxTextureUploads||!verifyBinding())return;
      let payload=null,sourceType=null;
      for(let i=args.length-1;i>=0;i--){if(ArrayBuffer.isView(args[i])||args[i] instanceof ArrayBuffer){payload=summarizePayload(args[i],null,null,limits);sourceType=payload?.sourceType||null;break;}if(args[i]&&typeof args[i]==='object'&&!sourceType)sourceType=args[i].constructor?.name||'Object';}
      const active=safeGetParameter(gl.ACTIVE_TEXTURE),binding2d=safeGetParameter(gl.TEXTURE_BINDING_2D);
      textureUploads.push({at:Date.now(),method,numericArgs:args.map(v=>typeof v==='number'?v:null),activeTexture:active,texture2D:textureId(binding2d),sourceType,payload,binding:{...binding},authorityEligible:false});
    }
    function installMethod(name,before,after){
      const original=gl[name];if(typeof original!=='function')return;
      const wrapper=function(){const args=Array.from(arguments);try{before?.(args);}catch(e){reject('P42_OBSERVATION_HOOK_FAILED:'+name+':'+String(e?.message||e));}const out=original.apply(this,arguments);try{after?.(args,out);}catch(e){reject('P42_OBSERVATION_HOOK_FAILED:'+name+':'+String(e?.message||e));}return out;};
      originals.set(name,original);wrappers.set(name,wrapper);try{Object.defineProperty(gl,name,{value:wrapper,writable:true,configurable:true});}catch(_){gl[name]=wrapper;}if(gl[name]!==wrapper)throw new Error(`P42 hook install failed: ${name}`);
    }
    function installHooks(){
      installMethod('bufferData',args=>captureBufferUpload('bufferData',args));installMethod('bufferSubData',args=>captureBufferUpload('bufferSubData',args));installMethod('texImage2D',args=>captureTextureUpload('texImage2D',args));installMethod('texSubImage2D',args=>captureTextureUpload('texSubImage2D',args));
      installMethod('activeTexture',null,args=>{activeTextureShadow=args[0];});
      installMethod('bindTexture',null,args=>{const unit=activeTextureShadow??safeGetParameter(gl.ACTIVE_TEXTURE),target=args[0],tex=args[1],row=textureShadow.get(unit)||{};if(target===gl.TEXTURE_2D)row.texture2D=textureId(tex);else if(target===gl.TEXTURE_CUBE_MAP)row.textureCube=textureId(tex);else if(gl.TEXTURE_3D!=null&&target===gl.TEXTURE_3D)row.texture3D=textureId(tex);else if(gl.TEXTURE_2D_ARRAY!=null&&target===gl.TEXTURE_2D_ARRAY)row.texture2DArray=textureId(tex);textureShadow.set(unit,row);});
      installMethod('bindBufferRange',null,args=>{const [target,index,buf,offset,size]=args;rangeBindings.set(`${target}:${index}`,{target,index,bufferId:bufferId(buf),offset,size});});
      installMethod('bindBufferBase',null,args=>{const [target,index,buf]=args;rangeBindings.set(`${target}:${index}`,{target,index,bufferId:bufferId(buf),offset:0,size:null});});
      installMethod('drawArrays',args=>captureSubmission('drawArrays',args));installMethod('drawElements',args=>captureSubmission('drawElements',args));
      if(options.captureRafFrames!==false&&typeof root.requestAnimationFrame==='function'){
        const native=root.requestAnimationFrame,wrap=function(cb){return native.call(this,function(ts){if(lastRafTimestamp!==ts){lastRafTimestamp=ts;frameSequence++;lastFrameIdentity=ts;}return cb.apply(this,arguments);});};originals.set('root.requestAnimationFrame',native);wrappers.set('root.requestAnimationFrame',wrap);root.requestAnimationFrame=wrap;
      }
      installed=true;
    }
    function teardown(){
      if(timer!=null){try{clearTimeout(timer);}catch(_){}timer=null;}
      for(const [name,original] of originals.entries()){
        if(name==='root.requestAnimationFrame'){const wrap=wrappers.get(name);if(root.requestAnimationFrame===wrap)root.requestAnimationFrame=original;else teardownConflicts.push(name);continue;}
        const wrap=wrappers.get(name);if(gl[name]===wrap){try{Object.defineProperty(gl,name,{value:original,writable:true,configurable:true});}catch(_){gl[name]=original;}}else teardownConflicts.push(name);
      }
      installed=false;
    }
    function start(expectedBinding){
      if(state!=='IDLE'&&!terminal)throw new Error('P42 probe already active');if(!bindingValid(expectedBinding))throw new Error('exact runtimeEpoch/rendererEpoch/authorityKey binding required');
      binding={runtimeEpoch:expectedBinding.runtimeEpoch,rendererEpoch:expectedBinding.rendererEpoch,authorityKey:expectedBinding.authorityKey};startedAt=Date.now();endedAt=null;state='OBSERVING';terminal=false;reason='BOUNDED_DIAGNOSTIC_CAPTURE_ACTIVE';
      if(bindingProvider&&!sameBinding(safe(()=>bindingProvider(),null),binding)){reject('STALE_OR_MIXED_AUTHORITY_BINDING');return status();}
      installHooks();timer=setTimeout(()=>seal('BOUNDED_WALL_LIMIT_REACHED'),limits.maxWallMs);return status();
    }
    function markFrame(frameIdentity=null,rafTimestamp=null){if(terminal)return status();frameSequence++;lastFrameIdentity=frameIdentity??frameSequence;if(finite(rafTimestamp))lastRafTimestamp=rafTimestamp;return status();}
    function stop(stopReason='STOPPED_BY_HARNESS'){if(!terminal){state=submissions.length?'CAPTURE_READY':'CAPTURE_EMPTY';reason=stopReason;terminal=true;endedAt=Date.now();teardown();}return status();}
    function groups(){
      const map=new Map();for(const s of submissions){let g=map.get(s.groupKey);if(!g){g={groupKey:s.groupKey,method:s.draw.method,mode:s.draw.mode,programShaderSetHash:s.program?.shaderSetHash?.value||null,arrayBufferId:s.buffers.array.bufferId,elementArrayBufferId:s.buffers.element.bufferId,submissionSequences:[],frameSequences:[],frameIdentities:[],baselinePlayers:new Set()};map.set(s.groupKey,g);}g.submissionSequences.push(s.submissionSequence);if(!g.frameSequences.includes(s.frameSequence))g.frameSequences.push(s.frameSequence);if(s.frameIdentity!=null&&!g.frameIdentities.includes(s.frameIdentity))g.frameIdentities.push(s.frameIdentity);for(const p of Object.keys(s.diagnosticCorrelation?.players||{}))g.baselinePlayers.add(p);}
      return [...map.values()].sort((a,b)=>a.groupKey.localeCompare(b.groupKey)).map(g=>({...g,baselinePlayers:[...g.baselinePlayers].sort(),observationCount:g.submissionSequences.length}));
    }
    function status(){return{schema:SCHEMA,state,terminal,reason,installed,binding:binding?{...binding}:null,bindingFreshness:{providerPresent:!!bindingProvider,checkedOnEveryObservedHook:!!bindingProvider},submissionCount:submissions.length,bufferUploadCount:bufferUploads.length,textureUploadCount:textureUploads.length,frameSequence,limits:{...limits},authorityEligible:false,...SAFETY};}
    function result(){const gs=groups();return{schema:SCHEMA,state,terminal,reason,startedAt,endedAt,binding:binding?{...binding}:null,bindingFreshness:{providerPresent:!!bindingProvider,checkedOnEveryObservedHook:!!bindingProvider},limits:{...limits},submissions:clone(submissions),bufferUploads:clone(bufferUploads),textureUploads:clone(textureUploads),submissionGroups:gs,mappingAssessment:{status:'DIAGNOSTIC_ONLY_NO_AUTHORITY_SELECTION',selectionMade:false,selectedSubmission:null,selectedGroup:null,ambiguityPreserved:gs.length!==1||submissions.length!==1,groupCount:gs.length,authorityEligible:false,forbiddenAuthorityPromotions:['PIXEL','SCREENSHOT','OCR','TEMPLATE','NEAREST_ONLY','TIMING_ONLY','ORDER_ONLY','GUESSED_OFFSET']},correlationContract:{classification:CLASSIFICATION,diagnosticOnly:true,productionCoordinates:false,authorityEligible:false},teardown:{installed,conflicts:[...teardownConflicts]},authorityEligible:false,...SAFETY};}
    return Object.freeze({schema:SCHEMA,start,status,result,stop,markFrame});
  }
  return Object.freeze({SCHEMA,CLASSIFICATION,DEFAULT_LIMITS,createProbe,_test:{fnv1a64,payloadView,summarizePayload,baselineFromStatus,sameBinding}});
});
