'use strict';
(function(factory){
  const API=factory();
  if(typeof globalThis!=='undefined')globalThis.WOFWasmWebGLCallsiteFingerprintProbeP46=API;
  if(typeof module!=='undefined'&&module.exports)module.exports=API;
})(function(){
  const SCHEMA='wof-wasm-webgl-callsite-fingerprint-probe-v1';
  const SAFETY=Object.freeze({
    readOnly:true,
    ramWrites:0,
    inputInjection:false,
    ownerSelectionRequired:false,
    manualSeedRequired:false,
    promotion:false,
    alphaLiveMoved:false,
    mappingOnly:true,
    authorityEligible:false
  });
  const DEFAULT_LIMITS=Object.freeze({
    maxWallMs:15000,
    maxEvents:384,
    maxDrawSubmissions:256,
    maxBufferEvents:192,
    maxAttribEvents:192,
    maxRawStackChars:4096,
    maxStackLines:48,
    maxNormalizedFrames:32
  });
  const INTERNAL_STACK_MARKERS=Object.freeze([
    'defaultStackProvider',
    'captureCallsite',
    'recordDraw',
    'recordBufferEvent',
    'recordAttribEvent',
    'recordBoundaryEvent',
    'guardedCapture',
    'p46WrappedWebGLBoundary'
  ]);
  const finite=v=>Number.isFinite(v);
  const nonempty=v=>typeof v==='string'&&v.trim().length>0;
  const bindingValid=b=>!!b&&nonempty(b.runtimeEpoch)&&nonempty(b.rendererEpoch)&&nonempty(b.authorityKey);
  const sameBinding=(a,b)=>bindingValid(a)&&bindingValid(b)&&a.runtimeEpoch===b.runtimeEpoch&&a.rendererEpoch===b.rendererEpoch&&a.authorityKey===b.authorityKey;
  const clone=v=>v==null?v:JSON.parse(JSON.stringify(v));
  const unique=values=>[...new Set(values)];
  function normalizedLimits(input={}){
    const out={};
    for(const [key,fallback] of Object.entries(DEFAULT_LIMITS)){
      const n=Number(input[key]);
      out[key]=finite(n)&&n>0?Math.max(1,Math.floor(n)):fallback;
    }
    return out;
  }
  function textBytes(text){
    try{return new TextEncoder().encode(String(text));}
    catch(_){return Uint8Array.from(Array.from(String(text),c=>c.charCodeAt(0)&255));}
  }
  function fnv1a64(text){
    const bytes=textBytes(text);
    let h=14695981039346656037n;
    for(const b of bytes){h^=BigInt(b);h=BigInt.asUintN(64,h*1099511628211n);}
    return{algorithm:'FNV1A64',value:h.toString(16).padStart(16,'0'),inputBytes:bytes.byteLength};
  }
  function normalizeFrameLine(line){return String(line||'').trim().replace(/\s+/g,' ');}
  function isInternalFrame(line){return INTERNAL_STACK_MARKERS.some(marker=>line.includes(marker));}
  function parseFunctionName(line,isWasm){
    let m=line.match(/^at\s+([^\s(]+)\s*\(/);
    if(m&&m[1]&&!/^wasm-function\[/i.test(m[1]))return m[1];
    m=line.match(/^([^@\s]+)@/);
    if(m&&m[1]&&!/^wasm-function\[/i.test(m[1]))return m[1];
    if(!isWasm){
      m=line.match(/^at\s+([^\s]+)\s+/);
      if(m&&m[1])return m[1];
    }
    return null;
  }
  function parseFrame(line,index){
    const normalizedLine=normalizeFrameLine(line);
    const indexMatch=normalizedLine.match(/wasm-function\[(\d+)\]/i);
    const isWasm=!!indexMatch||/wasm:\/\//i.test(normalizedLine)||/\.wasm(?::|\?|\/|\)|$)/i.test(normalizedLine);
    const offsetMatch=isWasm?normalizedLine.match(/(?:wasm-function\[\d+\]|wasm:\/\/[^\s)]*?)(?::|\+)(0x[0-9a-f]+)/i):null;
    const functionName=parseFunctionName(normalizedLine,isWasm);
    return{
      stackIndex:index,
      classification:isWasm?'WASM':'JS',
      normalizedLine,
      functionName:functionName||'UNRESOLVED',
      wasmFunctionIndex:isWasm?(indexMatch?Number(indexMatch[1]):'UNRESOLVED'):'NOT_AVAILABLE',
      wasmFunctionIndexToken:isWasm?(indexMatch?indexMatch[0]:'UNRESOLVED'):'NOT_AVAILABLE',
      wasmFunctionName:isWasm?(functionName||'UNRESOLVED'):'NOT_AVAILABLE',
      wasmOffset:isWasm?(offsetMatch?offsetMatch[1]:'UNRESOLVED'):'NOT_AVAILABLE'
    };
  }
  function summarizeWasm(frames){
    const wasmFrames=frames.filter(frame=>frame.classification==='WASM');
    if(!wasmFrames.length){
      return{
        status:'NOT_AVAILABLE',
        frameCount:0,
        functionIndexStatus:'NOT_AVAILABLE',functionIndices:['NOT_AVAILABLE'],
        functionNameStatus:'NOT_AVAILABLE',functionNames:['NOT_AVAILABLE'],
        offsetStatus:'NOT_AVAILABLE',offsets:['NOT_AVAILABLE'],
        frames:[]
      };
    }
    const indices=unique(wasmFrames.map(f=>f.wasmFunctionIndex).filter(v=>Number.isInteger(v)));
    const names=unique(wasmFrames.map(f=>f.wasmFunctionName).filter(v=>v!=='UNRESOLVED'));
    const offsets=unique(wasmFrames.map(f=>f.wasmOffset).filter(v=>v!=='UNRESOLVED'));
    return{
      status:'AVAILABLE',
      frameCount:wasmFrames.length,
      functionIndexStatus:indices.length?'AVAILABLE':'UNRESOLVED',functionIndices:indices.length?indices:['UNRESOLVED'],
      functionNameStatus:names.length?'AVAILABLE':'UNRESOLVED',functionNames:names.length?names:['UNRESOLVED'],
      offsetStatus:offsets.length?'AVAILABLE':'UNRESOLVED',offsets:offsets.length?offsets:['UNRESOLVED'],
      frames:wasmFrames.map(clone)
    };
  }
  function summarizeJs(frames){
    const jsFrames=frames.filter(frame=>frame.classification==='JS');
    if(!jsFrames.length){
      return{status:'NOT_AVAILABLE',immediateJsCaller:'NOT_AVAILABLE',observedFunctionNames:['NOT_AVAILABLE'],semanticRole:'UNRESOLVED',frames:[]};
    }
    const names=unique(jsFrames.map(f=>f.functionName).filter(v=>v!=='UNRESOLVED'));
    const first=jsFrames[0];
    return{
      status:'AVAILABLE',
      immediateJsCaller:{functionName:first.functionName,normalizedLine:first.normalizedLine},
      observedFunctionNames:names.length?names:['UNRESOLVED'],
      semanticRole:'UNRESOLVED',
      frames:jsFrames.map(clone)
    };
  }
  function defaultStackProvider(){
    try{return String(new Error('P46_CALLSITE').stack||'');}
    catch(_){return '';}
  }
  function boundedStack(raw,limits){
    const original=String(raw||'');
    const charBounded=original.slice(0,limits.maxRawStackChars);
    const allLines=charBounded.split(/\r?\n/);
    const capturedLines=allLines.slice(0,limits.maxStackLines);
    const rawStack=capturedLines.join('\n');
    return{
      rawStack,
      rawStackStatus:rawStack?'AVAILABLE':'NOT_AVAILABLE',
      rawLengthChars:original.length,
      capturedLengthChars:rawStack.length,
      truncated:original.length>charBounded.length||allLines.length>capturedLines.length
    };
  }
  function createProbe(options={}){
    const root=options.root||(typeof globalThis!=='undefined'?globalThis:null);
    const gl=options.gl||root?.I_fdC8Q;
    if(!root||!gl)throw new Error('P46 browser/WebGL diagnostic environment missing');
    const limits=normalizedLimits(options.limits||{});
    const now=typeof options.clock==='function'?options.clock:()=>Date.now();
    const stackProvider=typeof options.stackProvider==='function'?options.stackProvider:defaultStackProvider;
    const bindingProvider=typeof options.bindingProvider==='function'?options.bindingProvider:null;
    const strictModuleIdentity=options.strictModuleIdentity!==false;
    const originals=new Map(),wrappers=new Map(),objectIds=new WeakMap();
    const bufferUploadsById=new Map(),attribState=new Map(),bufferBindingShadow=new Map();
    const events=[],draws=[],bufferEvents=[],attribEvents=[],teardownConflicts=[];
    let nextObjectId=1,eventSequence=0,drawSubmissionSequence=0,state='IDLE',terminal=false,reason='NOT_STARTED',binding=null,startedAt=null,endedAt=null,timer=null,installed=false;
    let moduleRef=null,asmRef=null,moduleSurfaceStartSnapshot=null;

    function objectId(obj,prefix='O'){
      if(obj==null)return null;
      if((typeof obj!=='object'&&typeof obj!=='function'))return`${prefix}:primitive:${String(obj)}`;
      let id=objectIds.get(obj);
      if(!id){id=`${prefix}${nextObjectId++}`;objectIds.set(obj,id);}
      return id;
    }
    function safe(fn,fallback=null){try{return fn();}catch(_){return fallback;}}
    function safeGetParameter(param){return param==null?null:safe(()=>gl.getParameter(param),null);}
    function moduleSurfaceSnapshot(){
      const mod=root.Module??null,asm=(mod&&(typeof mod==='object'||typeof mod==='function'))?(mod.asm??null):null;
      return{
        Module:mod==null?{status:'NOT_AVAILABLE',objectId:'NOT_AVAILABLE',type:'NOT_AVAILABLE'}:{status:'AVAILABLE',objectId:objectId(mod,'M'),type:typeof mod,constructorName:safe(()=>mod.constructor?.name,'UNRESOLVED')||'UNRESOLVED'},
        ModuleAsm:asm==null?{status:'NOT_AVAILABLE',objectId:'NOT_AVAILABLE',type:'NOT_AVAILABLE'}:{status:'AVAILABLE',objectId:objectId(asm,'A'),type:typeof asm,constructorName:safe(()=>asm.constructor?.name,'UNRESOLVED')||'UNRESOLVED'},
        relationship:mod==null||asm==null?'NOT_AVAILABLE':(mod===asm?'SAME_OBJECT':'DISTINCT_OBJECTS')
      };
    }
    function verifyModuleSurface(){
      if(!strictModuleIdentity)return true;
      const currentModule=root.Module??null;
      const currentAsm=(currentModule&&(typeof currentModule==='object'||typeof currentModule==='function'))?(currentModule.asm??null):null;
      if(currentModule!==moduleRef||currentAsm!==asmRef){reject('MODULE_OR_ASM_IDENTITY_CHANGED');return false;}
      return true;
    }
    function verifyBinding(){
      if(!bindingProvider)return true;
      const current=safe(()=>bindingProvider(),null);
      if(!sameBinding(current,binding)){reject('STALE_OR_MIXED_AUTHORITY_BINDING');return false;}
      return true;
    }
    function verifyCaptureContext(){return verifyBinding()&&verifyModuleSurface();}
    function captureCallsite(meta){
      let raw='';
      try{raw=String(stackProvider(clone(meta))||'');}catch(_){raw='';}
      const bounded=boundedStack(raw,limits);
      const lines=bounded.rawStack?bounded.rawStack.split(/\r?\n/):[];
      const frameLines=lines.filter(line=>{
        const n=normalizeFrameLine(line);
        return n&&!/^error(?::|$)/i.test(n)&&!isInternalFrame(n);
      }).slice(0,limits.maxNormalizedFrames);
      const frames=frameLines.map((line,index)=>parseFrame(line,index));
      const wasm=summarizeWasm(frames),js=summarizeJs(frames);
      const canonical={boundaryKind:meta.kind,boundaryMethod:meta.method,frames:frames.map(frame=>({classification:frame.classification,normalizedLine:frame.normalizedLine,wasmFunctionIndex:frame.wasmFunctionIndex,wasmFunctionName:frame.wasmFunctionName,wasmOffset:frame.wasmOffset}))};
      const fingerprint=frames.length?{status:'AVAILABLE',...fnv1a64(JSON.stringify(canonical)),frameCount:frames.length}:{status:'NOT_AVAILABLE',algorithm:'FNV1A64',value:null,inputBytes:0,frameCount:0};
      return{
        ...bounded,
        normalizedFrames:frames,
        normalizedCallsiteFingerprint:fingerprint,
        wasm,
        jsWrapperOrImport:js,
        moduleSurface:moduleSurfaceSnapshot()
      };
    }
    function boundBuffer(target){
      if(target===gl.ARRAY_BUFFER&&gl.ARRAY_BUFFER_BINDING!=null)return safeGetParameter(gl.ARRAY_BUFFER_BINDING);
      if(target===gl.ELEMENT_ARRAY_BUFFER&&gl.ELEMENT_ARRAY_BUFFER_BINDING!=null)return safeGetParameter(gl.ELEMENT_ARRAY_BUFFER_BINDING);
      return bufferBindingShadow.get(target)?.object||null;
    }
    function appendEvent(kind,method,args,details){
      if(terminal||!verifyCaptureContext())return null;
      const sequence=++eventSequence;
      const callsite=captureCallsite({kind,method,eventSequence:sequence,drawSubmissionSequence});
      const row={
        eventSequence:sequence,
        at:now(),
        kind,method,
        binding:{...binding},
        argsSummary:args,
        callsite,
        ...details,
        authorityEligible:false,
        mappingOnly:true
      };
      events.push(row);
      if(events.length>=limits.maxEvents)seal('BOUNDED_EVENT_LIMIT_REACHED');
      return row;
    }
    function rememberBufferEvent(row){
      if(!row?.bufferId)return;
      const list=bufferUploadsById.get(row.bufferId)||[];
      list.push({eventSequence:row.eventSequence,method:row.method,fingerprint:clone(row.callsite.normalizedCallsiteFingerprint),bufferId:row.bufferId});
      bufferUploadsById.set(row.bufferId,list);
    }
    function bufferAssociations(bufferId){
      return bufferId?(bufferUploadsById.get(bufferId)||[]).map(entry=>({...entry,associationBasis:'EXACT_BUFFER_OBJECT_ID'})):[];
    }
    function currentBufferSnapshot(){
      const arrayObject=gl.ARRAY_BUFFER_BINDING!=null?safeGetParameter(gl.ARRAY_BUFFER_BINDING):bufferBindingShadow.get(gl.ARRAY_BUFFER)?.object||null;
      const elementObject=gl.ELEMENT_ARRAY_BUFFER_BINDING!=null?safeGetParameter(gl.ELEMENT_ARRAY_BUFFER_BINDING):bufferBindingShadow.get(gl.ELEMENT_ARRAY_BUFFER)?.object||null;
      return{arrayBufferId:objectId(arrayObject,'B'),elementArrayBufferId:objectId(elementObject,'B')};
    }
    function attribAssociations(){
      return [...attribState.values()].sort((a,b)=>a.index-b.index).map(row=>({...clone(row),associationBasis:'EXACT_ATTRIB_INDEX_AND_BUFFER_OBJECT_ID'}));
    }
    function recordDraw(method,args){
      if(draws.length>=limits.maxDrawSubmissions){seal('BOUNDED_DRAW_LIMIT_REACHED');return;}
      const buffers=currentBufferSnapshot();
      const row=appendEvent('DRAW',method,method==='drawArrays'?{mode:args[0],first:args[1],count:args[2]}:{mode:args[0],count:args[1],indexType:args[2],indexByteOffset:args[3]}, {
        drawSubmissionSequence:++drawSubmissionSequence,
        buffers,
        exactAssociations:{
          arrayBufferUploads:bufferAssociations(buffers.arrayBufferId),
          elementArrayBufferUploads:bufferAssociations(buffers.elementArrayBufferId),
          vertexAttribSetups:attribAssociations(),
          associationRule:'EXACT_OBJECT_OR_ATTRIB_STATE_IDENTITY_ONLY',
          semanticSelectionMade:false
        }
      });
      if(row)draws.push(row);
      if(draws.length>=limits.maxDrawSubmissions)seal('BOUNDED_DRAW_LIMIT_REACHED');
    }
    function recordBufferEvent(method,args){
      if(bufferEvents.length>=limits.maxBufferEvents)return;
      const target=args[0];
      let obj=null,details={target};
      if(method==='bindBuffer'){
        obj=args[1]??null;
        bufferBindingShadow.set(target,{object:obj,bufferId:objectId(obj,'B')});
        details={...details,bufferId:objectId(obj,'B'),bindingAction:'BIND'};
      }else if(method==='bindBufferBase'){
        obj=args[2]??null;
        details={...details,index:args[1],bufferId:objectId(obj,'B'),bindingAction:'BIND_BASE'};
      }else if(method==='bindBufferRange'){
        obj=args[2]??null;
        details={...details,index:args[1],bufferId:objectId(obj,'B'),offset:args[3],size:args[4],bindingAction:'BIND_RANGE'};
      }else{
        obj=boundBuffer(target);
        const isData=method==='bufferData';
        details={...details,bufferId:objectId(obj,'B'),uploadAction:method,destinationByteOffset:isData?null:(args[1]??null),usage:isData?(args[2]??null):null,payloadType:(isData?args[1]:args[2])?.constructor?.name||typeof (isData?args[1]:args[2])};
      }
      const row=appendEvent(method.startsWith('buffer')?'BUFFER_UPLOAD':'BUFFER_SETUP',method,{target},details);
      if(row){bufferEvents.push(row);if(method==='bufferData'||method==='bufferSubData')rememberBufferEvent(row);}
    }
    function recordAttribEvent(method,args){
      if(attribEvents.length>=limits.maxAttribEvents)return;
      const index=Number(args[0]);
      const currentArray=gl.ARRAY_BUFFER_BINDING!=null?safeGetParameter(gl.ARRAY_BUFFER_BINDING):bufferBindingShadow.get(gl.ARRAY_BUFFER)?.object||null;
      let details={index,bufferId:objectId(currentArray,'B')};
      if(method==='vertexAttribPointer'||method==='vertexAttribIPointer'){
        details={...details,size:args[1],type:args[2],normalized:method==='vertexAttribPointer'?!!args[3]:false,stride:method==='vertexAttribPointer'?args[4]:args[3],offset:method==='vertexAttribPointer'?args[5]:args[4],integer:method==='vertexAttribIPointer'};
      }else if(method==='vertexAttribDivisor')details={...details,divisor:args[1]};
      else if(method==='enableVertexAttribArray'||method==='disableVertexAttribArray')details={...details,enabled:method==='enableVertexAttribArray'};
      const row=appendEvent('VERTEX_ATTRIB_SETUP',method,{index},details);
      if(!row)return;
      attribEvents.push(row);
      const previous=attribState.get(index)||{index,bufferId:details.bufferId,enabled:null,divisor:null};
      const next={...previous,index,bufferId:details.bufferId??previous.bufferId,lastSetupEventSequence:row.eventSequence,lastSetupMethod:method,lastSetupFingerprint:clone(row.callsite.normalizedCallsiteFingerprint)};
      if(method==='vertexAttribPointer'||method==='vertexAttribIPointer')Object.assign(next,{size:details.size,type:details.type,normalized:details.normalized,stride:details.stride,offset:details.offset,integer:details.integer});
      if(method==='vertexAttribDivisor')next.divisor=details.divisor;
      if(method==='enableVertexAttribArray'||method==='disableVertexAttribArray')next.enabled=details.enabled;
      attribState.set(index,next);
    }
    function guardedCapture(kind,method,args){
      if(terminal)return;
      try{
        if(kind==='DRAW')recordDraw(method,args);
        else if(kind==='BUFFER')recordBufferEvent(method,args);
        else if(kind==='ATTRIB')recordAttribEvent(method,args);
      }catch(_){reject('PROBE_CAPTURE_ERROR');}
    }
    function installMethod(method,kind){
      if(typeof gl[method]!=='function'||originals.has(method))return;
      const original=gl[method];
      function p46WrappedWebGLBoundary(...args){
        const result=Reflect.apply(original,this,args);
        guardedCapture(kind,method,args);
        return result;
      }
      originals.set(method,original);wrappers.set(method,p46WrappedWebGLBoundary);gl[method]=p46WrappedWebGLBoundary;
    }
    function install(){
      if(installed)return;
      for(const method of ['drawArrays','drawElements'])installMethod(method,'DRAW');
      for(const method of ['bufferData','bufferSubData','bindBuffer','bindBufferBase','bindBufferRange'])installMethod(method,'BUFFER');
      for(const method of ['vertexAttribPointer','vertexAttribIPointer','enableVertexAttribArray','disableVertexAttribArray','vertexAttribDivisor'])installMethod(method,'ATTRIB');
      installed=true;
    }
    function teardown(){
      if(timer!=null){safe(()=>clearTimeout(timer));timer=null;}
      for(const [method,original] of originals.entries()){
        const wrapper=wrappers.get(method);
        if(gl[method]===wrapper)gl[method]=original;
        else if(gl[method]!==original)teardownConflicts.push({method,reason:'WRAPPER_REPLACED_EXTERNALLY'});
      }
      installed=false;
    }
    function reject(code){
      if(terminal)return;
      state='REJECTED';reason=code;terminal=true;endedAt=now();teardown();
    }
    function seal(code='BOUNDED_CAPTURE_COMPLETE'){
      if(terminal)return;
      state=events.some(event=>event.kind==='DRAW')?'CAPTURE_READY':(events.length?'CAPTURE_NO_DRAWS':'CAPTURE_EMPTY');reason=code;terminal=true;endedAt=now();teardown();
    }
    function summarizeFingerprints(){
      const groups=new Map();
      for(const event of events){
        const fp=event.callsite?.normalizedCallsiteFingerprint;
        const key=fp?.status==='AVAILABLE'?fp.value:'NOT_AVAILABLE';
        const existing=groups.get(key)||{fingerprintStatus:fp?.status||'NOT_AVAILABLE',fingerprint:key==='NOT_AVAILABLE'?null:key,count:0,boundaries:[],wasmFunctionIndices:[],wasmOffsets:[],jsFunctionNames:[]};
        existing.count++;
        existing.boundaries.push(`${event.kind}:${event.method}`);
        const wasm=event.callsite?.wasm;
        if(wasm?.functionIndexStatus==='AVAILABLE')existing.wasmFunctionIndices.push(...wasm.functionIndices);
        if(wasm?.offsetStatus==='AVAILABLE')existing.wasmOffsets.push(...wasm.offsets);
        const js=event.callsite?.jsWrapperOrImport;
        if(js?.status==='AVAILABLE')existing.jsFunctionNames.push(...js.observedFunctionNames.filter(v=>v!=='UNRESOLVED'));
        groups.set(key,existing);
      }
      return [...groups.values()].map(group=>({...group,boundaries:unique(group.boundaries),wasmFunctionIndices:unique(group.wasmFunctionIndices),wasmOffsets:unique(group.wasmOffsets),jsFunctionNames:unique(group.jsFunctionNames)}));
    }
    function start(startBinding){
      if(state!=='IDLE')return result();
      if(!bindingValid(startBinding)){state='REJECTED';reason='INVALID_START_BINDING';terminal=true;startedAt=endedAt=now();return result();}
      binding={runtimeEpoch:startBinding.runtimeEpoch,rendererEpoch:startBinding.rendererEpoch,authorityKey:startBinding.authorityKey};
      moduleRef=root.Module??null;
      asmRef=(moduleRef&&(typeof moduleRef==='object'||typeof moduleRef==='function'))?(moduleRef.asm??null):null;
      moduleSurfaceStartSnapshot=moduleSurfaceSnapshot();
      startedAt=now();state='OBSERVING';reason='OBSERVING';install();
      timer=setTimeout(()=>seal('BOUNDED_WALL_TIME_REACHED'),limits.maxWallMs);
      return result();
    }
    function stop(code='EXPLICIT_STOP'){seal(code);return result();}
    function result(){
      return{
        schema:SCHEMA,
        state,reason,terminal,
        binding:binding?{...binding}:null,
        startedAt,endedAt,
        limits:{...limits},
        moduleSurfaceAtStart:moduleSurfaceStartSnapshot?clone(moduleSurfaceStartSnapshot):null,
        installedMethods:[...originals.keys()],
        eventCount:events.length,
        drawCount:draws.length,
        events:events.map(clone),
        draws:draws.map(clone),
        bufferEvents:bufferEvents.map(clone),
        vertexAttribEvents:attribEvents.map(clone),
        callsiteFingerprintGroups:summarizeFingerprints(),
        mappingAssessment:{status:'CALLSITE_CORRELATION_EVIDENCE_ONLY',selectionMade:false,semanticRendererMapping:'UNRESOLVED',authorityEligible:false,orderOnlySelection:false,timingOnlySelection:false,nearestSelection:false,guessedWasmSymbol:false,guessedWasmOffset:false},
        teardown:{complete:!installed,conflicts:teardownConflicts.map(clone)},
        authorityEligible:false,
        mappingOnly:true,
        proofBoundary:{nativeMarkerRendererSource:false,rendererAuthorityProof:false,p29Pass:false,p32Qualification:false},
        safety:{...SAFETY}
      };
    }
    return{start,stop,result,seal,reject};
  }
  return{SCHEMA,DEFAULT_LIMITS,SAFETY,createProbe,parseFrame,summarizeWasm};
});
