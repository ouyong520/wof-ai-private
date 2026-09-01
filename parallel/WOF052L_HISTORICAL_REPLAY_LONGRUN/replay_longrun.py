#!/usr/bin/env python3
from pathlib import Path
import argparse, itertools, json, hashlib

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def dedup(cycles):
    seen=set(); out=[]
    for c in cycles:
        k=c["cycleId"]
        if k not in seen:
            seen.add(k); out.append(c)
    return out

def counts(cycles):
    d={}
    for c in dedup(cycles):
        d[c["outcome"]]=d.get(c["outcome"],0)+1
    return d

def run(snapshot):
    m = snapshot["matureSanity"]
    mature=[]
    for x in m:
        s=x["support"]; floor=x["minProspectiveSignals"]
        mature.append({
            "id":x["id"],"type":x["type"],"historicalSupport":s,
            "dropOneSupport":max(0,s-1),"duplicateOneDedupSupport":s,
            "historicalCountResilientToSingleMissing": (s-1)>=floor,
            "prospectiveGateSatisfiedByHistoricalReplay":False,
            "roomLeaveOneOut":"NOT_EVALUABLE_FROM_COMMITTED_SUMMARY",
            "hardMissEstimate":"UNKNOWN_FROM_POSITIVE_SUPPORT_SUMMARY",
            "decision":"KEEP_EXISTING_RESEARCH_CANDIDATE_SEMANTICS"
        })

    t18=snapshot["t18"]; c18=t18["wof051"]
    perm18=0
    for p in itertools.permutations(c18):
        assert counts(p)=={"A4704":1,"A4712":1}
        perm18+=1
    loo18=[]
    for i,c in enumerate(c18):
        cc=c18[:i]+c18[i+1:]
        loo18.append({"removed":c["cycleId"],"remaining":counts(cc)})
    dup18=[]
    for c in c18:
        cc=c18+[dict(c)]
        dup18.append({"duplicated":c["cycleId"],"dedupCounts":counts(cc)})
    jitter=[-40,-20,-10,0,10,20,40]
    jitter_checks=0; order_preserved=0
    for a in jitter:
        for b in jitter:
            l1=max(0,c18[0]["leadMs"]+a); l2=max(0,c18[1]["leadMs"]+b)
            jitter_checks+=1
            order_preserved += int(l1<l2)
    t18_result={
        "permutationsChecked":perm18,
        "baselineOutcomeCounts":counts(c18),
        "wof052AdditionalCandidateCoverage":0,
        "leaveOneCycleOut":loo18,
        "duplicateSampleDedup":dup18,
        "timingJitterDiagnostic":{"offsetsMs":jitter,"combinations":jitter_checks,
                                  "A4704EarlierThanA4712":order_preserved,
                                  "predictorClaimAllowed":False,
                                  "reason":"n=1 per outcome; timing separation is diagnostic only"},
        "orderedWindowSweep":[
            {"feature":"first distinct post-anchor state","status":"NO_COMMITTED_SUPPORT_PATTERN"},
            {"feature":"post-anchor pair","status":"NO_COMMITTED_SUPPORT_PATTERN"},
            {"feature":"post-anchor triple","status":"NO_COMMITTED_SUPPORT_PATTERN"},
            {"feature":"descriptor/body/frameEnd/next progression","status":"NO_COMMITTED_SUPPORT_PATTERN"},
            {"feature":"exact timer progression","status":"NO_COMMITTED_SUPPORT_PATTERN"},
            {"feature":"terminal timer hold","status":"NO_COMMITTED_SUPPORT_PATTERN"},
            {"feature":"timer-normalized progression","status":"NO_COMMITTED_SUPPORT_PATTERN"},
            {"feature":"pre-anchor tail","status":"DEFER_UNLESS_POST_ANCHOR_REMAINS_SHARED"}
        ],
        "verdict":"NOT_READY_NEEDS_NEW_REAL_T18_CANDIDATE_CYCLES",
        "zeroCoverageIsFailure":False
    }

    t23=snapshot["t23"]; c23=t23["cycles"]
    baseline=counts(c23)
    tail=lambda xs: sum(1 for c in dedup(xs) if c.get("a5888Tail3"))
    perm_count=0
    for p in itertools.permutations(c23):
        assert counts(p)==baseline
        assert tail(p)==1
        perm_count+=1
    loo=[]
    for i,c in enumerate(c23):
        cc=c23[:i]+c23[i+1:]
        loo.append({"removed":c["cycleId"],"outcomes":counts(cc),"tail3Support":tail(cc)})
    dup=[]
    for c in c23:
        cc=c23+[dict(c)]
        dup.append({"duplicated":c["cycleId"],"outcomes":counts(cc),"tail3Support":tail(cc)})
    t23_result={
        "permutationsChecked":perm_count,
        "baselineOutcomeCounts":baseline,
        "a5888Tail3Support":tail(c23),
        "leaveOneCycleOut":loo,
        "duplicateSampleDedup":dup,
        "roomCountWithT23":t23["roomCountWithT23"],
        "leaveOneRoomOut":"COLLAPSES_ALL_T23_EVIDENCE_BECAUSE_WOF047_T23_WAS_ONE_ROOM",
        "roomReorder":"AGGREGATE_INVARIANT_BUT_NO_CROSS_ROOM_EVIDENCE",
        "hardMissEstimate":"NOT_PROSPECTIVE; CANNOT_ESTIMATE_FROM_8_DISCOVERY_CYCLES",
        "verdict":"KEEP_RESEARCH_ONLY_MANIFEST_BUT_DISCOVERY_SUPPORT_IS_FRAGILE_1_OF_2_A5888"
    }

    local=snapshot["localStructuralCorpus"]
    plan={
      "priority":"T18 (0x12) BODY4728 ordered discriminator",
      "doNotRequestOwnerNow":True,
      "captureMode":"natural/opportunistic after Recorder/live-proof gate permits; no manual attack hunting",
      "freezeMinimum":{
        "candidateContainingResolvedCyclesByOutcome":{"A4704":2,"A4712":2},
        "baselineAlreadyKnown":{"A4704":1,"A4712":1},
        "minimumAdditionalSuccessfulOutcomeCoverageIf_the_next_cycles_split_ideally":{"A4704":1,"A4712":1},
        "orderedPattern":"shortest exact or TM* tail2/tail3/pair/triple with support>=2 for one outcome and oppositeSupport==0",
        "stability":"targetStable=1.0, sideStable=1.0, retargetFree=1.0 for both outcomes",
        "identity":"World 921031 golden SHA only",
        "safety":"readOnly=true; ramWrites=0; inputInjection=false"
      },
      "durabilityPreference":{
        "rooms":">=2 for repeated winning branch when natural coverage permits",
        "targets":">=2 when natural coverage permits",
        "fallback":"if not achieved, label branch room/target-conditioned; do not claim universal invariance"
      },
      "secondaryT23":{
        "A5888Tail3":"one additional unique A5888 cycle repeating exact/TM* tail3 would raise discovery support 1->2; prefer a different room",
        "A4792_A4920":"do not freeze until a branch-specific ordered predicate repeats in >=2 unique cycles",
        "priorityRelativeToT18":"secondary because T23 A5888 already has a research-only manifest while T18 has no ordered manifest"
      },
      "stopCaptureWhen":"the above bounded counters are met; do not use a generic 1h/2h duration as the evidence target"
    }

    queue=[
      {"id":x["id"],"status":"KEEP_EXISTING_RESEARCH_ONLY","historicalSupport":x["support"],
       "prospectiveProofStillRequired":True} for x in m
    ]
    queue += [
      {"id":"T23_A5888_BODY4936_TAIL3","status":"KEEP_QUEUED_FRAGILE_DISCOVERY_SUPPORT",
       "historicalSupport":1,"knownA5888Cycles":2,"crossRoom":False,"prospectiveProofStillRequired":True},
      {"id":"T18_BODY4728_POST_ANCHOR_SPLIT","status":"NOT_READY",
       "reason":"only 1 A4704 + 1 A4712 anchor cycle and no committed repeated post-anchor discriminator; WOF-052 added 0 target coverage",
       "prospectiveProofStillRequired":True}
    ]

    result={
      "schema":"wof052l-historical-replay-longrun-result-v1",
      "stageId":snapshot["stageId"],
      "browserTypeNormalization":snapshot["browserTypeNormalization"],
      "sourceLimitations":{
        "rawPerFrameReplay":"not reconstructed where only committed summaries/manifests exist",
        "roomLevelMatureCandidateSupport":"not fully enumerated in compiled manifests",
        "localExactAttackLabels":local["exactLocalAttackLabel"],
        "stageSceneWaveLabels":local["stageSceneWaveLabels"],
        "pmDeliveryReassessmentGate":snapshot["guards"]["deliveryReassessmentGate"]
      },
      "workload":{
        "t18OrderPermutations":perm18,
        "t18TimingJitterCombinations":jitter_checks,
        "t23OrderPermutations":perm_count,
        "t23MissingSampleRuns":len(c23),
        "t23DuplicateSampleRuns":len(c23),
        "matureSingleMissingChecks":len(mature),
        "matureDuplicateChecks":len(mature),
        "totalDeterministicChecks":perm18+jitter_checks+perm_count+len(c23)*2+len(mature)*2
      },
      "matureSanity":mature,
      "t18":t18_result,
      "t23":t23_result,
      "candidateQueue":queue,
      "minimalNextCapturePlan":plan,
      "decision":{
        "newDurableOrderedCandidateFound":False,
        "existingResearchCandidatesRemainValid":True,
        "keyAmbiguityNeedsNewRealEvidence":True,
        "reason":"retained Browser-labelled T18 evidence has no repeated ordered discriminator; T23 tail3 has support 1 and all 8 T23 cycles are one room; local structural corpus lacks exact move labels",
        "stopCondition":"WOF052L HISTORICAL REPLAY LONGRUN READY — MINIMAL NEXT CAPTURE PLAN"
      }
    }
    canon=json.dumps(result,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    result["canonicalSha256"]=hashlib.sha256(canon).hexdigest()
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",default="evidence_snapshot.json")
    ap.add_argument("--output",default="REPLAY_MATRIX.json")
    args=ap.parse_args()
    r=run(load(args.snapshot))
    Path(args.output).write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"stopCondition":r["decision"]["stopCondition"],"workload":r["workload"],
                      "sha256":r["canonicalSha256"]},ensure_ascii=False))
if __name__=="__main__":
    main()
