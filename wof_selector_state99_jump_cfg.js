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
function genericLen(p){
 const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;
 if(w===0x4E75||w===0x4E73||w===0x4E77)return 2;
 if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0)return 2+eaWords(m,r,'L')*2;
 if(g===6)return (w&255)===0?4:2;
 if(g===1||g===2||g===3){const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;return 2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;}
 if((w&0xF1C0)===0x41C0)return 2+eaWords(m,r,'L')*2;
 if((w&0xF100)===0x7000)return 2;
 if((w&0xFF00)===0x4200||(w&0xFF00)===0x4400||(w&0xFF00)===0x4600||(w&0xFF00)===0x4A00){const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B';return 2+eaWords(m,r,size)*2;}
 if((w&0xFFC0)===0x4880||(w&0xFFC0)===0x48C0)return 2;
 if(g===0){
   if((w&0xFF00)===0x0800){return 4+eaWords(m,r,'B')*2;}
   const op=(w>>8)&15,sz=(w>>6)&3;if([0,2,4,6,10,12].includes(op)&&sz!==3){const size=sz===2?'L':sz===1?'W':'B',imm=size==='L'?4:2;return 2+imm+eaWords(m,r,size)*2;}
 }
 if(g===5){const sz=(w>>6)&3;if(sz===3){return 2+eaWords(m,r,'B')*2;}const size=sz===2?'L':sz===1?'W':'B';return 2+eaWords(m,r,size)*2;}
 if([8,9,11,12,13].includes(g)){const opm=(w>>6)&7;let size='W';if(opm===0||opm===4)size='B';else if(opm===2||opm===6)size='L';return 2+eaWords(m,r,size)*2;}
 if(g===14){if(((w>>6)&3)===3)return 2+eaWords(m,r,'W')*2;return 2;}
 return 2;
}
function decCtl(p){
 const w=r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;
 if(w===0x4E75||w===0x4E73||w===0x4E77)return{at:p,len:2,kind:'RTS',target:null,fall:false};
 if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){const kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';let t=null;const len=2+eaWords(m,r,'L')*2;if(m===7&&r===0)t=s16(r16(p+2))&0xFFFFFF;else if(m===7&&r===1)t=r32(p+2)&0xFFFFFF;else if(m===7&&r===2)t=(p+2+s16(r16(p+2)))>>>0;return{at:p,len,kind,target:t,fall:kind==='JSR'};}
 if(g===6){const cc=(w>>8)&15,d=w&255,len=d===0?4:2,disp=d===0?s16(r16(p+2)):s8(d),t=(p+2+disp)>>>0;return{at:p,len,kind:cc===0?'BRA':cc===1?'BSR':'Bcc'+cc,target:t,fall:cc!==0};}
 return null;
}
const JUMP=0x010EB0,EXT=r16(JUMP+2),TABLE=(JUMP+2+s8(EXT&255))>>>0;
const table=[];
for(let i=0;i<9;i++){const at=TABLE+i*2,v=r16(at),sv=s16(v),target=(TABLE+sv)>>>0;table.push({indexByte:i*2,at:h(at),word:hw(v),signed:sv,target:h(target)});}
const uniq=[...new Set(table.map(x=>parseInt(x.target,16)))];
const TARGETS=[0x010F48,0x010FA2];
function walk(start){
 const q=[{pc:start,path:[]}],seen=new Set(),hits=[];let qi=0;
 while(qi<q.length&&qi<5000){const s=q[qi++],pc=s.pc;if(pc<0x010A00||pc>=0x011100)continue;if(seen.has(pc))continue;seen.add(pc);
   if(TARGETS.includes(pc)){hits.push({target:h(pc),path:s.path.map(h).join(' -> ')+' -> '+h(pc)});continue;}
   let p=pc;
   for(let n=0;n<140&&p>=0x010A00&&p<0x011100;n++){
     if(TARGETS.includes(p)){hits.push({target:h(p),path:[...s.path,p].map(h).join(' -> ')});break;}
     const c=decCtl(p);
     if(c){
       const np=[...s.path,p];
       if(c.target!=null&&c.target>=0x010A00&&c.target<0x011100)q.push({pc:c.target,path:np});
       if(c.kind==='RTS'||c.kind==='BRA'||c.kind==='JMP')break;
       p+=c.len;continue;
     }
     p+=Math.max(2,genericLen(p));
   }
 }
 return{visited:seen.size,hits:hits.slice(0,20)};
}
function rawWin(t){const a=[];for(let p=Math.max(0,t-16);p<=Math.min(MAX-2,t+48);p+=2)a.push({at:h(p),word:hw(r16(p)),mark:p===t?'TARGET':''});return a;}
const rows=uniq.map(t=>{const w=walk(t);return{target:h(t),visited:w.visited,reachesDispatch:w.hits.length>0,hits:w.hits,raw:rawWin(t)};});
const incoming=[];
for(let p=0x010A00;p<0x011100;p+=2){const c=decCtl(p);if(c&&c.target!=null&&uniq.includes(c.target))incoming.push({at:h(p),kind:c.kind,target:h(c.target),word:hw(r16(p))});}
const verdict={jumpAt:h(JUMP),jumpWord:hw(r16(JUMP)),ext:hw(EXT),tableBase:h(TABLE),entries:table.length,uniqueTargets:uniq.length,targetsReachDispatch:rows.filter(x=>x.reachesDispatch).length,totalReachHits:rows.reduce((n,x)=>n+x.hits.length,0),incomingToStateTargets:incoming.length};
const out={version:'wof-selector-state99-jump-cfg-v1',verdict,table,rows,incoming};self.__WOF_SELECTOR_STATE99_JUMP_CFG=out;
console.log('=== SELECTOR STATE99 JUMP CFG VERDICT ===');console.table([verdict]);
console.log('=== STATE99 TABLE ===');console.table(table);
console.log('=== STATE99 TARGET REACHABILITY ===');console.table(rows.map(x=>({target:x.target,visited:x.visited,reachesDispatch:x.reachesDispatch,hits:x.hits.map(y=>y.target).join(' ')})));
console.log('=== SELECTOR STATE99 JUMP CFG JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_SELECTOR_STATE99_JUMP_CFG_ERROR',e);throw e;});
