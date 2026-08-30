(()=>{
'use strict';
try{ self.WOFDISPREV?.stop?.(); }catch(_){}

const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;

const load=async f=>{
  const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});
  if(!r.ok) throw new Error('fetch failed '+r.status+' '+f);
  return (0,eval)(await r.text());
};

async function ensure(){
  if(!self.__WOF_DISPATCH_EDGE_SELECTOR){
    await load('wof_resume_dispatch_selector.js');
    if(!self.__WOF_DISPATCH_EDGE_SELECTOR) throw new Error('selector frontier unavailable');
  }
  if(!self.__WOF_ROM_LOC_CACHE) await load('wof_rom_focus_inspect.js');
  for(let i=0;i<300&&!self.__WOF_ROM_LOC_CACHE;i++) await sleep(50);
  if(!self.__WOF_ROM_LOC_CACHE) throw new Error('ROM cache unavailable');
}

function env(){
  const MOD=_0x515056,C=self.__WOF_ROM_LOC_CACHE,M=MOD.HEAPU8;
  const base=C.base,SW=!!C.swap16,MAX=Math.min(0x100000,M.length-base),DELTA=C.offlineDelta|0;
  const r8=o=>M[base+(SW?(o^1):o)]>>>0;
  const r16=o=>((r8(o)<<8)|r8(o+1))>>>0;
  const r32=o=>(r8(o)*0x1000000+r8(o+1)*0x10000+r8(o+2)*0x100+r8(o+3))>>>0;
  const s8=v=>v&0x80?v-0x100:v;
  const s16=v=>v&0x8000?v-0x10000:v;
  const h=x=>'0x'+(x>>>0).toString(16).toUpperCase().padStart(6,'0');
  return{MAX,r8,r16,r32,s8,s16,h};
}

function eaWords(m,r,size){
  if(m<=4) return 0;
  if(m===5||m===6) return 1;
  if(m===7){
    if(r===0||r===2||r===3) return 1;
    if(r===1) return 2;
    if(r===4) return size==='L'?2:1;
  }
  return 0;
}

