(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: D0=20 ATTACK_READY proven; post-chain Stage2 frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v16',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
  dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream. First long is frame/payload end pointer, not code.',
  activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero, matching prior Future AI.',
  stage1Proof:'Across V2+V3+V4, 10/10 exact D0=20 entries reached active attack; observed leads span 39..400ms across types 9,10,27,33,34. Current evidence supports D0=20 as a low-false-positive ATTACK_READY signal, but sample size is still finite.',
  v4Proof:'V4 captured 3/3 exact entries -> active, no noActive. Leads 201/219/279ms. Entry target matched active target in all 3. No target switch occurred in those watches.',
  stage2Correction:'The old Stage2 hypothesis (early action2A change while still inside D0=20) is too sparse: V4 triggered it 0 times. Type27 showed D0=20 can exit before active: one watch exited at159ms then active at219ms; another exited at20ms while timer still10 then active at201ms. Therefore the stronger Stage2 candidate should be sought in the post-D0=20 descriptor chain, not only action2A changes inside D0=20.',
  targetPolicy:'Keep target live from enemy+0x7E/+0x6A because earlier runtime proved retargeting can occur while a descriptor is already playing.',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'Trace descriptor/state transitions after exact D0=20 entry until enemy+0x70 active. Resolve each transition against type level2 roots D0=0..24 or prove natural chain-next using previous enemy+0x2C. Identify the last pre-active descriptor/state and its lead distribution as a replacement Stage2 IMMINENT signal.',
  nextScript:'wof_d020_postchain_stage2_v5.js',
  nextMarker:'=== D0=20 POSTCHAIN STAGE2 V5 JSON ===',
  note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, or raw-even-address opcode sweeping. D0=20 Stage1 is now the stable frontier; Stage2 must come from post-chain runtime evidence.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: trace post-D0=20 descriptor chain to find a stronger Stage2 before active attack.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});