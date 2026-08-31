(async()=>{
'use strict';
const RAW='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/';
const load=async f=>{const r=await fetch(RAW+f+'?x='+Date.now(),{cache:'no-store'});if(!r.ok)throw new Error('fetch failed '+r.status+' '+f);return(0,eval)(await r.text());};
console.log('♻️ WOF resume: D0=20 ATTACK_READY proven; explicit-next Stage2 frontier');
if(!self.__WOF_DISPATCH_INCOMING){await load('wof_dispatch_incoming_edges.js');await WOFDISPIN.run();}
if(!self.__WOF_ROM_LOC_CACHE)throw new Error('ROM cache missing after resume');
const current={
  version:'wof-resume-dispatch-selector-v17',
  selectorSolved:true,
  selectorField:'enemy+0x7E',
  playerIndexValues:'P1=0 / P2=4 / P3=8',
  selectedPointerCache:'enemy+0x6A low16 = BE1C/BEFC/BFDC',
  selectedPlayerActionBridgeConfirmed:true,
  strongestBridge:'0x006834 MOVEA.W 106(A0),A1 -> CMPI.B #4,41(A1) -> BEQ 0x006850 -> read enemy+0x2A -> indexed action JMP',
  d0Provenance:'0x006A10 MOVEQ #16,D0 -> JSR 0x25C8; 0x006A62 MOVEQ #20,D0 -> JSR 0x25C8',
  dispatcherSemantic:'0x25C8 selects type-specific action descriptors; 0x247C consumes descriptor stream. First long is frame/payload end pointer, not code.',
  activeAttackField:'enemy+0x70 U16; active start = 0 -> nonzero, matching prior Future AI.',
  stage1Proof:'Across V2+V3+V4+V5, 12/12 exact D0=20 entries reached active attack across observed types 9,10,16,20,27,33,34. Observed entry-to-active leads now span 39..539ms. D0=20 is the current low-false-positive ATTACK_READY signal.',
  v5Proof:'V5 captured 2/2 exact D0=20 -> active. T16 D0=20 descriptor0x084D9C had explicit next0x084C3A; runtime entered0x084C3A at282ms and active58ms later. T20 D0=20 descriptor0x082B22 had explicit next0x082A4C; runtime entered0x082A4C at520ms and active19ms later.',
  next1CommonSignature:'Both V5 last-pre descriptors were exactly the explicit pointer stored in D0=20.next and had timer1, value30=0x0000FFFF, action2A=6, b2B=4, attack0. This is a strong Stage2 candidate but not yet universal: type35 static D0=20.next=0x817CC continues into a longer startup chain, so validate by type rather than hard-code globally.',
  targetPolicy:'Keep target live from enemy+0x7E/+0x6A because earlier runtime proved retargeting can occur while descriptors play.',
  endToEndStructuralProofConfirmed:true,
  causalFrontier:'For each exact D0=20 watch, parse the type-specific explicit D0=20.next descriptor, detect its live entry, and measure next1->active lead. Count attacks that become active before next1. Decide whether next1 is universal IMMINENT, a per-type IMMINENT signal, or only one branch of the startup model.',
  nextScript:'wof_d020_next1_stage2_runtime_v6.js',
  nextMarker:'=== D0=20 NEXT1 STAGE2 RUNTIME V6 JSON ===',
  note:'Do not restart selector search, Focus Multiroom, 44-edge scan, 0x0080F2, 0x11C26 bridge, or raw-even-address opcode sweeping. Stage1 D0=20 is established; Stage2 must be validated from explicit next descriptors with per-type evidence.'
};
self.__WOF_RESUME_FRONTIER=current;
console.log('=== CURRENT SELECTOR FRONTIER ===');console.table([current]);
console.log('NEXT: validate type-specific D0=20.next descriptor as Stage2 IMMINENT.');
return current;
})().catch(e=>{console.error('WOF_RESUME_ERROR',e);throw e;});