function decode(E,p){
  if(p<0||p+1>=E.MAX) return null;
  const w=E.r16(p),g=w>>>12,m=(w>>3)&7,r=w&7;
  let len=2,kind='OP',writesD0=false,d0Root='',d0Transform='',cmp=false,bcc=false,target=null,fall=true;

  if(w===0x4E75||w===0x4E73||w===0x4E77){
    kind='RET';fall=false;
  }else if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){
    kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';
    len=2+eaWords(m,r,'L')*2;
    fall=kind==='JSR';
    if(m===7&&r===0) target=E.s16(E.r16(p+2))>>>0;
    else if(m===7&&r===1) target=E.r32(p+2);
    else if(m===7&&r===2) target=(p+2+E.s16(E.r16(p+2)))>>>0;
  }else if(g===6){
    const cc=(w>>8)&15,d=w&255;
    len=d===0?4:2;
    const disp=d===0?E.s16(E.r16(p+2)):E.s8(d);
    target=(p+2+disp)>>>0;
    kind=cc===0?'BRA':cc===1?'BSR':'BCC';
    bcc=kind==='BCC';
    fall=kind!=='BRA';
  }else if(g===1||g===2||g===3){
    const size=g===1?'B':g===2?'L':'W',sm=(w>>3)&7,sr=w&7,dm=(w>>6)&7,dr=(w>>9)&7;
    len=2+(eaWords(sm,sr,size)+eaWords(dm,dr,size))*2;
    if(dm===0&&dr===0){
      writesD0=true;
      if(sm===0)d0Root='D'+sr;
      else if(sm===1)d0Root='A'+sr;
      else if(sm===2)d0Root='(A'+sr+')';
      else if(sm===3)d0Root='(A'+sr+')+';
      else if(sm===4)d0Root='-(A'+sr+')';
      else if(sm===5)d0Root=E.s16(E.r16(p+2))+'(A'+sr+')';
      else if(sm===6)d0Root='indexed(A'+sr+')';
      else if(sm===7&&sr===4)d0Root='#IMM';
      else d0Root='EA';
    }
  }else if((w&0xF100)===0x7000){
    kind='MOVEQ';
    if(((w>>9)&7)===0){writesD0=true;d0Root='#'+E.s8(w&255);}
  }else if(g===14){
    const sz=(w>>6)&3;
    if(sz!==3){
      if((w&7)===0){
        writesD0=true;
        const cnt=((w>>9)&7)||8,dir=(w&0x0100)?'L':'R',typ=['AS','LS','ROX','RO'][(w>>3)&3];
        d0Transform=typ+dir+'#'+cnt;
      }
    }else len=2+eaWords(m,r,'W')*2;
  }else if(g===13||g===9||g===8||g===12||g===11){
    const sz=(w>>6)&3,size=sz===2?'L':sz===1?'W':'B';
    len=2+eaWords(m,r,size)*2;
    const dr=(w>>9)&7;
    if(g===11) cmp=true;
    else if(dr===0){
      writesD0=true;
      d0Transform=(g===13?'ADD':g===9?'SUB':g===8?'OR':'AND')+'-D0';
    }
  }else if(g===5){
    const sz=(w>>6)&3;
    if(sz===3&&m===1){len=4;kind='DBCC';bcc=true;}
    else{
      const size=sz===2?'L':sz===1?'W':'B';
      len=2+eaWords(m,r,size)*2;
      if(m===0&&r===0){
        writesD0=true;
        d0Transform=((w&0x0100)?'SUBQ':'ADDQ')+'#'+(((w>>9)&7)||8);
      }
    }
  }else if(g===0){
    const op=(w>>8)&15,sz=(w>>6)&3;
    if([0,2,4,6,10,12].includes(op)&&sz!==3){
      const size=sz===2?'L':sz===1?'W':'B';
      len=2+(size==='L'?4:2)+eaWords(m,r,size)*2;
      if(op===12) cmp=true;
      else if(m===0&&r===0){
        writesD0=true;
        d0Transform=['ORI','','ANDI','','SUBI','','ADDI','','','','EORI'][op]+'-D0';
      }
    }
  }else if(g===4){
    if((w&0xFFF8)===0x4E50)len=4;
    else if((w&0xFB80)===0x4880&&m>=2)len=4+eaWords(m,r,(w&0x40)?'L':'W')*2;
    else if((w&0xF1C0)===0x41C0)len=2+eaWords(m,r,'L')*2;
    else len=2+eaWords(m,r,'W')*2;
  }

  len=Math.max(2,len);
  return{at:p,w,len,next:p+len,kind,writesD0,d0Root,d0Transform,cmp,bcc,target,fall};
}

const PLAYERS=[
  {id:'P1',w:0xBE1C,l:0xFFBE1C},
  {id:'P2',w:0xBEFC,l:0xFFBEFC},
  {id:'P3',w:0xBFDC,l:0xFFBFDC}
];

function insEvidence(E,d){
  const players=[],refs=[],stride=[],ramHi=[];
  for(let q=d.at;q<Math.min(d.next,E.MAX-3);q+=2){
    const w=E.r16(q),l=E.r32(q);
    for(const p of PLAYERS){
      if(w===p.w||l===p.l){players.push(p.id);refs.push(p.id+'@'+E.h(d.at));}
    }
    if(w===0x00E0) stride.push(E.h(d.at));
    if(w===0xFFBE||w===0xFFBF) ramHi.push(E.h(d.at));
  }
  return{players:[...new Set(players)],refs:[...new Set(refs)],stride:[...new Set(stride)],ramHi:[...new Set(ramHi)]};
}

function buildControlMap(E,start,end){
  const map=new Map();
  for(let p=start&~1;p<end&&p<E.MAX-6;p+=2){
    const d=decode(E,p);
    if(!d||d.target==null) continue;
    if(!['BRA','BCC','BSR','JSR','JMP'].includes(d.kind)) continue;
    if(d.target<start||d.target>=end) continue;
    let a=map.get(d.target);
    if(!a){a=[];map.set(d.target,a);}
    a.push(d);
  }
  return map;
}

