(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
if(!self.__WOF_ROM_LOC_CACHE)await load('wof_resume_dispatch_selector.js');
const C=self.__WOF_ROM_LOC_CACHE;if(!C)throw new Error('ROM cache missing');
const M=_0x515056.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base);
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function eaText(ep,m,r,size){
 if(m===0)return'D'+r;if(m===1)return'A'+r;if(m===2)return'(A'+r+')';if(m===3)return'(A'+r+')+';if(m===4)return'-(A'+r+')';
 if(m===5)return s16(r16(ep))+'(A'+r+')';
 if(m===6){const x=r16(ep),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(A'+r+','+ir+')';}
 if(m===7&&r===0)return hw(r16(ep))+'.W';if(m===7&&r===1)return h(r32(ep))+'.L';
 if(m===7&&r===2){const d=s16(r16(ep));return d+'(PC)->'+h((ep+d)>>>0);}
 if(m===7&&r===3){const x=r16(ep),d=s8(x&255),ir=(x&0x8000?'A':'D')+((x>>12)&7)+(x&0x0800?'.L':'.W');return d+'(PC,'+ir+')';}
 if(m===7&&r===4)return'#'+(size==='L'?h(r32(ep)):hw(r16(ep)));
 return'EA('+m+','+r+')';
}
function dec(p){
 if(p<0||p+1>=MAX)return null;const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,text=hw(w),kind='OP',target=null,fall=true,terminal=false,reads=[],writes=[];
 if(w===0x4E75){kind='RTS';text='RTS';fall=false;terminal=true;}
 else if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=s16(r16(p+2))&0xFFFFFF;else if(m===7&&r===1)target=r32(p+2)&0xFFFFFF;else if(m===7&&r===2)target=(p+2+s16(r16(p+2)))>>>0;text=kind+' '+(target!=null?h(target):eaText(p+2,m,r,'L'));fall=kind==='JSR';terminal=kind==='JMP';}
 else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d);target=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;text=kind+' '+h(target);fall=cc!==0;terminal=cc===0;}
 else if((w&0xF100)===0x7000){const dr=(w>>9)&7,v=s8(w&255);kind='MOVEQ';text='MOVEQ #'+v+',D'+dr;writes=['D'+dr];}
 else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;const swd=eaWords(sm,sr,size),sep=p+2,dep=p+2+swd*2;len=2+(swd+eaWords(dm,dr,size))*2;const src=eaText(sep,sm,sr,size),dst=dm===0?'D'+dr:dm===1?'A'+dr:eaText(dep,dm,dr,size);kind=dm===1?'MOVEA.'+size:'MOVE.'+size;text=kind+' '+src+','+dst;if(sm===0)reads.push('D'+sr);if(sm===1)reads.push('A'+sr);if(sm>=2&&sm<=6)reads.push('A'+sr);if(dm===0)writes.push('D'+dr);if(dm===1)writes.push('A'+dr);if(dm>=2&&dm<=6)reads.push('A'+dr);}
 else if((w&0xF1C0)===0x41C0){const ar=(w>>9)&7;len=2+eaWords(m,r,'L')*2;kind='LEA';text='LEA '+eaText(p+2,m,r,'L')+',A'+ar;writes=['A'+ar];if(m>=2&&m<=6)reads.push('A'+r);}
 else if(g===11){const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B',dr=(w>>9)&7;len=2+eaWords(m,r,size)*2;kind='CMP.'+size;text=kind+' '+eaText(p+2,m,r,size)+',D'+dr;reads.push('D'+dr);if(m>=2&&m<=6)reads.push('A'+r);}
 else if((w&0xFFC0)===0x4A00){const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B';len=2+eaWords(m,r,size)*2;kind='TST.'+size;text=kind+' '+eaText(p+2,m,r,size);if(m>=2&&m<=6)reads.push('A'+r);}
 return{at:p,atHex:h(p),word:hw(w),len,next:p+len,kind,text,target:target==null?'':h(target),fall,terminal,reads:[...new Set(reads)],writes:[...new Set(writes)]};
}
const READERS=[0x016D3E,0x016FC6,0x017662,0x0176B2],DISP=[0x25B6,0x25C8];
function raw(a,b){const z=[];for(let p=a&~1;p<=b&&p<MAX;p+=2)z.push({at:h(p),word:hw(r16(p)),mark:READERS.includes(p)?'READ 1FA':''});return z;}
function forward(start,maxIns=80,maxBytes=0x180){const out=[];let p=start;for(let i=0;i<maxIns&&p<start+maxBytes;){const d=dec(p);if(!d)break;out.push(d);p=d.next;i++;if(d.terminal)break;}return out;}
function localDispatcherCalls(lo,hi){const a=[];for(let p=lo&~1;p<hi-6;p+=2){const d=dec(p);if(d&&d.target&&DISP.includes(parseInt(d.target,16)))a.push({at:d.atHex,text:d.text,target:d.target});}return a;}
const rows=[];
for(const at of READERS){
 const first=dec(at);const reg=first?.writes.find(x=>/^D[01]$/.test(x))||'';const seq=forward(at,96,0x220);
 const uses=seq.filter((d,i)=>i===0||reg&&(d.reads.includes(reg)||d.writes.includes(reg))||d.kind==='JSR'||d.kind==='BSR'||d.kind.startsWith('Bcc')||d.kind.startsWith('CMP')).slice(0,40);
 const addrFromReg=seq.filter(d=>/^MOVEA\./.test(d.kind)&&reg&&d.reads.includes(reg));
 const dispNear=localDispatcherCalls(Math.max(0,at-0x80),Math.min(MAX,at+0x500));
 rows.push({at:h(at),first:first?first.text:'',reg,addrFromReg:addrFromReg.map(x=>({at:x.atHex,text:x.text})),uses:uses.map(x=>({at:x.atHex,text:x.text,reads:x.reads.join(','),writes:x.writes.join(','),target:x.target})),dispatcherCalls:dispNear,raw:raw(at-0x20,at+0x90)});
}
const verdict={readers:READERS.length,strictReads:rows.filter(x=>/506\(A5\),D[01]/.test(x.first)).length,readersPromotingToAddress:rows.filter(x=>x.addrFromReg.length).length,nearDispatcherCalls:rows.reduce((n,x)=>n+x.dispatcherCalls.length,0),topReader:rows[0]?.at||'',topFirst:rows[0]?.first||'',topPromotion:rows.find(x=>x.addrFromReg.length)?.addrFromReg[0]?.text||''};
const out={version:'wof-selector-1fa-consumers-bridge-v1',verdict,rows};self.__WOF_SELECTOR_1FA_CONSUMERS=out;
console.log('=== 1FA CONSUMER BRIDGE VERDICT ===');console.table([verdict]);
for(const x of rows){console.log('=== '+x.at+' '+x.first+' ===');console.table(x.uses);if(x.addrFromReg.length)console.table(x.addrFromReg);if(x.dispatcherCalls.length)console.table(x.dispatcherCalls);}
console.log('=== 1FA CONSUMER BRIDGE JSON ===');console.log(JSON.stringify(out,null,2));return out;
})().catch(e=>{console.error('WOF_SELECTOR_1FA_CONSUMER_ERROR',e);throw e;});