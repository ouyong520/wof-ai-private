(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v51',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'D8811E TM6 descriptor family is now production-shadow: WOF-040 24/24 strict<=120ms, A3232/target/side 24/24 across T37/T11/T34, P1/P2/P3 and both sides in 3 rooms. D867BA TM6 is production-shadow-candidate with recommended 220ms warning horizon: WOF-040 33/33 A3232/target/side across T36/T9/T33 and 4 rooms; 31<=120ms,1 jitter at121ms,1 clean late at200ms, no hard miss. T16 exact B4 remains production-shadow for imminent danger <=40ms, not exclusive A6432: WOF-040 54/54 timing hits,53 A6432+1 A4832; WOF-039 previously had1 A4840. T20 B0->B255 remains coarse A5136 production-shadow-candidate; WOF-040 had no forward transition entry, so no negative evidence; use 850ms audit horizon because WOF-039 reached780.8ms.',
 wof040:'Valid WOF-040 batch b-f998189b-ff0: 5 joined/5 complete/0 error/0 interrupted, readOnly=true,ramWrites=0. 59991 polls,198105 enemy samples,1002 ACTIVE edges,111 signals,109 strict,1 jitter,1 late,0 hard miss. Multiroom workflow is proven with 3P, pure2P(P2+P3) and pure1P(P2) coverage. Aggregate player-count samples [0P49,1P808,2P538,3P1017].',
 t24Correction:'WOF-040 had strong T24 coverage:6024 samples, A5440=19,A5424=16, yet all four old exact T24 prospective rules had rawMatch=0 and transitionEntry=0. Retrospective fingerprintTop nevertheless reproduced two old TM2 signatures around100ms (6 and5 samples). Therefore those fixed-lag T24 signatures remain retrospective/correlation only and are deprioritized. Next mining must constrain states to enemy+0x70==0 within the same zero->ACTIVE cycle to avoid previous-attack contamination.',
 collectorState:'WOF-040 coordinator workflow is validated: no short join window; 1P/2P/3P rooms accepted; TOP finalization downloads exactly one merged JSON. WOF-041 keeps this dual-mode workflow in a fresh IndexedDB v3 batch.',
 nextExperiment:'WOF-041 embeds WOF-041R. It prospectively rechecks promoted descriptor rules and runs a parallel same-cycle attack-zero precursor miner. cyclePrecursorTop only attributes states actually observed while +0x70==0 in the same cycle that later goes 0->nonzero; this is the next route for T24/T23/general precursor discovery.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v41.js',
 nextCopyId:'WOF-041',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V41 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not treat fixed-lag fingerprintTop as forward timing proof. Do not claim T16 B4 is exclusively A6432. Do not treat T20 850ms or D867 220ms as causal boundaries. Do not revive old T24 fixed-lag TM2/TM3/TM4 as prospective without same-cycle attack-zero evidence.'
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});