function prevFall(E,cur,limitStart){
  const out=[];
  for(let p=Math.max(limitStart,cur-10)&~1;p<cur;p+=2){
    const d=decode(E,p);
    if(d&&d.fall&&d.next===cur) out.push(d);
  }
  return out;
}

function stateKey(s){
  return s.cur+'|'+s.d0Root+'|'+s.players.join(',')+'|'+Math.min(s.cmp,2)+'|'+Math.min(s.anchors,2);
}

function addEvidence(E,s,d,viaControl){
  const ev=insEvidence(E,d);
  const players=[...new Set(s.players.concat(ev.players))];
  const refs=[...new Set(s.refs.concat(ev.refs))];
  const stride=[...new Set(s.stride.concat(ev.stride))];
  const ramHi=[...new Set(s.ramHi.concat(ev.ramHi))];
  let d0Root=s.d0Root,d0RootAt=s.d0RootAt,d0Transforms=s.d0Transforms.slice();
  if(!d0Root&&d.writesD0){
    if(d.d0Root){d0Root=d.d0Root;d0RootAt=d.at;}
    else if(d.d0Transform)d0Transforms.push(d.d0Transform+'@'+E.h(d.at));
  }
  const cmp=s.cmp+(d.cmp?1:0),bcc=s.bcc+(d.bcc?1:0),anchors=s.anchors+(viaControl?1:0);
  const score=players.length*300+cmp*45+bcc*22+stride.length*55+ramHi.length*28+(d0Root&&!d0Root.startsWith('#')?70:0)+anchors*18;
  return{
    cur:d.at,steps:s.steps+1,players,refs,stride,ramHi,cmp,bcc,anchors,
    d0Root,d0RootAt,d0Transforms,score,
    path:s.path.length<14?[E.h(d.at)].concat(s.path):s.path
  };
}

function searchEdge(E,row){
  const edgeAt=parseInt(row.at,16);
  const limitStart=Math.max(0,edgeAt-0x1800);
  const ctrlStart=Math.max(0,edgeAt-0x10000);
  const ctrlEnd=Math.min(E.MAX,edgeAt+0x800);
  const controlMap=buildControlMap(E,ctrlStart,ctrlEnd);

  const seed={cur:edgeAt,steps:0,players:[],refs:[],stride:[],ramHi:[],cmp:0,bcc:0,anchors:0,d0Root:'',d0RootAt:'',d0Transforms:[],score:0,path:[E.h(edgeAt)]};
  const q=[seed],seen=new Map(),candidates=[];
  let qi=0,visited=0,maxQueue=0;

  while(qi<q.length&&visited<14000&&!stopped){
    const s=q[qi++];visited++;
    if(q.length-qi>maxQueue)maxQueue=q.length-qi;
    if(s.steps>=110||s.cur<=limitStart) continue;

    const preds=[];
    for(const d of prevFall(E,s.cur,limitStart)) preds.push({d,viaControl:false});
    for(const d of controlMap.get(s.cur)||[]) preds.push({d,viaControl:true});

    for(const x of preds){
      if(x.d.at>=s.cur&&!x.viaControl) continue;
      if(edgeAt-x.d.at>0x1800&&!x.viaControl) continue;
      const ns=addEvidence(E,s,x.d,x.viaControl);
      const k=stateKey(ns);
      const old=seen.get(k);
      if(old!=null&&old>=ns.score) continue;
      seen.set(k,ns.score);
      q.push(ns);

      if(ns.players.length||ns.stride.length||ns.ramHi.length||(ns.cmp>0&&ns.d0Root&&!ns.d0Root.startsWith('#'))){
        candidates.push(ns);
      }
    }
  }

  const uniq=[];
  const sig=new Set();
  for(const s of candidates.sort((a,b)=>b.score-a.score||a.cur-b.cur)){
    const k=s.cur+'|'+s.players.join(',')+'|'+s.cmp+'|'+s.bcc+'|'+s.d0Root+'|'+s.anchors;
    if(sig.has(k))continue;
    sig.add(k);
    uniq.push({
      edgeAt:E.h(edgeAt),at:E.h(s.cur),steps:s.steps,anchors:s.anchors,
      players:s.players.join(','),playerRefs:s.refs.join(' '),stride:s.stride.join(' '),ramHi:s.ramHi.join(' '),
      cmp:s.cmp,bcc:s.bcc,d0Root:s.d0Root,d0RootAt:s.d0RootAt!==''?E.h(s.d0RootAt):'',
      d0Transforms:s.d0Transforms.join(' '),score:s.score,path:s.path.join(' <- ')
    });
    if(uniq.length>=40)break;
  }

  return{edgeAt:E.h(edgeAt),visited,maxQueue,controlTargets:controlMap.size,candidates:uniq};
}

