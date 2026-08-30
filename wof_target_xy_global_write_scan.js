(()=>{
'use strict';
try{self.WOFTARGETXYGLOBAL?.stop?.();}catch(_){}
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let stopped=false;
const load=async f=>{const r=await fetch(RAW+f+'?x='+Math.random());if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return (0,eval)(await r.text());};
async function ensure(){if(!self.__WOF_ROM_LOC_CACHE)await load('wof_rom_focus_inspect.js');for(let i=0;i<300&&!self.__WOF_ROM_LOC_CACHE;i++)await sleep(50);if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM state unavailable');}
function env(){const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8,base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
 const r8=o=>M[base+(SW?(o^1):o)]>>>0,r16=o=>((r8(o)<<8)|r8(o+1))>>>0,r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0,s16=v=>v&0x8000?v-0x10000:v,h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0'),off=x=>h((x-DELTA)>>>0),hw=x=>'0x'+(x&0xffff).toString(16).toUpperCase().padStart(4,'0');return{MAX,r8,r16,r32,s16,h,off,hw};}
function eaWords(m,r,size){if(m<=4)return 0;if(m===5||m===6)return 1;if(m===7){if(r===0||r===2||r===3)return 1;if(r===1)return 2;if(r===4)return size==='L'?2:1;}return 0;}
function regName(m,r){return m===0?'D'+r:m===1?'A'+r:'';}
function moveWrite(E,p){const w=E.r16(p),g=w>>>12;if(g!==1&&g!==2&&g!==3)return null;const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;if(dm!==5)return null;const sw=eaWords(sm,sr,size),ext=p+2+sw*2;if(ext+1>=E.MAX)return null;const disp=E.s16(E.r16(ext));if(disp!==0x3e&&disp!==0x42)return null;return{at:p,op:w,kind:'MOVE.'+size,baseReg:'A'+dr,disp,srcReg:regName(sm,sr),srcMode:sm,srcEaReg:sr,len:2+(sw+1)*2};}
function singleWrite(E,p){const w=E.r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;if(m!==5)return null;let size='W',ext=p+2,kind='';
 if(g===5&&((w>>6)&3)!==3){size=((w>>6)&3)===2?'L':((w>>6)&3)===1?'W':'B';kind='ADDQ/SUBQ';}
 else if(g===4&&(((w&0xff00)===0x4200)||((w&0xff00)===0x4400)||((w&0xff00)===0x4600))){size=((w>>6)&3)===2?'L':((w>>6)&3)===1?'W':'B';kind='CLR/NEG/NOT';}
 else if(g===0){const op=(w>>8)&15,sz=(w>>6)&3;if(![0,2,4,6,10].includes(op)||sz===3)return null;size=sz===2?'L':sz===1?'W':'B';ext=p+2+(size==='L'?4:2);kind='IMM-EA';}
 else return null;
 if(ext+1>=E.MAX)return null;const disp=E.s16(E.r16(ext));if(disp!==0x3e&&disp!==0x42)return null;return{at:p,op:w,kind:kind+'.'+size,baseReg:'A'+r,disp,srcReg:'',srcMode:'',srcEaReg:'',len:ext-p+2};}
function ctx(E,p){const out=[];for(let q=Math.max(0,p-0x16)&~1;q<=Math.min(E.MAX-2,p+0x1a);q+=2)out.push({at:E.h(q),offline:E.off(q),word:E.hw(E.r16(q)),mark:q===p?'<<< WRITE':''});return out;}
function clusters(E,writes){const out=[];const a=[...writes].sort((x,y)=>x.at-y.at);for(let i=0;i<a.length;i++){const x=a[i];for(let j=i+1;j<a.length&&a[j].at-x.at<=0x180;j++){const y=a[j];if(x.baseReg!==y.baseReg||x.disp===y.disp)continue;const lo=Math.min(x.at,y.at),hi=Math.max(x.at,y.at),dist=hi-lo;out.push({baseReg:x.baseReg,xAt:x.disp===0x3e?x.at:y.at,yAt:x.disp===0x42?x.at:y.at,distance:dist,lo,hi,xKind:x.disp===0x3e?x.kind:y.kind,yKind:x.disp===0x42?x.kind:y.kind,xSrc:x.disp===0x3e?x.srcReg:y.srcReg,ySrc:x.disp===0x42?x.srcReg:y.srcReg});}}
 return [...new Map(out.map(z=>[z.xAt+'|'+z.yAt+'|'+z.baseReg,z])).values()].sort((a,b)=>a.distance-b.distance||a.lo-b.lo);}
async function run(){stopped=false;await ensure();const E=env();console.log('🌐 WOF global ROM target XY write scan v1 · +0x3E/+0x42');const writes=[];
 for(let p=0;p+8<E.MAX;p+=2){if(stopped)throw new Error('stopped');const a=moveWrite(E,p)||singleWrite(E,p);if(a)writes.push(a);if((p&0x1ffff)===0x1fffe)await sleep(0);}
 const ded=[...new Map(writes.map(x=>[x.at+'|'+x.disp,x])).values()];console.log('=== GLOBAL XY WRITE SITES ===');console.table(ded.map(x=>({at:E.h(x.at),offline:E.off(x.at),field:'0x'+x.disp.toString(16).toUpperCase(),kind:x.kind,baseReg:x.baseReg,srcReg:x.srcReg,op:E.hw(x.op)})).slice(0,240));
 const pairs=clusters(E,ded);console.log('=== GLOBAL XY PAIRED WRITE CLUSTERS ===');console.table(pairs.slice(0,120).map(x=>({xAt:E.h(x.xAt),yAt:E.h(x.yAt),offlineX:E.off(x.xAt),offlineY:E.off(x.yAt),baseReg:x.baseReg,distance:x.distance,xKind:x.xKind,yKind:x.yKind,xSrc:x.xSrc,ySrc:x.ySrc})));
 const top=pairs[0]||null;if(top){console.log('=== TOP GLOBAL X WRITE CONTEXT ===');console.table(ctx(E,top.xAt));console.log('=== TOP GLOBAL Y WRITE CONTEXT ===');console.table(ctx(E,top.yAt));}
 const byBase={};for(const x of ded)byBase[x.baseReg]=(byBase[x.baseReg]||0)+1;
 const verdict={globalWriteSites:ded.length,xWriteSites:ded.filter(x=>x.disp===0x3e).length,yWriteSites:ded.filter(x=>x.disp===0x42).length,pairedClusters:pairs.length,topXAt:top?E.h(top.xAt):'',topYAt:top?E.h(top.yAt):'',topOfflineX:top?E.off(top.xAt):'',topOfflineY:top?E.off(top.yAt):'',topBaseReg:top?.baseReg||'',topDistance:top?.distance??'',topXKind:top?.xKind||'',topYKind:top?.yKind||'',topXSrc:top?.xSrc||'',topYSrc:top?.ySrc||'',baseSummary:Object.entries(byBase).map(([k,v])=>k+':'+v).join(' ')};
 console.log('=== GLOBAL TARGET XY WRITE VERDICT ===');console.table([verdict]);
 if(pairs.length)console.log('🎯 全 ROM 找到同一 A 基址附近同时写 +0x3E/+0x42 的代码簇；下一步验证 top cluster 的真实指令边界/调用来源，并追 xSrc/ySrc。');else if(ded.length)console.warn('⚠️ 全 ROM 有单字段写但没有近距离 X/Y 配对；下一步按共享 helper/caller 组合这些写点。');else console.warn('⚠️ 全 ROM 连直接 d16(An) 写都没有；说明字段写入使用 alias/indexed/MOVEM 或来自非 ROM 执行路径，下一步只能做动态变化→state/action 反推。');
 const out={version:'wof-target-xy-global-write-v1',verdict,writes:ded,pairs};self.__WOF_TARGET_XY_GLOBAL=out;return out;}
self.WOFTARGETXYGLOBAL={version:'wof-target-xy-global-write-v1',run,stop(){stopped=true;}};console.log('✅ WOF global target XY writer scan v1 loaded');console.log('执行 await WOFTARGETXYGLOBAL.run()');
})();