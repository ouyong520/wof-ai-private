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
const TABLE=0x010CF8, EDGES=[0x010F48,0x010FA2], PLAYERS=[0xFFBE1C,0xFFBEFC,0xFFBFDC];
const table=[0,1,2].map(i=>({slot:i,at:h(TABLE+i*4),value:h(r32(TABLE+i*4))}));
function nearEdge(p){let best=EDGES[0],d=Math.abs(p-best);for(const e of EDGES){const x=Math.abs(p-e);if(x<d){d=x;best=e;}}return{edge:h(best),distance:d};}
function window(p,before=8,after=10){const a=[];for(let q=Math.max(0,p-before*2)&~1;q<Math.min(MAX,p+(after+1)*2);q+=2)a.push({at:h(q),word:hw(r16(q)),mark:q===p?'HERE':EDGES.includes(q)?'EDGE':q===TABLE?'TABLE':''});return a;}
const xrefs=[];
for(let p=0;p+5<MAX;p+=2){const w=r16(p),ea=w&0x3f;
  if(ea===0x3A){const ext=r16(p+2),t=(p+2+s16(ext))>>>0;if(t===TABLE){const n=nearEdge(p);xrefs.push({at:h(p),word:hw(w),kind:'PC+d16',ext:hw(ext),base:h(t),nearestEdge:n.edge,distance:n.distance});}}
  if(ea===0x3B){const ext=r16(p+2),t=(p+2+s8(ext&255))>>>0;if(t===TABLE){const ir=(ext&0x8000?'A':'D')+((ext>>12)&7)+(ext&0x0800?'.L':'.W');const n=nearEdge(p);xrefs.push({at:h(p),word:hw(w),kind:'PC+index',ext:hw(ext),index:ir,base:h(t),nearestEdge:n.edge,distance:n.distance});}}
  if(ea===0x39){const t=r32(p+2)>>>0;if(t===TABLE){const n=nearEdge(p);xrefs.push({at:h(p),word:hw(w),kind:'abs.L EA',ext:h(t),base:h(t),nearestEdge:n.edge,distance:n.distance});}}
}
const literalBaseHits=[];for(let p=0;p+3<MAX;p+=2)if(r32(p)===TABLE)literalBaseHits.push(h(p));
const local=xrefs.filter(x=>{const p=parseInt(x.at,16);return p>=0x010800&&p<0x011400;}).sort((a,b)=>a.distance-b.distance);
const all=xrefs.slice().sort((a,b)=>a.distance-b.distance);
const focus=(local.length?local:all).slice(0,12).map(x=>({...x,window:window(parseInt(x.at,16),7,9)}));
const edgeWindows=EDGES.map(e=>({edge:h(e),window:window(e,14,12)}));
const verdict={tableBase:h(TABLE),tableValid:table.every((x,i)=>parseInt(x.value,16)===PLAYERS[i]),xrefs:xrefs.length,localXrefs:local.length,literalBaseHits:literalBaseHits.length,topXref:(local[0]||all[0])?.at||'',topKind:(local[0]||all[0])?.kind||'',topIndex:(local[0]||all[0])?.index||'',topNearestEdge:(local[0]||all[0])?.nearestEdge||'',topDistance:(local[0]||all[0])?.distance??-1};
const out={version:'wof-player-table-10cf8-xrefs-v1',verdict,table,xrefs:all.slice(0,40),literalBaseHits:literalBaseHits.slice(0,40),focus,edgeWindows};
self.__WOF_PLAYER_TABLE_10CF8_XREFS=out;
console.log('=== 10CF8 PLAYER TABLE XREF VERDICT ===');console.table([verdict]);
console.log('=== 10CF8 PLAYER TABLE XREFS ===');console.table(out.xrefs);
console.log('=== 10CF8 PLAYER TABLE FOCUS ===');console.dir(focus,{depth:null});
console.log('=== 10CF8 PLAYER TABLE XREF JSON ===');console.log(JSON.stringify(out,null,2));
return out;
})().catch(e=>{console.error('WOF_PLAYER_TABLE_10CF8_XREF_ERROR',e);throw e;});