async function run(){
  stopped=false;
  await ensure();
  const E=env(),S=self.__WOF_DISPATCH_EDGE_SELECTOR;
  const interesting=(S.rows||[]).filter(r=>r.cmp>0||(r.d0Root&&!String(r.d0Root).startsWith('#')));
  if(!interesting.length) throw new Error('no interesting dispatcher edges');

  const scans=[];
  for(const row of interesting){
    if(stopped)break;
    scans.push(searchEdge(E,row));
    await sleep(0);
  }

  const all=scans.flatMap(x=>x.candidates);
  all.sort((a,b)=>b.score-a.score||a.at.localeCompare(b.at));
  const strong=all.filter(r=>r.players&&r.cmp>0);
  const tableish=all.filter(r=>r.stride||r.ramHi);
  const d0cmp=all.filter(r=>r.cmp>0&&r.d0Root&&!String(r.d0Root).startsWith('#'));
  const top=strong[0]||tableish[0]||d0cmp[0]||all[0]||null;

  console.log('=== REVERSE CFG EDGE STATS ===');
  console.table(scans.map(x=>({edgeAt:x.edgeAt,visited:x.visited,maxQueue:x.maxQueue,controlTargets:x.controlTargets,candidates:x.candidates.length})));
  console.log('=== REVERSE CFG SELECTOR CANDIDATES (TOP 20) ===');
  console.table(all.slice(0,20));

  const verdict={
    interestingEdges:interesting.length,
    statesVisited:scans.reduce((n,x)=>n+x.visited,0),
    candidates:all.length,
    playerCmpCandidates:strong.length,
    strideOrRamHiCandidates:tableish.length,
    nonImmediateD0CmpCandidates:d0cmp.length,
    topEdgeAt:top?.edgeAt||'',topAt:top?.at||'',topPlayers:top?.players||'',topCmp:top?.cmp??0,
    topBcc:top?.bcc??0,topAnchors:top?.anchors??0,topD0Root:top?.d0Root||'',topStride:top?.stride||'',topRamHi:top?.ramHi||''
  };
  console.log('=== REVERSE CFG SELECTOR VERDICT ===');
  console.table([verdict]);

  if(strong.length) console.log('🎯 多候选 reverse CFG 已出现 player ref + CMP；下一步只围绕 topAt 解真实 selector 条件和目标玩家寄存器。');
  else if(tableish.length) console.log('🎯 reverse CFG 出现 player stride / RAM-high 线索；下一步只围绕 topAt 解共享 player table/index。');
  else if(d0cmp.length) console.log('🎯 reverse CFG 保留了 CMP + non-immediate D0 链；下一步只围绕 topAt 再向上追 D0 来源。');
  else console.warn('⚠️ 反向多边界 CFG 在 0x1800 内仍无 player/table 证据；下一步只扩大这 2 条 edge 的 reverse depth，不扫全 ROM。');

  const out={version:'wof-dispatch-reverse-cfg-selector-v1',verdict,scans,interesting};
  self.__WOF_DISPATCH_REVERSE_SELECTOR=out;
  return out;
}

self.WOFDISPREV={version:'wof-dispatch-reverse-cfg-selector-v1',run,stop(){stopped=true;}};
console.log('✅ WOF dispatcher reverse-CFG selector loaded');
console.log('执行 await WOFDISPREV.run()');
})();
