(()=>{
'use strict';
try{self.WOFFOCUSDEEP?.stop?.();}catch(_){}
const MOD=_0x515056;if(!MOD?.HEAPU8)throw new Error('HEAPU8 unavailable');
const C=self.__WOF_ROM_LOC_CACHE;if(!C||!Number.isInteger(C.base))throw new Error('先运行 WOFFOCUSROM.locate()');
const LAST=self.__WOF_ROM_FOCUS_LAST;if(!LAST?.longRefs)throw new Error('先运行 await WOFFOCUSROM.result()');
const M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
const PLAYER={P1:0x00FFBE1C,P2:0x00FFBEFC,P3:0x00FFBFDC};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;
const r8=o=>M[base+(SW?(o^1):o)]>>>0;
const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
const s8=v=>v&0x80?v-0x100:v,s16=v=>v&0x8000?v-0x10000:v;
const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
const off=x=>h((x-DELTA)>>>0);
const TYPES=(LAST.types||[]).map(x=>({type:x.type,entry:Number(x.entry??x.liveEntry??0)})).filter(x=>Number.isFinite(x.entry)&&x.entry<MAX);
function callAt(p){const w=r16(p);if(w===0x4EB9||w===0x4EF9){const t=r32(p+2);if(t<MAX)return{at:p,target:t,kind:w===0x4EB9?'JSR.L':'JMP.L',len:6};}if((w&0xFF00)===0x6100){const d=w&255;let t,len=2;if(d===0){t=p+2+s16(r16(p+2));len=4;}else t=p+2+s8(d);if(t>=0&&t<MAX)return{at:p,target:t,kind:'BSR',len};}return null;}
function calls(start,span=0x600){const end=Math.min(MAX,start+span),out=[];for(let p=start&~1;p+2<end;p+=2){const c=callAt(p);if(c)out.push(c);}return out;}
function findFuncStart(addr){addr=Math.max(0,Math.min(MAX-2,addr&~1));let term=-1,pro=-1;for(let p=addr;p>=Math.max(0,addr-0x180);p-=2){const w=r16(p);if((w&0xFFF8)===0x4E50||w===0x48E7){pro=p;break;}if(w===0x4E75||w===0x4E73||w===0x4E77){term=p+2;break;}}return pro>=0?pro:(term>=0?term:Math.max(0,(addr-0x80)&~1));}
function findFuncEnd(start){for(let p=start;p<Math.min(MAX,start+0x800);p+=2){const w=r16(p);if(w===0x4E75||w===0x4E73||w===0x4E77)return p+2;}return Math.min(MAX,start+0x600);}
function features(start,end=findFuncEnd(start)){let p1=0,p2=0,p3=0,e0=0,c2=0,c3=0,cmp=0,branch=0,dbcc=0,tst=0,xy=0,leaAbs=0,addsE0=0;
 for(let p=start&~1;p+1<end;p+=2){const w=r16(p);if(p+3<end){const d=r32(p);if(d===PLAYER.P1)p1++;if(d===PLAYER.P2)p2++;if(d===PLAYER.P3)p3++;if(d===PLAYER.P1||d===PLAYER.P2||d===PLAYER.P3){const prev=p>=2?r16(p-2):0;if((prev&0xF1FF)===0x41F9||(prev&0xF1FF)===0x207C||prev===0x4879)leaAbs++;}}
  if(w===0x00E0||w===0xFFE0){e0++;const prev=p>=2?r16(p-2):0;if((prev&0xF000)===0x5000||(prev&0xF000)===0xD000)addsE0++;}
  if(w===0x0002)c2++;if(w===0x0003)c3++;
  if((w&0xF000)===0xB000)cmp++;
  if((w&0xF000)===0x6000)branch++;
  if((w&0xF0F8)===0x50C8)dbcc++;
  if((w&0xFF00)===0x4A00)tst++;
  if(w===0x0004||w===0x0008||w===0x000C)xy++;
 }
 const all3=!!(p1&&p2&&p3),playerRefs=p1+p2+p3;
 let score=playerRefs*18+(all3?70:0)+Math.min(e0,5)*10+Math.min(c2+c3,4)*4+Math.min(cmp,12)*1.8+Math.min(branch,18)*.7+Math.min(dbcc,4)*9+Math.min(xy,10)*1.4+Math.min(tst,8)*.8+leaAbs*8+addsE0*10;
 if(all3&&cmp)score+=35;if(all3&&e0)score+=45;if(e0&&dbcc)score+=25;if(all3&&(c2||c3||dbcc))score+=30;
 return{p1,p2,p3,playerRefs,all3,e0,c2,c3,cmp,branch,dbcc,tst,xy,leaAbs,addsE0,score:+score.toFixed(1)};
}
function refClusters(){const a=(LAST.longRefs||[]).map(x=>({player:x.player,at:parseInt(x.off,16)})).filter(x=>Number.isFinite(x.at)).sort((x,y)=>x.at-y.at),groups=[];let g=[];for(const x of a){if(!g.length||x.at-g[g.length-1].at<=0x100)g.push(x);else{groups.push(g);g=[x];}}if(g.length)groups.push(g);return groups.map((g,i)=>{const min=g[0].at,max=g[g.length-1].at,fs=findFuncStart(min),fe=findFuncEnd(fs),f=features(fs,fe),ps=[...new Set(g.map(x=>x.player))];return{id:i,refs:g.length,players:ps.join(','),triple:ps.includes('P1')&&ps.includes('P2')&&ps.includes('P3'),min,max,func:fs,end:fe,features:f};}).sort((a,b)=>(b.triple-a.triple)||(b.features.score-a.features.score));}
async function buildReverse(){console.log('🧭 建立1MB ROM反向调用索引…');const rev=new Map(),all=[];for(let start=0;start<MAX;start+=0x8000){const end=Math.min(MAX,start+0x8000);for(let p=start&~1;p+2<end;p+=2){const c=callAt(p);if(!c)continue;all.push(c);let a=rev.get(c.target);if(!a)rev.set(c.target,a=[]);a.push(c);}if((start&0x1FFFF)===0x18000)await sleep(0);}return{rev,all};}
function callersNear(rev,target,slack=0x20){const out=[];for(let d=-slack;d<=slack;d+=2){const a=rev.get(target+d);if(a)out.push(...a);}return out;}
function nearestTypes(addr,rad=0x1200){return TYPES.filter(t=>Math.abs(t.entry-addr)<=rad).map(t=>t.type);}
function reverseWalk(cluster,rev,depthMax=4){const rows=[],seen=new Set(),q=[{func:cluster.func,depth:0,via:null}];while(q.length){const n=q.shift();if(seen.has(n.func)||n.depth>depthMax)continue;seen.add(n.func);const fe=findFuncEnd(n.func),f=features(n.func,fe),types=nearestTypes(n.func);rows.push({func:n.func,end:fe,depth:n.depth,via:n.via,features:f,types});if(n.depth===depthMax)continue;const cs=callersNear(rev,n.func,0x20);for(const c of cs){const caller=findFuncStart(c.at);if(!seen.has(caller))q.push({func:caller,depth:n.depth+1,via:c});}}
 return rows;}
async function run(){console.log('🧠 ROM Target Selector deep v2 · 从P1/P2/P3引用反向追敌人AI');const clusters=refClusters();console.log('=== PLAYER REF CLUSTERS ===');console.table(clusters.map(c=>({id:c.id,refs:c.refs,players:c.players,triple:c.triple,func:h(c.func),offlineFunc:off(c.func),end:h(c.end),score:c.features.score,E0:c.features.e0,cmp:c.features.cmp,DBcc:c.features.dbcc,count2:c.features.c2,count3:c.features.c3,xy:c.features.xy})));
 const {rev,all}=await buildReverse(),cand=[];for(const c of clusters){const path=reverseWalk(c,rev,4);for(const n of path){const typeN=n.types.length,typeBonus=typeN?Math.min(80,typeN*12):0,depthBonus=Math.max(0,30-n.depth*6),tripleBonus=c.triple?45:0;let score=n.features.score+typeBonus+depthBonus+tripleBonus;if(n.depth>0&&typeN)score+=35;cand.push({cluster:c.id,clusterFunc:h(c.func),func:h(n.func),offlineFunc:off(n.func),depth:n.depth,types:n.types.join(','),typeN,score:+score.toFixed(1),p1:n.features.p1,p2:n.features.p2,p3:n.features.p3,E0:n.features.e0,cmp:n.features.cmp,DBcc:n.features.dbcc,count2:n.features.c2,count3:n.features.c3,xy:n.features.xy,branches:n.features.branch,playerRefs:n.features.playerRefs});}}
 cand.sort((a,b)=>b.score-a.score);const top=cand.slice(0,60),strong=top.filter(x=>x.typeN>0||((x.p1&&x.p2&&x.p3)&&(x.E0||x.DBcc||x.count2||x.count3)));
 console.log('=== TARGET SELECTOR TOP ===');console.table(top.slice(0,30));console.log('=== STRONG TARGET SELECTOR CANDIDATES ===');console.table(strong.slice(0,20));
 const out={version:'rom-focus-deep-v2-reverse-callgraph',rom:{base:'0x'+base.toString(16).toUpperCase(),swap16:SW,offlineDelta:DELTA},clusters:clusters.map(c=>({id:c.id,refs:c.refs,players:c.players,triple:c.triple,func:h(c.func),offlineFunc:off(c.func),end:h(c.end),features:c.features})),callCount:all.length,top,strong};self.__WOF_ROM_FOCUS_DEEP=out;return out;}
self.WOFFOCUSDEEP={version:'rom-focus-deep-v2-reverse-callgraph',run,clusters:refClusters,features:a=>{a=typeof a==='string'?parseInt(a,16):a;const s=findFuncStart(a);return{start:h(s),end:h(findFuncEnd(s)),features:features(s)};},stop(){stopped=true;}};
console.log('✅ WOF ROM focus deep v2 loaded · 不再依赖 common helpers');console.log('执行 await WOFFOCUSDEEP.run()');
})();