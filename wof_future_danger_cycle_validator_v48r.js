(async()=>{
'use strict';
const COPY_ID='WOF-048R';
const PROJECT='WOF-AI-PRIVATE';
const VERSION='wof-future-danger-cycle-validator-v48r';
const MARKER='=== WOF FUTURE DANGER CYCLE VALIDATOR V48R JSON ===';
const BASE={copyId:'WOF-047R',project:'WOF-AI-PRIVATE',version:'wof-future-danger-cycle-validator-v47r',marker:'=== WOF FUTURE DANGER CYCLE VALIDATOR V47R JSON ==='};
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_cycle_validator_v47r.js';
console.log(`[${COPY_ID}] ${PROJECT} ${VERSION}`);
let code=await fetch(SRC+'?x='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('WOF-048R base validator fetch '+r.status);return r.text();});
const edgeAnchor="const resolve=(c,s,t)=>{if(!c)return;diag.activeEdges++;";
if(!code.includes(edgeAnchor))throw new Error(`[${COPY_ID}] trace retarget patch anchor not found`);
code=code.replace(edgeAnchor,"const resolve=(c,s,t)=>{if(!c)return;if(c.lastTarget7E!==s.target7E){c.retargets.push({relMs:r1(t-c.startedAt),from7E:c.lastTarget7E,to7E:s.target7E,atActiveEdge:true});c.lastTarget7E=s.target7E;diag.retargets++;}diag.activeEdges++;");
code=code.replace("self.__WOF_V47R_RESULT=base;console.log(MARKER);console.log(JSON.stringify(base,null,2));return base;","self.__WOF_V47R_RESULT=base;return base;");
const base=await(0,eval)(code);
if(!base||base.copyId!==BASE.copyId||base.project!==BASE.project||base.version!==BASE.version||base.expectedMarker!==BASE.marker||base.readOnly!==true||base.ramWrites!==0)throw new Error(`[${COPY_ID}] embedded WOF-047R identity mismatch`);
const family=s=>String(s||'').replace(/\|TM[^|]*/,'|TM*');
const add=(m,k,n=1)=>{if(!k)return;m[k]=(m[k]||0)+n;};
const top=(m,n=40)=>Object.entries(m).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,n).map(([key,count])=>({key,count}));
const summary={totalCycles:0,byAttack:{}};
for(const tr of (base.t23CycleTraces||[])){
  const attack=String(tr.activeAttack??'unknown');
  const s=summary.byAttack[attack]||(summary.byAttack[attack]={cycles:0,startedMidCycle:0,targetStable:0,sideStable:0,finalExact:{},tail2Exact:{},tail3Exact:{},finalFamily:{},tail2Family:{},tail3Family:{},transitions:{},triples:{}});
  s.cycles++;summary.totalCycles++;if(tr.startedMidCycle)s.startedMidCycle++;if(tr.targetStable)s.targetStable++;if(tr.sideStable)s.sideStable++;
  const exact=(tr.states||[]).map(st=>String(st.signature||'')).filter(Boolean);
  const exact1=exact.at(-1)||null,exact2=exact.slice(-2),exact3=exact.slice(-3);
  add(s.finalExact,exact1);if(exact2.length===2)add(s.tail2Exact,exact2.join(' -> '));if(exact3.length===3)add(s.tail3Exact,exact3.join(' -> '));
  const seq=[];
  for(const st of (tr.states||[])){const f=family(st.signature);if(!seq.length||seq[seq.length-1]!==f)seq.push(f);}
  tr.familyTail1=seq.at(-1)||null;tr.familyTail2=seq.slice(-2);tr.familyTail3=seq.slice(-3);
  add(s.finalFamily,tr.familyTail1);if(tr.familyTail2.length===2)add(s.tail2Family,tr.familyTail2.join(' -> '));if(tr.familyTail3.length===3)add(s.tail3Family,tr.familyTail3.join(' -> '));
  for(let i=1;i<seq.length;i++)add(s.transitions,seq[i-1]+' -> '+seq[i]);
  for(let i=2;i<seq.length;i++)add(s.triples,seq[i-2]+' -> '+seq[i-1]+' -> '+seq[i]);
}
for(const s of Object.values(summary.byAttack)){
  s.targetStableRate=s.cycles?+(s.targetStable/s.cycles).toFixed(3):null;
  s.sideStableRate=s.cycles?+(s.sideStable/s.cycles).toFixed(3):null;
  s.finalExactTop=top(s.finalExact);s.tail2ExactTop=top(s.tail2Exact);s.tail3ExactTop=top(s.tail3Exact);
  s.finalFamilyTop=top(s.finalFamily);s.tail2FamilyTop=top(s.tail2Family);s.tail3FamilyTop=top(s.tail3Family);s.transitionTop=top(s.transitions,80);s.tripleTop=top(s.triples,80);
  delete s.finalExact;delete s.tail2Exact;delete s.tail3Exact;delete s.finalFamily;delete s.tail2Family;delete s.tail3Family;delete s.transitions;delete s.triples;
}
base.copyId=COPY_ID;base.project=PROJECT;base.version=VERSION;base.expectedMarker=MARKER;base.readOnly=true;base.ramWrites=0;
base.t23SequenceSummary=summary;
base.model.t23SequencePolicy='WOF-047 proved ordered T23 traces work. WOF-048 keeps those traces, fixes retarget logging when target changes on the same poll as ACTIVE, and summarizes BOTH exact timer-bearing tails and timer-normalized TM* families plus transition/triple frequencies by activeAttack. Keep exact timers because WOF-045 TM5 and WOF-047 TM11/TM12 on the BODY4976/A6/B4 branch may discriminate outcomes. All sequence summaries remain discovery only until prospectively validated.';
self.__WOF_V48R_RESULT=base;
console.log(MARKER);console.log(JSON.stringify(base,null,2));return base;
})().catch(e=>{console.error('[WOF-048R] ERROR',e);throw e;});
