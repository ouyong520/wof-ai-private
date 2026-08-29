from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9.6" not in s:
    raise SystemExit('expected V4.9.6 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,1)

# Stabilize conservative WATCH across Family/slot churn. WATCH is not an action command,
# so continuity should mean "some danger persists", not "the exact same branch persists".
rep(
"""function stable(name,r){
  const s=ST[name],h=r.hit||{},uh=r.upHit||{},dh=r.downHit||{};
  const action=actionOf(r);
  let k=action+'|'+(h.slot??-1)+'|'+(h.family??'');
  if(action==='AB')k+='|'+(uh.slot??-1)+'|'+(uh.family??'')+'|'+(dh.slot??-1)+'|'+(dh.family??'');
  if(k===s.k)s.n++;else{s.k=k;s.n=1;s.v=null;}
  const need=(r.shadowWatchOnly||r.guardWatchOnly)?1:action==='SAFE'?2:action==='WATCH'?2:action==='AB'?3:((+r.hitMs||9999)<=300?2:3);
  if(s.n>=need)s.v=r;
  return s.v;
}""",
"""function stable(name,r){
  const s=ST[name],h=r.hit||{},uh=r.upHit||{},dh=r.downHit||{};
  const action=actionOf(r);
  let k=action==='WATCH'?'WATCH':action+'|'+(h.slot??-1)+'|'+(h.family??'');
  if(action==='AB')k+='|'+(uh.slot??-1)+'|'+(uh.family??'')+'|'+(dh.slot??-1)+'|'+(dh.family??'');
  if(k===s.k)s.n++;else{s.k=k;s.n=1;s.v=null;}
  const imminentWatch=action==='WATCH'&&(+r.hitMs||9999)<=150;
  const need=(r.shadowWatchOnly||r.guardWatchOnly||imminentWatch)?1:action==='SAFE'?2:action==='WATCH'?2:action==='AB'?3:((+r.hitMs||9999)<=300?2:3);
  if(s.n>=need)s.v=r;
  return s.v;
}""",
'WATCH continuity stabilizer')

# Miss diagnostics: nearest is useful but can be unrelated when multiple hazards compete.
# Save the actual raw collision branch that generated the warning too.
rep(
"""  function captureMissCase(kind,name,ps,raw,now,hp0,hp1){
    const n=raw?.stay?.nearest||null;
    const c={id:MISS_CASES.length+1,kind,player:name,hp:hp0+'→'+hp1,
      at:+now.toFixed(1),pos:[+ps.x.toFixed(1),+ps.y.toFixed(1),+ps.z.toFixed(1)],
      nearest:n?{family:n.family||null,source:n.source||null,variant:n.variant||null,slot:n.slot??null,type:n.type??null,
        t:n.t,confidence:+(+n.confidence||0).toFixed(3),survival:+(+n.survival||0).toFixed(3),
        clearance:raw?.stay?.minClearance==null?null:+raw.stay.minClearance.toFixed(3)}:null,
      candidates:missEnemyCandidates(ps,now)};""",
"""  function captureMissCase(kind,name,ps,raw,now,hp0,hp1){
    const n=raw?.stay?.nearest||null,rh=raw?.hit||raw?.stay?.hit||null;
    const c={id:MISS_CASES.length+1,kind,player:name,hp:hp0+'→'+hp1,
      at:+now.toFixed(1),pos:[+ps.x.toFixed(1),+ps.y.toFixed(1),+ps.z.toFixed(1)],
      rawHit:rh?{family:rh.family||null,source:rh.source||null,variant:rh.variant||null,slot:rh.slot??null,type:rh.type??null,
        t:rh.t,confidence:+(+rh.confidence||0).toFixed(3),survival:+(+rh.survival||0).toFixed(3),guardWatch:!!rh.guardWatch}:null,
      nearest:n?{family:n.family||null,source:n.source||null,variant:n.variant||null,slot:n.slot??null,type:n.type??null,
        t:n.t,confidence:+(+n.confidence||0).toFixed(3),survival:+(+n.survival||0).toFixed(3),
        clearance:raw?.stay?.minClearance==null?null:+raw.stay.minClearance.toFixed(3)}:null,
      candidates:missEnemyCandidates(ps,now)};""",
'capture rawHit')

rep(
"""  const missTop=MISS_CASES.slice(-6).map(c=>({id:c.id,kind:c.kind,player:c.player,hp:c.hp,nearest:c.nearest,
    candidates:(c.candidates||[]).slice(0,3).map(x=>({slot:x.slot,type:x.type,attack:x.attack,locked:x.locked,ageMs:x.ageMs,dx:x.dx,dy:x.dy,dz:x.dz,startupTop:x.startupTop}))}));""",
"""  const missTop=MISS_CASES.slice(-6).map(c=>({id:c.id,kind:c.kind,player:c.player,hp:c.hp,rawHit:c.rawHit,nearest:c.nearest,
    candidates:(c.candidates||[]).slice(0,3).map(x=>({slot:x.slot,type:x.type,attack:x.attack,locked:x.locked,ageMs:x.ageMs,dx:x.dx,dy:x.dy,dz:x.dz,startupTop:x.startupTop}))}));""",
'missTop rawHit')

rep("version:'offline-dynamic-spectator-calibrated-v4.9.6'","version:'offline-dynamic-spectator-calibrated-v4.9.7'",'version')
rep("qlog('✅ WOF V4.9.6 先观察后行动/漏判护栏版启动');","qlog('✅ WOF V4.9.7 WATCH连续性/紧急预警版启动');",'startup')
rep(
"qlog('⚡ 稳定器: WATCH与<=300ms紧急UP/DOWN为2帧确认；AB仍需3帧；<=250ms危险保留较宽紧急核心');",
"qlog('⚡ 稳定器: WATCH不再绑定具体slot/Family；任意连续WATCH可确认，<=150ms紧急WATCH单帧确认；UP/DOWN/AB规则不变');",
'startup stabilizer info')
rep(
"qlog('🔬 漏判取证: 真实SAFE漏判自动保存最近600ms敌人状态/ATTACK/Family候选；WOFV4.misses()可查看');",
"qlog('🔬 漏判取证: unstable/safeMiss同时保存rawHit与nearest，并保留最近600ms敌人ATTACK/Family候选');",
'startup miss info')

p.write_text(s,encoding='utf-8')
print('patched V4.9.7',len(s))
