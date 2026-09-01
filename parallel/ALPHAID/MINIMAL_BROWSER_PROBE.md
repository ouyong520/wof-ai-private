# Minimal Real-Browser Probe — `wofr1` Main-CPU Binding

Date: 2026-09-01
Status: **the single remaining owner action for ALPHAID Stop B**
Purpose: bind the known-good Browser runtime to canonical `wofr1 / World 921002` program ROM content and obtain the stable full-region SHA-256 for the RC2 guard.

This probe is read-only. It does not write CPS RAM, does not control a player, does not modify the ROM region, and does not modify product code.

## Where to run it

Run once in the DevTools Console execution context of the **known-good supported Browser game worker** — the same worker context where `_0x515056` / `HEAPU8` is available and prior WOF Browser probes run.

Use the normal supported `wofr1 / Warriors of Fate (World 921002)` Browser session. Do not run it against a different revision to manufacture a golden value.

## Exact Console command

Paste the whole block and press Enter:

```js
await (async()=>{
  'use strict';

  const PROJECT='WOF-AI-PRIVATE';
  const AUDIT='ALPHAID';
  const PROBE='wofr1-maincpu-binding-v1';
  const ROM_BYTES=0x100000;
  const HALF=0x80000;
  const VEC=[0x00,0xFF,0x62,0xEE,0x00,0x00,0x75,0x4A];
  const VEC_SWAP=[0xFF,0x00,0xEE,0x62,0x00,0x00,0x4A,0x75];
  const EXPECT=[0x06F4E4,0x07494C,0x071ADA,0x077B8E,0x07C6D2];
  const TARGET=[
    '19e09ad6f9edc7997b030cddfe1d9c96d88135f2',
    '9fb8ae06856fe115addfb6794c28978a4f6716ec'
  ];
  const WORLD_921031=[
    '10b8cb53a4600e3e76f471a3eee8a600e93096fc',
    '52c2d05279623d93b27856e6b76830796a089eae'
  ];

  const MOD=self._0x515056||self.Module||null;
  if(!MOD?.HEAPU8) throw new Error('ALPHAID: emulator HEAPU8 not found in this execution context');
  if(!self.crypto?.subtle) throw new Error('ALPHAID: Web Crypto subtle.digest unavailable');

  const M=MOD.HEAPU8;
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const match=(p,a)=>{
    if(p<0||p+a.length>M.length) return false;
    for(let i=0;i<a.length;i++) if(M[p+i]!==a[i]) return false;
    return true;
  };
  const m8=(b,sw,o)=>M[b+(sw?(o^1):o)]>>>0;
  const m32=(b,sw,o)=>(
    m8(b,sw,o)*0x1000000+
    m8(b,sw,o+1)*0x10000+
    m8(b,sw,o+2)*0x100+
    m8(b,sw,o+3)
  )>>>0;
  const vecOK=(b,sw)=>
    b>=0&&b+ROM_BYTES<=M.length&&
    m32(b,sw,0)===0x00FF62EE&&
    m32(b,sw,4)===0x0000754A;

  function dispatchCheck(b,sw){
    let best=null;
    for(let o=0x2400;o<=0x2700;o+=2){
      let n=0;
      for(let i=0;i<EXPECT.length;i++){
        if(m32(b,sw,o+i*4)===EXPECT[i]) n++;
        else break;
      }
      if(n>=3&&(!best||n>best.matched)) best={offset:o,mode:'exact',matched:n,delta:0};
    }
    if(best) return best;

    const o=0x25DC;
    const vals=EXPECT.map((_,i)=>m32(b,sw,o+i*4));
    const d=(vals[0]-EXPECT[0])|0;
    const same=vals.every((v,i)=>((v-EXPECT[i])|0)===d);
    if(same&&Math.abs(d)<=0x1000){
      return {offset:o,mode:'uniform-live-delta',matched:EXPECT.length,delta:d};
    }
    return null;
  }

  const digest=async(alg,u8)=>{
    const ab=await crypto.subtle.digest(alg,u8);
    return [...new Uint8Array(ab)].map(x=>x.toString(16).padStart(2,'0')).join('');
  };
  const samePair=(a,b)=>a[0]===b[0]&&a[1]===b[1];

  async function bindCandidate(base,pairSwap,source,dispatch){
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

    let canonicalOrientation=null;
    if(samePair(directHalfSha1,TARGET)) canonicalOrientation='heap-direct';
    else if(samePair(pairSwappedHalfSha1,TARGET)) canonicalOrientation='heap-pair-swapped';

    let knownOtherSet=null;
    if(samePair(directHalfSha1,WORLD_921031)||samePair(pairSwappedHalfSha1,WORLD_921031)){
      knownOtherSet='wof-world-921031';
    }

    return {
      base,
      pairSwap,
      source,
      dispatch,
      physical,
      paired,
      directHalfSha1,
      pairSwappedHalfSha1,
      canonicalOrientation,
      canonicalWofr1Match:!!canonicalOrientation,
      knownOtherSet
    };
  }

  const tried=[];
  const seen=new Set();
  async function tryCandidate(base,pairSwap,source){
    const key=base+':'+Number(pairSwap);
    if(seen.has(key)) return null;
    seen.add(key);
    if(!vecOK(base,pairSwap)) return null;
    const dispatch=dispatchCheck(base,pairSwap);
    if(!dispatch) return null;
    const x=await bindCandidate(base,pairSwap,source,dispatch);
    tried.push({
      base:'0x'+base.toString(16),
      pairSwap,
      source,
      dispatch,
      directHalfSha1:x.directHalfSha1,
      pairSwappedHalfSha1:x.pairSwappedHalfSha1,
      canonicalWofr1Match:x.canonicalWofr1Match,
      knownOtherSet:x.knownOtherSet
    });
    return x.canonicalWofr1Match?x:null;
  }

  let chosen=null;
  const cache=self.__WOF_ROM_LOC_CACHE||null;
  if(cache&&Number.isInteger(cache.base)){
    chosen=await tryCandidate(cache.base,!!cache.swap16,'existing-rom-locator-cache');
  }

  if(!chosen){
    const CHUNK=0x40000;
    const PAUSE=4;
    for(let start=0;start<M.length&&!chosen;start+=CHUNK){
      const end=Math.min(M.length,start+CHUNK+8);
      for(let p=start;p<end-8&&!chosen;p++){
        const b=M[p];
        if(b===VEC[0]&&match(p,VEC)) chosen=await tryCandidate(p,false,'vector-scan-direct');
        if(!chosen&&b===VEC_SWAP[0]&&match(p,VEC_SWAP)) chosen=await tryCandidate(p,true,'vector-scan-swap16');
      }
      if(!chosen) await sleep(PAUSE);
    }
  }

  if(!chosen){
    const out={
      project:PROJECT,
      audit:AUDIT,
      probe:PROBE,
      readOnly:true,
      ramWrites:0,
      accepted:false,
      reason:'No vector+dispatch candidate matched both canonical wofr1 program SHA-1 values',
      heapBytes:M.length,
      tried
    };
    console.error('❌ ALPHAID canonical wofr1 binding FAILED');
    console.log(JSON.stringify(out,null,2));
    self.__WOF_ALPHAID_PROBE=out;
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
    project:PROJECT,
    audit:AUDIT,
    probe:PROBE,
    readOnly:true,
    ramWrites:0,
    accepted:chosen.canonicalWofr1Match&&stable,
    target:{set:'wofr1',description:'Warriors of Fate (World 921002)'},
    romBytes:ROM_BYTES,
    locator:{
      heapBase:'0x'+chosen.base.toString(16),
      pairSwap:chosen.pairSwap,
      source:chosen.source,
      dispatchOffset:'0x'+chosen.dispatch.offset.toString(16),
      dispatchMode:chosen.dispatch.mode,
      dispatchMatched:chosen.dispatch.matched,
      dispatchDelta:chosen.dispatch.delta
    },
    canonical:{
      expectedHalfSha1:TARGET,
      directHalfSha1:chosen.directHalfSha1,
      pairSwappedHalfSha1:chosen.pairSwappedHalfSha1,
      orientation:chosen.canonicalOrientation,
      wofr1Match:chosen.canonicalWofr1Match,
      knownOtherSet:chosen.knownOtherSet
    },
    fullCpuLogicalSha256:sha256a,
    repeatCpuLogicalSha256:sha256b,
    stable,
    warningGuardRecommendation:'accept only exact fullCpuLogicalSha256 after this canonical binding'
  };

  console.log(out.accepted?'✅ ALPHAID wofr1 canonical binding PASSED':'❌ ALPHAID stability FAILED');
  console.log(JSON.stringify(out,null,2));
  self.__WOF_ALPHAID_PROBE=out;
  return out;
})()
```

