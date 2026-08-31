(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v49',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match the expected run.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 selectedPointerCache:'enemy+0x6A supporting only when BE1C/BEFC/BFDC',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 retargetPolicy:'Always use live enemy+0x7E',
 productionState:'T16 exact B4 remains production-shadow with direct LEFT+RIGHT strong coverage. T20 B0->B255 -> A5136 is production-shadow-candidate after WOF-037 forward prospective6/6; coarse early warning lead418.6..680.1ms, not precise countdown. T33/T34 type-specific TM6 A3232 remain production-shadow-candidates. D867BA/D8811E descriptor-family TM6 rules are pending forward validation. T24 exact TM2 and T23 B0 remain prospective pending coverage.',
 latestEvidence:'WOF-037 correct/read-only:40039 enemy samples,140 ACTIVE edges. T20 A5136 forward6/6 strict, attack/target/side6/6, LEFT1 RIGHT5. Fallback mining also reproduced ~100ms A3232 TM6 structure in T9 FE867BA/NX85ECE (3 samples) and T11 FE8811E/NX879E2 (2 samples), matching historical T33/T34 descriptor structures but still retrospective for these new types.',
 batchPlan:'WOF-039 is the current test. It embeds WOF-038 independently in up to5 room Workers for120s each. Paste the SAME WOF-039 command into 4-5 live gstyphoon.js Worker consoles within a45s join window. Same-origin IndexedDB keeps room sessions separate, records player-count/presence and enemy-type/target context, then one elected Worker prints one merged WOF-039 JSON. A closed room is reported as interrupted instead of corrupting other rooms.',
 scenePolicy:'No authoritative stage/scene RAM field is currently proven; do not invent one. Multiroom output uses roomId plus player presence, enemy-type composition and target distribution as context fingerprints.',
 embeddedValidator:'WOF-038 / wof-future-danger-descriptor-family-validator-v38; validates D867BA_3232_TM6_120, D8811E_3232_TM6_120, T20 A5136 reconfirmation, and opportunistic T16/T23/T24 rules.',
 nextScript:'wof_future_danger_multiroom_batch_v39.js',
 nextCopyId:'WOF-039',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM BATCH V39 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not treat retrospective fixed-lag samples as forward timing proof. Do not mix rooms before per-room validation. Do not invent a stage ID. Do not restore broad T16 FAST/MID,broad T30_FAST,absDx130,T16 4840 divergence,or ambiguous T24 TM3/TM4 rules.'
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});