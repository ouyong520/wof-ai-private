(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){
  const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);
  if(good(self._0x515056))return self._0x515056;
  const find=()=>{for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k];}catch(_){continue;}if(good(v))return{k,v};}return null;};
  const until=performance.now()+8000;
  while(performance.now()<until){const hit=find();if(hit){self._0x515056=hit.v;self.__WOF_MODULE_GLOBAL_KEY=hit.k;console.log('✅ WOF WASM module resolved:',hit.k,'→ _0x515056');return hit.v;}await new Promise(r=>setTimeout(r,50));}
  throw new Error('WOF WASM module not found in this execution context. Select the gstyphoon.js Worker after the game is running, then rerun the current script.');
}
await ensureWasmModule();
console.log('♻️ WOF resume: independent-cycle signature validation frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v31',
 selectorSolved:true,
 selectorField:'enemy+0x7E',
 playerIndexValues:'P1=0 / P2=4 / P3=8',
 selectedPointerCacheCorrection:'enemy+0x6A is supporting selected-player cache only when BE1C/BEFC/BFDC; +0x7E is authoritative target identity.',
 moduleResolution:'Room changes may expose the same Emscripten Module under a different obfuscated global. Resume now scans the current Worker for the HEAPU8/HEAPU32 module and aliases it to _0x515056 before loading probes.',
 d0Provenance:'0x006A62 MOVEQ #20,D0 -> JSR 0x25C8; 0x25C8 selects type descriptor and 0x247C consumes it.',
 activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero.',
 xyFields:'object +4/+8 are confirmed X/Y 16.16 fixed-point. Z is still not confirmed.',
 v18Totals:'V18 captured6764 prospective signature watches,269 ACTIVE edges,241 coarse groups,412 descriptor groups and1573 fine groups in120s. All269 ACTIVE edges had valid live targets.',
 v18Breakthrough:'Several pre-active signatures were extremely predictive inside the room. T16 BODY4856 descriptor FE851AE/NX84C44/VFFFF had multiple state/action variants with observed p100=1, large exposure counts and mostly attack6432; e.g. S0/A4/B2 n57 p100=1 attack6432 purity0.842, S0/A4/B4 n42 p100=1 purity0.857, S2/A4/B4 n26 p100=1 purity1, S2/A0/B0 n16 p100=1 purity1. Target retention was ~0.98-1 and side stability1 in these samples.',
 v18MidSignature:'T16 S2/A4/B2 BODY4856 descriptor FE85240/NX84C3A/V100000 had n28 descriptor exposures, p100=0 but p250=1, attack6432 purity1, targetSame1 and sideStable1; its observed leads were159..222ms. Fine timer substates move progressively closer to ACTIVE.',
 v18T7:'T7 S0/A6/B4 BODY1800 descriptor FE81C5E/NX817FE/V0 had7/7 <=250ms with leads79..220, target/side stable1 and attack family2528/2536. FE81CA4/NX81808/V0 had6/6 <=250ms and5/6 <=100ms, same attack family.',
 v18T30Candidate:'A coarse T30 S0/A0/B0 BODY1800 signature had6/6 <=100ms with leads20..21ms and mostly attack2528, despite global T30 D0 entry being unreliable. Treat this only as a branch candidate until independent-cycle/room validation.',
 v18Geometry:'Fresh ACTIVE clusters were large enough to show useful attack-family geometry but still not hitboxes. T16 attack6432 n135 had absDx P90=292/P95=317 and absDy P90=14/P95=17; target-side purity0.978. T7 attack2528 n28 had absDx P90=247/P95=250 and absDy P90/P95=8. These are empirical ACTIVE-start distributions.',
 v18CountCaveat:'V18 watch counts are state-entry observations, not guaranteed independent attack episodes. Multiple signature transitions may resolve to the same eventual ACTIVE edge, so raw n57/n42/etc must not be treated as57/42 independent attacks. V19 fixes this by allowing at most one signal per rule/slot/attack-cycle.',
 currentTimingRules:'Legacy type rules remain shadow-only: T9/T10/T33 ENTRY<=500, T13 ENTRY<=250 provisional, T21 EXIT<=250 provisional. T30 type-wide <=500 remains removed. New branch candidates can supersede type timing only after independent validation.',
 retargetPolicy:'Always use live enemy+0x7E; never freeze target or side.',
 geometryFrontier:'First validate candidate branch rules with independent-cycle deduplication. For hits, attach resulting attack family and branch-conditioned ACTIVE geometry. Only after cross-room precision is high should these feed production Danger Map and Safe Path.',
 endToEndStructuralProofConfirmed:true,
 causalFrontier:'Run V19 independent-cycle validator for T16 fast100, T16 mid250, two T7 250ms descriptors, and T30 fast100 coarse candidate. Do not promote V18 raw exposure counts directly.',
 nextScript:'wof_future_danger_rule_validator_v19.js',
 nextMarker:'=== FUTURE DANGER RULE VALIDATOR V19 JSON ===',
 note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal-next1 search, universal timer assumptions, exact-start-timer gating, T30 type-wide warning, or call empirical ACTIVE geometry an exact hitbox.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');
console.table([current]);
console.log('NEXT: run V19 independent-cycle candidate-rule validator.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});