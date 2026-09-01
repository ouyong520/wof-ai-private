(async()=>{
'use strict';
const RELEASE='wof-alpha-rc1';
const BASE='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/product/alpha/';
const bust=u=>u+(u.includes('?')?'&':'?')+'x='+Date.now();
const getText=async name=>{const r=await fetch(bust(BASE+name),{cache:'no-store'});if(!r.ok)throw new Error(name+' fetch '+r.status);return r.text();};
const isWindow=typeof window!=='undefined'&&typeof document!=='undefined';
if(isWindow){
  try{window.WOFALPHAHUD?.dispose?.();}catch(_){}
  const code=await getText('wof_alpha_hud.js');(0,eval)(code);
  window.WOFALPHA={release:RELEASE,mode:'top-hud',readOnly:true,inputInjection:false};
  console.log('✅ WOF Alpha RC1 HUD loaded. Load the same Alpha loader in the live gstyphoon.js Worker.');
  return window.WOFALPHA;
}
try{self.__WOF_ALPHA_RUNTIME?.stop?.();}catch(_){}
const CHANNEL='wof-alpha-v1',TICK_MS=10;
const bc=new BroadcastChannel(CHANNEL);
const publishDiagnostic=(state,reason,detail)=>{try{bc.postMessage({schema:CHANNEL,kind:'diagnostic',release:RELEASE,state,reason,detail:detail||null,sentAt:Date.now(),warnings:[]});}catch(_){};};
try{
  if(!self.WOFAlphaCore||self.WOFAlphaCore.VERSION!=='wof-alpha-core-rc1'){const code=await getText('wof_alpha_core.js');(0,eval)(code);}
  const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
  let moduleHit=null;
  if(good(self._0x515056))moduleHit={key:'_0x515056',value:self._0x515056};
  if(!moduleHit){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){moduleHit={key:k,value:v};break;}}}
  const MOD=moduleHit?.value||null,M=MOD?.HEAPU8||null,R=MOD?.HEAPU32?.[0x2e39e4>>>2]>>>0;
  const heapOk=!!(M&&R&&R+0x10000<M.length);
  const idx=a=>R+((((a-0xFF0000)&0xffff)^1));
  const B=a=>{const i=idx(a);if(!M||i<0||i>=M.length)throw new Error('RAM read out of range');return M[i]>>>0;};
  let selfIndexes=null;
  if(heapOk){try{selfIndexes=[B(0xFFBE1C+0x7C),B(0xFFBEFC+0x7C),B(0xFFBFDC+0x7C)];}catch(_){selfIndexes=null;}}
  const guard=self.WOFAlphaCore.validateIdentityProbe({moduleOk:!!moduleHit,ramBase:R,ramWithinHeap:heapOk,selfIndexes});
  if(!guard.ok){publishDiagnostic('disabled','unsupported-runtime',guard.reasons.join('; '));self.__WOF_ALPHA_RUNTIME={release:RELEASE,running:false,guard,readOnly:true,ramWrites:0,inputInjection:false,status(){return this;},stop(){try{bc.close();}catch(_){}}};console.error('⛔ WOF Alpha disabled:',guard.reasons.join('; '));return self.__WOF_ALPHA_RUNTIME;}
  const U16=a=>((B(a)<<8)|B(a+1))>>>0;
  const U32=a=>(B(a)*0x1000000+B(a+1)*0x10000+B(a+2)*0x100+B(a+3))>>>0;
  const S32=a=>{const v=U32(a);return v>=0x80000000?v-0x100000000:v;};
  const X=a=>Math.round(S32(a+4)/65536);
  const ENEMY=0xFFC0BC,STRIDE=0xE0,SLOTS=20,PBASE={0:0xFFBE1C,4:0xFFBEFC,8:0xFFBFDC},PN={0:'P1',4:'P2',8:'P3'};
  function snap(slot){
    const a=ENEMY+slot*STRIDE,type=U16(a+0x20);if(type>=47)return null;
    const frameEnd=U32(a+0x12),next=U32(a+0x2C);if(!frameEnd&&!next)return null;
    const target7E=U16(a+0x7E),pb=PBASE[target7E],enemyX=X(a),targetX=pb?X(pb):null;
    return{slot,type,target7E,target:PN[target7E]||null,state99:B(a+0x99),action2A:B(a+0x2A),b2B:B(a+0x2B),body:U16(a+0x6E),attack:U16(a+0x70),frameEnd,next,value30:U32(a+0x30),timer34:U16(a+0x34),payload6C:U16(a+0x6C),enemyX,targetX};
  }
  const engine=self.WOFAlphaCore.createEngine();let running=true,timer=null,lastSentAt=0,lastError=null;
  const send=()=>{
    if(!running)return;
    try{
      const snaps=[];for(let i=0;i<SLOTS;i++){const s=snap(i);if(s)snaps.push(s);}
      const msg=engine.step(snaps,performance.now());msg.release=RELEASE;msg.identity=guard.signature;msg.readOnly=true;msg.ramWrites=0;msg.inputInjection=false;msg.sentAt=Date.now();bc.postMessage(msg);lastSentAt=msg.sentAt;
    }catch(e){lastError=String(e?.stack||e);running=false;if(timer){clearInterval(timer);timer=null;}engine.clearAll();publishDiagnostic('disabled','runtime-exception',lastError);console.error('⛔ WOF Alpha fail-closed runtime exception',e);}
  };
  timer=setInterval(send,TICK_MS);send();
  self.__WOF_ALPHA_RUNTIME={release:RELEASE,coreVersion:self.WOFAlphaCore.VERSION,identity:guard.signature,moduleKey:moduleHit.key,readOnly:true,ramWrites:0,inputInjection:false,get running(){return running;},status(){return{release:RELEASE,running,lastSentAt,lastError,identity:guard.signature,moduleKey:moduleHit.key,readOnly:true,ramWrites:0,inputInjection:false,engine:engine.diagnostics()};},stop(){running=false;if(timer){clearInterval(timer);timer=null;}engine.clearAll();try{bc.close();}catch(_){}}};
  console.log('✅ WOF Alpha RC1 worker active | fail-closed | read-only |',guard.signature);
  return self.__WOF_ALPHA_RUNTIME.status();
}catch(e){publishDiagnostic('disabled','loader-exception',String(e?.stack||e));try{bc.close();}catch(_){}console.error('⛔ WOF Alpha loader failed closed',e);throw e;}
})().catch(e=>console.error('WOF Alpha RC1',e));
