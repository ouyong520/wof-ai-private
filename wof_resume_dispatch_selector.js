(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found; select live gstyphoon.js Worker.');}
await ensureWasmModule();if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v56',
 copyIdPolicy:'Reject returned data unless copyId/project/version/marker match expected run; readOnly=true; ramWrites=0.',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target;0/4/8=P1/P2/P3',
 activeAttackField:'enemy+0x70 U16 0->nonzero ACTIVE-start convention, not exact damage/hitbox onset',
 productionState:'WOF-045 is clean:137/137 total signals strict,0 jitter/late/hard miss/censored,0 retargets. T20 B0->B255 remains production-shadow-coarse:10/10 strict A5136/target/side at460.0..1020.1ms. D867BA:41/41 strict A3232/target/side across T9/T33 and all5 rooms. D8811E:14/14 strict A3232/target/side at99.0..109.8ms. T24 BODY7512/TM3 -> A5440:14/14 strict A5440/target/side at49.1..59.4ms. T24 BODY7520/TM4 level -> A5424:15/15 strict A5424/target/side at59.9..71.0ms. T16 B4:23/23 danger timing, all A6432 in this batch; historical non6432/retarget counterexamples remain authoritative.',
 wof045:'Valid WOF-045 batch b-c45e8d2d-d9d:5 joined/5 complete/0 error/0 interrupted,readOnly=true,ramWrites=0. 59994 polls,202612 enemy samples,1025 ACTIVE edges,137 signals/137 strict/0 miss. Player-count samples [0P119,1P42,2P1179,3P1088]. All five embedded WOF-045R validations passed.',
 focusState:'WOF-045 fixed the WOF-044 exporter bug: real cyclePrecursorFocus objects are present. Two T23 rooms emitted populated T23 arrays (up to120 entries); the T18 room emitted populated T18 focus. Empty arrays in rooms without those types are expected.',
 t18State:'The two WOF-044 T18 same-cycle candidates passed direct WOF-045 prospective validation: BODY7512 FE8BBB2 NX8B290 V180001 TM4 -> A5440 =10/10 strict, target/side10/10, lead60.5..70.4ms; BODY7520 FE8BBDE NX8B2A4 V180001 TM4 -> A5424 =10/10 strict,target/side10/10,lead61.5..70.3ms. Combined with WOF-044 9/9 discovery each, both are promoted to production-shadow in WOF-046.',
 t23State:'Old BODY4920/B0 remains retired. Focused same-cycle mining found a new short-lead A4792 branch in one T23 room: S0/A6/B4 BODY4976 FE84868 NX83F20 V0 TM5 P6C0 -> A4792 in4/4 cycles, first lead79.3..89.4ms,target/side4/4. Another T23 room showed an alternate long persistent branch (e.g. S2/A4/B0 BODY0 FE84A98 NX83D14 TM20) with only2 cycles and 1.4..2.9s leads; keep mining it, do not promote yet.',
 collectorState:'Dual-mode coordinator remains proven: Worker=collect, top=finalize/download one merged JSON; no short join window; max5 rooms. WOF-046 uses fresh IndexedDB v8.',
 nextExperiment:'WOF-046 embeds WOF-046R. It promotes both T18 TM4 rules to production-shadow and directly prospectively validates the new T23 BODY4976/A6/B4/TM5 -> A4792 candidate with once-per-zero-cycle level arm, horizon100ms/tail300ms. WOF-045 focused mining remains active for alternate T23 branches; existing T16/T20/D867/D881/T24 rules continue audit.',
 scenePolicy:'No authoritative stage/scene RAM field is proven; room context uses player presence, enemy-type composition and target distribution only.',
 nextScript:'wof_future_danger_multiroom_coordinator_v46.js',
 nextCopyId:'WOF-046',
 nextMarker:'=== WOF FUTURE DANGER MULTIROOM COORDINATOR V46 JSON ===',
 exclusions:'Do not restart selector/identity/player-table/dispatcher/descriptor work. Do not call +0x70 exact hitbox/damage onset. Do not use absDx as causal timing boundary. Do not freeze target from warning entry; re-read +0x7E. Do not claim T16 B4 is exclusively A6432. Do not treat T20 1250ms,D867220ms,D881135ms as causal boundaries. Do not revive retired fixed-lag T24 BODY5424/5440 or old T23 BODY4920/B0 rules. Do not promote the alternate long-lead T23 branch from only2 cycles.',
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT:',current.nextCopyId,current.nextScript);return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});