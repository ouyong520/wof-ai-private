(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;console.log('✅ WOF WASM module resolved:',k,'→ _0x515056');return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found in this execution context. Select the live gstyphoon.js Worker after the game is running.');}
await ensureWasmModule();
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v33',
 copyIdPolicy:'Every user-executed probe command now carries a unique WOF-### first-line copy ID. Reject returned data if copyId/project/version/marker do not match the expected run.',
 selectorSolved:true,selectorField:'enemy+0x7E authoritative target identity; 0/4/8=P1/P2/P3',selectedPointerCache:'enemy+0x6A supporting cache only when exactly BE1C/BEFC/BFDC',playerIdentity:'player+0x7C = P1 0 / P2 4 / P3 8',
 d0Provenance:'0x006A62 MOVEQ #20,D0 -> JSR0x25C8; 0x25C8 selects type descriptor and 0x247C consumes data descriptor',activeAttackField:'enemy+0x70 U16 0->nonzero = validated ACTIVE-start convention, not exact damage/hitbox onset',xyFields:'object+4/+8 confirmed X/Y 16.16 fixed; Z unconfirmed',retargetPolicy:'Always use live enemy+0x7E throughout warning/ACTIVE',
 v20Result:'Adaptive validator: T16_FAST_100 fresh independent transitions17/17 <=100ms, attack expected17/17, target/side17/17. T16_MID_250 1/1 at197ms. T30_FAST_100 2/2 at20ms. T7 branch candidates degraded to precision0.5 and0.667 and were dropped.',
 v21Result:'Live rule shadow in another room: T16_FAST_100 63/63 <=100ms precision1.0, targetSame63/63, sideStable63/63. Attack identity was6432 in61/63, with one4832 and one4840, so timing rule is production-quality shadow but attack ID must not be hard-coded. T16_MID_250 14/14 <=250ms, target/side14/14, all6432. T30_FAST_100 6/6 <=100ms, target/side6/6. Combined fresh T30 FAST evidence is8/8 across V20+V21.',
 v21Geometry:'T16_FAST signal absDx median159/P90318, absDy median4/P9020; ACTIVE absDx median159/P90310, absDy median3/P9023. T16_MID ACTIVE P90 about310x12. T30_FAST ACTIVE P90 about296x10. Empirical only, not hitboxes.',
 v21AttackCorrection:'Do not equate T16_FAST with attack6432. Two validated FAST hits ended as attack4832 and attack4840 while timing/target/side remained correct.',
 productionTiming:'T16_FAST_100 => production-shadow IMMINENT <=100ms. T16_MID_250 => provisional-high. T30_FAST_100 => provisional-high. Legacy type-level T30<=500 remains removed. T7 V18 candidates dropped.',
 geometryFrontier:'V22 maintains a live danger-map state for the three branch rules, expires warnings at horizon, updates live target/side from+7E, measures empirical envelope coverage, and splits ACTIVE geometry by actual attack ID. This is the bridge to Safe Path scoring; no empirical envelope is called an exact hitbox.',
 nextScript:'wof_future_danger_map_production_shadow_v22.js',nextCopyId:'WOF-022',nextMarker:'=== WOF FUTURE DANGER MAP PRODUCTION SHADOW V22 JSON ===',
 exclusions:'Do not restart Focus Multiroom, selector/identity proof, pointer-table proof,44-edge scan,0x0080F2,0x11C26, universal next1/timer assumptions, exact-start-timer gate, T30 type-wide warning, or call empirical geometry exact hitboxes.'
};self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});