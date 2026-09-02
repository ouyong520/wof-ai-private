(function(ROOT,f){const a=f(ROOT);if(typeof module!=='undefined'&&module.exports)module.exports=a;ROOT.WOFAlphaProofAuthorityV2=a;})(typeof self!=='undefined'?self:globalThis,function(ROOT){
'use strict';
const VERSION='WOF_ALPHA_AUTHORITY_V2';
const ROM='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62';
const TRUST_NAME='__WOF_ALPHA_PROOF_AUTHORITY_V2_TRUST_ROOT';
const SIGNER_NAME='__WOF_ALPHA_PROOF_AUTHORITY_V2_SIGNER';
const TRUST_SCHEMA='wof-alpha-proof-authority-trust-root-v2';
const SIGNER_SCHEMA='wof-alpha-proof-authority-signer-v2';
const LIFE_SCHEMA='wof-alpha-proof-lifecycle-authority-v2';
const HEX32=/^[0-9a-f]{32}$/;
const HEX40=/^[0-9a-f]{40}$/;
const HEX64=/^[0-9a-f]{64}$/;
const SOURCES=new Set(['TRUSTED_LAUNCH','ATTESTED_CONTROL_PLANE']);
const finite=v=>typeof v==='number'&&Number.isFinite(v);
const pos=v=>Number.isSafeInteger(v)&&v>0;
const clone=x=>x==null?x:JSON.parse(JSON.stringify(x));
function immutableGlobal(name){const d=Object.getOwnPropertyDescriptor(ROOT,name);if(!d||d.configurable!==false||!Object.prototype.hasOwnProperty.call(d,'value')||d.writable!==false||!d.value||typeof d.value!=='object'||!Object.isFrozen(d.value))return null;return d.value}
function freshWindow(x,nowMs=Date.now()){return finite(x?.issuedAt)&&finite(x?.expiresAt)&&x.issuedAt<=nowMs+5000&&nowMs-x.issuedAt<=15*60*1000&&x.expiresAt>nowMs&&x.expiresAt-x.issuedAt<=30*60*1000}
function validTrust(x,candidateCommit,nowMs=Date.now()){return !!x&&x.schema===TRUST_SCHEMA&&SOURCES.has(x.source)&&typeof x.authorityRootId==='string'&&x.authorityRootId.length>=8&&HEX64.test(x.signerFingerprint)&&HEX40.test(x.candidateCommit)&&x.candidateCommit===candidateCommit&&freshWindow(x,nowMs)}
function trustedRoot(candidateCommit,nowMs=Date.now()){const x=immutableGlobal(TRUST_NAME);return validTrust(x,candidateCommit,nowMs)?x:null}
function validSignerShape(x,candidateCommit,nowMs=Date.now()){return !!x&&x.schema===SIGNER_SCHEMA&&SOURCES.has(x.source)&&HEX64.test(x.signerFingerprint)&&HEX40.test(x.candidateCommit)&&x.candidateCommit===candidateCommit&&pos(x.workerGeneration)&&freshWindow(x,nowMs)&&x.publicKey&&typeof x.publicKey==='object'&&typeof x.sign==='function'&&typeof x.readLifecycleAuthority==='function'}
function signerProvider(candidateCommit,nowMs=Date.now()){const x=immutableGlobal(SIGNER_NAME);return validSignerShape(x,candidateCommit,nowMs)?x:null}
function validAuthority(a){return !!a&&typeof a.session==='string'&&HEX32.test(a.session)&&pos(a.workerGeneration)&&typeof a.runtimeEpoch==='string'&&HEX32.test(a.runtimeEpoch)&&pos(a.pairGeneration)&&typeof a.pairNonce==='string'&&HEX32.test(a.pairNonce)&&a.launcherIdentitySha===ROM&&a.channel==='WOF_ALPHA_'+a.session}
function fromBinding(b,workerGeneration){const a={session:b?.session,workerGeneration,runtimeEpoch:b?.runtimeEpoch,pairGeneration:b?.pairGeneration,pairNonce:b?.pairNonce,launcherIdentitySha:b?.launcherIdentitySha,channel:b?.channel};return validAuthority(a)?Object.freeze(a):null}
function authorityText(a){return validAuthority(a)?[a.session,a.workerGeneration,a.runtimeEpoch,a.pairGeneration,a.pairNonce,a.launcherIdentitySha,a.channel].join('|'):null}
function sameAuthority(a,b){const x=authorityText(a),y=authorityText(b);return !!x&&x===y}
function liveText(proofSessionId,nonce,a){const t=authorityText(a);return typeof proofSessionId==='string'&&proofSessionId.length>=8&&typeof nonce==='string'&&HEX32.test(nonce)&&t?['WOF_ALPHA_DUAL_LIVE_V2',proofSessionId,nonce,t].join('|'):null}
function gapText(w){const t=authorityText(w?.authority);if(!t||typeof w?.proofSessionId!=='string'||typeof w?.requestId!=='string'||typeof w?.transactionId!=='string'||!finite(w?.startedAt)||!finite(w?.endedAt)||!finite(w?.durationMs)||w?.ok!==true)return null;return['WOF_ALPHA_DUAL_GAP_V2',w.proofSessionId,w.requestId,w.transactionId,w.startedAt,w.endedAt,w.durationMs,'1',t].join('|')}
function lifecycleEnvelope(x,a,nowMs=Date.now()){if(!x||x.schema!==LIFE_SCHEMA||!sameAuthority(x.authority,a)||!finite(x.issuedAt)||!finite(x.expiresAt)||x.issuedAt>nowMs+50||nowMs-x.issuedAt>250||x.expiresAt<=nowMs||x.expiresAt-x.issuedAt>500||!x.players||typeof x.players!=='object'||!Array.isArray(x.enemies))return null;return x}
function lifeRecord(x,{present,type,slot}){if(!x||x.present!==present)return null;if(present!==true)return{xPresent:false};if(!pos(x.generation)||typeof x.token!=='string'||!HEX32.test(x.token))return null;if(slot!=null&&x.slot!==slot)return null;if(type!=null&&x.type!==type)return null;return{generation:x.generation,token:x.token,xPresent:true}}
async function fingerprint(publicKey){try{if(!ROOT?.crypto?.subtle||!publicKey||publicKey.type!=='public')return null;const raw=await ROOT.crypto.subtle.exportKey('raw',publicKey),d=await ROOT.crypto.subtle.digest('SHA-256',raw);return[...new Uint8Array(d)].map(v=>v.toString(16).padStart(2,'0')).join('')}catch(_){return null}}
return Object.freeze({VERSION,ROM,TRUST_NAME,SIGNER_NAME,TRUST_SCHEMA,SIGNER_SCHEMA,LIFE_SCHEMA,HEX32,HEX40,HEX64,finite,pos,clone,immutableGlobal,freshWindow,validTrust,trustedRoot,validSignerShape,signerProvider,validAuthority,fromBinding,authorityText,sameAuthority,liveText,gapText,lifecycleEnvelope,lifeRecord,fingerprint});
});
