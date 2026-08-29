(()=>{
  const M=_0x515056.HEAPU8;
  const R=_0x515056.HEAPU32[0x2e39e4>>>2]>>>0;
  if(!R) throw new Error('CPS RAM pointer unavailable');
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
  const BASE={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC};
  const OBJ_LEN=0xE0,RAM_LEN=0x10000;
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const hx=(n,w=2)=>'0x'+Number(n).toString(16).toUpperCase().padStart(w,'0');
  const safe=(fn,d=null)=>{try{return fn();}catch(e){return d;}};
  const val=a=>a==null?null:(typeof a==='object'&&'length'in a?Array.from(a):a);

  function workerState(){
    return {
      localPlayer:safe(()=>_0x2f9e12),
      inputMasks:safe(()=>val(_0x510901)),
      inputHead:safe(()=>val(_0x56ebd7)),
      sharedInput:safe(()=>val(_0x806137)),
      sharedLink:safe(()=>val(_0x1b3181)),
      linkMode:safe(()=>_0x4a4e73),
      linkRunning:safe(()=>_0x4e7623),
      wsOpen:safe(()=>!!_0xe02728&&_0xe02728.readyState),
      P1_up:safe(()=>val(_0x383392)),P1_down:safe(()=>val(_0x2cfd38)),
      P1_left:safe(()=>val(_0x42c5ad)),P1_right:safe(()=>val(_0x332c33)),
      P1_b5:safe(()=>val(_0x4b36ba)),P1_b6:safe(()=>val(_0xedd11f)),
      P1_aux0:safe(()=>val(_0x2e3e11)),P1_aux1:safe(()=>val(_0x11ba21)),
      P2_up:safe(()=>val(_0x4c69e5)),P2_down:safe(()=>val(_0x214656)),
      P2_left:safe(()=>val(_0x329aee)),P2_right:safe(()=>val(_0x19bce3)),
      P2_b5:safe(()=>val(_0x21e0b1)),P2_b6:safe(()=>val(_0x189837)),
      P2_aux0:safe(()=>val(_0x90edf)),P2_aux1:safe(()=>val(_0x3a3c98))
    };
  }

  function flatten(x,p='',out={}){
    if(Array.isArray(x)){for(let i=0;i<x.length;i++)out[p+'['+i+']']=x[i];}
    else if(x&&typeof x==='object'){for(const k of Object.keys(x))flatten(x[k],p?p+'.'+k:k,out);}
    else out[p]=x;
    return out;
  }

  function modeStat(samples,keys){
    const out={};
    for(const k of keys){
      const cnt=new Map();
      for(const s of samples){const v=s[k];const id=typeof v+':'+String(v);cnt.set(id,{v,c:(cnt.get(id)?.c||0)+1});}
      let best={v:null,c:0};for(const q of cnt.values())if(q.c>best.c)best=q;
      out[k]={mode:best.v,stability:best.c/samples.length,unique:cnt.size};
    }
    return out;
  }

  async function snapWorker(label='snap',durationMs=1200,stepMs=40){
    const samples=[],n=Math.max(5,Math.round(durationMs/stepMs));
    for(let i=0;i<n;i++){samples.push(flatten(workerState()));await sleep(stepMs);}
    const keys=[...new Set(samples.flatMap(Object.keys))];
    const stat=modeStat(samples,keys);
    WOFPRESENCE.workerSnaps[label]={label,samples:n,stat};
    return {label,samples:n,stable:Object.values(stat).filter(x=>x.stability>=.95).length};
  }

  async function snapObject(player='P2',label='snap',durationMs=1200,stepMs=40){
    const base=BASE[player];if(base==null)throw new Error('player must be P1/P2/P3');
    const samples=[],n=Math.max(5,Math.round(durationMs/stepMs));
    for(let k=0;k<n;k++){const a=new Uint8Array(OBJ_LEN);for(let i=0;i<OBJ_LEN;i++)a[i]=B(base+i);samples.push(a);await sleep(stepMs);}
    const stat=byteStats(samples,OBJ_LEN);
    WOFPRESENCE.objectSnaps[player+':'+label]={player,label,samples:n,stat};
    return {player,label,samples:n,stable:stat.filter(x=>x.stability>=.95).length};
  }

  function byteStats(samples,len){
    const cand=new Uint8Array(len),vote=new Int16Array(len);
    for(const s of samples)for(let i=0;i<len;i++){
      const v=s[i];if(vote[i]===0){cand[i]=v;vote[i]=1;}else if(cand[i]===v)vote[i]++;else vote[i]--;
    }
    const count=new Uint16Array(len),uniq=new Uint8Array(len),first=new Uint8Array(len);first.set(samples[0]);
    for(const s of samples)for(let i=0;i<len;i++){if(s[i]===cand[i])count[i]++;if(s[i]!==first[i])uniq[i]=1;}
    return Array.from({length:len},(_,i)=>({mode:cand[i],stability:count[i]/samples.length,changed:!!uniq[i]}));
  }

  async function snapRam(label='snap',durationMs=960,stepMs=80){
    const samples=[],n=Math.max(6,Math.round(durationMs/stepMs));
    for(let k=0;k<n;k++){
      const a=new Uint8Array(RAM_LEN);for(let i=0;i<RAM_LEN;i++)a[i]=B(0xFF0000+i);samples.push(a);await sleep(stepMs);
    }
    const stat=byteStats(samples,RAM_LEN);
    WOFPRESENCE.ramSnaps[label]={label,samples:n,stat};
    return {label,samples:n,stable:stat.filter(x=>x.stability>=.95).length};
  }

  function diffWorker(a='left',b='joined',min=.9){
    const A=WOFPRESENCE.workerSnaps[a],C=WOFPRESENCE.workerSnaps[b];if(!A||!C)throw new Error('missing worker snapshots');
    const rows=[];for(const k of new Set([...Object.keys(A.stat),...Object.keys(C.stat)])){
      const x=A.stat[k],y=C.stat[k];if(x&&y&&x.stability>=min&&y.stability>=min&&String(x.mode)!==String(y.mode))rows.push({field:k,[a]:x.mode,[b]:y.mode,stableA:+x.stability.toFixed(2),stableB:+y.stability.toFixed(2)});
    }
    console.table(rows);return rows;
  }

  function diffObject(player='P2',a='left',b='joined',min=.95){
    const A=WOFPRESENCE.objectSnaps[player+':'+a],C=WOFPRESENCE.objectSnaps[player+':'+b];if(!A||!C)throw new Error('missing object snapshots');
    const rows=[];for(let i=0;i<OBJ_LEN;i++){const x=A.stat[i],y=C.stat[i];if(x.stability>=min&&y.stability>=min&&x.mode!==y.mode)rows.push({offset:hx(i),address:hx(BASE[player]+i,6),[a]:x.mode,[b]:y.mode,stableA:+x.stability.toFixed(2),stableB:+y.stability.toFixed(2)});}
    console.table(rows);return rows;
  }

  function diffRam(a='left',b='joined',min=.95,limit=250){
    const A=WOFPRESENCE.ramSnaps[a],C=WOFPRESENCE.ramSnaps[b];if(!A||!C)throw new Error('missing RAM snapshots');
    const rows=[];for(let i=0;i<RAM_LEN;i++){const x=A.stat[i],y=C.stat[i];if(x.stability>=min&&y.stability>=min&&x.mode!==y.mode)rows.push({address:hx(0xFF0000+i,6),[a]:x.mode,[b]:y.mode,stableA:+x.stability.toFixed(2),stableB:+y.stability.toFixed(2)});}
    const shown=rows.slice(0,limit);console.table(shown);if(rows.length>limit)console.log('... RAM candidates',rows.length,'showing',limit);return rows;
  }

  async function capture(label){
    console.log('📸 capture',label,'开始，请在约1.3秒内保持“加入/离开”状态不变');
    await Promise.all([snapWorker(label,1200,40),snapObject('P2',label,1200,40),snapRam(label,960,80)]);
    console.log('✅ capture',label,'完成');
    return {worker:WOFPRESENCE.workerSnaps[label],object:WOFPRESENCE.objectSnaps['P2:'+label],ram:WOFPRESENCE.ramSnaps[label]};
  }

  function compare(a='left',b='joined'){
    console.log('=== Worker稳定变化 ===');const w=diffWorker(a,b,.9);
    console.log('=== P2对象稳定变化 ===');const o=diffObject('P2',a,b,.95);
    console.log('=== 全64KB CPS RAM稳定变化 ===');const r=diffRam(a,b,.95,250);
    const result={worker:w,object:o,ram:r};WOFPRESENCE.lastCompare=result;return result;
  }

  function peek(player='P2'){
    const base=BASE[player];const known={flag:B(base),type:(B(base+0x20)<<8)|B(base+0x21),body:(B(base+0x6E)<<8)|B(base+0x6F),attack:(B(base+0x70)<<8)|B(base+0x71),status82:B(base+0x82),hp83:B(base+0x83),worker:workerState()};
    console.log('👤',player,known);return known;
  }

  self.WOFPRESENCE={version:'presence-probe-v2',workerSnaps:{},objectSnaps:{},ramSnaps:{},lastCompare:null,workerState,snapWorker,snapObject,snapRam,diffWorker,diffObject,diffRam,capture,compare,peek};
  console.log('✅ WOF 玩家加入/离开探针 v2 已加载（只读：Worker状态 + P2对象 + 全64KB CPS RAM）');
})();
