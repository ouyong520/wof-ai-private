(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
async function ensureWasmModule(){const good=v=>!!(v&&v.HEAPU8 instanceof Uint8Array&&v.HEAPU32 instanceof Uint32Array&&v.HEAPU8.buffer===v.HEAPU32.buffer);if(good(self._0x515056))return self._0x515056;const until=performance.now()+8000;while(performance.now()<until){for(const k of Object.getOwnPropertyNames(self)){let v;try{v=self[k]}catch(_){continue}if(good(v)){self._0x515056=v;self.__WOF_MODULE_GLOBAL_KEY=k;console.log('✅ WOF WASM module resolved:',k,'→ _0x515056');return v;}}await new Promise(r=>setTimeout(r,50));}throw new Error('WOF WASM module not found in this execution context. Select the live gstyphoon.js Worker after the game is running.');}
await ensureWasmModule();
console.log('♻️ WOF resume: adaptive validation frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
 version:'wof-resume-dispatch-selector-v32',
 selectorSolved:true,
 selectorField:'enemy+0x7E authoritative target identity; 0/4/8=P1/P2/P3',
 selectedPointerCache:'enemy+0x6A supporting cache only when exactly BE1C/BEFC/BFDC; invalid/transitional values occur',
 playerIdentity:'player+0x7C = P1 0 / P2 4 / P3 8',
 d0Provenance:'0x006A62 MOVEQ #20,D0 -> JSR 0x25C8; 0x25C8 selects type descriptor and 0x247C consumes it. Descriptor is data, not code.',
 activeAttackField:'enemy+0x70 U16; active start convention = 0 -> nonzero. Do not call it exact damage/hitbox onset.',
 xyFields:'object +4/+8 confirmed X/Y 16.16 fixed-point; Z unconfirmed',
 moduleResolution:'Room changes can change the Emscripten Module global. Probes/resume should resolve a HEAPU8/HEAPU32 module in the live gstyphoon.js Worker and alias to _0x515056.',
 v18Breakthrough:'Prospective pre-active signature learner found strong branch-conditioned candidates. T16 BODY4856 FE851AE/NX84C44/VFFFF multiple variants had p100=1 in-room; T16 S2/A4/B2 FE85240/NX84C3A/V100000 had p250=1 and attack6432 purity1. T7 FE81C5E/NX817FE and FE81CA4/NX81808 were p250=1 in-room. T30 S0/A0/B0 BODY1800 was 6/6 <=100ms in-room. V18 counts were correlated state-entry observations, not independent attacks.',
 v19Result:'V19 independent-cycle validator ran correctly for120s: readOnly true, ramWrites0, strict gates true, 6000 polls,19890 enemy samples,133 ACTIVE edges with133 valid live targets, but0 candidate signals. This is NOT negative evidence for the five branch candidates because the room did not expose their exact signatures. ACTIVE clusters show the room was dominated by T27/T30/T33/T34; T30 had attacks but not the T30 S0/A0/B0 BODY1800 candidate transition.',
 v19RoomGeometry:'Fresh ACTIVE examples: T27 A4992 n44 absDx P90=46 absDy P90=1; T27 A5000 n18 absDx P90=9; T30 A2528 n12 absDx P90=191 absDy P90=9; T30 A2536 n4 absDx P90=147 absDy P90=8; T33 A3232 n8 absDx P90=430 absDy P90=55; T33 A5336 n7 absDx P90=430 absDy P90=42; T34 A3232 n9 absDx P90=479 absDy P90=71. These remain empirical ACTIVE-start distributions, not hitboxes.',
 timingRules:'Legacy type-level shadow rules: T9/T10/T33 D0-entry <=500; T13 D0-entry <=250 provisional; T21 D0-exit <=250 provisional. T30 type-wide <=500 removed. T18/T24/T20/T22 are branch-variable. New T16/T7/T30 branch candidates require independent-room/cycle validation before promotion.',
 retargetPolicy:'Always use live enemy+0x7E at warning/ACTIVE; never freeze target or side.',
 v20Plan:'Avoid useless zero-signal rooms. V20 combines opportunistic independent-cycle validation of all five V18 branch candidates with generic structural D0=20 capture for every type seen. It reports typeSamples/rawMatchSamples/transitionEntries so zero branch signals are interpretable, and records per-type D0 leads <=250/500/1000 plus ACTIVE geometry.',
 nextScript:'wof_future_danger_adaptive_validator_v20.js',
 nextMarker:'=== FUTURE DANGER ADAPTIVE VALIDATOR V20 JSON ===',
 exclusions:'Do not restart Focus Multiroom, selector/identity proof, pointer-table proof, 44-edge scan, 0x0080F2, 0x11C26 bridge, universal next1/timer assumptions, exact-start-timer gating, T30 type-wide warning, or call empirical geometry exact hitboxes.'
};
self.__WOF_RESUME_FRONTIER=current;console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);console.log('NEXT: run V20 adaptive branch + D0 validator.');return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});