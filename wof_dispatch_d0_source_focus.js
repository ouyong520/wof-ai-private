(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
if(!self.__WOF_DISPATCH_REVERSE_SELECTOR){await load('wof_dispatch_reverse_cfg_selector.js');await WOFDISPREV.run();}
const R=self.__WOF_DISPATCH_REVERSE_SELECTOR;
if(!R)throw new Error('reverse selector result missing');
const C=self.__WOF_ROM_LOC_CACHE,MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v;
const s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
const all=(R.scans||[]).flatMap(x=>x.candidates||[]).sort((a,b)=>(b.score||0)-(a.score||0)||String(a.at).localeCompare(String(b.at)));
const V=R.verdict||{};
const top=all.find(x=>x.at===V.topAt&&x.edgeAt===V.topEdgeAt)||all[0];
if(!top)throw new Error('top reverse candidate missing');
function eaSrc(p,mode,reg,size){
  if(mode===0)return{text:'D'+reg,reg:'D'+reg};
  if(mode===1)return{text:'A'+reg,reg:'A'+reg};
  if(mode===2)return{text:'(A'+reg+')',baseReg:'A'+reg};
  if(mode===3)return{text:'(A'+reg+')+',baseReg:'A'+reg};
  if(mode===4)return{text:'-(A'+reg+')',baseReg:'A'+reg};
  if(mode===5){const d=s16(r16(p+2));return{text:d+'(A'+reg+')',baseReg:'A'+reg,disp:d};}
  if(mode===6){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7),isz=(x&0x0800)?'.L':'.W';return{text:d+'(A'+reg+','+ir+isz+')',baseReg:'A'+reg,indexReg:ir,indexSize:isz,disp:d,ext:hw(x)};}
  if(mode===7&&reg===0){const a=s16(r16(p+2));return{text:hw(a)+' .W',abs:a>>>0};}
  if(mode===7&&reg===1){const a=r32(p+2);return{text:h(a)+' .L',abs:a};}
  if(mode===7&&reg===2){const d=s16(r16(p+2)),a=(p+2+d)>>>0;return{text:d+'(PC) -> '+h(a),pcTarget:a};}
  if(mode===7&&reg===3){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7),isz=(x&0x0800)?'.L':'.W',a=(p+2+d)>>>0;return{text:d+'(PC,'+ir+isz+') base='+h(a),indexReg:ir,indexSize:isz,pcBase:a,ext:hw(x)};}
  if(mode===7&&reg===4){const imm=size==='L'?r32(p+2):r16(p+2);return{text:'#'+(size==='L'?h(imm):hw(imm)),imm};}
  return{text:'EA('+mode+','+reg+')'};
}
function moveToD0(p){
  const w=r16(p),g=w>>>12;if(!(g===1||g===2||g===3))return null;
  const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
  if(dm!==0||dr!==0)return null;
  const src=eaSrc(p,sm,sr,size);
  return{at:h(p),word:hw(w),size,source:src.text,baseReg:src.baseReg||'',indexReg:src.indexReg||'',indexSize:src.indexSize||'',disp:src.disp??'',ext:src.ext||''};
}
function ctlCmp(p){
  const w=r16(p),g=w>>>12;
  if(g===6){const cc=(w>>8)&15,d=w&255,len=d===0?4:2,disp=d===0?s16(r16(p+2)):s8(d),target=(p+2+disp)>>>0;return{at:h(p),word:hw(w),kind:cc===0?'BRA':cc===1?'BSR':'BCC'+cc,target:h(target)};}
  if(g===11)return{at:h(p),word:hw(w),kind:'CMP-family',target:''};
  if(g===0&&((w>>8)&15)===12)return{at:h(p),word:hw(w),kind:'CMPI-family',target:''};
  if(g===5&&((w>>6)&3)===3&&((w>>3)&7)===1)return{at:h(p),word:hw(w),kind:'DBcc',target:''};
  return null;
}
const rootAt=parseInt(top.d0RootAt,16);
const root=Number.isFinite(rootAt)?moveToD0(rootAt):null;
const pathAddrs=[...String(top.path||'').matchAll(/0x[0-9A-Fa-f]+/g)].map(m=>parseInt(m[0],16)).filter(x=>Number.isFinite(x));
const ctlRows=[];for(const p of pathAddrs){const z=ctlCmp(p);if(z)ctlRows.push(z);}
const raw=[];if(Number.isFinite(rootAt)){for(let p=Math.max(0,rootAt-0x18)&~1;p<=Math.min(MAX-2,rootAt+0x18);p+=2)raw.push({at:h(p),word:hw(r16(p)),mark:p===rootAt?'<<< D0 ROOT':''});}
console.log('=== D0 SOURCE FOCUS ===');
console.table([{edgeAt:top.edgeAt,topAt:top.at,steps:top.steps,anchors:top.anchors,cmp:top.cmp,bcc:top.bcc,d0Root:top.d0Root,d0RootAt:top.d0RootAt,score:top.score}]);
console.log('=== D0 ROOT DECODE ===');
console.table(root?[root]:[{at:top.d0RootAt,source:'decoder did not recognize MOVE -> D0'}]);
console.log('=== CMP / BRANCH ON STORED PATH ===');
console.table(ctlRows);
console.log('=== RAW WORDS AROUND D0 ROOT ===');
console.table(raw);
const out={version:'wof-dispatch-d0-source-focus-v1',top,root,ctlRows,raw};self.__WOF_DISPATCH_D0_FOCUS=out;
console.log('=== D0 SOURCE FOCUS JSON ===');
console.log(JSON.stringify({edgeAt:top.edgeAt,topAt:top.at,d0Root:top.d0Root,d0RootAt:top.d0RootAt,root,cmp:top.cmp,bcc:top.bcc,anchors:top.anchors,path:top.path},null,2));
return out;
})().catch(e=>{console.error('WOF_D0_FOCUS_ERROR',e);throw e;});
