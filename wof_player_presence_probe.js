(()=>{
  const M=_0x515056.HEAPU8;
  const R=_0x515056.HEAPU32[0x2e39e4>>>2]>>>0;
  if(!R) throw new Error('CPS RAM pointer unavailable');
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
  const BASE={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC};
  const LEN=0xE0;
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const hex=n=>'0x'+n.toString(16).toUpperCase().padStart(2,'0');

  async function snap(player='P2',label='snap',durationMs=1200,stepMs=40){
    const base=BASE[player];
    if(base==null) throw new Error('player must be P1/P2/P3');
    const samples=[];
    const n=Math.max(5,Math.round(durationMs/stepMs));
    for(let k=0;k<n;k++){
      samples.push(Array.from({length:LEN},(_,i)=>B(base+i)));
      await sleep(stepMs);
    }
    const stat=[];
    for(let off=0;off<LEN;off++){
      const cnt=new Map();
      for(const s of samples)cnt.set(s[off],(cnt.get(s[off])||0)+1);
      let mode=0,best=0;
      for(const [v,c] of cnt)if(c>best){best=c;mode=v;}
      stat.push({off,mode,stability:best/samples.length,unique:cnt.size});
    }
    const key=player+':'+label;
    WOFPRESENCE.snaps[key]={player,label,at:performance.now(),samples: samples.length,stat};
    console.log('📸 presence snapshot',key,'samples',samples.length,'— 请保持这个状态直到采样完成');
    return {key,stable:stat.filter(x=>x.stability>=0.95).length};
  }

  function diff(player='P2',a='left',b='joined',minStability=.95){
    const A=WOFPRESENCE.snaps[player+':'+a],Bv=WOFPRESENCE.snaps[player+':'+b];
    if(!A||!Bv)throw new Error('missing snapshots: '+player+':'+a+' / '+player+':'+b);
    const rows=[];
    for(let i=0;i<LEN;i++){
      const x=A.stat[i],y=Bv.stat[i];
      if(x.stability>=minStability&&y.stability>=minStability&&x.mode!==y.mode){
        rows.push({offset:hex(i),[a]:x.mode,[b]:y.mode,stableA:+x.stability.toFixed(2),stableB:+y.stability.toFixed(2)});
      }
    }
    console.table(rows);
    console.log('🔎 stable changed bytes:',rows.length);
    return rows;
  }

  function peek(player='P2'){
    const base=BASE[player];
    const known={flag:B(base),type:(B(base+0x20)<<8)|B(base+0x21),body:(B(base+0x6E)<<8)|B(base+0x6F),attack:(B(base+0x70)<<8)|B(base+0x71),status82:B(base+0x82),hp83:B(base+0x83)};
    console.log('👤',player,known);
    return known;
  }

  self.WOFPRESENCE={snaps:{},snap,diff,peek};
  console.log('✅ WOF 玩家加入/离开 RAM 探针已加载（只读）');
  console.log('现在P2离开态: await WOFPRESENCE.snap("P2","left")');
  console.log('P2重新加入后: await WOFPRESENCE.snap("P2","joined")');
  console.log('最后比较: WOFPRESENCE.diff("P2","left","joined")');
})();
