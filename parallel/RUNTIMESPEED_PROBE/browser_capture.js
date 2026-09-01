(async()=>{
'use strict';
const VERSION='wof-runtime-speed-browser-capture-v1';
const SCHEMA='wof-runtime-speed-capture-v1';
const MAGIC='WOFSPC1\n';
const RAM_SIZE=0x10000;
const DEFAULT_SECONDS=15;
const DEFAULT_INTERVAL_MS=8;
const cfg=self.__WOF_SPEED_PROBE_CONFIG||{};
const seconds=Number(cfg.seconds||DEFAULT_SECONDS);
const intervalMs=Number(cfg.intervalMs||DEFAULT_INTERVAL_MS);
const uploadUrl=String(cfg.uploadUrl||'');
const token=String(cfg.token||'');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const isDedicatedWorker=typeof DedicatedWorkerGlobalScope!=='undefined'&&self instanceof DedicatedWorkerGlobalScope;
if(!isDedicatedWorker)throw new Error('Run this loader in the existing gstyphoon dedicated Worker console; it does not replace or wrap the game Worker.');
if(!uploadUrl)throw new Error('Missing local uploadUrl from run_probe.py');
if(!(seconds>0&&seconds<=30))throw new Error('seconds out of range');
if(!(intervalMs>=5&&intervalMs<=20))throw new Error('intervalMs out of range');

const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
async function moduleFind(){
  if(good(self._0x515056))return self._0x515056;
  const until=performance.now()+30000;
  while(performance.now()<until){
    for(const k of Object.getOwnPropertyNames(self)){
      let v;try{v=self[k];}catch(_){continue;}
      if(good(v)){self._0x515056=v;self.__WOF_SPEED_MODULE_GLOBAL_KEY=k;return v;}
    }
    await sleep(50);
  }
  return null;
}
const MOD=await moduleFind();
if(!MOD)throw new Error('WASM Module/HEAP views not found');
const M=MOD.HEAPU8;
const R=MOD.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!R||R+RAM_SIZE>M.length)throw new Error('CPS RAM base pointer invalid or outside HEAP');
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const activeStructure=()=>{
  const bases=[0xFFBE1C,0xFFBEFC,0xFFBFDC],ids=[0,4,8];
  try{
    for(let i=0;i<3;i++){
      const a=bases[i];
      if(B(a)!==1||B(a+1)!==0||B(a+2)!==0||B(a+3)!==0)return false;
      if(U16(a+0x7C)!==ids[i])return false;
    }
    return true;
  }catch(_){return false;}
};
const readyUntil=performance.now()+30000;
while(performance.now()<readyUntil&&!activeStructure())await sleep(50);
if(!activeStructure())throw new Error('Live WOF P1/P2/P3 CPS RAM structure was not observed');
console.log('WOF_SPEED_PROBE_READY','read-only; stop input; capture starts in 3 seconds');
await sleep(3000);
console.log('WOF_SPEED_PROBE_CAPTURING',seconds+' seconds');

const maxSamples=Math.ceil((seconds*1000)/intervalMs)+128;
const rawFrames=new Uint8Array(maxSamples*RAM_SIZE);
const times=new Float64Array(maxSamples);
let count=0;
const start=performance.now();
while(true){
  const now=performance.now();
  if(count>0&&now-start>=seconds*1000)break;
  if(count>=maxSamples)throw new Error('Capture sample buffer exhausted');
  rawFrames.set(M.subarray(R,R+RAM_SIZE),count*RAM_SIZE);
  times[count]=performance.now()-start;
  count++;
  const deadline=start+count*intervalMs;
  const delay=deadline-performance.now();
  if(delay>0)await sleep(delay);else await sleep(0);
}
console.log('WOF_SPEED_PROBE_FINALIZING','timed capture complete');
if(count<2)throw new Error('Too few Browser samples captured');

for(let n=0;n<count;n++){
  const base=n*RAM_SIZE,end=base+RAM_SIZE;
  for(let i=base;i<end;i+=2){const x=rawFrames[i];rawFrames[i]=rawFrames[i+1];rawFrames[i+1]=x;}
  if((n&63)===63)await sleep(0);
}
const spanMs=times[count-1]-times[0];
const achievedHz=(count-1)/(spanMs/1000);
const intervals=[];for(let i=1;i<count;i++)intervals.push(times[i]-times[i-1]);
intervals.sort((a,b)=>a-b);
const p95=intervals[Math.min(intervals.length-1,Math.floor(0.95*(intervals.length-1)))];
const header={
  schemaVersion:SCHEMA,captureToolVersion:VERSION,runtime:'browser',readOnly:true,writesGameMemory:false,inputInjection:false,
  timestampClock:'performance.now',timestampUnit:'milliseconds-from-capture-start',requestedSeconds:seconds,targetIntervalMs:intervalMs,
  sampleCount:count,measuredSpanMs:Number(spanMs.toFixed(6)),achievedHz:Number(achievedHz.toFixed(6)),
  ram:{logicalStart:'0xFF0000',bytesPerSample:RAM_SIZE,normalized:true,normalization:'browser wasm hostOffset=logicalOffset^1; normalized after timed capture',sourceRamBase:R},
  session:{probeTokenSuffix:token.slice(-8),moduleGlobalKey:self.__WOF_SPEED_MODULE_GLOBAL_KEY||null},
  captureQuality:{monotonicTimestamps:Array.from(times.subarray(1,count)).every((v,i)=>v>times[i]),intervalP95Ms:Number(p95.toFixed(6))}
};
const enc=new TextEncoder();
const headerBytes=enc.encode(JSON.stringify(header));
const prefix=new Uint8Array(MAGIC.length+4+headerBytes.length);
for(let i=0;i<MAGIC.length;i++)prefix[i]=MAGIC.charCodeAt(i);
new DataView(prefix.buffer).setUint32(MAGIC.length,headerBytes.length,true);
prefix.set(headerBytes,MAGIC.length+4);
const parts=[prefix];
for(let i=0;i<count;i++){
  const tbuf=new ArrayBuffer(8);new DataView(tbuf).setFloat64(0,times[i],true);parts.push(tbuf);
  parts.push(rawFrames.subarray(i*RAM_SIZE,(i+1)*RAM_SIZE));
}
const plain=new Blob(parts,{type:'application/octet-stream'});
let payload,format,mime;
if(typeof CompressionStream==='function'){
  payload=await new Response(plain.stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer();
  format='gzip';mime='application/gzip';
}else{
  payload=await plain.arrayBuffer();format='plain';mime='application/octet-stream';
}
const resp=await fetch(uploadUrl,{method:'POST',mode:'cors',cache:'no-store',headers:{'Content-Type':mime,'X-WOF-Speed-Token':token,'X-WOF-Speed-Format':format},body:payload});
if(!resp.ok)throw new Error('Local probe upload failed: HTTP '+resp.status+' '+await resp.text());
const uploaded=await resp.json();
const summary={ok:true,runtime:'browser',sampleCount:count,measuredSpanMs:Number(spanMs.toFixed(3)),achievedHz:Number(achievedHz.toFixed(3)),format,uploaded:!!uploaded.ok,readOnly:true,writesGameMemory:false,inputInjection:false};
console.log('WOF_SPEED_PROBE_BROWSER_DONE',JSON.stringify(summary));
return summary;
})().catch(e=>{console.error('WOF_RUNTIME_SPEED_PROBE_ERROR',e);throw e;});