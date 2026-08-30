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
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function dec(p){
 if(p<0||p+1>=MAX)return null;const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;let len=2,kind='OP',target=null,fall=true,terminal=false;
 if(w===0x4E75||w===0x4E73||w===0x4E77){kind='RET';fall=false;terminal=true;}
 else if(w===0x4E72){kind='STOP';len=4;fall=false;terminal=true;}
 else if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';fall=kind==='JSR';len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)target=s16(r16(p+2))&0xFFFFFF;else if(m===7&&r===1)target=r32(p+2)&0xFFFFFF;else if(m===7&&r===2)target=(p+2+s16(r16(p+2)))>>>0;}
 else if(g===6){const cc=(w>>8)&15,d=w&255;len=d===0?4:2;const disp=d===0?s16(r16(p+2)):s8(d);target=(p+2+disp)>>>0;kind=cc===0?'BRA':cc===1?'BSR':'Bcc'+cc;fall=cc!==0;}
 else if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;len=2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;}
 else if(g===5){const sz=(w>>6)&3;if(sz===3&&m===1){kind='DBcc';len=4;target=(p+2+s16(r16(p+2)))>>>0;}else len=2+eaWords(m,r,sz===2?'L':sz===1?'W':'B')*2;}
 else if(g===0){if([0x003C,0x007C,0x023C,0x027C,0x0A3C,0x0A7C].includes(w))len=4;else if((w&0xF138)===0x0108)len=4;else if((w&0xFF00)===0x0800)len=4+eaWords(m,r,'B')*2;else if((w&0xF100)===0x0100)len=2+eaWords(m,r,'B')*2;else{const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)&&sz!==3){const s=sz===2?'L':sz===1?'W':'B';len=2+(s==='L'?4:2)+eaWords(m,r,s)*2;}}}
 else if(g===4){if((w&0xFFF8)===0x4E50)len=4;else if((w&0xFB80)===0x4880&&m>=2)len=4+eaWords(m,r,(w&0x40)?'L':'W')*2;else if((w&0xF1C0)===0x41C0)len=2+eaWords(m,r,'L')*2;else if((w&0xFFC0)===0x4840&&m!==0)len=2+eaWords(m,r,'L')*2;else len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===8){if((w&0xF1F0)!==0x8100)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===9||g===13){const special=(w&0xF130)===(g===9?0x9100:0xD100),a=((w>>6)&7)===3||((w>>6)&7)===7;if(!special)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===11){const cmpm=(w&0xF138)===0xB108,a=((w>>6)&7)===3||((w>>6)&7)===7;if(!cmpm)len=2+eaWords(m,r,a?(((w>>6)&1)?'L':'W'):(((w>>6)&3)===2?'L':'W'))*2;}
 else if(g===12){const exg=(w&0xF1F8)===0xC140||(w&0xF1F8)===0xC148||(w&0xF1F8)===0xC188,abcd=(w&0xF1F0)===0xC100;if(!exg&&!abcd)len=2+eaWords(m,r,((w>>6)&3)===2?'L':'W')*2;}
 else if(g===14&&((w>>6)&3)===3)len=2+eaWords(m,r,'W')*2;
 else if(g===10||g===15){kind='LINE';fall=false;terminal=true;}
 len=Math.max(2,len);return{at:p,word:w,len,next:p+len,kind,target,fall,terminal};
}
const LO=0x011190,HI=0x0111C2,CMP=0x0111B4;
function directCtl(p){const d=dec(p);if(!d||d.target==null)return null;if(!(d.kind==='JSR'||d.kind==='JMP'||d.kind==='BRA'||d.kind==='BSR'||d.kind==='DBcc'||d.kind.startsWith('Bcc')))return null;return d;}
function pathToCmp(start){const q=[start],seen=new Set(),path=[];while(q.length&&seen.size<80){const p=q.shift();if(p<CMP-0x80||p>CMP+0x20||(p&1)||seen.has(p))continue;seen.add(p);const d=dec(p);if(!d)continue;path.push({at:h(p),word:hw(d.word),kind:d.kind,len:d.len,target:d.target==null?'':h(d.target)});if(p===CMP)return{reaches:true,steps:seen.size,path:path.slice(-20)};if(d.kind==='BRA'||d.kind==='JMP'){if(d.target!=null)q.push(d.target);continue;}if(d.kind.startsWith('Bcc')||d.kind==='DBcc'){q.push(d.next);if(d.target!=null)q.push(d.target);continue;}if(d.terminal)continue;q.push(d.next);}return{reaches:false,steps:seen.size,path:path.slice(-20)};}
const rows=[];
for(let p=0;p<MAX-6;p+=2){const d=directCtl(p);if(!d||d.target<LO||d.target>HI)continue;const z=pathToCmp(d.target);rows.push({at:h(p),word:hw(d.word),kind:d.kind,target:h(d.target),external:!(p>=LO&&p<=HI),reachesCmp:z.reaches,path:z.reaches?z.path.map(x=>x.at).join(' -> '):''});}
rows.sort((a,b)=>(b.reachesCmp-a.reachesCmp)||(b.external-a.external)||(parseInt(a.at,16)-parseInt(b.at,16)));
const external=rows.filter(x=>x.external),reaching=rows.filter(x=>x.reachesCmp),externalReaching=rows.filter(x=>x.external&&x.reachesCmp);
const raw=[];for(let p=0x011180;p<=0x0111BC;p+=2)raw.push({at:h(p),word:hw(r16(p))});
const verdict={range:h(LO)+'..'+h(HI),cmpAt:h(CMP),incoming:rows.length,externalIncoming:external.length,reachesCmp:reaching.length,externalReachesCmp:externalReaching.length,topAt:externalReaching[0]?.at||reaching[0]?.at||'',topKind:externalReaching[0]?.kind||reaching[0]?.kind||'',topTarget:externalReaching[0]?.target||reaching[0]?.target||'',topPath:externalReaching[0]?.path||reaching[0]?.path||''};
const out={version:'wof-dispatch-111b4-entry-incoming-v1',verdict,rows,raw};self.__WOF_111B4_ENTRY_INCOMING=out;
console.log('=== 111B4 ENTRY INCOMING VERDICT ===');console.table([verdict]);
console.log('=== INCOMING CONTROL TO 111190..1111C2 ===');console.table(rows);
console.log('=== RAW WORDS 111180..1111BC ===');console.table(raw);
console.log('=== 111B4 ENTRY INCOMING JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_111B4_ENTRY_INCOMING_ERROR',e);throw e;});