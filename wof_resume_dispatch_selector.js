(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v54',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'WOF-043 makes both T24 current-cycle rules production-shadows. T24 BODY7512/TM3 S2 -> A5440:18/18 strict, A5440/target/side18/18,49.4..58.7ms across3 rooms. T24 BODY7520/TM4 state99 2/4 level-trigger -> A5424:21/21 strict,A5424/target/side21/21,60.8..71.5ms across3 rooms, proving the WOF-042 zero-entry issue was an entry-detector blind spot. T20 B0->B255 remains production-shadow-coarse:9/9 strict A5136/target/side,458.6..800.2ms across3 rooms. D867BA remains production-shadow:35/35 strict A3232/target35/35,side34/35 across T9/T33/T36 and all5 rooms. D8811E remains production-shadow:9/9 strict A3232/target/side across T34/T37/T11. T16 B4 remains imminent-danger production-shadow:20/20 strict,all A6432 this batch,target20/20,side19/20; historical non6432 counterexamples still forbid exclusive attack semantics.',
 wof043:'Valid WOF-043 batch b-e6844556-f8b:5 joined/5 complete/0 error/0 interrupted,readOnly=true,ramWrites=0. 59894 polls,182907 enemy samples,889 ACTIVE edges,112 signals,112 strict,0 jitter/late/hard miss,0 retargets. Player-count samples [0P18,1P458,2P1465,3P484]; all five embedded WOF-043R validations passed.',
 t24State:'Both real same-cycle T24 precursors are now production-shadows. BODY7512/TM3 S2 predicts A5440 around49-59ms. BODY7520/TM4 with state99 2/4, armed once per zero->ACTIVE cycle by level observation, predicts A5424 around61-72ms. Retired fixed-lag BODY5424/5440 signatures remain forbidden.',
 t23State:'Old T23 BODY4920/B0 rule is retired: WOF-043 again rawMatch=0 despite6490 T23 samples and9 A4792 edges. Global cyclePrecursorTop can crowd low-frequency types out, so WOF-044 adds per-room cyclePrecursorFocus.T23 and .T18 arrays from the same-cycle attack-zero miner.',
 collectorState:'Dual-mode coordinator remains proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-044 uses fresh IndexedDB v6.',
 nextExperiment:'WOF-044 embeds WOF-044R. It keeps both T24 rules as production-shadows, retires the old T23 rule explicitly, and adds focused same-cycle attack-zero precursor retention for T23 and T18 so new forward candidates can be selected without global-top crowding. Existing T16/T20/D867/D881 production rules continue prospective audit.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v44.js',
 nextCopyId:'WOF-044',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V44 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms,D867220ms,D881135ms as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules.'
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});