(()=>{
'use strict';
const C=self.__WOF_ROM_LOC_CACHE;
if(!C)throw new Error('ROM cache missing; run resume first');
const MOD=_0x515056,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v;
const s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');

function eaWords(m,r,size){
  if(m<=4)return 0;
  if(m===5||m===6)return 1;
  if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}
  return 0;
}
function eaText(p,m,r,size){
  if(m===0)return 'D'+r;
  if(m===1)return 'A'+r;
  if(m===2)return '(A'+r+')';
  if(m===3)return '(A'+r+')+';
  if(m===4)return '-(A'+r+')';
  if(m===5)return s16(r16(p+2))+'(A'+r+')';
  if(m===6){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(A'+r+','+ir+')';}
  if(m===7&&r===0)return hw(r16(p+2))+'.W';
  if(m===7&&r===1)return h(r32(p+2))+'.L';
  if(m===7&&r===2){const d=s16(r16(p+2));return d+'(PC)->'+h((p+2+d)>>>0);}
  if(m===7&&r===3){const x=r16(p+2),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(PC,'+ir+')';}
  if(m===7&&r===4)return '#'+(size==='L'?h(r32(p+2)):hw(r16(p+2)));
  return 'EA('+m+','+r+')';
}
function decode(p){
  const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;
  let len=2,kind='OP',text='OP '+hw(w),writesD0=false,d0Source='',terminal=false;
  if(w===0x4E75){kind='RTS';text='RTS';terminal=true;}
  else if((w&0xF100)===0x7000){const dr=(w>>9)&7,imm=s8(w&255);kind='MOVEQ';text='MOVEQ #'+imm+',D'+dr;if(dr===0){writesD0=true;d0Source='#'+imm;}}
  else if(g===1||g===2||g===3){
    const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
    const swd=eaWords(sm,sr,size),dwd=eaWords(dm,dr,size);
    len=2+(swd+dwd)*2;
    const src=eaText(p,sm,sr,size);
    const dp=p+2+swd*2;
    const dst=eaText(dp,dm,dr,size);
    kind='MOVE.'+size;text='MOVE.'+size+' '+src+','+dst;
    if(dm===0&&dr===0){writesD0=true;d0Source=src;}
  }
  else if((w&0xFFC0)===0x4200){
    const sz=(w>>6)&3,size=sz===0?'B':sz===1?'W':sz===2?'L':'?';len=2+eaWords(m,r,size)*2;const dst=eaText(p,m,r,size);kind='CLR.'+size;text='CLR.'+size+' '+dst;if(m===0&&r===0){writesD0=true;d0Source='#0';}
  }
  else if((w&0xFFC0)===0x4A00){const sz=(w>>6)&3,size=sz===0?'B':sz===1?'W':sz===2?'L':'?';len=2+eaWords(m,r,size)*2;kind='TST.'+size;text='TST.'+size+' '+eaText(p,m,r,size);}
  else if((w&0xFFF8)===0x4880){const dr=w&7;kind='EXT.W';text='EXT.W D'+dr;if(dr===0){writesD0=true;d0Source='D0';}}
  else if((w&0xFFF8)===0x48C0){const dr=w&7;kind='EXT.L';text='EXT.L D'+dr;if(dr===0){writesD0=true;d0Source='D0';}}
  else if(g===0){
    const op=(w>>8)&15,sz=(w>>6)&3;
    if([0,2,4,6,10,12].includes(op)&&sz!==3){const size=sz===0?'B':sz===1?'W':'L',immBytes=size==='L'?4:2;len=2+immBytes+eaWords(m,r,size)*2;const names={0:'ORI',2:'ANDI',4:'SUBI',6:'ADDI',10:'EORI',12:'CMPI'};const imm=size==='L'?r32(p+2):r16(p+2);const ep=p+2+immBytes;const dst=eaText(ep,m,r,size);kind=names[op]+'.'+size;text=names[op]+'.'+size+' #'+(size==='L'?h(imm):hw(imm))+','+dst;if(m===0&&r===0&&op!==12){writesD0=true;d0Source='D0';}}
  }
  else if(g===14&&((w>>6)&3)!==3){const dr=w&7,cnt=((w>>9)&7)||8,dir=(w&0x0100)?'L':'R',typ=['AS','LS','ROX','RO'][(w>>3)&3],size=['B','W','L'][(w>>6)&3]||'?';kind=typ+dir+'.'+size;text=kind+' #'+cnt+',D'+dr;if(dr===0){writesD0=true;d0Source='D0';}}
  else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d),t=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'BCC'+cc;text=kind+' '+h(t);if(kind==='BRA')terminal=true;}
  return{at:h(p),word:hw(w),len,kind,text,writesD0,d0Source,terminal};
}

const entry=0x01AD5A,ins=[];let p=entry;
for(let i=0;i<12&&p<MAX;i++){
  const d=decode(p);ins.push(d);p+=d.len;if(d.terminal)break;
}
const raw=[];for(let q=entry;q<Math.min(MAX,entry+0x20);q+=2)raw.push({at:h(q),word:hw(r16(q))});
const d0Writes=ins.filter(x=>x.writesD0);
const caller=[
  {at:'0x01ACD2',text:'BSR 0x01AD5A'},
  {at:'0x01ACD6',text:'CMPI.B #8,D0'},
  {at:'0x01ACDA',text:'BNE 0x01ACEE'},
  {at:'0x01ACDC',text:'MOVEQ #-16,D0'},
  {at:'0x01ACDE',text:'JSR 0x0025C8'}
];
console.log('=== AD5A STRICT LEAF ===');console.table(ins);
console.log('=== AD5A D0 WRITES ===');console.table(d0Writes);
console.log('=== AD5A RAW WORDS ===');console.table(raw);
const out={entry:h(entry),ins,d0Writes,caller,returnPc:h(p)};
self.__WOF_AD5A_LEAF=out;
console.log('=== AD5A LEAF JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})();
