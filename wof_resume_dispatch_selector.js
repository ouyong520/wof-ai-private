(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v48',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match the expected run.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 selectedPointerCache:'enemy+0x6A supporting only when BE1C/BEFC/BFDC',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 retargetPolicy:'Always use live enemy+0x7E',
 productionState:'T16 exact B4 remains production-shadow with direct LEFT+RIGHT strong coverage. T20 B0->B255 -> A5136 is now production-shadow-candidate after WOF-037 independent forward prospective 6/6 strict, expected attack/target/side all6/6, LEFT1 RIGHT5, lead418.6..680.1ms; classify as coarse early warning, not precise countdown. T33/T34 type-specific TM6 attack3232 remain production-shadow-candidates. T24 exact TM2 rules and T23 B0 rule remain prospective candidates pending coverage.',
 v37Result:'Correct WOF-037: identity matched; readOnly=true;ramWrites=0;120002.3ms/10ms;40039 enemy samples;140 ACTIVE edges. T20 A5136 B0->B255 had6 signals/6 evaluable/6 strict/0 jitter/late/hard miss;6/6 actual attack5136,target6/6,side6/6;lead418.6,458.6,530.1,647.8,670.1,680.1;entry sides LEFT1 RIGHT5. Entry absDx did not explain lead monotonically, so do not derive distance thresholds. T23 rule and two narrow T20 A4792 transition rules had zero entries; no negative rule evidence, but low utility/coverage. Fallback mining showed descriptor-family recurrence: current T9 FE867BA/NX85ECE/V100000/BODY2872/A4/B2/P6C2784 TM6 had3 retrospective ~100ms samples before A3232; T11 FE8811E/NX879E2 same structure had2 ~100ms samples. These mirror historical T33/T34 TM6 candidates and motivate type-agnostic descriptor-family prospective validation.',
 v38Plan:'Forward prospective validator for two type-agnostic exact 3232 descriptor families: D867BA_3232_TM6_120 and D8811E_3232_TM6_120. Signals arm only on live entry into exact TM6 state and output entryTypeCounts to prove or falsify cross-enemy-type generalization. Reconfirm T20 A5136 early-warning candidate and opportunistically retain T16/T23/four T24 exact rules. Fallback terminal/fixed-lag mining remains discovery only.',
 nextScript:'wof_future_danger_descriptor_family_validator_v38.js',
 nextCopyId:'WOF-038',
 nextMarker:'=== WOF FUTURE DANGER DESCRIPTOR FAMILY VALIDATOR V38 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not treat WOF-037 zero-entry T23/T20-4792 rules as failures; they simply lacked entry coverage. Do not treat retrospective fixed-lag samples as forward timing proof. Do not promote descriptor-family rules until WOF-038 prospective evidence. Do not restore broad T16 FAST/MID,broad T30_FAST,absDx130,T16 4840 divergence,or ambiguous T24 TM3/TM4 rules.'
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
