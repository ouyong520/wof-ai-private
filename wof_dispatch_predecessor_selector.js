(()=>{
'use strict';
try{ self.WOFDISPPRED?.stop?.(); }catch(_){}

const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let stopped=false;

const load=async f=>{
  const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});
  if(!r.ok) throw new Error('fetch failed '+r.status+' '+f);
  return (0,eval)(await r.text());
};

async function ensure(){
  if(!self.__WOF_DISPATCH_INCOMING){
    await load('wof_dispatch_incoming_edges.js');
    await WOFDISPIN.run();
  }
  if(!self.__WOF_DISPATCH_EDGE_SELECTOR){
    await load('wof_dispatch_edge_selector_scan.js');
    await WOFDISPEDGE.run();
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
  const off=x=>h((x-DELTA)>>>0);
  return{MAX,r8,r16,r32,s8,s16,h,off};
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
  let len=2,kind='OP',writesD0=false,d0Root='',d0Transform='',cmp=false,bcc=false,terminal=false,target=null,fall=true;

  if(w===0x4E75||w===0x4E73||w===0x4E77){
    kind='RET';terminal=true;fall=false;
  }else if((w&0xFFC0)===0x4E80||(w&0xFFC0)===0x4EC0){
    kind=(w&0xFFC0)===0x4E80?'JSR':'JMP';
    len=2+eaWords(m,r,'L')*2;
    terminal=kind==='JMP';fall=kind==='JSR';
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
    terminal=kind==='BRA';
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
  return{at:p,w,len,next:p+len,kind,writesD0,d0Root,d0Transform,cmp,bcc,terminal,target,fall};
}

function linearBack(E,at,maxIns=64,maxBytes=0x180){
  let cur=at,rev=[];
  for(let n=0;n<maxIns&&cur>0;n++){
    const c=[];
    for(let p=Math.max(0,cur-10)&~1;p<cur;p+=2){
      const d=decode(E,p);
      if(d&&d.next===cur&&d.fall)c.push(d);
    }
    if(!c.length) break;
    c.sort((a,b)=>b.len-a.len||b.at-a.at);
    const d=c[0];
    rev.push(d);
    cur=d.at;
    if(at-cur>=maxBytes) break;
  }
  return rev.reverse();
}

const PLAYERS=[
  {id:'P1',w:0xBE1C,l:0xFFBE1C},
  {id:'P2',w:0xBEFC,l:0xFFBEFC},
  {id:'P3',w:0xBFDC,l:0xFFBFDC}
];

function evidence(E,chain){
  const players=new Set(),refs=[],stride=[],ramHi=[];
  const cmpAts=[],bccAts=[];
  for(const d of chain){
    if(d.cmp) cmpAts.push(E.h(d.at));
    if(d.bcc) bccAts.push(E.h(d.at));
    for(let q=d.at;q<Math.min(d.next,E.MAX-3);q+=2){
      const w=E.r16(q),l=E.r32(q);
      for(const p of PLAYERS){
        if(w===p.w||l===p.l){players.add(p.id);refs.push(p.id+'@'+E.h(d.at));}
      }
      if(w===0x00E0) stride.push(E.h(d.at));
      if(w===0xFFBE||w===0xFFBF) ramHi.push(E.h(d.at));
    }
  }
  return{
    players:[...players],refs:[...new Set(refs)],
    stride:[...new Set(stride)],ramHi:[...new Set(ramHi)],cmpAts,bccAts
  };
}

function d0Prov(chain){
  let root='',rootAt='',trans=[];
  for(const d of chain){
    if(!d.writesD0) continue;
    if(d.d0Root){root=d.d0Root;rootAt=d.at;trans=[];}
    else if(d.d0Transform) trans.push(d.d0Transform+'@'+d.at.toString(16));
  }
  return{root,rootAt,trans};
}

function localControlPreds(E,targetSet,start,end,excludeSet){
  const out=[];
  for(let p=start&~1;p<end&&p<E.MAX-6;p+=2){
    if(excludeSet.has(p)) continue;
    const d=decode(E,p);
    if(!d||d.target==null) continue;
    if(!targetSet.has(d.target)) continue;
    if(!['BRA','BCC','BSR','JSR','JMP'].includes(d.kind)) continue;
    out.push(d);
  }
  return out;
}

async function run(){
  stopped=false;
  await ensure();
  const E=env(),S=self.__WOF_DISPATCH_EDGE_SELECTOR;
  const interesting=(S.rows||[]).filter(r=>r.cmp>0||(r.d0Root&&!String(r.d0Root).startsWith('#')));
  if(!interesting.length) throw new Error('no interesting dispatcher edges in selector result');

  const edgeRows=[],predRows=[];
  for(const row of interesting){
    if(stopped) break;
    const edgeAt=parseInt(row.at,16);
    const base=linearBack(E,edgeAt,64,0x180);
    const basePlus=base.concat([decode(E,edgeAt)]).filter(Boolean);
    const ev=evidence(E,basePlus),pr=d0Prov(basePlus);
    const chainStart=base.length?base[0].at:edgeAt;
    const targetSet=new Set(basePlus.map(d=>d.at));
    const excludeSet=new Set(basePlus.map(d=>d.at));

    edgeRows.push({
      edgeAt:E.h(edgeAt),target:row.target,chainStart:E.h(chainStart),chainIns:basePlus.length,
      players:ev.players.join(','),playerRefs:ev.refs.join(' '),stride:ev.stride.join(' '),ramHi:ev.ramHi.join(' '),
      cmp:ev.cmpAts.length,cmpAts:ev.cmpAts.join(' '),bcc:ev.bccAts.length,bccAts:ev.bccAts.join(' '),
      d0Root:pr.root,d0RootAt:pr.rootAt!==''?E.h(pr.rootAt):'',d0Transforms:pr.trans.join(' ')
    });

    const scanStart=Math.max(0,chainStart-0x3000);
    const scanEnd=Math.min(E.MAX,edgeAt+0x200);
    const preds=localControlPreds(E,targetSet,scanStart,scanEnd,excludeSet);

    for(const pd of preds){
      const up=linearBack(E,pd.at,72,0x220).concat([pd]);
      const pev=evidence(E,up),ppr=d0Prov(up);
      const nonImm=!!(ppr.root&&!String(ppr.root).startsWith('#'));
      const score=pev.players.length*220+pev.cmpAts.length*35+pev.bccAts.length*18+pev.stride.length*40+pev.ramHi.length*20+(nonImm?55:0);
      predRows.push({
        edgeAt:E.h(edgeAt),edgeTarget:row.target,predAt:E.h(pd.at),predKind:pd.kind,predTarget:E.h(pd.target),
        upstreamStart:up.length?E.h(up[0].at):E.h(pd.at),upIns:up.length,
        players:pev.players.join(','),playerRefs:pev.refs.join(' '),stride:pev.stride.join(' '),ramHi:pev.ramHi.join(' '),
        cmp:pev.cmpAts.length,cmpAts:pev.cmpAts.join(' '),bcc:pev.bccAts.length,bccAts:pev.bccAts.join(' '),
        d0Root:ppr.root,d0RootAt:ppr.rootAt!==''?E.h(ppr.rootAt):'',d0Transforms:ppr.trans.join(' '),score
      });
    }
  }

  const uniq=[];
  const seen=new Set();
  for(const r of predRows.sort((a,b)=>b.score-a.score||a.predAt.localeCompare(b.predAt))){
    const k=r.edgeAt+'|'+r.predAt+'|'+r.predTarget;
    if(seen.has(k)) continue;
    seen.add(k);uniq.push(r);
  }

  console.log('=== INTERESTING EDGE BASE CHAINS ===');
  console.table(edgeRows);
  console.log('=== LOCAL CFG PREDECESSOR CANDIDATES (TOP 16) ===');
  console.table(uniq.slice(0,16));

  const strong=uniq.filter(r=>r.players&&r.cmp>0);
  const tableish=uniq.filter(r=>r.stride||r.ramHi);
  const top=strong[0]||tableish[0]||uniq[0]||null;
  const verdict={
    interestingEdges:interesting.length,
    localPredEdges:uniq.length,
    predsWithPlayerRefs:uniq.filter(r=>r.players).length,
    predsWithCmp:uniq.filter(r=>r.cmp>0).length,
    predsWithPlayerCmp:strong.length,
    predsWithStrideOrRamHi:tableish.length,
    nonImmediateD0:uniq.filter(r=>r.d0Root&&!String(r.d0Root).startsWith('#')).length,
    topPredAt:top?.predAt||'',topEdgeAt:top?.edgeAt||'',topPlayers:top?.players||'',topCmp:top?.cmp??0,
    topStride:top?.stride||'',topRamHi:top?.ramHi||'',topD0Root:top?.d0Root||''
  };

  console.log('=== DISPATCH PREDECESSOR SELECTOR VERDICT ===');
  console.table([verdict]);
  if(strong.length) console.log('🎯 predecessor 层出现 player ref + CMP；下一步只围绕 topPredAt 解 selector 分支和目标玩家寄存器。');
  else if(tableish.length) console.log('🎯 predecessor 层出现 player stride / RAM-high 证据；下一步只围绕 topPredAt 解共享 player table/index。');
  else if(uniq.length) console.warn('⚠️ 已找到局部真实 control predecessors，但这一层仍无 player 证据；下一步只对 top predecessor 再向上扩一层。');
  else console.warn('⚠️ 这 1–2 条 interesting edge 的 ±局部窗口没有 direct control predecessor；下一步只扩大这些 edge 的 predecessor 窗口，不回扫整个 ROM。');

  const out={version:'wof-dispatch-predecessor-selector-v1',verdict,edgeRows,predRows:uniq,interesting};
  self.__WOF_DISPATCH_PRED_SELECTOR=out;
  return out;
}

self.WOFDISPPRED={version:'wof-dispatch-predecessor-selector-v1',run,stop(){stopped=true;}};
console.log('✅ WOF dispatcher predecessor selector loaded');
console.log('执行 await WOFDISPPRED.run()');
})();
