(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v53',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'WOF-042 strengthens the production set. D867BA TM6 is production-shadow with 14/14 strict A3232/target/side this batch. D8811E is production-shadow with 6/6 strict within135ms. T20 B0->B255 is promoted to production-shadow-coarse: WOF-042 6/6 strict A5136/target/side at420.6..580.6ms, on top of prior WOF-037/WOF-039/WOF-041 evidence; 1250ms remains only an audit window, not countdown. T16 B4 remains imminent-danger production-shadow:56/56 within40ms+jitter,54 A6432+2 A4832, but two signals retargeted exactly at ACTIVE so entry target is not guaranteed final; always re-read live +0x7E.',
 wof042:'Valid WOF-042 batch b-14ce196a-f24:5 joined/5 complete/0 error/0 interrupted,readOnly=true,ramWrites=0. 59816 polls,190429 enemy samples,1018 ACTIVE edges,93 signals,92 strict,1 jitter,0 late,0 hard miss. Aggregate player-count samples [0P0,1P105,2P1058,3P1264]; all five embedded WOF-042R validations passed.',
 t24State:'T24 BODY7512/TM3 S2 -> A5440 is now production-shadow:11/11 prospective strict, A5440/target/side11/11, lead49.0..58.2ms across2 rooms. T24 BODY7520/TM4 -> A5424 had17 raw samples but zero edge-entry signals; same-cycle miner nevertheless captured S2 six cycles at61.6..71.6ms and S4 five cycles at61.5..71.2ms, all A5424 with target/side stable. This indicates an entry-detector blind spot when the state is already held at first observation, not negative rule evidence. WOF-043 uses once-per-zero-cycle level arming and widens state99 to2/4 for this candidate.',
 t16Retarget:'WOF-042 recorded exactly two T16 B4 retargets in one room: P1->P3 at17.1ms and P1->P2 at20.3ms, both at ACTIVE. Danger timing stayed valid, but targetSame fell54/56 and sideSame55/56. Production consumer must use live enemy+0x7E at decision time, never freeze target at initial warning.',
 t23State:'Old T23 BODY4920/B0 exact rule again had zero raw match despite5116 T23 samples and15 A4792 edges, so it is effectively retired as a forward candidate. Same-cycle miner continues discovery; no repeated high-confidence T23 A4792 precursor is promoted yet.',
 collectorState:'Dual-mode coordinator remains proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-043 uses fresh IndexedDB v5.',
 nextExperiment:'WOF-043 embeds WOF-043R. It promotes T24 BODY7512/TM3 S2->A5440 to production-shadow, directly validates a once-per-zero-cycle level-trigger BODY7520/TM4 state992/4->A5424 rule, keeps D867/D881 production shadows, audits T16 retarget behavior, keeps T20 as production-shadow-coarse, and continues same-cycle mining for T23/other gaps.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v43.js',
 nextCopyId:'WOF-043',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V43 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms,D867220ms,D881135ms as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules.'
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});