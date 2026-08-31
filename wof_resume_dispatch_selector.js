(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v52',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'D867BA TM6 descriptor family is now production-shadow: WOF-041 10/10 strict within 220ms, A3232/target/side10/10; combine with WOF-040 cross-type T36/T9/T33 evidence. D8811E remains production-shadow: WOF-041 22/22 A3232/target/side,20<=120ms+2 jitter at120.1/120.9ms; next audit horizon135ms. T16 exact B4 remains imminent-danger production-shadow: WOF-041 172/172 <=40ms danger hits,170 A6432+1 A4832+1 A4840, target/side172/172. T20 B0->B255 remains strong coarse A5136 production-shadow-candidate: WOF-041 watcher27/28 within 1100ms tail, while same-cycle miner shows the matching room had14/14 B255->A5136 cycles including one first-lead1190.4ms; next audit horizon1250ms/tail1500ms, still not countdown.',
 wof041:'Valid WOF-041 batch b-281d582f-3a0: 5 joined/5 complete/0 error/0 interrupted, readOnly=true,ramWrites=0. 59937 polls,191524 enemy samples,1166 ACTIVE edges,232 signals,229 strict,2 jitter,0 real-late,1 watcher hard-miss. Aggregate player-count samples [0P1,1P0,2P865,3P1559]; this batch is mainly 2P/3P, while 1P workflow was already proven in WOF-040.',
 t24Discovery:'Old fixed-lag-derived T24 rules again had rawMatch=0/entry=0 despite T24 samples9198,A5440=23,A5424=21. The same-cycle attack-zero miner found new real precursor states in two independent rooms: A5440 candidate S2/A2/B4 BODY7512 FE8AF46 NX8A6D0 V180001 TM3 P6C0, 8+8 cycles, first lead49.0..59.6ms,target/side16/16; A5424 candidate S2/A2/B4 BODY7520 FE8AF6C NX8A6E4 V180001 TM4 P6C0,8+8 cycles,first lead49.5..70.3ms,target/side16/16. These are not the retired BODY5424/5440 fixed-lag signatures.',
 t23State:'T23 A4792 same-cycle mining produced only 4-cycle evidence in one room with long/persistent states and target/side rate0.75, so no T23 prospective promotion yet.',
 collectorState:'WOF-040/WOF-041 dual-mode coordinator is validated: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-042 uses fresh IndexedDB v4.',
 nextExperiment:'WOF-042 embeds WOF-042R. It directly prospectively validates T24 BODY7512/TM3->A5440 and BODY7520/TM4->A5424, promotes D867 status to production-shadow, audits D881 at135ms, extends T20 audit to1250ms/1500ms tail, and continues same-cycle attack-zero mining.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v42.js',
 nextCopyId:'WOF-042',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V42 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not treat fixed-lag fingerprintTop as forward timing proof. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms, D867 220ms, or D881 135ms as causal boundaries. Do not revive retired T24 BODY5424/5440 fixed-lag rules; only the new same-cycle BODY7512/BODY7520 candidates are prospective.'
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});