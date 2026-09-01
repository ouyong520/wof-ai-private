#!/usr/bin/env python3
"""SEQMINER v2 — WinKawaks-local ordered enemy sequence miner."""
import argparse, glob, gzip, json, os
from collections import Counter, defaultdict

STRIDE=0xE0; PLAYERS=3; ENEMIES=20; BLOCK=STRIDE*(PLAYERS+ENEMIES)
FLAG_MASK=0x001C0000
FIELDS={
 "type":(0x24,1),"pulse28":(0x28,1),"action2d":(0x2D,1),"state2e":(0x2E,1),
 "cursor":(0x2F,4),"timer34":(0x34,1),"mode35":(0x35,1),"gate37":(0x37,1),
 "assoc_ptr":(0x3D,2),"fine6c":(0x6C,1),"target":(0x6D,2),"fine70":(0x70,1),
 "phase72":(0x72,1),"coarse73":(0x73,1),"coarse77":(0x77,1),"flag99":(0x99,1),
 "profile_b0":(0xB0,1),"profile_b4":(0xB4,1),"profile_b6":(0xB6,1),
 "walk_b9":(0xB9,1),"walk_timer_bb":(0xBB,1),"assoc_c6":(0xC6,1),"sync_cc":(0xCC,1)
}
CORE=("type","action2d","state2e","logical_cursor","cursor_flags","mode35","gate37",
      "fine6c","fine70","phase72","coarse73","coarse77")
CTX=("target","assoc_ptr","assoc_c6","split_ref","sync_cc","profile_b0","profile_b4",
     "profile_b6","pulse28","flag99","walk_b9","walk_timer_bb")

def u(buf,off,w,signed=False): return int.from_bytes(buf[off:off+w],"big",signed=signed)
def sgn(v): return json.dumps(v,separators=(",",":"),ensure_ascii=False)

def rows(path):
    op=gzip.open if path.endswith(".gz") else open
    with op(path,"rt",encoding="utf-8",errors="replace") as f:
        for line in f:
            line=line.strip()
            if line: yield json.loads(line)

def rawblock(o):
    if isinstance(o,dict) and isinstance(o.get("rawBlockHex"),str):
        try:
            b=bytes.fromhex(o["rawBlockHex"].strip())
            if len(b)>=BLOCK: return b[:BLOCK]
        except ValueError: pass
    stack=[o]
    while stack:
        x=stack.pop()
        if isinstance(x,dict):
            for k,v in x.items():
                if isinstance(v,str) and any(q in k.lower() for q in ("raw","block","bytes","data")):
                    try:
                        b=bytes.fromhex(v.strip())
                        if len(b)>=BLOCK: return b[:BLOCK]
                    except ValueError: pass
                elif isinstance(v,(dict,list)): stack.append(v)
        elif isinstance(x,list): stack.extend(x)
    return None

def frame_id(o,i):
    for k in ("sequence","frame","frameIndex","frame_index","seq","sampleIndex"):
        if isinstance(o,dict) and isinstance(o.get(k),(int,float)): return int(o[k])
    return i

def state(e):
    d={n:u(e,o,w) for n,(o,w) in FIELDS.items()}
    d["logical_cursor"]=d["cursor"] & ~FLAG_MASK
    d["cursor_flags"]=d["cursor"] & FLAG_MASK
    # Proven EFIELD split encoding: high byte +0x6F, low byte +0x68.
    d["split_ref"]=(e[0x6F]<<8)|e[0x68]
    d["x"]=u(e,0x07,4,True); d["y"]=u(e,0x0B,4,True)
    return d

def core(st): return tuple(st[n] for n in CORE)
def context(st): return core(st)+tuple(st[n] for n in CTX)
def guard(st): return (st["type"],st["profile_b4"],st["profile_b6"])

def timer_bucket(delta):
    if delta<=0:return "0"
    if delta==1:return "1"
    if delta==2:return "2"
    if delta<=5:return "3-5"
    if delta<=10:return "6-10"
    return "11+"

