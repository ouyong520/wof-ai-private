(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');

const wrapper=[
 {at:0x011190,text:'MOVE.B 43(A0),D0',word:r16(0x011190),ext:r16(0x011192)},
 {at:0x011194,text:'MOVE.W 14(PC,D0.W),D1',word:r16(0x011194),ext:r16(0x011196)},
 {at:0x011198,text:'JSR 10(PC,D1.W)',word:r16(0x011198),ext:r16(0x01119A)},
 {at:0x01119C,text:'JSR 0x2698.W',word:r16(0x01119C),ext:r16(0x01119E)},
 {at:0x0111A0,text:'BRA 0x011BD0',word:r16(0x0111A0),ext:r16(0x0111A2)}
].map(x=>({...x,at:h(x.at),word:hw(x.word),ext:hw(x.ext)}));

const TABLE=0x0111A4;
const table=[];
for(const d0 of [0,2,4]){const at=TABLE+d0,w=r16(at),off=s16(w),target=(TABLE+off)>>>0;table.push({d0,at:h(at),word:hw(w),signed:off,target:h(target)});}

const a5=[];
for(let p=0;p<MAX-6;p+=2){const w=r16(p);let kind='',value=null,len=0;
 if(w===0x4BF9){kind='LEA abs.L,A5';value=r32(p+2)>>>0;len=6;}
 else if(w===0x4BF8){kind='LEA abs.W,A5';value=s16(r16(p+2))>>>0;len=4;}
 else if(w===0x2A7C){kind='MOVEA.L #imm,A5';value=r32(p+2)>>>0;len=6;}
 else if(w===0x3A7C){kind='MOVEA.W #imm,A5';value=s16(r16(p+2))>>>0;len=4;}
 else if(w===0x2A79){kind='MOVEA.L abs.L,A5';value=r32(p+2)>>>0;len=6;}
 else if(w===0x2A78){kind='MOVEA.L abs.W,A5';value=s16(r16(p+2))>>>0;len=4;}
 if(kind)a5.push({at:h(p),word:hw(w),kind,value:h(value),ramLike:((value>>>16)&0xff)===0xff||((value>>>16)&0xffff)===0x00ff,len});
}

const players=[0x00FFBE1C,0x00FFBEFC,0x00FFBFDC];
const player32=[];
for(const v of players){const hits=[];for(let p=0;p<MAX-3;p++){if(r32(p)===v)hits.push(h(p));}player32.push({value:h(v),count:hits.length,hits:hits.slice(0,32)});}
const lows=[0xBE1C,0xBEFC,0xBFDC];
const player16=[];
for(const v of lows){const hits=[];for(let p=0;p<MAX-1;p+=2){if(r16(p)===v)hits.push(h(p));}player16.push({value:hw(v),count:hits.length,hits:hits.slice(0,32)});}

const verdict={
 wrapperEntry:'0x011190',
 stateField:'43(A0)',
 tableBase:'0x0111A4',
 tableEntries:table.length,
 state0Target:table[0].target,
 state2Target:table[1].target,
 state4Target:table[2].target,
 a5InitCandidates:a5.length,
 a5RamLikeCandidates:a5.filter(x=>x.ramLike).length,
 player32Total:player32.reduce((n,x)=>n+x.count,0),
 player16Total:player16.reduce((n,x)=>n+x.count,0)
};
const out={version:'wof-dispatch-111190-table-a5-role-v1',verdict,wrapper,table,a5InitCandidates:a5,player32,player16};
self.__WOF_111190_TABLE_A5_ROLE=out;
console.log('=== 111190 TABLE + A5 ROLE JSON ===');
console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_111190_TABLE_A5_ROLE_ERROR',e);throw e;});
