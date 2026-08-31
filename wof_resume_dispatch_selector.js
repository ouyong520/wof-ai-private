(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v59',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'WOF-048 one-room audit stayed clean:19/19 strict,0 hard miss. T20 6/6 strict A5136/target/side lead481.0..799.5ms; D867BA11/11 strict A3232/target/side lead99.2..111.3ms across T33/T9; D8811E2/2 strict A3232/target/side lead99.9/109.3ms. T16/T24/T18 had zero coverage only.',
 wof048:'Batch b-bdb16c09-b10 valid:1 joined/1 complete/0 error/0 interrupted,readOnly=true,ramWrites=0,11997 polls/39546 enemy samples/164 ACTIVE edges,pure3P histogram[0,0,0,495]. Embedded WOF-048R identity passed.',
 t23State:'WOF-047 remains the latest positive T23 sequence evidence:8 resolved cycles=A4792 3/A4920 3/A5888 2 and single states are attack-ambiguous. WOF-048 dedicated trace saw t23Samples0,attackZeroStarts0,activeEdges0,resolvedCycles0,t23CycleTraces[],sequenceSummary.totalCycles0. This is coverage absence, not a sequence failure; no promotion.',
 traceInstrumentation:'WOF-048R retains the active-edge retarget logging fix and t23SequenceSummary with timer-normalized TM* final/tail2/tail3 plus transition pair/triple frequency by activeAttack. WOF-048 had no T23 and therefore did not exercise these features.',
 collectorState:'Dual-mode coordinator proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-049 uses fresh IndexedDB v11.',
 nextExperiment:'WOF-049 is a semantic repeat of WOF-048 instrumentation. Main need is coverage: run several rooms in parallel, ideally up to5, to increase probability of repeated T23 A4792/A4920/A5888 sequence families while keeping wall-clock near one 120s collection window. Continue production audits; do not create a new T23 production rule until repeated attack-specific ordered sequence evidence is prospectively testable.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v49.js',
 nextCopyId:'WOF-049',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V49 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms,D867220ms,D881135ms as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules. Zero coverage is not forward failure. Do not promote from sparse T23 traces.',
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});
