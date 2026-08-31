(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: target/action AI + descriptor startup + lead-to-active frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v13',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  action68Exact:'action2A=0 -> 0x006862; action2A=2 -> 0x006904',
  d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
  dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream. First long is frame/payload end pointer, not code.',
  d0_16Pattern:'Across observed types 18/19/31/12, D0=16 descriptor is timer=32767 with explicit self-loop; same long-hold pattern as type35.',
  d0_20Pattern:'Across observed types 18/19/31/12, D0=20 descriptor is short timer (12/10/4/10) with explicit next into each type main descriptor chain. Type35 D0=20 is timer16 then startup/pre-active chain.',
  allTypeRuntimeProof:'Latest 15s all-type capture observed types 12,18,19,31; exact D0=20 fingerprints were seen live. D0=16 was not seen in that window.',
  asyncDecisionExecutionProof:'Type19 live event: at t=10281ms D0=20 descriptor active with target=P3, selectedPlayer29=0, action2A=14; at t=10301ms same D0=20 descriptor still active while target switched to P1, +0x6A BFDC->BE1C, selectedPlayer29 became4 and action2A became2. Therefore target/action AI can update while descriptor animation/execution is already playing; do not model decision and descriptor as one synchronous chain.',
  activeAttackField:'enemy+0x70 U16. Prior Future AI defines active attack start as transition attack 0 -> nonzero.',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'Measure exact D0=20 descriptor entry -> enemy+0x70 0->nonzero lead time, while tracking target7E/+0x6A/selectedPlayer+0x29/action2A and player HP. This produces the real Future Danger startup lead and verifies which target is current at active start.',
  nextScript:'wof_d020_to_active_lead_runtime_v2.js',
  nextMarker:'=== D0=20 TO ACTIVE LEAD RUNTIME V2 JSON ===',
  note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, or raw-even-address opcode sweeping. Do not treat descriptor pointers or frameEnd pointers as executable code.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: exact D0=20 startup entry -> active attack (+0x70) lead timing.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});