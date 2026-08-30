(()=>{
'use strict';
const C=self.__WOF_ROM_LOC_CACHE;
if(!C)throw new Error('ROM cache missing; run resume first');
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
 if(m===7&&r===4){return'#'+(size==='L'?h(r32(p+2)):hw(r16(p+2)));}
 return'EA('+m+','+r+')';
}
function dec(p){
 const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,text=hw(w),kind='OP',writesD0=false,readsD0=false;
 if(w===0x4E75)return{at:h(p),word:hw(w),len:2,kind:'RTS',text:'RTS',writesD0:false,readsD0:false};
 if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';len=2+eaWords(m,r,'L')*2;let t='';if(m===7&&r===0)t=h(s16(r16(p+2))>>>0);else if(m===7&&r===1)t=h(r32(p+2));else if(m===7&&r===2)t=h((p+2+s16(r16(p+2)))>>>0);text=kind+' '+(t||eaText(p,m,r,'L'));return{at:h(p),word:hw(w),len,kind,text,target:t,writesD0:false,readsD0:false};}
 if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d),t=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;text=kind+' '+h(t);return{at:h(p),word:hw(w),len,kind,text,target:h(t),writesD0:false,readsD0:false};}
 if((w&0xF100)===0x7000){const dr=(w>>9)&7,v=s8(w&255);kind='MOVEQ';text='MOVEQ #'+v+',D'+dr;writesD0=dr===0;return{at:h(p),word:hw(w),len:2,kind,text,writesD0,readsD0:false};}
 if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;len=2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;const src=eaText(p,sm,sr,size);let dp=p+2+eaWords(sm,sr,size)*2;const dst=dm===0?'D'+dr:dm===1?'A'+dr:eaText(dp,dm,dr,size);kind='MOVE.'+size;text=kind+' '+src+','+dst;writesD0=dm===0&&dr===0;readsD0=sm===0&&sr===0;return{at:h(p),word:hw(w),len,kind,text,writesD0,readsD0,src,dst};}
 if(g===0){
  const op=(w>>8)&15,sz=(w>>6)&3;
  if((w&0xF100)===0x0100){/* dynamic bit op */}
  if((w&0xFF00)===0x0800){const typ=['BTST','BCHG','BCLR','BSET'][(w>>6)&3],bit=r16(p+2),dest=eaText(p+2,m,r,'B');len=4+eaWords(m,r,'B')*2;kind=typ;text=typ+' #'+bit+','+dest;readsD0=m===0&&r===0;writesD0=readsD0&&typ!=='BTST';return{at:h(p),word:hw(w),len,kind,text,writesD0,readsD0};}
  if([0,2,4,6,10,12].includes(op)&&sz!==3){const size=sz===2?'L':sz===1?'W':'B',immBytes=size==='L'?4:2,imm=size==='L'?r32(p+2):r16(p+2);len=2+immBytes+eaWords(m,r,size)*2;const names={0:'ORI',2:'ANDI',4:'SUBI',6:'ADDI',10:'EORI',12:'CMPI'};kind=names[op]+'.'+size;text=kind+' #'+(size==='L'?h(imm):hw(imm))+','+eaText(p+immBytes,m,r,size);readsD0=m===0&&r===0;writesD0=readsD0&&op!==12;return{at:h(p),word:hw(w),len,kind,text,writesD0,readsD0};}
 }
 if(g===5){const sz=(w>>6)&3;if(sz!==3){const size=sz===2?'L':sz===1?'W':'B',v=((w>>9)&7)||8,sub=!!(w&0x0100),dst=eaText(p,m,r,size);len=2+eaWords(m,r,size)*2;kind=(sub?'SUBQ':'ADDQ')+'.'+size;text=kind+' #'+v+','+dst;readsD0=m===0&&r===0;writesD0=readsD0;return{at:h(p),word:hw(w),len,kind,text,writesD0,readsD0};}}
 if(g===11){const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B',dr=(w>>9)&7;len=2+eaWords(m,r,size)*2;kind='CMP.'+size;text=kind+' '+eaText(p,m,r,size)+',D'+dr;readsD0=dr===0||(m===0&&r===0);return{at:h(p),word:hw(w),len,kind,text,writesD0:false,readsD0};}
 if(g===4){if((w&0xFFC0)===0x4A00){const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B';len=2+eaWords(m,r,size)*2;kind='TST.'+size;text=kind+' '+eaText(p,m,r,size);readsD0=m===0&&r===0;return{at:h(p),word:hw(w),len,kind,text,writesD0:false,readsD0};}if((w&0xFFC0)===0x4600){const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B';len=2+eaWords(m,r,size)*2;kind='NOT.'+size;text=kind+' '+eaText(p,m,r,size);readsD0=m===0&&r===0;writesD0=readsD0;return{at:h(p),word:hw(w),len,kind,text,writesD0,readsD0};}}
 return{at:h(p),word:hw(w),len,kind,text,writesD0,readsD0};
}
function linear(start,end,max=128){const a=[];let p=start;for(let i=0;i<max&&p<end;){const d=dec(p);a.push(d);p+=Math.max(2,d.len);i++;if(d.kind==='RTS')break;}return a;}
const table=[];for(let i=0;i<16;i++)table.push({index:i,at:h(0x1AD64+i),value:r8(0x1AD64+i),hex:'0x'+r8(0x1AD64+i).toString(16).toUpperCase().padStart(2,'0')});
const ad0a=linear(0x1AD0A,0x1AD5A,80);
const caller=linear(0x1AC94,0x1ACEE,80);
const d0chain=caller.filter(x=>x.writesD0||x.readsD0||x.kind==='BSR'||x.kind==='JSR'||x.kind.startsWith('Bcc')||x.kind==='BRA');
const ad0aD0=ad0a.filter(x=>x.writesD0||x.readsD0||x.kind.startsWith('Bcc')||x.kind==='BRA');
console.log('=== AD5A 16-BYTE CLASS TABLE ===');console.table(table);
console.log('=== AD0A STRICT LINEAR ===');console.table(ad0a);
console.log('=== AD0A D0-RELEVANT ===');console.table(ad0aD0);
console.log('=== CALLER D0 LOW4 CHAIN ===');console.table(d0chain);
const out={version:'wof-dispatch-low4-chain-v1',table,ad0a,ad0aD0,caller,d0chain};self.__WOF_DISPATCH_LOW4_CHAIN=out;
console.log('=== LOW4 CHAIN JSON ===');
console.log(JSON.stringify({table:table.map(x=>x.value),ad0aD0,d0chain},null,2));
return out;
})();