def hold_bucket(n):
    if n<=0:return "0"
    if n==1:return "1"
    if n<=3:return "2-3"
    if n<=9:return "4-9"
    if n<=29:return "10-29"
    return "30+"

def new_distinct(fi,st):
    return {"frameStart":fi,"frameEnd":fi,"dwellFrames":1,
            "timerStart":st["timer34"],"timerEnd":st["timer34"],
            "timerMin":st["timer34"],"timerMax":st["timer34"],
            "timer1Frames":int(st["timer34"]==1),
            "terminalTimer1Frames":int(st["timer34"]==1),**st}

def extend_distinct(x,fi,st):
    x["frameEnd"]=fi; x["dwellFrames"]=max(1,fi-x["frameStart"]+1)
    x["timerEnd"]=st["timer34"]; x["timerMin"]=min(x["timerMin"],st["timer34"])
    x["timerMax"]=max(x["timerMax"],st["timer34"])
    if st["timer34"]==1:
        x["timer1Frames"]+=1; x["terminalTimer1Frames"]+=1
    else: x["terminalTimer1Frames"]=0

def scene_meta(o,path):
    for k in ("scene","sceneId","room","wave","stage"):
        if isinstance(o,dict) and o.get(k) is not None: return str(o[k]),"explicit"
    return os.path.basename(path),"capture-fallback"

def event_value(e,st,attack_offset,attack_width,endian):
    if not st["type"]: return 0
    if attack_offset is None: return st["coarse73"]
    if attack_offset<0 or attack_offset+attack_width>STRIDE:
        raise ValueError("attack field outside 0xE0 enemy object")
    return int.from_bytes(e[attack_offset:attack_offset+attack_width],endian)

def mine(paths,attack_offset=None,attack_width=2,endian="big"):
    cycles=[]; ceilings=defaultdict(int); meta={"frames":{},"unresolved":Counter()}
    for path in paths:
        active={}; frames=0; last_scene=(os.path.basename(path),"capture-fallback")
        for i,o in enumerate(rows(path)):
            rb=rawblock(o)
            if rb is None: continue
            fi=frame_id(o,i); sc,quality=scene_meta(o,path); last_scene=(sc,quality); frames+=1
            for slot in range(ENEMIES):
                e=rb[(PLAYERS+slot)*STRIDE:(PLAYERS+slot+1)*STRIDE]; st=state(e)
                ev=event_value(e,st,attack_offset,attack_width,endian)
                if st["type"]: ceilings[st["logical_cursor"]]=max(ceilings[st["logical_cursor"]],st["timer34"])
                cur=active.get(slot)
                if not st["type"]:
                    if cur and cur["states"]: meta["unresolved"]["type_absent_before_event"]+=1
                    active.pop(slot,None); continue
                g=guard(st)
                if cur and g!=cur["guard"]:
                    if cur["states"]: meta["unresolved"]["episode_guard_change_before_event"]+=1
                    active.pop(slot,None); cur=None
                if ev==0:
                    if cur is None:
                        cur={"source":os.path.basename(path),"scene":sc,"sceneLabelQuality":quality,
                             "slot":slot,"guard":g,"type":st["type"],"start_frame":fi,
                             "last_zero_frame":fi,"target_start":st["target"],"target_changes":[],
                             "association_changes":[],"split_ref_changes":[],"states":[]}
                        active[slot]=cur
                    if st["target"]!=cur["target_start"] and (not cur["target_changes"] or cur["target_changes"][-1]["target"]!=st["target"]):
                        cur["target_changes"].append({"frame":fi,"target":st["target"]})
                    if cur["states"]:
                        p=cur["states"][-1]
                        if p["assoc_c6"]!=st["assoc_c6"]:
                            cur["association_changes"].append({"frame":fi,"from":p["assoc_c6"],"to":st["assoc_c6"]})
                        if p["split_ref"]!=st["split_ref"]:
                            cur["split_ref_changes"].append({"frame":fi,"from":p["split_ref"],"to":st["split_ref"]})
                    if not cur["states"] or core(cur["states"][-1])!=core(st): cur["states"].append(new_distinct(fi,st))
                    else: extend_distinct(cur["states"][-1],fi,st)
                    cur["last_zero_frame"]=fi
                else:
                    if cur and cur["states"]:
                        cur["active_frame"]=fi; cur["eventual_attack"]=ev; cur["target_end"]=st["target"]
                        if st["target"]!=cur["target_start"] and (not cur["target_changes"] or cur["target_changes"][-1]["target"]!=st["target"]):
                            cur["target_changes"].append({"frame":fi,"target":st["target"],"atEventEdge":True})
                        cur["target_stable"]=(cur["target_start"]==st["target"] and not cur["target_changes"])
                        cur["active_state"]=st; cycles.append(cur)
                    active.pop(slot,None)
        meta["frames"][os.path.basename(path)]=frames
        meta.setdefault("sceneLabelQuality",Counter())[last_scene[1]]+=1
        meta["unresolved"]["open_at_eof"]+=sum(1 for c in active.values() if c["states"])
    for c in cycles:
        for st in c["states"]:
            ceil=ceilings[st["logical_cursor"]]; st["timerCeiling"]=ceil
            for src,dst in (("timerStart","timerStartBucket"),("timerEnd","timerEndBucket"),("timerMin","timerMinBucket")):
                st[dst]=timer_bucket(max(0,ceil-st[src]))
            st["terminalTimer1Bucket"]=hold_bucket(st["terminalTimer1Frames"])
    meta["unresolved"]=dict(meta["unresolved"]); meta["sceneLabelQuality"]=dict(meta.get("sceneLabelQuality",{}))
    return cycles,meta

