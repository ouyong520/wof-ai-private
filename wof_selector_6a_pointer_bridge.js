(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const MOD=_0x515056,RM=MOD.HEAPU8,RBASE=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0,ROMBASE=C.base,SW=!!C.swap16;
if(!RM||!RBASE)throw new Error('CPS RAM base unavailable');
const MAX=Math.min(0x30000,RM.length-ROMBASE);
const rr8=o=>RM[ROMBASE+(SW?(o^1):o)]>>>0;
const rr16=o=>((rr8(o)<<8)|rr8(o+1))>>>0;
const s16=v=>v&0x8000?v-0x10000:v;
const h=(v,n=6)=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(n,'0');
const hw=v=>'0x'+(v&0xffff).toString(16).toUpperCase().padStart(4,'0');

// ---------- runtime correlation: enemy+0x6A vs enemy+0x7E ----------
const POOL=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const PLOW={0:0xBE1C,4:0xBEFC,8:0xBFDC};
const B=a=>RM[RBASE+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0;
const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
const st=Array.from({length:SLOTS},(_,slot)=>({slot,n:0,active:0,valid:0,match:0,nonzero:0,nonzeroMatch:0,byTarget:new Map(),ptrs:new Map()}));
function bump(m,k){m.set(k,(m.get(k)||0)+1);}
function top(m,n=6){return[...m.entries()].sort((a,b)=>b[1]-a[1]).slice(0,n).map(([v,c])=>({v:hw(v),c}));}
const t0=performance.now();
while(performance.now()-t0<1400){
  for(const s of st){
    const a=POOL+s.slot*STRIDE,type=U16(a+0x20),x=S32(a+4),y=S32(a+8),target=U16(a+0x7E),ptr=U16(a+0x6A),active=(type!==0||x!==0||y!==0);
    s.n++;if(active)s.active++;bump(s.ptrs,ptr);
    if(target===0||target===4||target===8){s.valid++;bump(s.byTarget,target);if(ptr===PLOW[target])s.match++;if(ptr!==0){s.nonzero++;if(ptr===PLOW[target])s.nonzeroMatch++;}}
  }
  await sleep(20);
}
const runtimeRows=st.map(s=>({slot:s.slot,activePct:+(s.active/s.n).toFixed(3),validPct:+(s.valid/s.n).toFixed(3),matchPct:s.valid?+(s.match/s.valid).toFixed(3):0,nonzeroMatchPct:s.nonzero?+(s.nonzeroMatch/s.nonzero).toFixed(3):0,ptrTop:top(s.ptrs,5)})).filter(x=>x.activePct>=.2).sort((a,b)=>b.matchPct-a.matchPct||b.activePct-a.activePct);
const liveValid=runtimeRows.filter(x=>x.validPct>=.5);

// ---------- compact raw static scan for +0x6A accesses ----------
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function eaInfo(m,r,size,ep){
  if(m===0)return{kind:'D',reg:'D'+r,text:'D'+r};
  if(m===1)return{kind:'A',reg:'A'+r,text:'A'+r};
  if(m===2)return{kind:'ind',reg:'A'+r,text:'(A'+r+')'};
  if(m===3)return{kind:'post',reg:'A'+r,text:'(A'+r+')+'};
  if(m===4)return{kind:'pre',reg:'A'+r,text:'-(A'+r+')'};
  if(m===5){const d=s16(rr16(ep));return{kind:'d16A',reg:'A'+r,disp:d,text:d+'(A'+r+')'};}
  if(m===6){const x=rr16(ep),d=(x&255)&0x80?(x&255)-0x100:(x&255);return{kind:'idxA',reg:'A'+r,disp:d,text:d+'(A'+r+',idx)'};}
  if(m===7&&r===0)return{kind:'absW',text:hw(rr16(ep))+'.W'};
  if(m===7&&r===1)return{kind:'absL',text:h((rr16(ep)<<16)|rr16(ep+2),8)+'.L'};
  if(m===7&&r===4)return{kind:'imm',text:'#'+(size==='L'?h((rr16(ep)<<16)|rr16(ep+2),8):hw(rr16(ep)))};
  return{kind:'other',text:'EA('+m+','+r+')'};
}
function moveAt(p){
  const w=rr16(p),g=w>>>12;if(g!==1&&g!==2&&g!==3)return null;
  const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
  const swd=eaWords(sm,sr,size),dwd=eaWords(dm,dr,size),sep=p+2,dep=p+2+swd*2;
  const src=eaInfo(sm,sr,size,sep),dst=eaInfo(dm,dr,size,dep);
  const isMoveA=(dm===1&&(size==='W'||size==='L'));
  return{at:p,word:w,size,src,dst,len:2+(swd+dwd)*2,mn:isMoveA?'MOVEA.'+size:'MOVE.'+size};
}
function fieldOf(e){return e&&e.kind==='d16A'?e.disp:null;}
function rawWindow(p,b=14,a=18){const z=[];for(let q=Math.max(0,p-b*2)&~1;q<=Math.min(MAX-2,p+a*2);q+=2)z.push({at:h(q),word:hw(rr16(q)),mark:q===p?'HERE':''});return z;}
const FIELDS=new Set([0x6A,0x7E,0x7C,0x2A,0x2B,0x72,0x99,0x04,0x08]);
const moves=[];
for(let p=0;p<MAX-8;p+=2){const m=moveAt(p);if(m)moves.push(m);}
const refs=moves.filter(m=>FIELDS.has(fieldOf(m.src))||FIELDS.has(fieldOf(m.dst)));
const sixA=refs.filter(m=>fieldOf(m.src)===0x6A||fieldOf(m.dst)===0x6A);
function nearbyRefs(p,rad=0x80){
  return refs.filter(m=>Math.abs(m.at-p)<=rad).map(m=>({at:h(m.at),mn:m.mn,src:m.src.text,dst:m.dst.text,srcField:fieldOf(m.src),dstField:fieldOf(m.dst)}));
}
const candidates=sixA.map(m=>{
  const near=nearbyRefs(m.at,0x80),fields=new Set();for(const x of near){if(x.srcField!=null)fields.add(x.srcField);if(x.dstField!=null)fields.add(x.dstField);}
  const read=fieldOf(m.src)===0x6A,write=fieldOf(m.dst)===0x6A,movea=read&&m.mn.startsWith('MOVEA.W');
  let score=0;if(movea)score+=20;if(read)score+=6;if(write)score+=5;if(fields.has(0x7E))score+=10;if(fields.has(0x2A)||fields.has(0x2B))score+=8;if(fields.has(0x72))score+=5;if(fields.has(0x99))score+=5;if(fields.has(0x04)||fields.has(0x08))score+=4;
  return{at:h(m.at),word:hw(m.word),mn:m.mn,src:m.src.text,dst:m.dst.text,read6A:read,write6A:write,moveaFrom6A:movea,score,nearFields:[...fields].sort((a,b)=>a-b).map(x=>'+0x'+x.toString(16).toUpperCase().padStart(2,'0')),nearRefs:near.slice(0,36),raw:rawWindow(m.at)};
}).sort((a,b)=>b.score-a.score||parseInt(a.at,16)-parseInt(b.at,16));

// Pair candidates where a +0x7E access sits near a +0x6A access.
const pairCandidates=[];
for(const c of candidates){
  const p=parseInt(c.at,16);const n=refs.filter(m=>Math.abs(m.at-p)<=0x60&&(fieldOf(m.src)===0x7E||fieldOf(m.dst)===0x7E));
  if(n.length)pairCandidates.push({sixAAt:c.at,sixAText:c.mn+' '+c.src+' -> '+c.dst,score:c.score,sevenE:n.slice(0,12).map(m=>({at:h(m.at),mn:m.mn,src:m.src.text,dst:m.dst.text,delta:m.at-p}))});
}

const verdict={
  version:'wof-selector-6a-pointer-bridge-v1',readOnly:true,ramWrites:0,
  runtimeLiveSlots:liveValid.length,
  runtimeMostlyExact:liveValid.length?liveValid.filter(x=>x.matchPct>=.8).length:0,
  runtimeAnyExact:liveValid.some(x=>x.matchPct>0),
  sixAAccessCandidates:candidates.length,
  moveaWordReaders:candidates.filter(x=>x.moveaFrom6A).length,
  sixASevenENearPairs:pairCandidates.length,
  topCandidate:candidates[0]?{at:candidates[0].at,mn:candidates[0].mn,src:candidates[0].src,dst:candidates[0].dst,score:candidates[0].score}:null
};
const out={version:'wof-selector-6a-pointer-bridge-v1',verdict,runtimeRows:runtimeRows.slice(0,20),pointerMap:{P1:'0xBE1C',P2:'0xBEFC',P3:'0xBFDC'},pairCandidates:pairCandidates.slice(0,20),topStaticCandidates:candidates.slice(0,24)};
self.__WOF_SELECTOR_6A_POINTER_BRIDGE=out;
console.log('=== SELECTOR 6A POINTER BRIDGE VERDICT ===');console.table([verdict]);
console.log('=== SELECTOR 6A POINTER RUNTIME ===');console.table(out.runtimeRows.map(x=>({slot:x.slot,activePct:x.activePct,validPct:x.validPct,matchPct:x.matchPct,nonzeroMatchPct:x.nonzeroMatchPct,ptrTop:x.ptrTop.map(y=>y.v+':'+y.c).join(' ')})));
console.log('=== SELECTOR 6A POINTER BRIDGE JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_6A_POINTER_BRIDGE_ERROR',e);throw e;});
