(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: target/action AI + D0=20 pre-active timing/preemption frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v14',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
  dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream. First long is frame/payload end pointer, not code.',
  d0_16Pattern:'Across observed types, D0=16 is a timer=32767 explicit self-loop long-hold descriptor.',
  d0_20Pattern:'Across observed types, D0=20 is a short timed descriptor leading into the type-specific action chain; type35 historical frames classify this family as pre-active/startup.',
  asyncDecisionExecutionProof:'Target7E/+0x6A/selectedPlayer+0x29/action2A can change while a D0=20 descriptor is already playing. Decision layer and descriptor execution layer are asynchronous.',
  activeAttackField:'enemy+0x70 U16; active start convention is 0 -> nonzero, matching prior Future AI.',
  firstLeadTimingProof:'20s exact-entry capture produced 3/3 D0=20 -> active transitions: T10 startTimer24 lead398ms to attack3232; T33 startTimer20 lead161ms to attack2928; T33 startTimer20 lead39ms to attack2936. min/median/max=39/161/398ms.',
  timingInterpretation:'T10 24 ticks -> 398ms is approximately natural 60fps expiry. T33 20-tick entries reached active at 161ms and39ms, far earlier than nominal ~333ms, proving D0=20 can be preempted/advanced into active before its nominal timer expires. Do not estimate lead as timer*16.7ms without preemption modeling.',
  targetStabilityInFirstLeadSamples:'All first 3 exact lead samples kept P3 from D0=20 entry through active start; no target switch or HP drop occurred inside those watches. Sample size is too small for a general target-stability claim.',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'Collect more exact D0=20 entries while logging the live timer trace to classify natural-expire vs early-action-preempt vs target-switch-preempt. Then use per-type/preemption lead distributions as Future Danger startup timing instead of a fixed timer formula.',
  nextScript:'wof_d020_preempt_timer_runtime_v3.js',
  nextMarker:'=== D0=20 PREEMPT TIMER RUNTIME V3 JSON ===',
  note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, or raw-even-address opcode sweeping. D0=20 is a predictive pre-active/attack-ready window, not a guaranteed fixed countdown.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: classify D0=20 natural expiry vs early preemption using live timer traces.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});