def exact_state(st):
    return core(st)+(st["timerStart"],st["timerEnd"],st["timerMin"],st["timerMax"],st["terminalTimer1Frames"])
def norm_state(st):
    return core(st)+(st["timerStartBucket"],st["timerEndBucket"],st["timerMinBucket"],st["terminalTimer1Bucket"])

def features(c):
    C=[core(x) for x in c["states"]]; X=[context(x) for x in c["states"]]
    E=[exact_state(x) for x in c["states"]]; N=[norm_state(x) for x in c["states"]]
    tail=lambda q,n:[tuple(q[-n:])] if len(q)>=n else []
    return {
      "final":[C[-1]],"final_context":[X[-1]],"final_timer_exact":[E[-1]],"final_timer_norm":[N[-1]],
      "tail2":tail(C,2),"tail3":tail(C,3),"tail2_context":tail(X,2),"tail3_context":tail(X,3),
      "tail2_timer_exact":tail(E,2),"tail3_timer_exact":tail(E,3),
      "tail2_timer_norm":tail(N,2),"tail3_timer_norm":tail(N,3),
      "pair":[tuple(C[i:i+2]) for i in range(len(C)-1)],
      "triple":[tuple(C[i:i+3]) for i in range(len(C)-2)],
      "pair_timer_exact":[tuple(E[i:i+2]) for i in range(len(E)-1)],
      "triple_timer_exact":[tuple(E[i:i+3]) for i in range(len(E)-2)],
      "pair_timer_norm":[tuple(N[i:i+2]) for i in range(len(N)-1)],
      "triple_timer_norm":[tuple(N[i:i+3]) for i in range(len(N)-2)]
    }

