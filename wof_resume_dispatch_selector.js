(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: D0=20 ATTACK_READY feature; per-type branch-learning frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v18',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  selectedPointerCacheCorrection:'enemy+0x6A is a selected-player pointer cache only when populated with BE1C/BEFC/BFDC. V6 observed transitional/non-player values 0000 and CC1C, so +0x7E is authoritative for target identity; +0x6A is supporting evidence only when valid.',
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
  dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream. First long is frame/payload end pointer, not code.',
  activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero, matching prior Future AI.',
  stage1Evidence:'V2-V5 had 12/12 exact D0=20 watches reach active. V6 added 13 exact: 11 active, 1 retrigger/censored, 1 timeout with no active for at least 1800ms. Combined evidence is 23 active out of 24 evaluable exact watches plus 1 censored retrigger. Therefore D0=20 remains a strong ATTACK_READY feature but is not a universal guaranteed <=1000ms attack signal.',
  v6Next1Falsification:'V6 falsified D0=20.next as a universal IMMINENT Stage2. Of 11 active watches, 9 entered next1 before/at active and 2 became active before next1. next1->active leads were 0,202,360,680,740,741,741,900,979ms; median740ms and only one <=100ms.',
  type24Complexity:'Type24 dominated V6 and shows branch-specific behavior: D0=20 leads ranged 180..1199ms; some paths enter next1/next2 and remain pre-active for 600-900ms, one path attacks before next1, one exact watch timed out, and one watch retriggered into another D0=20. This rules out a single universal descriptor Stage2.',
  retargetProof:'V6 type38 entered D0=20 targeting P1 with +0x6A=0000, then at active start retargeted to P3 while +0x6A became BFDC. Keep target live from enemy+0x7E and do not freeze target at warning entry.',
  futureDangerInterpretation:'Use D0=20 as one predictive feature/ATTACK_READY state with type/state-conditioned time distribution. Build Stage2 from repeated per-type post-D0 runtime branch signatures rather than a universal next1. Retriggers are censored, not false positives; timeouts/no-active within the prediction horizon reduce confidence.',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'Learn per-type post-D0 branch signatures from frameEnd12,nextDesc2C,value30,state99,action2A,b2B and descriptor resolution. For each signature measure active rate and remaining lead buckets <=100/250/500/1000ms. Promote only repeated high-precision short-lead signatures to Stage2 IMMINENT.',
  nextScript:'wof_d020_type_branch_learner_v7.js',
  nextMarker:'=== D0=20 TYPE BRANCH LEARNER V7 JSON ===',
  note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, or raw-even-address opcode sweeping. Do not claim D0=20 or D0=20.next is universally imminent.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: learn per-type post-D0 branch signatures and remaining active lead.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});