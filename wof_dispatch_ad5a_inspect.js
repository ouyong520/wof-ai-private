(()=>{
'use strict';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};

async function ensure(){
  if(!self.__WOF_ROM_LOC_CACHE) await load('wof_rom_focus_inspect.js');
  for(let i=0;i<300&&!self.__WOF_ROM_LOC_CACHE;i++) await sleep(50);
  if(!self.__WOF_ROM_LOC_CACHE) throw new Error('ROM cache unavailable');
}

function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8;
  const base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
  const r8=o=>M[base+(SW?(o^1):o)]>>>0;
  const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
  const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v;
  const s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
  const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
  return{MAX,r8,r16,r32,s8,s16,h,hw};
}

function eaWords(m,r,size){
  if(m<=4)return 0;
  if(m===5||m===6)return 1;
  if(m===7){
    if(r===0||r===2||r===3)return 1;
    if(r===1)return 2;
    if(r===4)return size==='L'?2:1;
  }
  return 0;
}

function eaText(E,p,m,r,size,extOff=2){
  if(m===0)return 'D'+r;
  if(m===1)return 'A'+r;
  if(m===2)return '(A'+r+')';
  if(m===3)return '(A'+r+')+';
  if(m===4)return '-(A'+r+')';
  if(m===5){const d=E.s16(E.r16(p+extOff));return d+'(A'+r+')';}
  if(m===6){const x=E.r16(p+extOff),d=E.s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(A'+r+','+ir+')';}
  if(m===7&&r===0)return E.hw(E.r16(p+extOff))+'.W';
  if(m===7&&r===1)return E.h(E.r32(p+extOff))+'.L';
  if(m===7&&r===2){const d=E.s16(E.r16(p+extOff));return d+'(PC)->'+E.h((p+extOff+d)>>>0);}
  if(m===7&&r===3){const x=E.r16(p+extOff),d=E.s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(PC,'+ir+')->'+E.h((p+extOff+d)>>>0);}
  if(m===7&&r===4){const v=size==='L'?E.r32(p+extOff):E.r16(p+extOff);return '#'+(size==='L'?E.h(v):E.hw(v));}
  return 'EA('+m+','+r+')';
}

function decode(E,p){
  const w=E.r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;
  let len=2,kind='OP',text=E.hw(w),target=null,fall=true,cmp=false,call=false;

  if(w===0x4E75){kind='RTS';text='RTS';fall=false;}
  else if(w===0x4E73){kind='RTE';text='RTE';fall=false;}
  else if(w===0x4E77){kind='RTR';text='RTR';fall=false;}
  else if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){
    kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';call=kind==='JSR';
    len=2+eaWords(m,r,'L')*2;fall=kind==='JSR';
    const src=eaText(E,p,m,r,'L');text=kind+' '+src;
    if(m===7&&r===0)target=E.s16(E.r16(p+2))>>>0;
    else if(m===7&&r===1)target=E.r32(p+2);
    else if(m===7&&r===2)target=(p+2+E.s16(E.r16(p+2)))>>>0;
    if(target!=null)text=kind+' '+E.h(target);
  }
  else if(g===6){
    const cc=(w>>8)&15,d=w&255;len=d===0?4:2;
    const disp=d===0?E.s16(E.r16(p+2)):E.s8(d);target=(p+2+disp)>>>0;
    kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;call=kind==='BSR';fall=kind!=='BRA';text=kind+' '+E.h(target);
  }
  else if(g===1||g===2||g===3){
    const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
    const sw=eaWords(sm,sr,size),dw=eaWords(dm,dr,size);len=2+(sw+dw)*2;
    const src=eaText(E,p,sm,sr,size,2),dst=eaText(E,p,dm,dr,size,2+sw*2);
    kind='MOVE.'+size;text=kind+' '+src+','+dst;
  }
  else if((w&0xF100)===0x7000){kind='MOVEQ';text='MOVEQ #'+E.s8(w&255)+',D'+((w>>9)&7);}
  else if((w&0xF1C0)===0x41C0){
    len=2+eaWords(m,r,'L')*2;kind='LEA';text='LEA '+eaText(E,p,m,r,'L')+',A'+((w>>9)&7);
  }
  else if(g===11){
    const opm=(w>>6)&7,size=opm===0?'B':opm===1?'W':opm===2?'L':'?';
    len=2+eaWords(m,r,size==='?'?'W':size)*2;kind='CMP-family';cmp=true;text='CMP-family '+eaText(E,p,m,r,size==='?'?'W':size)+',D'+((w>>9)&7);
  }
  else if(g===0&&((w>>8)&15)===12&&((w>>6)&3)!==3){
    const sz=(w>>6)&3,size=sz===0?'B':sz===1?'W':'L',immWords=size==='L'?2:1;
    len=2+immWords*2+eaWords(m,r,size)*2;kind='CMPI.'+size;cmp=true;
    const imm=size==='L'?E.r32(p+2):E.r16(p+2);text=kind+' #'+(size==='L'?E.h(imm):E.hw(imm))+','+eaText(E,p,m,r,size,2+immWords*2);
  }
  else if((w&0xFF00)===0x4A00){
    const sz=(w>>6)&3,size=sz===0?'B':sz===1?'W':sz===2?'L':'?';len=2+eaWords(m,r,size==='?'?'W':size)*2;kind='TST.'+size;text=kind+' '+eaText(E,p,m,r,size==='?'?'W':size);
  }
  else if(g===5){
    const sz=(w>>6)&3;
    if(sz===3&&m===1){len=4;kind='DBcc';target=(p+2+E.s16(E.r16(p+2)))>>>0;text='DBcc D'+r+','+E.h(target);}
    else{const size=sz===0?'B':sz===1?'W':'L';len=2+eaWords(m,r,size)*2;kind=(w&0x0100)?'SUBQ.'+size:'ADDQ.'+size;text=kind+' #'+((((w>>9)&7)||8))+','+eaText(E,p,m,r,size);}
  }
  else if(g===13||g===9||g===8||g===12){
    const sz=(w>>6)&3,size=sz===0?'B':sz===1?'W':sz===2?'L':'?';len=2+eaWords(m,r,size==='?'?'W':size)*2;
    kind=(g===13?'ADD':g===9?'SUB':g===8?'OR':'AND')+'-family';text=kind+' '+eaText(E,p,m,r,size==='?'?'W':size)+',D'+((w>>9)&7);
  }
  else if(g===4){
    if((w&0xFFF8)===0x4E50){len=4;kind='LINK';text='LINK A'+r+',#'+E.s16(E.r16(p+2));}
    else if((w&0xFFF8)===0x4E58){kind='UNLK';text='UNLK A'+r;}
    else{len=2+eaWords(m,r,'W')*2;kind='G4';text='G4 '+E.hw(w);}
  }

  len=Math.max(2,len);
  return{at:p,w,len,next:p+len,kind,text,target,fall,cmp,call};
}

const PLAY=[{id:'P1',w:0xBE1C,l:0xFFBE1C},{id:'P2',w:0xBEFC,l:0xFFBEFC},{id:'P3',w:0xBFDC,l:0xFFBFDC}];
function ev(E,d){
  const players=new Set(),fields=new Set(),stride=false,ramHi=false;
  for(let q=d.at;q<Math.min(d.next,E.MAX-3);q+=2){
    const w=E.r16(q),l=E.r32(q);
    for(const p of PLAY)if(w===p.w||l===p.l)players.add(p.id);
    if(w===0x00E0)stride=true;
    if(w===0xFFBE||w===0xFFBF)ramHi=true;
  }
  const s=d.text;
  for(const m of s.matchAll(/(-?\d+)\(A0(?:,|\))/g))fields.add(parseInt(m[1],10));
  return{players:[...players],fields:[...fields],stride,ramHi};
}

function inspect(E,entry,maxSpan=0x240){
  const lo=entry,hi=Math.min(E.MAX,entry+maxSpan),q=[entry],seen=new Set(),rows=[],calls=[];
  while(q.length&&seen.size<240){
    const p=q.shift();if(p<lo||p>=hi||seen.has(p))continue;seen.add(p);
    const d=decode(E,p),x=ev(E,d);
    rows.push({at:E.h(d.at),word:E.hw(d.w),len:d.len,kind:d.kind,text:d.text,players:x.players.join(','),A0fields:x.fields.join(','),stride:x.stride?'E0':'',ramHi:x.ramHi?'FFBE/FFBF':''});
    if(d.call&&d.target!=null)calls.push({at:E.h(d.at),kind:d.kind,target:E.h(d.target)});
    if(d.kind==='BRA'){if(d.target!=null&&d.target>=lo&&d.target<hi)q.push(d.target);continue;}
    if(d.kind.startsWith('Bcc')){if(d.target!=null&&d.target>=lo&&d.target<hi)q.push(d.target);q.push(d.next);continue;}
    if(d.kind==='DBcc'){if(d.target!=null&&d.target>=lo&&d.target<hi)q.push(d.target);q.push(d.next);continue;}
    if(d.kind==='RTS'||d.kind==='RTE'||d.kind==='RTR'||d.kind==='JMP')continue;
    q.push(d.next);
  }
  rows.sort((a,b)=>parseInt(a.at,16)-parseInt(b.at,16));
  const players=[...new Set(rows.flatMap(r=>r.players?r.players.split(','):[]).filter(Boolean))];
  const fields=[...new Set(rows.flatMap(r=>r.A0fields?r.A0fields.split(',').map(Number):[]))].sort((a,b)=>a-b);
  return{entry:E.h(entry),rows,calls,summary:{ins:rows.length,players:players.join(','),A0fields:fields.join(','),strideHits:rows.filter(r=>r.stride).length,ramHiHits:rows.filter(r=>r.ramHi).length,cmpHits:rows.filter(r=>r.kind.includes('CMP')).length,calls:calls.map(c=>c.target).join(' ')}};
}

async function run(){
  await ensure();const E=env();
  const ad5a=inspect(E,0x01AD5A,0x260),ad0a=inspect(E,0x01AD0A,0x180);
  console.log('=== AD5A SUMMARY ===');console.table([ad5a.summary]);
  console.log('=== AD5A STRICT CFG ===');console.table(ad5a.rows);
  console.log('=== AD0A SUMMARY ===');console.table([ad0a.summary]);
  console.log('=== AD0A STRICT CFG ===');console.table(ad0a.rows);
  const compact={ad5a:{entry:ad5a.entry,summary:ad5a.summary,calls:ad5a.calls,interesting:ad5a.rows.filter(r=>r.players||r.stride||r.ramHi||r.A0fields||r.kind.includes('CMP')||r.kind.startsWith('Bcc')||r.kind==='JSR'||r.kind==='BSR')},ad0a:{entry:ad0a.entry,summary:ad0a.summary,calls:ad0a.calls,interesting:ad0a.rows.filter(r=>r.players||r.stride||r.ramHi||r.A0fields||r.kind.includes('CMP')||r.kind.startsWith('Bcc')||r.kind==='JSR'||r.kind==='BSR')}};
  self.__WOF_AD5A_INSPECT=compact;
  console.log('=== AD5A INSPECT JSON ===');console.log(JSON.stringify(compact,null,2));
  return compact;
}

self.WOFAD5A={run};
console.log('✅ WOF AD5A/AD0A strict inspector loaded');
console.log('执行 await WOFAD5A.run()');
})();