def branchpoints(cycles):
    attacks=defaultdict(Counter); nxt=defaultdict(lambda:defaultdict(Counter))
    prv=defaultdict(lambda:defaultdict(Counter)); timers=defaultdict(lambda:defaultdict(Counter))
    for c in cycles:
        a=str(c["eventual_attack"]); seq=[core(x) for x in c["states"]]
        for i,x in enumerate(seq):
            k=sgn(x); attacks[k][a]+=1
            nxt[k][a][sgn(seq[i+1]) if i+1<len(seq) else "<EVENT_NEXT>"]+=1
            prv[k][a][sgn(seq[i-1]) if i else "<CYCLE_START>"]+=1
            st=c["states"][i]; timers[k][a][sgn((st["timerStart"],st["timerEnd"],st["terminalTimer1Frames"]))]+=1
    out=[]
    for k,dist in attacks.items():
        if len(dist)<2: continue
        sets={a:set(nxt[k][a]) for a in dist}; union=set().union(*sets.values()); common=set.intersection(*sets.values()) if sets else set()
        out.append({"anchor":k,"attack_distribution":dict(dist),"occurrences":sum(dist.values()),
                    "next_by_attack":{a:dict(v.most_common(20)) for a,v in nxt[k].items()},
                    "prev_by_attack":{a:dict(v.most_common(20)) for a,v in prv[k].items()},
                    "timer_profile_by_attack":{a:dict(v.most_common(20)) for a,v in timers[k].items()},
                    "has_post_anchor_divergence":bool(union-common)})
    out.sort(key=lambda x:(x["has_post_anchor_divergence"],len(x["attack_distribution"]),x["occurrences"]),reverse=True)
    return out[:300]

def summarize(cycles,meta,mode):
    by_attack=defaultdict(list); counts=defaultdict(lambda:defaultdict(Counter))
    srcs=defaultdict(lambda:defaultdict(lambda:defaultdict(set))); scenes=defaultdict(lambda:defaultdict(lambda:defaultdict(set)))
    targets=defaultdict(lambda:defaultdict(lambda:defaultdict(set))); stable=defaultdict(lambda:defaultdict(lambda:defaultdict(Counter)))
    finals=defaultdict(set)
    for c in cycles:
        a=str(c["eventual_attack"]); by_attack[a].append(c); finals[sgn(core(c["states"][-1]))].add(a)
        for kind,vals in features(c).items():
            for v in {sgn(z) for z in vals}:
                counts[kind][v][a]+=1; srcs[kind][v][a].add(c["source"]); scenes[kind][v][a].add(c["scene"])
                targets[kind][v][a].add(c["target_start"]); stable[kind][v][a]["stable" if c["target_stable"] else "changed"]+=1
    cand=[]
    for kind,mp in counts.items():
        for v,dist in mp.items():
            total=sum(dist.values())
            if total<2: continue
            win,n=max(dist.items(),key=lambda z:z[1]); purity=n/total
            so=len(srcs[kind][v][win]); se=len(scenes[kind][v][win]); tg=len(targets[kind][v][win])
            sf=stable[kind][v][win]["stable"]/n if n else 0
            ev="same_cycle_evidence" if n>=2 else "discovery_correlation"
            if mode!="phase73-structural-proxy" and purity==1 and n>=3 and so>=2: ev="potentially_prospectively_testable_candidate"
            score=purity*(1+min(n,20)/20)*(1+min(so,3)/6)*(1+min(tg,3)/9)*(0.85+0.15*sf)
            cand.append({"kind":kind,"signature":v,"winner_attack":win,"attack_distribution":dict(dist),
                         "support":n,"total_cycles_with_signature":total,"purity":round(purity,6),
                         "source_count":so,"scene_count":se,"target_count":tg,
                         "winner_target_stable_fraction":round(sf,6),"score":round(score,6),"evidence_class":ev})
    cand.sort(key=lambda x:(x["evidence_class"]=="potentially_prospectively_testable_candidate",
                           x["purity"],x["support"],x["source_count"],x["target_count"],x["score"]),reverse=True)
    return {"version":"seqminer-generated-v2","mode":mode,"evidenceNamespace":"WinKawaks-local-discovery-only",
            "productionPromotion":False,
            "semanticGuard":"phase73 mode is structural proxy only; explicit mode requires a separately proven WinKawaks-local attack field",
            "total_cycles":len(cycles),"meta":meta,
            "attacks":{a:{"cycles":len(cs),"sources":sorted({c["source"] for c in cs}),
                          "scenes":sorted({c["scene"] for c in cs}),"targets":sorted({c["target_start"] for c in cs}),
                          "targetStableCycles":sum(c["target_stable"] for c in cs)} for a,cs in by_attack.items()},
            "ambiguous_final_states":[{"signature":k,"attacks":sorted(v)} for k,v in finals.items() if len(v)>1],
            "ambiguous_state_branchpoints":branchpoints(cycles),"ranked_candidates":cand[:500]}

