(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v57',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'Two WOF-046 batches keep production strong. Combined: T16 B4 225/225 danger tail hits (224 strict+1 jitter),A6432=223+A4840=2,target/side225/225; T20 14/14 strict A5136/target/side at460.8..700.4ms; D867BA16/16 strict A3232/target/side at99.1..119.6ms; D8811E21/21 eventual A3232/target/side with20 strict+1 clean209.5ms late; T24 A5440 28/28 strict, T24 A5424 34/34 strict; T18 A5440 33/33 strict, T18 A5424 33/33 strict.',
 wof046:'BatchA b-65a0db92-24c valid:5 joined/4 complete/1 interrupted/0 error,readOnly=true,ramWrites=0,47998 polls/181961 enemy samples/989 ACTIVE edges/294 signals all strict. BatchB b-b1f1a5a3-92c valid:4/4 complete,0 error/interrupted,48000 polls/168660 samples/958 ACTIVE edges/110 signals=108 strict+1 jitter+1 real-late,0 hard miss. All completed embedded WOF-046R identities passed.',
 t23State:'Old BODY4920/B0 remains retired. The WOF-045 short candidate S0/A6/B4 BODY4976 FE84868 NX83F20 V0 TM5 -> A4792 had rawMatch0/signals0 in both WOF-046 batches: zero coverage, not failure. BatchB still had7379 T23 samples and12 A4792 edges. Focus data shows common T23 single states are attack-ambiguous: S2/A4/B0 BODY0 FE84A98 NX83D14 TM20 appears before A4792/A4920/A5848 and the A4792 long branch had targetSame0/4; S0/A4/B2 BODY4936 FE84060 NX83C60 TM1 appears before both A4792 and A4920. Next step is ordered sequence discrimination.',
 collectorState:'Dual-mode coordinator proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-047 uses fresh IndexedDB v9.',
 nextExperiment:'WOF-047 embeds WOF-047R. It keeps WOF-046 production audits and the prior short T23 candidate audit, while adding t23CycleTraces: up to120 resolved T23 zero->ACTIVE cycles per room, last48 distinct ordered states, first/last lead, target/side evolution, retargets and tail1/tail2/tail3. Sequence traces are discovery only; use them to find transition pairs/triples that discriminate A4792 from A4920/A5848, then build a later prospective validator.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v47.js',
 nextCopyId:'WOF-047',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V47 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms,D867220ms,D881135ms as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules. Do not call WOF-046 short T23 rawMatch0 a failure; it had no coverage. Do not promote current ambiguous T23 single-state fingerprints.',
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});