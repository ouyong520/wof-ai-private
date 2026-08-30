(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
if(!self.__WOF_DISPATCH_REVERSE_SELECTOR){await load('wof_dispatch_reverse_cfg_selector.js');await WOFDISPREV.run();}
const R=self.__WOF_DISPATCH_REVERSE_SELECTOR,V=R.verdict||{};
const all=(R.scans||[]).flatMap(x=>x.candidates||[]).sort((a,b)=>(b.score||0)-(a.score||0));
const top=all.find(x=>x.at===V.topAt&&x.edgeAt===V.topEdgeAt)||all[0];
if(!top)throw new Error('top reverse candidate missing');
const C=self.__WOF_ROM_LOC_CACHE,MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v;
const s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function eaText(p,m,r,size){
  if(m===0)return'D'+r;if(m===1)return'A'+r;if(m===2)return'(A'+r+')';if(m===3)return'(A'+r+')+';if(m===4)return'-(A'+r+')';
  if(m===5)return s16(r16(p+2))+'(A'+r+')';
  if(m===6){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(A'+r+','+ir+')';}
  if(m===7&&r===0)return hw(r16(p+2))+'.W';
  if(m===7&&r===1)return h(r32(p+2))+'.L';
  if(m===7&&r===2){const a=(p+2+s16(r16(p+2)))>>>0;return s16(r16(p+2))+'(PC)->'+h(a);}
  if(m===7&&r===3){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W'),a=(p+2+d)>>>0;return d+'(PC,'+ir+')->'+h(a);}
  if(m===7&&r===4)return'#'+(size==='L'?h(r32(p+2)):hw(r16(p+2)));
  return'EA('+m+','+r+')';
}
function writerAt(p){
  if(p<0||p+1>=MAX)return null;
  const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;
  if(g===1||g===2||g===3){
    const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
    const src=eaText(p,sm,sr,size);
    if(dm===0&&dr===1)return{at:h(p),word:hw(w),reg:'D1',op:'MOVE.'+size,src};
    if(dm===1&&dr===1&&size!=='B')return{at:h(p),word:hw(w),reg:'A1',op:'MOVEA.'+size,src};
  }
  if((w&0xF1C0)===0x41C0&&((w>>9)&7)===1){const src=eaText(p,m,r,'L');return{at:h(p),word:hw(w),reg:'A1',op:'LEA',src};}
  if((w&0xF100)===0x7000&&((w>>9)&7)===1)return{at:h(p),word:hw(w),reg:'D1',op:'MOVEQ',src:'#'+s8(w&255)};
  if(g===5&&((w>>6)&3)!==3){const dr=r,dm=m;if((dm===0&&dr===1)||(dm===1&&dr===1)){const n=((w>>9)&7)||8;return{at:h(p),word:hw(w),reg:dm===0?'D1':'A1',op:(w&0x0100?'SUBQ':'ADDQ'),src:'#'+n};}}
  if(g===13||g===9){const op=g===13?'ADD':'SUB',opmode=(w>>6)&7,dn=(w>>9)&7;
    if(dn===1&&(opmode===0||opmode===1||opmode===2)){const size=opmode===0?'B':opmode===1?'W':'L';return{at:h(p),word:hw(w),reg:'D1',op:op+'.'+size,src:eaText(p,m,r,size)};}
    if(dn===1&&(opmode===3||opmode===7)){const size=opmode===3?'W':'L';return{at:h(p),word:hw(w),reg:'A1',op:op+'A.'+size,src:eaText(p,m,r,size)};}
    if(r===1&&m===0&&(opmode===4||opmode===5||opmode===6)){const size=opmode===4?'B':opmode===5?'W':'L';return{at:h(p),word:hw(w),reg:'D1',op:op+'.'+size+' Dn->EA',src:'D'+dn};}
  }
  if(g===14&&r===1&&((w>>6)&3)!==3){const cnt=((w>>9)&7)||8,dir=w&0x0100?'L':'R',typ=['AS','LS','ROX','RO'][(w>>3)&3];return{at:h(p),word:hw(w),reg:'D1',op:typ+dir,src:'#'+cnt};}
  return null;
}
function ctlAt(p){const w=r16(p),g=w>>>12;if(g===6){const cc=(w>>8)&15,d=w&255,disp=d===0?s16(r16(p+2)):s8(d),t=(p+2+disp)>>>0;return{at:h(p),word:hw(w),kind:cc===0?'BRA':cc===1?'BSR':'BCC'+cc,target:h(t)};}if(g===11)return{at:h(p),word:hw(w),kind:'CMP-family',target:''};if(g===0&&((w>>8)&15)===12)return{at:h(p),word:hw(w),kind:'CMPI-family',target:''};return null;}
const rootAt=parseInt(top.d0RootAt,16),topAt=parseInt(top.at,16);
const start=Math.max(0,Math.min(topAt,rootAt)-0x300),end=Math.min(MAX,rootAt+2);
const writers=[];for(let p=start&~1;p<end;p+=2){const z=writerAt(p);if(z){z.distance=rootAt-p;z.inFrontier=p>=topAt&&p<=rootAt;z.score=(z.inFrontier?1000:0)-Math.abs(rootAt-p);writers.push(z);}}
writers.sort((a,b)=>b.score-a.score||a.distance-b.distance);
const controls=[];for(let p=Math.max(start,topAt-0x80)&~1;p<=rootAt;p+=2){const z=ctlAt(p);if(z)controls.push(z);}
const compact={edgeAt:top.edgeAt,topAt:top.at,d0RootAt:top.d0RootAt,d0Load:'MOVE.W 0(A1,D1.W),D0',A1:writers.filter(x=>x.reg==='A1').slice(0,8),D1:writers.filter(x=>x.reg==='D1').slice(0,12),controls:controls.slice(-20)};
console.log('=== A1/D1 WRITER CANDIDATES ===');console.table(writers.slice(0,24));
console.log('=== LOCAL CMP / BRANCH ===');console.table(controls.slice(-24));
console.log('=== A1 D1 TRACE JSON ===');console.log(JSON.stringify(compact,null,2));
self.__WOF_DISPATCH_A1D1_TRACE={version:'wof-dispatch-a1-d1-trace-v1',top,writers,controls,compact};
return self.__WOF_DISPATCH_A1D1_TRACE;
})().catch(e=>{console.error('WOF_A1D1_TRACE_ERROR',e);throw e;});