def write(outdir,cycles,s):
    os.makedirs(outdir,exist_ok=True)
    with open(os.path.join(outdir,"CYCLES.generated.jsonl"),"w",encoding="utf-8") as f:
        for c in cycles:f.write(json.dumps(c,ensure_ascii=False)+"\n")
    for name,obj in (("CANDIDATES.generated.json",s),("BRANCHPOINTS.generated.json",s["ambiguous_state_branchpoints"])):
        with open(os.path.join(outdir,name),"w",encoding="utf-8") as f: json.dump(obj,f,indent=2,ensure_ascii=False)
    lines=["# SEQMINER generated sequence atlas","",f"- mode: `{s['mode']}`",f"- cycles: **{s['total_cycles']}**",""]
    for a,d in s["attacks"].items():
        lines += [f"## Event `{a}`",f"- cycles: {d['cycles']}",f"- sources: {d['sources']}",f"- targets: {d['targets']}",""]
    lines += ["## Top candidates",""]
    for c in s["ranked_candidates"][:75]:
        lines.append(f"- `{c['kind']}` -> `{c['winner_attack']}` {c['support']}/{c['total_cycles_with_signature']} purity {c['purity']:.3f}; sources {c['source_count']}; targets {c['target_count']} — `{c['evidence_class']}`")
    with open(os.path.join(outdir,"SEQUENCE_ATLAS.generated.md"),"w",encoding="utf-8") as f:f.write("\n".join(lines)+"\n")
    lines=["# SEQMINER generated ambiguous branchpoints",""]
    for b in s["ambiguous_state_branchpoints"][:75]:
        lines += [f"## `{b['anchor']}`",f"- attacks: `{b['attack_distribution']}`",f"- post-anchor divergence: `{b['has_post_anchor_divergence']}`",f"- next: `{b['next_by_attack']}`",""]
    with open(os.path.join(outdir,"ATTACK_BRANCHES.generated.md"),"w",encoding="utf-8") as f:f.write("\n".join(lines)+"\n")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--captures",required=True); ap.add_argument("--output",required=True)
    ap.add_argument("--attack-offset",type=lambda x:int(x,0)); ap.add_argument("--attack-width",type=int,default=2)
    ap.add_argument("--attack-endian",choices=("big","little","be","le"),default="be")
    a=ap.parse_args(); paths=sorted(glob.glob(os.path.join(a.captures,"*.jsonl"))+glob.glob(os.path.join(a.captures,"*.jsonl.gz")))
    endian="big" if a.attack_endian in ("big","be") else "little"
    cycles,meta=mine(paths,a.attack_offset,a.attack_width,endian)
    mode="phase73-structural-proxy" if a.attack_offset is None else f"explicit-attack-offset-{hex(a.attack_offset)}"
    s=summarize(cycles,meta,mode); write(a.output,cycles,s)
    print(json.dumps({"version":s["version"],"mode":mode,"files":len(paths),"cycles":len(cycles),
                      "ambiguousBranchpoints":len(s["ambiguous_state_branchpoints"]),
                      "candidates":len(s["ranked_candidates"])},indent=2))

if __name__=="__main__": main()