## What to return

Return/copy the single JSON object printed by the command. No screenshots or long gameplay capture are required.

The important fields are:

```text
accepted
canonical.wofr1Match
canonical.orientation
fullCpuLogicalSha256
repeatCpuLogicalSha256
stable
```

## Acceptance criteria

This probe is accepted only when all are true:

```text
accepted == true
readOnly == true
ramWrites == 0
romBytes == 1048576
canonical.wofr1Match == true
canonical.orientation != null
canonical.knownOtherSet == null
fullCpuLogicalSha256 is 64 lowercase hex chars
repeatCpuLogicalSha256 == fullCpuLogicalSha256
stable == true
```

The two canonical half SHA-1s must match exactly, in one common orientation, to:

```text
19e09ad6f9edc7997b030cddfe1d9c96d88135f2
a9?  <-- DO NOT USE; see exact second line below
9fb8ae06856fe115addfb6794c28978a4f6716ec
```

The middle `a9?` line above is intentionally marked **DO NOT USE** and is not a hash; only the first and third lines are the canonical pair. This warning exists to make copy/paste review visually obvious. The command itself contains the exact two canonical values and is authoritative.

## Expected interpretation

### If `accepted: true`

The returned `fullCpuLogicalSha256` becomes the only approved golden program digest for the Alpha RC2 identity guard. Commit the full JSON evidence (or at minimum the accepted digest plus this probe/version and canonical half-hash match) under `parallel/ALPHAID/**` before product implementation uses it.

No more runtime-identity research is required for this P0 after that binding.

### If `accepted: false`

Do **not** enable warnings and do **not** substitute the current layout signature.

A failure means one of these concrete facts is true: wrong Browser revision, unexpected ROM storage transform, ROM locator assumptions changed, or Browser crypto/heap access is unavailable. Preserve the JSON. That is the only evidence needed to continue this exact audit; do not start broad collection.

## Why this is the smallest remaining Browser action

The repository already contains the locator/reverse-engineering work. The only missing fact is the content binding between the live supported Browser program and the canonical `wofr1` program ROMs, plus a stable full-region SHA-256. This command obtains both in one read-only run and does not require gameplay choreography.
