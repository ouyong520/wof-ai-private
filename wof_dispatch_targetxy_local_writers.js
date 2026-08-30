(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE) await load('wof_resume_low4_chain.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache unavailable');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function eaText(p,m,r,size){
 if(m===0)return'D'+r;if(m===1)return'A'+r;if(m===2)return'(A'+r+')';if(m===3)return'(A'+r+')+';if(m===4)return'-(A'+r+')';
 if(m===5)return s16(r16(p+2))+'(A'+r+')';
 if(m===6){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(A'+r+','+ir+')';}
 if(m===7&&r===0)return hw(r16(p+2))+'.W';if(m===7&&r===1)return h(r32(p+2))+'.L';
 if(m===7&&r===2){const d=s16(r16(p+2));return d+'(PC)->'+h((p+2+d)>>>0);}
 if(m===7&&r===3){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(PC,'+ir+')->'+h((p+2+d)>>>0);}
 if(m===7&&r===4)return'#'+(size==='L'?h(r32(p+2)):hw(r16(p+2)));
 return'EA('+m+','+r+')';
}
function decodeMove(p){
 const w=r16(p),g=w>>>12;if(!(g===1||g===2||g===3))return null;
 const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
 const swd=eaWords(sm,sr,size),dpos=p+2+swd*2,dwd=eaWords(dm,dr,size),len=2+(swd+dwd)*2;
 const src=eaText(p,sm,sr,size),dst=dm===0?'D'+dr:dm===1?'A'+dr:eaText(dpos,dm,dr,size);
 let targetDisp=null;if(dm===5&&dr===0)targetDisp=s16(r16(dpos+2));
 return{at:h(p),word:hw(w),len,size,src,dst,targetDisp};
}
function classifySource(p,mv){
 const s=mv.src;let cls='other';
 if(/^\d+\(A\d\)/.test(s)||/^-\d+\(A\d\)/.test(s))cls='A-reg field';
 else if(/^\(A\d\)/.test(s)||/^\-\(A\d\)/.test(s))cls='A-reg memory';
 else if(/^D\d$/.test(s))cls='data-reg';
 else if(/^A\d$/.test(s))cls='addr-reg';
 else if(s.includes('PC'))cls='PC-relative';
 else if(s.startsWith('#'))cls='immediate';
 return cls;
}
const START=0x01A800,END=0x01AE00;
const rows=[];
for(let p=START;p<END-8;p+=2){
 const mv=decodeMove(p);if(!mv)continue;
 if(mv.targetDisp!==64&&mv.targetDisp!==68)continue;
 rows.push({...mv,field:mv.targetDisp===64?'+0x40':'+0x44',sourceClass:classifySource(p,mv)});
}
function rawAround(at){const p=parseInt(at,16),a=[];for(let q=Math.max(0,p-16)&~1;q<=Math.min(MAX-2,p+20);q+=2)a.push({at:h(q),word:hw(r16(q)),mark:q===p?'<<< WRITER':''});return a;}
const details=rows.map(r=>({writer:r,raw:rawAround(r.at)}));
console.log('=== LOCAL WRITERS OF A0+0x40 / A0+0x44 ===');console.table(rows);
for(const d of details){console.log('=== '+d.writer.field+' writer '+d.writer.at+' : '+d.writer.src+' -> '+d.writer.dst+' ===');console.table(d.raw);}
const sourceRegs=[...new Set(rows.flatMap(r=>[...r.src.matchAll(/A([0-7])/g)].map(m=>'A'+m[1])).filter(x=>x!=='A0'))];
const verdict={range:h(START)+'..'+h(END),writers:rows.length,write40:rows.filter(r=>r.targetDisp===64).length,write44:rows.filter(r=>r.targetDisp===68).length,sourceRegs:sourceRegs.join(' '),top40:rows.find(r=>r.targetDisp===64)?.at||'',top44:rows.find(r=>r.targetDisp===68)?.at||''};
console.log('=== TARGET XY LOCAL WRITER VERDICT ===');console.table([verdict]);
const out={version:'wof-dispatch-targetxy-local-writers-v1',verdict,rows,details};self.__WOF_TARGETXY_LOCAL_WRITERS=out;
console.log('=== TARGET XY LOCAL WRITER JSON ===');console.log(JSON.stringify({verdict,rows},null,2));
return out;
})().catch(e=>{console.error('WOF_TARGETXY_LOCAL_WRITER_ERROR',e);throw e;});
