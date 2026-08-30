(()=>{
  'use strict';
  try{self.WOFCAM?.stop?.();}catch(_){}
  const M=_0x515056?.HEAPU8,R=_0x515056?.HEAPU32?.[0x2e39e4>>>2]>>>0;
  if(!M||!R)throw new Error('CPS RAM base unavailable');
  const P1=0xFFBE1C,START=0x0000,END=0xBE00,STEP=2,N=(END-START)/STEP;
  const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))];
  const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
  const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
  const X=()=>S32(P1+4)/65536;
  const valid=new Uint16Array(N),strong=new Uint16Array(N),changes=new Uint16Array(N),follow=new Uint16Array(N),smooth=new Uint16Array(N),last=new Uint16Array(N),minv=new Uint16Array(N),maxv=new Uint16Array(N);
  minv.fill(0xffff);
  let samples=0,prevPx=null,timer=null,running=true,startedAt=Date.now();
  function word(off){return ((M[R+off+1]<<8)|M[R+off])>>>0;}
  function tick(){
    if(!running)return;const px=X();if(!Number.isFinite(px))return;
    for(let i=0,off=START;i<N;i++,off+=STEP){
      const v=word(off),sx=px-v;
      if(sx>=-48&&sx<=432)valid[i]++;
      if(sx>=8&&sx<=376)strong[i]++;
      if(v<minv[i])minv[i]=v;if(v>maxv[i])maxv[i]=v;
      if(samples){const dv=v-last[i],dp=px-prevPx;if(Math.abs(dv)<=24)smooth[i]++;if(dv!==0){changes[i]++;if(Math.abs(dp)>=0.25&&Math.sign(dv)===Math.sign(dp))follow[i]++;}}
      last[i]=v;
    }
    prevPx=px;samples++;
  }
  function result(limit=24){
    const px=X(),rows=[];
    for(let i=0,off=START;i<N;i++,off+=STEP){
      const ch=changes[i],rng=maxv[i]-minv[i];if(samples<10||rng<4||valid[i]<samples*.55)continue;
      const vr=valid[i]/samples,sr=strong[i]/samples,fr=ch?follow[i]/ch:0,sm=samples>1?smooth[i]/(samples-1):0;
      const score=vr*4+sr*3+Math.min(1,rng/96)*1.5+Math.min(1,ch/20)*1.2+fr*1.5+sm*.3;
      rows.push({address:'0x'+(0xFF0000+off).toString(16).toUpperCase(),offset:'0x'+off.toString(16).toUpperCase(),value:last[i],screenX:+(px-last[i]).toFixed(2),range:rng,changes:ch,valid:+vr.toFixed(3),strong:+sr.toFixed(3),follow:+fr.toFixed(3),score:+score.toFixed(3)});
    }
    rows.sort((a,b)=>b.score-a.score);
    const out={version:'camera-ram-correlation-v1',running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),playerX:+px.toFixed(2),top:rows.slice(0,limit)};
    console.table(out.top);return out;
  }
  timer=setInterval(tick,100);tick();
  self.WOFCAM={version:'camera-ram-correlation-v1',result,stop(){running=false;if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF camera probe stopped');},status(){return{running,samples,seconds:+((Date.now()-startedAt)/1000).toFixed(1),playerX:X()}}};
  console.log('✅ WOF camera RAM probe started');
  console.log('🎮 正常左右移动并让画面明显横向滚动 15~20 秒，然后运行 WOFCAM.result()');
})();