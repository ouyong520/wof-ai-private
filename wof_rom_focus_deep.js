(()=>{
'use strict';
try{self.WOFFOCUSDEEP?.stop?.();}catch(_){}
const MOD=_0x515056;if(!MOD?.HEAPU8)throw new Error('HEAPU8 unavailable');
const C=self.__WOF_ROM_LOC_CACHE;if(!C||!Number.isInteger(C.base))throw new Error('先运行 WOFFOCUSROM.locate()');
const LAST=self.__WOF_ROM_FOCUS_LAST;if(!LAST?.helpers?.length)throw new Error('先运行 await WOFFOCUSROM.result()');
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
function calls(start,span=0x500){const end=Math.min(MAX,start+span),out=[];for(let p=start&~1;p+2<end;p+=2){const w=r16(p);if(w===0x4EB9||w===0x4EF9){const t=r32(p+2);if(t<MAX)out.push({at:p,target:t,kind:w===0x4EB9?'JSR.L':'JMP.L'});}else if((w&0xFF00)===0x6100){const d=w&255;let t;if(d===0&&p+4<=end)t=p+2+s16(r16(p+2));else t=p+2+s8(d);if(t>=0&&t<MAX)out.push({at:p,target:t,kind:'BSR'});}}return out;}
function features(start,span=0x500){const end=Math.min(MAX,start+span);let p1=0,p2=0,p3=0,low1=0,low2=0,low3=0,e0=0,count3=0,count2=0,cmp=0,branch=0,dbcc=0,tst=0,xyOff=0,absPlayerLoad=0;
 for(let p=start&~1;p+1<end;p+=2){const w=r16(p);if(p+3<end){const d=r32(p);if(d===PLAYER.P1)p1++;if(d===PLAYER.P2)p2++;if(d===PLAYER.P3)p3++;if((d===PLAYER.P1||d===PLAYER.P2||d===PLAYER.P3)&&p>=2){const prev=r16(p-2);if((prev&0xF1FF)===0x41F9||(prev&0xF1FF)===0x207C||prev===0x4879)absPlayerLoad++;}}
  if(w===(PLAYER.P1&0xffff))low1++;if(w===(PLAYER.P2&0xffff))low2++;if(w===(PLAYER.P3&0xffff))low3++;
  if(w===0x00E0||w===0xFFE0)e0++;
  if(w===0x0003||w===0x0002)w===0x0003?count3++:count2++;
  if((w&0xF000)===0xB000)cmp++;
  if((w&0xF000)===0x6000)branch++;
  if((w&0xF0F8)===0x50C8)dbcc++;
  if((w&0xFF00)===0x4A00)tst++;
  if(w===0x0004||w===0x0008||w===0x000C)xyOff++;
 }
 const playerLong=p1+p2+p3,playerLow=low1+low2+low3;
 let score=0;score+=p1*18+(p2+p3)*10+absPlayerLoad*10+Math.min(e0,4)*9+Math.min(count3+count2,4)*4+Math.min(cmp,12)*1.6+Math.min(branch,16)*.7+Math.min(dbcc,4)*7+Math.min(xyOff,8)*1.5+Math.min(tst,8)*.8+Math.min(playerLow,6)*2;
 if(p1&&e0)score+=30;if(p1&&e0&&(count3||count2))score+=28;if((playerLong>=2)&&cmp)score+=20;if(dbcc&&e0)score+=18;
 return{p1,p2,p3,playerLong,playerLow,e0,count3,count2,cmp,branch,dbcc,tst,xyOff,absPlayerLoad,score:+score.toFixed(1)};
}
function mergeTypes(root){const raw=LAST.helpers.find(x=>parseInt(x.target,16)===root);return raw?.types||'';}
function roots(){const rs=new Set();for(const x of LAST.helpers.slice(0,80)){const t=parseInt(x.target,16);if(Number.isFinite(t)&&t<MAX)rs.add(t);} // existing common helpers
 // Add every direct P1 long reference neighborhood, because selectors may be one layer below common helpers.
 for(let p=0;p+4<MAX;p+=2)if(r32(p)===PLAYER.P1){for(const b of [p&~0x7F,Math.max(0,(p-0x100)&~1)])rs.add(b);}
 return[...rs];}
function analyzeRoot(root,depth=2){const seen=new Map(),q=[{addr:root,depth:0,parent:null}];while(q.length){const n=q.shift();if(n.addr<0||n.addr>=MAX||seen.has(n.addr)||n.depth>depth)continue;const f=features(n.addr);const cs=calls(n.addr);seen.set(n.addr,{addr:n.addr,depth:n.depth,parent:n.parent,features:f,calls:cs.length});if(n.depth<depth)for(const c of cs.slice(0,80))q.push({addr:c.target,depth:n.depth+1,parent:n.addr});}
 const nodes=[...seen.values()].sort((a,b)=>b.features.score-a.features.score);const best=nodes[0]||null;let score=best?.features.score||0;const rootF=features(root);score+=Math.min(20,(LAST.helpers.find(x=>parseInt(x.target,16)===root)?.callerGroups||0)*1.3);if(best&&best.depth>0)score+=6;return{root,best,nodes,rootF,score:+score.toFixed(1)};}
async function run(){console.log('🧠 ROM Target Selector 深挖开始 · 只扫描1MB ROM，不扫256MB HEAP');const rs=roots(),rows=[];for(let i=0;i<rs.length;i++){if(stopped)throw new Error('deep scan stopped');const z=analyzeRoot(rs[i],2),b=z.best;if(b&&(b.features.score>=8||z.rootF.score>=8)){rows.push({root:h(z.root),offlineRoot:off(z.root),types:mergeTypes(z.root),best:h(b.addr),offlineBest:off(b.addr),depth:b.depth,score:z.score,p1:b.features.p1,p2:b.features.p2,p3:b.features.p3,E0:b.features.e0,count3:b.features.count3,count2:b.features.count2,cmp:b.features.cmp,branches:b.features.branch,DBcc:b.features.dbcc,xy:b.features.xyOff,playerLoads:b.features.absPlayerLoad,calls:b.calls});}if(i%20===19)await sleep(0);}
 rows.sort((a,b)=>b.score-a.score);const top=rows.slice(0,40);console.log('=== TARGET SELECTOR TOP ===');console.table(top);
 const strong=top.filter(x=>x.p1>0&&x.E0>0&&(x.count3>0||x.count2>0||x.DBcc>0));console.log('=== STRONG SIGNATURE: P1 + E0 + player-loop evidence ===');console.table(strong.slice(0,20));
 const out={version:'rom-focus-deep-v1',rom:{base:'0x'+base.toString(16).toUpperCase(),swap16:SW,offlineDelta:DELTA},top,strong};self.__WOF_ROM_FOCUS_DEEP=out;return out;}
self.WOFFOCUSDEEP={version:'rom-focus-deep-v1',run,features:a=>features(typeof a==='string'?parseInt(a,16):a),calls:a=>calls(typeof a==='string'?parseInt(a,16):a),inspect(a){a=typeof a==='string'?parseInt(a,16):a;const z=analyzeRoot(a,2);console.table(z.nodes.map(n=>({addr:h(n.addr),offline:off(n.addr),depth:n.depth,parent:n.parent==null?'':h(n.parent),score:n.features.score,p1:n.features.p1,p2:n.features.p2,p3:n.features.p3,E0:n.features.e0,count3:n.features.count3,count2:n.features.count2,cmp:n.features.cmp,branch:n.features.branch,DBcc:n.features.dbcc,xy:n.features.xyOff,calls:n.calls})));return z;},stop(){stopped=true;}};
console.log('✅ WOF ROM focus deep v1 loaded');console.log('执行 await WOFFOCUSDEEP.run()');
})();