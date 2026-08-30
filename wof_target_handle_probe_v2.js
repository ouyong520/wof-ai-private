(()=>{
'use strict';
try{self.WOFTARGETHANDLE?.stop?.();}catch(_){}
const MOD=_0x515056,M=MOD?.HEAPU8,R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;
if(!M||!R)throw new Error('CPS RAM unavailable');
const PLAYERS=[{name:'P1',base:0xFFBE1C},{name:'P2',base:0xFFBEFC},{name:'P3',base:0xFFBFDC}],POOL=0xFFC0BC,STRIDE=0xE0,N=20,TICK=40,DURATION=40000;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0;
const U16=a=>((B(a)<<8)|B(a+1))>>>0,U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
const S16=a=>{const v=U16(a);return v&0x8000?v-0x10000:v;},S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;},W=v=>v/65536;
const hx=v=>'0x'+(v>>>0).toString(16).toUpperCase().padStart(4,'0'),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const player=p=>B(p.base)?{name:p.name,base:p.base,lo:p.base&0xffff,x:W(S32(p.base+4)),y:W(S32(p.base+8)),z:W(S32(p.base+12))}:null;
const actor=i=>{const b=POOL+i*STRIDE;if(!B(b))return null;return{slot:i,base:b,type:U16(b+0x20),x:W(S32(b+4)),y:W(S32(b+8)),z:W(S32(b+12))};};
const WORDS=STRIDE/2;
const stat=Array.from({length:WORDS},()=>({samples:0,playerHandleSamples:0,motionN:0,advSum:0,wins:0,losses:0,switches:0,switchMotionN:0,switchAdvSum:0,players:{P1:0,P2:0,P3:0}}));
const H=Array.from({length:N},()=>({last:null,lastHandles:Array(WORDS).fill(null),lastSwitchAt:Array(WORDS).fill(0)}));
const id8A=Array.from({length:STRIDE},()=>({n:0,motionN:0,adv:0,wins:0,players:{P1:0,P2:0,P3:0}}));
const id8B=Array.from({length:STRIDE},()=>({n:0,motionN:0,adv:0,wins:0,players:{P1:0,P2:0,P3:0}}));
let running=true,timer=null,finishTimer=null,samples=0,startedAt=Date.now();
function motionAdv(prev,o,ps,targetName){
  if(!prev)return null;const mx=o.x-prev.x,my=o.y-prev.y,mz=o.z-prev.z,m=Math.hypot(mx,my,mz);if(m<.06)return null;
  const score=p=>{const dx=p.x-o.x,dy=p.y-o.y,dz=p.z-o.z,d=Math.hypot(dx,dy,dz)||1;const align=(mx*dx+my*dy+mz*dz)/(m*d);const prevD=prev.dist?.[p.name]??d,gain=(prevD-d)/Math.max(.06,m);return .72*clamp(align,-1,1)+.28*clamp(gain,-1,1);};
  const vals=Object.fromEntries(ps.map(p=>[p.name,score(p)])),t=vals[targetName];if(t==null)return null;const other=Math.max(...Object.entries(vals).filter(([n])=>n!==targetName).map(([,v])=>v),-1);return{adv:t-other,target:t,other};
}
function tick(){if(!running)return;const ps=PLAYERS.map(player).filter(Boolean),byLo=new Map(ps.map(p=>[p.lo,p.name]));for(let i=0;i<N;i++){
  const o=actor(i),h=H[i];if(!o){H[i]={last:null,lastHandles:Array(WORDS).fill(null),lastSwitchAt:Array(WORDS).fill(0)};continue;}
  const now=Date.now();
  for(let wi=0;wi<WORDS;wi++){
    const off=wi*2,v=U16(o.base+off),name=byLo.get(v),r=stat[wi];r.samples++;
    const prevName=h.lastHandles[wi];
    if(name){r.playerHandleSamples++;r.players[name]++;const ma=motionAdv(h.last,o,ps,name);if(ma){r.motionN++;r.advSum+=ma.adv;if(ma.adv>.05)r.wins++;else if(ma.adv<-.05)r.losses++;if(now-h.lastSwitchAt[wi]<=650){r.switchMotionN++;r.switchAdvSum+=ma.adv;}}}
    if(name&&prevName&&name!==prevName){r.switches++;h.lastSwitchAt[wi]=now;}
    h.lastHandles[wi]=name||null;
  }
  for(let off=0;off<STRIDE;off++){
    const v=B(o.base+off);for(const [arr,mapMode] of [[id8A,0],[id8B,1]]){let name=null;if(mapMode===0&&v<=2)name='P'+(v+1);if(mapMode===1&&v>=1&&v<=3)name='P'+v;if(!name)continue;const r=arr[off];r.n++;r.players[name]++;const ma=motionAdv(h.last,o,ps,name);if(ma){r.motionN++;r.adv+=ma.adv;if(ma.adv>.05)r.wins++;}}
  }
  h.last={x:o.x,y:o.y,z:o.z,dist:Object.fromEntries(ps.map(p=>[p.name,Math.hypot(p.x-o.x,p.y-o.y,p.z-o.z)]))};
 }samples++;}
const rate=(a,b)=>b?a/b:0;
function rankHandles(){const rows=[];for(let wi=0;wi<WORDS;wi++){const r=stat[wi];if(r.playerHandleSamples<20)continue;const occ=rate(r.playerHandleSamples,r.samples),meanAdv=rate(r.advSum,r.motionN),winRate=rate(r.wins,r.motionN),switchAdv=rate(r.switchAdvSum,r.switchMotionN),coverage=Object.values(r.players).filter(n=>n>=5).length;const score=occ*2.2+Math.max(-.5,meanAdv)*3+Math.max(0,winRate-.5)*2+Math.max(-.5,switchAdv)*2+Math.min(r.switches,20)*.025+coverage*.12;rows.push({offset:hx(wi*2),kind:'handle16',occupancy:+occ.toFixed(3),handleSamples:r.playerHandleSamples,motionN:r.motionN,meanAdv:+meanAdv.toFixed(3),winRate:+winRate.toFixed(3),switches:r.switches,switchMotionN:r.switchMotionN,postSwitchAdv:+switchAdv.toFixed(3),P1:r.players.P1,P2:r.players.P2,P3:r.players.P3,score:+score.toFixed(3)});}return rows.sort((a,b)=>b.score-a.score);}
function rankIds(arr,kind){const rows=[];for(let off=0;off<STRIDE;off++){const r=arr[off];if(r.n<20||r.motionN<8)continue;const meanAdv=rate(r.adv,r.motionN),winRate=rate(r.wins,r.motionN),coverage=Object.values(r.players).filter(n=>n>=5).length,score=Math.max(-.5,meanAdv)*3+Math.max(0,winRate-.5)*2+coverage*.1;rows.push({offset:hx(off),kind,samples:r.n,motionN:r.motionN,meanAdv:+meanAdv.toFixed(3),winRate:+winRate.toFixed(3),P1:r.players.P1,P2:r.players.P2,P3:r.players.P3,score:+score.toFixed(3)});}return rows.sort((a,b)=>b.score-a.score);}
function finish(){if(!running)return self.__WOF_TARGET_HANDLE_V2;running=false;if(timer)clearInterval(timer);if(finishTimer)clearTimeout(finishTimer);const handles=rankHandles(),id0=rankIds(id8A,'id8-0based'),id1=rankIds(id8B,'id8-1based'),best=[handles[0],id0[0],id1[0]].filter(Boolean).sort((a,b)=>b.score-a.score)[0];
 console.log('=== HANDLE16 → FUTURE MOTION CANDIDATES ===');console.table(handles.slice(0,24));console.log('=== PLAYER ID BYTE 0/1/2 CANDIDATES ===');console.table(id0.slice(0,20));console.log('=== PLAYER ID BYTE 1/2/3 CANDIDATES ===');console.table(id1.slice(0,20));
 const verdict={seconds:+((Date.now()-startedAt)/1000).toFixed(1),samples,livePlayers:PLAYERS.map(player).filter(Boolean).map(p=>p.name).join(','),handleCandidates:handles.length,id0Candidates:id0.length,id1Candidates:id1.length,topKind:best?.kind||'',topOffset:best?.offset||'',topScore:best?.score??'',topOccupancy:best?.occupancy??'',topMeanAdv:best?.meanAdv??'',topWinRate:best?.winRate??'',topSwitches:best?.switches??'',topPostSwitchAdv:best?.postSwitchAdv??''};console.log('=== HANDLE TARGET VERDICT V2 ===');console.table([verdict]);
 if(handles[0]?.occupancy>=.6&&handles[0]?.motionN>=20&&handles[0]?.meanAdv>.08)console.log('🎯 高置信 handle16：字段大部分时间指向某玩家，而且能预测怪物后续运动。下一步反查该 offset 的 ROM 写入点。');else if(handles.length)console.warn('⚠️ 有高占用 player-handle 字段，但运动预测优势不足；它们可能是碰撞/攻击/owner 引用，而非持续 target。优先比较 0x3A 与 0x6A 的 meanAdv / postSwitchAdv。');else console.warn('⚠️ 没有稳定 player-handle 字段；下一步转 target XY/短期 action target 写入时序。');
 const out={version:'wof-target-handle-v2',verdict,handles,id0,id1};self.__WOF_TARGET_HANDLE_V2=out;return out;}
timer=setInterval(tick,TICK);tick();finishTimer=setTimeout(finish,DURATION);self.WOFTARGETHANDLE={version:'wof-target-handle-v2',finish,stop(){if(!running)return;if(timer)clearInterval(timer);if(finishTimer)clearTimeout(finishTimer);running=false;console.log('⛔ handle target probe stopped');},status(){return{running,seconds:+((Date.now()-startedAt)/1000).toFixed(1),samples}}};
console.log('✅ WOF target handle probe v2 started · 40s auto-report');console.log('让怪在 P1/P2/P3 之间多次换追击对象；40 秒后自动输出 HANDLE TARGET VERDICT V2');
})();