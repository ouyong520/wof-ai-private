(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v55',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'WOF-044 keeps the production set strong. T20 B0->B255:13/13 strict A5136/target/side,410.5..869.5ms across3 rooms. D867BA:39/39 strict A3232/target/side across T33/T9 and all5 rooms. D8811E:14/14 eventual A3232/target/side;13 within135ms and one clean 209.5ms tail hit, so production-shadow remains valid and 135ms is only an audit horizon. T24 BODY7512/TM3 -> A5440:9 evaluable/9 strict plus1 end-of-run censored signal, all resolved attacks/target/side correct. T24 BODY7520/TM4 level -> A5424:9/9 strict A5424/target/side. T16 B4:47/47 danger timing hits,46 A6432+1 A4832; one P3->P1 retarget at ACTIVE again proves entry target is not final lock.',
 wof044:'Valid WOF-044 batch b-62677eb2-642:5 joined/5 complete/0 error/0 interrupted,readOnly=true,ramWrites=0. 59988 polls,211029 enemy samples,1057 ACTIVE edges,132 base signals,130 strict+1 late+1 censored,0 hard miss. Player-count samples [0P49,1P0,2P1412,3P979]; all five embedded WOF-044R validations passed.',
 t24State:'Both T24 current-cycle rules remain production-shadows. A5440 resolved9/9 strict at49.6..59.9ms; the tenth signal was censored by run end, not a miss. A5424 level trigger9/9 strict at60.0..71.0ms. Retired fixed-lag BODY5424/5440 signatures remain forbidden.',
 d881State:'D8811E TM6 produced14/14 A3232 with target/side14/14. One T34 event reached209.5ms and was classified realLate only because the audit horizon is135ms; tailHitRate stayed1 and this is not negative attack evidence.',
 t23State:'WOF-044 had3810 T23 samples and15 A4792 edges in the only T23 room, but old BODY4920/B0 still rawMatch0. It remains retired. Intended cyclePrecursorFocus export failed: output model text mentions the field but the actual result object has no cyclePrecursorFocus property, so WOF-044 did not deliver focused T23 candidates.',
 t18State:'Global cyclePrecursorTop did preserve two strong T18 same-cycle candidates in one room: S2/A2/B4 BODY7512 FE8BBB2 NX8B290 V180001 TM4 -> A5440,9/9 cycles, first lead60.2..70.5ms,target/side9/9; and BODY7520 FE8BBDE NX8B2A4 TM4 -> A5424,9/9 cycles, first lead60.7..71.1ms,target/side9/9. These are discovery evidence only until WOF-045 direct forward validation.',
 collectorState:'Dual-mode coordinator remains proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-045 uses fresh IndexedDB v7.',
 nextExperiment:'WOF-045 embeds WOF-045R. It fixes focused mining by running an independent parallel same-cycle focus probe and actually exporting cyclePrecursorFocus.T23/T18. It also directly forward-validates the two WOF-044 T18 TM4 candidates with once-per-zero-cycle level triggers. Existing T16/T20/D867/D881/T24 production rules continue audit.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v45.js',
 nextCopyId:'WOF-045',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V45 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms,D867220ms,D881135ms as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules. Do not treat WOF-044 missing cyclePrecursorFocus as absence of T23 precursors; it was an export bug.'
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});