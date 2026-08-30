(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_rom_focus_inspect.js');
for(let i=0;i<300&&!self.__WOF_ROM_LOC_CACHE;i++)await new Promise(r=>setTimeout(r,50));
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache unavailable');
const C=self.__WOF_ROM_LOC_CACHE,MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v;
const s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function eaExtWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
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
function feature(p){
 const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;
 if(w===0x4EB9)return{at:h(p),word:hw(w),kind:'JSR',text:'JSR '+h(r32(p+2)),target:h(r32(p+2)),len:6};
 if((w&0xF100)===0x7000){const d=(w>>9)&7,v=s8(w&255);return{at:h(p),word:hw(w),kind:'MOVEQ',text:'MOVEQ #'+v+',D'+d,len:2,writesD0:d===0};}
 if(g===6){const cc=(w>>8)&15,d=w&255,len=d===0?4:2,disp=d===0?s16(r16(p+2)):s8(d),t=(p+2+disp)>>>0;return{at:h(p),word:hw(w),kind:cc===0?'BRA':cc===1?'BSR':'BCC'+cc,text:(cc===0?'BRA':cc===1?'BSR':'BCC'+cc)+' '+h(t),target:h(t),len};}
 if(g===11){const opmode=(w>>6)&7,dn=(w>>9)&7;if(opmode<=2){const size=['B','W','L'][opmode],src=eaText(p,m,r,size),len=2+2*eaExtWords(m,r,size);return{at:h(p),word:hw(w),kind:'CMP',text:'CMP.'+size+' '+src+',D'+dn,len};}}
 if(g===0&&((w>>8)&15)===12){const sz=(w>>6)&3;if(sz!==3){const size=sz===0?'B':sz===1?'W':'L',immBytes=size==='L'?4:2,src=eaText(p+immBytes,m,r,size),len=2+immBytes+2*eaExtWords(m,r,size);return{at:h(p),word:hw(w),kind:'CMPI',text:'CMPI.'+size+' #IMM,'+src,len};}}
 return null;
}
const eb={};
eb.edgeAt='0x00EB70';eb.fieldLoad={at:'0x00EB62',word:hw(r16(0xEB62)),text:'MOVE.W '+s16(r16(0xEB64))+'(A0),D1',fieldDisp:s16(r16(0xEB64))};
eb.scale={at:'0x00EB66',word:hw(r16(0xEB66)),text:'ADD.W D1,D1'};
const leaDisp=s16(r16(0xEB6A)),tableBase=(0xEB68+2+leaDisp)>>>0;
eb.tableBase={at:'0x00EB68',word:hw(r16(0xEB68)),disp:leaDisp,address:h(tableBase),text:'LEA '+leaDisp+'(PC),A1 -> '+h(tableBase)};
eb.d0Load={at:'0x00EB6C',word:hw(r16(0xEB6C)),ext:hw(r16(0xEB6E)),text:'MOVE.W 0(A1,D1.W),D0'};
eb.call={at:'0x00EB70',word:hw(r16(0xEB70)),target:h(r32(0xEB72)),text:'JSR '+h(r32(0xEB72))};
const table=[];for(let i=0;i<32;i++){const u=r16(tableBase+i*2),v=s16(u);table.push({index:i,at:h(tableBase+i*2),word:hw(u),signed:v,stateLike:v>=0&&v<=0x100&&(v%4===0)});}eb.table=table;
eb.tableSummary={entries:table.length,stateLike:table.filter(x=>x.stateLike).length,unique:[...new Set(table.map(x=>x.signed))].join(' ')};
const acde={edgeAt:'0x01ACDE',callTarget:h(r32(0x1ACE0)),features:[],raw:[]};
for(let p=0x1AC80;p<=0x1ACE8;p+=2){const f=feature(p);if(f)acde.features.push(f);acde.raw.push({at:h(p),word:hw(r16(p)),tag:f?f.text:''});}
acde.summary={cmp:acde.features.filter(x=>x.kind==='CMP'||x.kind==='CMPI').length,bcc:acde.features.filter(x=>String(x.kind).startsWith('BCC')).length,moveqD0:acde.features.filter(x=>x.kind==='MOVEQ'&&x.writesD0).map(x=>x.text+'@'+x.at).join(' '),jsr:acde.features.filter(x=>x.kind==='JSR').map(x=>x.text+'@'+x.at).join(' ')};
const out={version:'wof-dispatch-two-edge-strict-decode-v1',eb70:eb,acde};self.__WOF_TWO_EDGE_STRICT=out;
console.log('=== EB70 STRICT CHAIN ===');console.table([eb.fieldLoad,eb.scale,eb.tableBase,eb.d0Load,eb.call]);
console.log('=== EA5E TABLE (32 WORDS) ===');console.table(table);
console.log('=== 1ACDE FEATURES ===');console.table(acde.features);
console.log('=== TWO EDGE STRICT JSON ===');
console.log(JSON.stringify({eb70:{edgeAt:eb.edgeAt,fieldLoad:eb.fieldLoad,tableBase:eb.tableBase,d0Load:eb.d0Load,call:eb.call,tableSummary:eb.tableSummary,table},acde:{edgeAt:acde.edgeAt,callTarget:acde.callTarget,summary:acde.summary,features:acde.features,raw:acde.raw}},null,2));
return out;
})().catch(e=>{console.error('WOF_TWO_EDGE_STRICT_ERROR',e);throw e;});
