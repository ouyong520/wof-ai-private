(()=>{
'use strict';
const VERSION='wof-owner-projection-proof-v1',CHANNEL='wof-owner-projection-proof-v1',G=globalThis,SAMPLE_TARGET=80;
try{G.WOFOWNERPROJECTION?.stop?.();}catch(_){}
const mod=G._0x515056,M=mod?.HEAPU8,R=mod?.HEAPU32?.[0x2e39e4>>>2]>>>0;if(!M||!R)throw new Error('CPS RAM base unavailable');
const PB={P1:0xFFBE1C,P2:0xFFBEFC,P3:0xFFBFDC},ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20;
const B=a=>M[R+((((a-0xFF0000)&0xffff)^1))]>>>0,U16=a=>((B(a)<<8)|B(a+1))>>>0,U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0,S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;},W=v=>v/65536;
const player=n=>{const a=PB[n];return a&&B(a)?{name:n,x:W(S32(a+4)),y:W(S32(a+8)),z:W(S32(a+12))}:null;};
function enemies(){const out=[];for(let i=0;i<SLOTS;i++){const a=ENEMY+i*STRIDE,type=U16(a+0x20);if(type>=47)continue;const frameEnd=U32(a+0x12),next=U32(a+0x2C);if(!frameEnd&&!next)continue;const target7E=U16(a+0x7E);if(![0,4,8].includes(target7E))continue;out.push({slot:i,type,target7E,x:W(S32(a+4)),y:W(S32(a+8)),z:W(S32(a+12))});}return out;}
const START=0,END=0xBE00,STEP=2,N=(END-START)/STEP,last=new Uint16Array(N),minv=new Uint16Array(N),maxv=new Uint16Array(N),changes=new Uint32Array(N),valid=new Uint32Array(N),strong=new Uint32Array(N),follow=new Uint32Array(N),smooth=new Uint32Array(N);minv.fill(0xffff);
let samples=0,activeTicks=0,inactiveTicks=0,prevPX=null,running=true,timer=null,locked=null,started=Date.now(),lastSentAt=0,lastUsableAt=0,pausedReason='WAITING_FOR_ACTIVE_P1';const bc=new BroadcastChannel(CHANNEL),round=(v,n=3)=>Number.isFinite(+v)?+(+v).toFixed(n):null;
function idx(a){const v=typeof a==='string'?parseInt(a,16):+a;return Number.isFinite(v)&&v>=0xFF0000&&v<0xFFBE00&&!((v-0xFF0000)&1)?(v-0xFF0000)/2:null;}
function rows(limit=8){const p=player('P1');if(!p)return[];const out=[];for(let i=0,off=START;i<N;i++,off+=STEP){const ch=changes[i],rng=maxv[i]-minv[i];if(samples<10||rng<4||valid[i]<samples*.55)continue;const vr=valid[i]/samples,sr=strong[i]/samples,fr=ch?follow[i]/ch:0,sm=samples>1?smooth[i]/(samples-1):0,score=vr*4+sr*3+Math.min(1,rng/96)*1.5+Math.min(1,ch/20)*1.2+fr*1.5+sm*.3;out.push({address:'0x'+(0xFF0000+off).toString(16).toUpperCase(),read:'u16be',value:last[i],screenX:round(p.x-last[i],2),range:rng,changes:ch,valid:round(vr),strong:round(sr),follow:round(fr),score:round(score)});}out.sort((a,b)=>b.score-a.score);return out.slice(0,limit);}
function quality(r){
  const a=r[0],b=r[1],gap=a&&b?a.score-b.score:null;
  if(pausedReason)return{ok:false,samples,targetSamples:SAMPLE_TARGET,remainingSamples:Math.max(0,SAMPLE_TARGET-samples),topAddress:a?.address||null,topScore:a?.score??null,scoreGap:round(gap),reason:pausedReason,conditioning:'PAUSED_PLAYER_INACTIVE',continuable:true};
  const ok=!!a&&samples>=SAMPLE_TARGET&&a.range>=8&&a.changes>=5&&a.valid>=.70&&a.strong>=.45&&a.follow>=.55&&(gap==null||gap>=.10);
  const reason=ok?null:!a?'NO_CANDIDATE':samples<SAMPLE_TARGET?'NEED_MORE_SAMPLES':a.range<8?'CAMERA_RANGE_TOO_SMALL':a.changes<5?'CAMERA_TOO_STATIC':a.valid<.70?'SCREEN_X_IMPLAUSIBLE':a.strong<.45?'SCREEN_X_WEAK':a.follow<.55?'CAMERA_FOLLOW_WEAK':'CANDIDATE_AMBIGUOUS';
  const conditioning=ok?'READY':reason==='NEED_MORE_SAMPLES'?'UNDER_TARGET':['CAMERA_RANGE_TOO_SMALL','CAMERA_TOO_STATIC'].includes(reason)?'LOW_CONTRAST_OR_DUPLICATE':reason==='CANDIDATE_AMBIGUOUS'?'AMBIGUOUS_CANDIDATES':reason==='CAMERA_FOLLOW_WEAK'?'WEAK_OR_CONFOUNDED_MOTION':'REUSABLE_PARTIAL';
  return{ok,samples,targetSamples:SAMPLE_TARGET,remainingSamples:Math.max(0,SAMPLE_TARGET-samples),topAddress:a?.address||null,topScore:a?.score??null,scoreGap:round(gap),reason,conditioning,continuable:!ok};
}
function guidance(q){
  const common='已保留当前有效样本；不要重启、不要重新打包、不要重新执行菜单 6。';
  if(q.ok)return{actionZh:'Camera 证据已满足阈值。按画面提示只点击一次 P1 头顶上方希望警告中心出现的位置。',nextCommandZh:'继续当前校准窗口并完成一次点击；无需运行新命令。'};
  if(q.reason==='WAITING_FOR_ACTIVE_P1')return{actionZh:'P1 当前不在活动场景。进入/回到可控制 P1 的房间后继续当前校准。'+common,nextCommandZh:'下一步：让 P1 出现在场景中并保持当前真人验证窗口打开。'};
  if(q.reason==='NEED_MORE_SAMPLES')return{actionZh:`继续正常左右移动并让背景明显滚动；有效样本 ${q.samples}/${q.targetSamples}，还需 ${q.remainingSamples}。`+common,nextCommandZh:'下一步：继续当前游戏中的左右移动；Camera READY 后按画面提示点击一次 P1 头顶。'};
  if(q.reason==='CAMERA_RANGE_TOO_SMALL')return{actionZh:'样本数量已够，但 camera 取值跨度太小。继续向左右更远处移动，让背景产生明显卷屏；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口做更大幅度左右卷屏，不要重新开始校准。'};
  if(q.reason==='CAMERA_TOO_STATIC')return{actionZh:'样本数量已够，但重复/静止样本过多。持续左右走动并经过会卷屏的区域；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口制造连续 camera 变化。'};
  if(q.reason==='CAMERA_FOLLOW_WEAK')return{actionZh:'camera 候选与 P1 运动相关性不足。只做清晰左右移动，暂时避免复杂纵深/跳跃；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口做单一左右卷屏动作。'};
  if(q.reason==='CANDIDATE_AMBIGUOUS')return{actionZh:'出现多个接近的 camera 候选。继续跨更长距离左右卷屏以拉开候选；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口做更长距离左右卷屏。'};
  if(q.reason==='SCREEN_X_IMPLAUSIBLE'||q.reason==='SCREEN_X_WEAK')return{actionZh:'当前样本对屏幕 X 的约束不足。让 P1 在可见区域内左右移动并触发卷屏；旧样本会继续复用。',nextCommandZh:'下一步：继续当前窗口保持 P1 可见并左右卷屏。'};
  return{actionZh:'继续当前校准并保持 P1 可见；现有样本不会丢失。',nextCommandZh:'下一步：继续当前真人验证窗口，不要重新运行工具。'};
}
function lockedCam(){if(!locked)return null;const i=idx(locked);return i==null?null:{address:'0x'+(0xFF0000+i*2).toString(16).toUpperCase(),read:'u16be',value:last[i]};}
function snap(){const top=rows(),q=quality(top);return{schema:CHANNEL,kind:'state',version:VERSION,sentAt:Date.now(),samples,seconds:round((Date.now()-started)/1000,1),players:{P1:player('P1'),P2:player('P2'),P3:player('P3')},enemies:enemies(),cameraTop:top,cameraQuality:q,guidance:guidance(q),sampling:{activeTicks,inactiveTicks,lastUsableAt,pausedReason,retainedSamples:samples,continuable:true},lockedCamera:lockedCam(),safety:{readOnly:true,ramWrites:0,inputInjection:false}};}
function send(){const m=snap();bc.postMessage(m);lastSentAt=m.sentAt;return m;}
function tick(){
  if(!running)return;
  const p=player('P1');
  if(!p){inactiveTicks++;pausedReason='WAITING_FOR_ACTIVE_P1';prevPX=null;send();return;}
  activeTicks++;pausedReason=null;lastUsableAt=Date.now();
  const dpx=prevPX==null?0:p.x-prevPX;
  for(let i=0,off=START;i<N;i++,off+=STEP){const v=U16(0xFF0000+off),old=last[i];if(v<minv[i])minv[i]=v;if(v>maxv[i])maxv[i]=v;if(samples&&v!==old){const dv=v-old;changes[i]++;if(Math.abs(dv)<=8)smooth[i]++;if(Math.abs(dpx)>=.2&&Math.sign(dv)===Math.sign(dpx))follow[i]++;}const sx=p.x-v;if(sx>=-48&&sx<=432)valid[i]++;if(sx>=8&&sx<=376)strong[i]++;last[i]=v;}
  samples++;prevPX=p.x;send();
}
bc.onmessage=e=>{const m=e.data;if(m?.schema!==CHANNEL)return;if(m.kind==='lock-camera'){const i=idx(m.address);if(i!=null){locked='0x'+(0xFF0000+i*2).toString(16).toUpperCase();send();}}else if(m.kind==='unlock-camera'){locked=null;send();}else if(m.kind==='request-state')send();};
timer=setInterval(tick,100);tick();
G.WOFOWNERPROJECTION={version:VERSION,mode:'worker',result:snap,status(){return{running,samples,lastSentAt,locked,sampling:snap().sampling,cameraQuality:snap().cameraQuality,guidance:snap().guidance};},stop(){running=false;if(timer)clearInterval(timer);try{bc.close();}catch(_){}try{delete G.WOFOWNERPROJECTION;}catch(_){}}};
})();
