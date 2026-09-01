(()=>{
'use strict';
(async()=>{
  const PROJECT='WOF-AI-PRIVATE';
  const AUDIT='PM-RUNTIME-IDENTITY-CORRECTION';
  const PROBE='wof-world-921031-maincpu-binding-v1';
  const ROM_BYTES=0x100000, HALF=0x80000;
  const VEC=[0x00,0xFF,0x62,0xEE,0x00,0x00,0x75,0x4A];
  const VEC_SWAP=[0xFF,0x00,0xEE,0x62,0x00,0x00,0x4A,0x75];
  const EXPECT=[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2];
  const TARGET=[
    '10b8cb53a4600e3e76f471a3eee8a600e93096fc',
    '52c2d05279623d93b27856e6b76830796a089eae'
  ];
  const OLD_921002=[
    '19e09ad6f9edc7997b030cddfe1d9c96d88135f2',
    '9fb8ae06856fe115addfb6794c28978a4f6716ec'
  ];

  const MOD=self._0x515056||self.Module||null;
  if(!MOD?.HEAPU8) throw new Error('WOF ID 921031: emulator HEAPU8 not found in this Worker context');
  if(!self.crypto?.subtle) throw new Error('WOF ID 921031: Web Crypto subtle.digest unavailable');
  const M=MOD.HEAPU8;
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const hex=buf=>[...new Uint8Array(buf)].map(x=>x.toString(16).padStart(2,'0')).join('');
  const digest=async(alg,u8)=>hex(await crypto.subtle.digest(alg,u8));
  const samePair=(a,b)=>a[0]===b[0]&&a[1]===b[1];
  const match=(p,a)=>{if(p<0||p+a.length>M.length)return false;for(let i=0;i<a.length;i++)if(M[p+i]!==a[i])return false;return true;};
  const m8=(b,sw,o)=>M[b+(sw?(o^1):o)]>>>0;
  const m32=(b,sw,o)=>(m8(b,sw,o)*0x1000000+m8(b,sw,o+1)*0x10000+m8(b,sw,o+2)*0x100+m8(b,sw,o+3))>>>0;
  const vecOK=(b,sw)=>b>=0&&b+ROM_BYTES<=M.length&&m32(b,sw,0)===0x00FF62EE&&m32(b,sw,4)===0x0000754A;

  function dispatchCheck(b,sw){
    let best=null;
    for(let o=0x2400;o<=0x2700;o+=2){
      let n=0;
      for(let i=0;i<EXPECT.length;i++){
        if(m32(b,sw,o+i*4)===EXPECT[i]) n++; else break;
      }
      if(n>=3&&(!best||n>best.matched)) best={offset:o,mode:'exact',matched:n,delta:0};
    }
    if(best) return best;
    const o=0x25DC;
    const vals=EXPECT.map((_,i)=>m32(b,sw,o+i*4));
    const d=(vals[0]-EXPECT[0])|0;
    const same=vals.every((v,i)=>((v-EXPECT[i])|0)===d);
    if(same&&Math.abs(d)<=0x1000) return {offset:o,mode:'uniform-live-delta',matched:EXPECT.length,delta:d};
    return null;
  }

  async function inspect(base,pairSwap,source){
    if(!vecOK(base,pairSwap)) return null;
    const dispatch=dispatchCheck(base,pairSwap);
    if(!dispatch) return null;
    const physical=M.slice(base,base+ROM_BYTES);
    const paired=new Uint8Array(ROM_BYTES);
    for(let i=0;i<ROM_BYTES;i++) paired[i]=physical[i^1];
    const directHalfSha1=[
      await digest('SHA-1',physical.subarray(0,HALF)),
      await digest('SHA-1',physical.subarray(HALF,ROM_BYTES))
    ];
    const pairSwappedHalfSha1=[
      await digest('SHA-1',paired.subarray(0,HALF)),
      await digest('SHA-1',paired.subarray(HALF,ROM_BYTES))
    ];
    const orientation=samePair(directHalfSha1,TARGET)?'heap-direct':samePair(pairSwappedHalfSha1,TARGET)?'heap-pair-swapped':null;
    const old921002=samePair(directHalfSha1,OLD_921002)||samePair(pairSwappedHalfSha1,OLD_921002);
    return {base,pairSwap,source,dispatch,physical,paired,directHalfSha1,pairSwappedHalfSha1,orientation,canonical921031Match:!!orientation,old921002};
  }

  const seen=new Set(), tried=[];
  async function tryOne(base,pairSwap,source){
    const key=base+':'+Number(pairSwap);
    if(seen.has(key)) return null;
    seen.add(key);
    const x=await inspect(base,pairSwap,source);
    if(!x) return null;
    tried.push({
      base:'0x'+base.toString(16),pairSwap,source,dispatch:x.dispatch,
      directHalfSha1:x.directHalfSha1,pairSwappedHalfSha1:x.pairSwappedHalfSha1,
      canonical921031Match:x.canonical921031Match,old921002:x.old921002
    });
    return x.canonical921031Match?x:null;
  }

  let chosen=null;
  const cache=self.__WOF_ROM_LOC_CACHE||null;
  if(cache&&Number.isInteger(cache.base)) chosen=await tryOne(cache.base,!!cache.swap16,'existing-rom-locator-cache');

  if(!chosen){
    const CHUNK=0x40000, PAUSE=4;
    for(let start=0;start<M.length&&!chosen;start+=CHUNK){
      const end=Math.min(M.length,start+CHUNK+8);
      for(let p=start;p<end-8&&!chosen;p++){
        const b=M[p];
        if(b===VEC[0]&&match(p,VEC)) chosen=await tryOne(p,false,'vector-scan-direct');
        if(!chosen&&b===VEC_SWAP[0]&&match(p,VEC_SWAP)) chosen=await tryOne(p,true,'vector-scan-swap16');
      }
      if(!chosen) await sleep(PAUSE);
    }
  }

  if(!chosen){
    const out={project:PROJECT,audit:AUDIT,probe:PROBE,readOnly:true,ramWrites:0,accepted:false,reason:'No candidate matched canonical wof / World 921031 program SHA-1 pair',heapBytes:M.length,tried};
    self.__WOF_ALPHAID_921031=out;
    console.error('❌ WOF 921031 identity binding FAILED');
    console.log(JSON.stringify(out,null,2));
    return out;
  }

  const logical=chosen.pairSwap?chosen.paired:chosen.physical;
  const sha256a=await digest('SHA-256',logical);
  await sleep(1500);
  const logical2=new Uint8Array(ROM_BYTES);
  for(let i=0;i<ROM_BYTES;i++) logical2[i]=M[chosen.base+(chosen.pairSwap?(i^1):i)];
  const sha256b=await digest('SHA-256',logical2);
  const stable=sha256a===sha256b;

  const out={
    project:PROJECT,audit:AUDIT,probe:PROBE,readOnly:true,ramWrites:0,
    accepted:chosen.canonical921031Match&&stable,
    target:{set:'wof',description:'Warriors of Fate (World 921031)'},
    romBytes:ROM_BYTES,
    locator:{heapBase:'0x'+chosen.base.toString(16),pairSwap:chosen.pairSwap,source:chosen.source,dispatchOffset:'0x'+chosen.dispatch.offset.toString(16),dispatchMode:chosen.dispatch.mode,dispatchMatched:chosen.dispatch.matched,dispatchDelta:chosen.dispatch.delta},
    canonical:{expectedHalfSha1:TARGET,directHalfSha1:chosen.directHalfSha1,pairSwappedHalfSha1:chosen.pairSwappedHalfSha1,orientation:chosen.orientation,world921031Match:chosen.canonical921031Match,old921002Match:chosen.old921002},
    fullCpuLogicalSha256:sha256a,
    repeatCpuLogicalSha256:sha256b,
    stable
  };
  self.__WOF_ALPHAID_921031=out;
  console.log(out.accepted?'✅ WOF World 921031 identity binding PASSED':'❌ WOF World 921031 identity stability FAILED');
  console.log(JSON.stringify(out,null,2));
  return out;
})().catch(e=>{console.error('❌ WOF 921031 identity probe error',e);});
})();
