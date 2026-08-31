(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: target/action AI + D0=20 two-stage Future Danger shadow frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v15',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
  dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream. First long is frame/payload end pointer, not code.',
  d0_16Pattern:'Across observed types, D0=16 is a timer=32767 explicit self-loop long-hold descriptor.',
  d0_20Pattern:'Across observed types, D0=20 is a short timed attack-ready/pre-active descriptor. Decision state can continue changing while it plays.',
  activeAttackField:'enemy+0x70 U16; active start convention is 0 -> nonzero, matching prior Future AI.',
  firstLeadTimingProof:'V2 captured 3/3 exact D0=20 entries reaching active with leads 39/161/398ms (types10/33).',
  v3TimingProof:'V3 captured 4/4 exact D0=20 entries reaching active: 3 natural-expire and 1 early-action-preempt. Leads 219/339/340/400ms. T10 timer24 naturally expired at400ms; T9 timer20 naturally expired at339/340ms; one T9 changed action2A 6->0 while timer8 and reached active19ms later.',
  combinedPredictiveEvidence:'Across V2+V3, 7 exact D0=20 watches all reached enemy+0x70 active within 39..400ms. This is strong predictive evidence but still too few samples to claim universal zero false positives.',
  twoStageHypothesis:'Stage1 exact D0=20 entry = ATTACK_READY early warning. Stage2 early action2A transition while still D0=20 and attack==0 = IMMINENT escalation; first observed stage2 lead was19ms. Keep target live from enemy+0x7E/+0x6A because target can switch while descriptor plays.',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'Shadow-validate the two-stage predictor across more live enemy types: measure D0=20 precision/no-active rate, entry-target stability/retargeting, and stage2 action-change -> active lead. If precision remains high, integrate D0=20 as a Future Danger startup source without RAM writes.',
  nextScript:'wof_d020_two_stage_shadow_v4.js',
  nextMarker:'=== D0=20 TWO-STAGE SHADOW V4 JSON ===',
  note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, or raw-even-address opcode sweeping. Do not hard-code timer*16.7ms as attack time because D0=20 can be preempted early.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: two-stage D0=20 ATTACK_READY -> action-preempt IMMINENT shadow validation.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});