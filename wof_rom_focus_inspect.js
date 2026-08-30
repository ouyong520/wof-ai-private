(()=>{
'use strict';
const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,L=self.__WOF_ROM_FOCUS_LAST,D=self.__WOF_ROM_FOCUS_DEEP;
if(!MOD?.HEAPU8||!C||!L?.longRefs||!D?.clusters)throw new Error('需要先完成 ROM focus bootstrap/deep v2');
const M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
const P={P1:0x00FFBE1C,P2:0x00FFBEFC,P3:0x00FFBFDC};
const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),w=x=>(x&0xffff).toString(16).toUpperCase().padStart(4,'0');
function callAt(p){const q=r16(p);if(q===0x4EB9||q===0x4EF9){const t=r32(p+2);if(t<MAX)return{at:p,target:t,kind:q===0x4EB9?'JSR.L':'JMP.L'};}if((q&0xFF00)===0x6100){const d=q&255,t=d===0?p+2+s16(r16(p+2)):p+2+s8(d);if(t>=0&&t<MAX)return{at:p,target:t,kind:'BSR'};}return null;}
function decodePrev(at){const a=[];for(let p=Math.max(0,at-8);p<=at+4;p+=2)a.push(w(r16(p)));const op2=at>=2?r16(at-2):0,op4=at>=4?r16(at-4):0;let hint='';if((op2&0xF1FF)===0x41F9)hint='LEA abs.L,A'+((op2>>9)&7);else if((op2&0xF1FF)===0x207C)hint='MOVEA.L #imm,A'+((op2>>9)&7);else if(op2===0x4879)hint='PEA abs.L';else if((op4&0xF1FF)===0x41F9)hint='LEA?';return{words:a.join(' '),hint};}
function refsIn(start,end){return (L.longRefs||[]).map(x=>({player:x.player,at:parseInt(x.off,16)})).filter(x=>x.at>=start&&x.at<end).map(x=>({player:x.player,at:h(x.at),offline:off(x.at),...decodePrev(x.at)}));}
function callers(start,end){const out=[];for(let p=0;p+6<MAX;p+=2){const c=callAt(p);if(c&&c.target>=start&&c.target<end)out.push({at:h(c.at),offlineAt:off(c.at),target:h(c.target),kind:c.kind});}return out;}
function pointerRefs(start,end){const out=[];for(let p=0;p+4<MAX;p+=2){const v=r32(p);if(v>=start&&v<end)out.push({at:h(p),offlineAt:off(p),value:h(v),prev:'0x'+w(p>=2?r16(p-2):0)});}return out;}
function branchEntrants(start,end){const out=[];for(let p=0;p+4<MAX;p+=2){const q=r16(p);if((q&0xF000)!==0x6000)continue;let t=null,len=2,d=q&255;if(d===0){t=p+2+s16(r16(p+2));len=4;}else if(d!==0xFF)t=p+2+s8(d);if(t!=null&&t>=start&&t<end&&(p<start||p>=end))out.push({at:h(p),target:h(t),op:'0x'+w(q),len});}return out;}
function hexLines(start,end,maxBytes=0x280){const stop=Math.min(end,start+maxBytes),rows=[];for(let p=start;p<stop;p+=16){let s='';for(let i=0;i<16&&p+i<stop;i++)s+=(i?' ':'')+r8(p+i).toString(16).toUpperCase().padStart(2,'0');rows.push({addr:h(p),offline:off(p),hex:s});}return rows;}
function nearestTypes(addr){const types=(L.types||[]).map(x=>({type:x.type,entry:Number(x.entry??x.liveEntry??0)})).filter(x=>Number.isFinite(x.entry));return types.map(x=>({...x,d:Math.abs(x.entry-addr)})).sort((a,b)=>a.d-b.d).slice(0,6).map(x=>({type:x.type,entry:h(x.entry),distance:x.d}));}
function run(){const strong=D.strong?.[0]||D.top?.[0]||null;console.log('=== FULL STRONG CANDIDATE ===');console.log(JSON.stringify(strong,null,2));const reports=[];for(const c0 of D.clusters){const start=parseInt(c0.func,16),end=parseInt(c0.end,16),refs=refsIn(start,end),cs=callers(start,end),prs=pointerRefs(start,end),bes=branchEntrants(start,end);const z={id:c0.id,start:h(start),offlineStart:off(start),end:h(end),size:end-start,features:c0.features,refs,callers:cs,pointerRefs:prs,branchEntrants:bes,nearestTypes:nearestTypes(start)};reports.push(z);console.log('\n=== CLUSTER '+c0.id+' '+h(start)+'..'+h(end)+' ===');console.log(JSON.stringify(z,null,2));console.log('--- ROM HEX ---');console.table(hexLines(start,end));}
console.log('\n=== VERDICT INPUT ===');console.table(reports.map(z=>({id:z.id,start:z.start,size:z.size,p1:z.features?.p1,p2:z.features?.p2,p3:z.features?.p3,cmp:z.features?.cmp,E0:z.features?.e0,DBcc:z.features?.dbcc,count2:z.features?.c2,count3:z.features?.c3,callers:z.callers.length,pointers:z.pointerRefs.length,externalBranches:z.branchEntrants.length,nearestType:z.nearestTypes[0]?.type,nearestDistance:z.nearestTypes[0]?.distance})));
const out={version:'rom-focus-inspect-v1',strong,reports};self.__WOF_ROM_FOCUS_INSPECT=out;return out;}
self.WOFFOCUSINSPECT={version:'rom-focus-inspect-v1',run};
console.log('✅ WOF ROM focus inspect v1 loaded');console.log('执行 WOFFOCUSINSPECT.run()');
})();