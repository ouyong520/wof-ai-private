from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9.8" not in s:
    raise SystemExit('expected V4.9.8 input')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,count)

# Raw imminent danger should never disappear only because an actionable branch is still
# waiting for its UP/DOWN/AB debounce. During that confirmation gap, surface WATCH only.
rep(
"""    watchPromoteMaxMs:280,
    attackTailGuardMs:280,""",
"""    watchPromoteMaxMs:280,
    debounceBridgeMs:350,
    attackTailGuardMs:280,""",
'debounce bridge cfg')

rep(
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
"""function stable(name,r){
  const s=ST[name],h=r.hit||{},uh=r.upHit||{},dh=r.downHit||{};
  const action=actionOf(r);
  let k=action==='WATCH'?'WATCH':action+'|'+(h.slot??-1)+'|'+(h.family??'');
  if(action==='AB')k+='|'+(uh.slot??-1)+'|'+(uh.family??'')+'|'+(dh.slot??-1)+'|'+(dh.family??'');
  if(k===s.k)s.n++;else{s.k=k;s.n=1;s.v=null;}
  const imminentWatch=action==='WATCH'&&(+r.hitMs||9999)<=150;
  const need=(r.shadowWatchOnly||r.guardWatchOnly||imminentWatch)?1:action==='SAFE'?2:action==='WATCH'?2:action==='AB'?3:((+r.hitMs||9999)<=300?2:3);
  if(s.n>=need){s.v=r;return s.v;}
  // A raw actionable warning can flicker before it reaches its action debounce count.
  // Bridge only the warning layer: never emit movement/AB and never calibrate FP from it.
  if(action!=='SAFE'&&(+r.hitMs||9999)<=CFG.debounceBridgeMs)
    return {...r,watchOnly:true,debounceWatchOnly:true,best:'WATCH'};
  return s.v;
}""",
'debounce bridge stabilizer')

rep(
"""  else if(action==='WATCH'&&r.noRoute)qlog('🟠',name,'WATCH无路','当前'+r.hitMs+'ms',h.family||'?',""",
"""  else if(action==='WATCH'&&r.debounceWatchOnly)qlog('🟦',name,'WATCH-稳定桥','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?', 'source',h.source||'?');
  else if(action==='WATCH'&&r.noRoute)qlog('🟠',name,'WATCH无路','当前'+r.hitMs+'ms',h.family||'?',""",
'print debounce bridge')

# Add bridge timestamps/counters to all three player audit buckets.
s=s.replace("lastTailWarnAt:-1e9,lastWatchEvidence:null,", "lastTailWarnAt:-1e9,lastBridgeWarnAt:-1e9,lastWatchEvidence:null,")
s=s.replace("tailCovered:0,watchPromoted:0,", "tailCovered:0,bridgeCovered:0,watchPromoted:0,")

rep(
"""A.lastGuardWarnAt=-1e9;A.lastGuardRawAt=-1e9;A.lastTailWarnAt=-1e9;A.lastWatchEvidence=null;A.recent={};""",
"""A.lastGuardWarnAt=-1e9;A.lastGuardRawAt=-1e9;A.lastTailWarnAt=-1e9;A.lastBridgeWarnAt=-1e9;A.lastWatchEvidence=null;A.recent={};""",
'reset bridge timestamp')

rep(
"""      const shadow=now-A.lastShadowWarnAt<=350,guard=now-A.lastGuardWarnAt<=350,tail=now-A.lastTailWarnAt<=350;
      if(shadow)A.stats.shadowCovered++;
      if(guard)A.stats.guardCovered++;
      if(tail)A.stats.tailCovered++;""",
"""      const shadow=now-A.lastShadowWarnAt<=350,guard=now-A.lastGuardWarnAt<=350,tail=now-A.lastTailWarnAt<=350,bridge=now-A.lastBridgeWarnAt<=350;
      if(shadow)A.stats.shadowCovered++;
      if(guard)A.stats.guardCovered++;
      if(tail)A.stats.tailCovered++;
      if(bridge)A.stats.bridgeCovered++;""",
'damage bridge coverage')

rep(
"""      qlog(tail?'🟧':guard?'🟫':shadow?'🟨':'🟩',name,tail?'攻击尾帧护栏覆盖掉血':guard?'主动攻击护栏覆盖掉血':shadow?'安全影子WATCH覆盖掉血':'稳定WATCH覆盖掉血','HP '+hpBefore+'→'+hp);""",
"""      qlog(tail?'🟧':guard?'🟫':shadow?'🟨':bridge?'🟦':'🟩',name,tail?'攻击尾帧护栏覆盖掉血':guard?'主动攻击护栏覆盖掉血':shadow?'安全影子WATCH覆盖掉血':bridge?'稳定桥WATCH覆盖掉血':'稳定WATCH覆盖掉血','HP '+hpBefore+'→'+hp);""",
'bridge coverage log')

rep(
"""  if(st?.tailWatchOnly)A.lastTailWarnAt=now;
  if(st&&action==='WATCH'&&!st.shadowWatchOnly&&!st.guardWatchOnly){""",
"""  if(st?.tailWatchOnly)A.lastTailWarnAt=now;
  if(st?.debounceWatchOnly)A.lastBridgeWarnAt=now;
  if(st&&action==='WATCH'&&!st.shadowWatchOnly&&!st.guardWatchOnly&&!st.debounceWatchOnly){""",
'bridge stable timestamp')

rep(
"""    if(st.geometryWatchOnly||st.edgeWatchOnly||st.shadowWatchOnly||st.guardWatchOnly)return;""",
"""    if(st.geometryWatchOnly||st.edgeWatchOnly||st.shadowWatchOnly||st.guardWatchOnly||st.debounceWatchOnly)return;""",
'bridge no fp audit')

rep(
"""const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,tailCovered:0,watchPromoted:0,""",
"""const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,guardCovered:0,tailCovered:0,bridgeCovered:0,watchPromoted:0,""",
'total bridge covered')

rep(
"""    tailDamageCoverage:damageEvents?+(total.tailCovered/damageEvents).toFixed(3):null,
    validated,damageEvents};""",
"""    tailDamageCoverage:damageEvents?+(total.tailCovered/damageEvents).toFixed(3):null,
    bridgeDamageCoverage:damageEvents?+(total.bridgeCovered/damageEvents).toFixed(3):null,
    validated,damageEvents};""",
'bridge metric')

rep("version:'offline-dynamic-spectator-calibrated-v4.9.8'","version:'offline-dynamic-spectator-calibrated-v4.9.9'",'version')
rep("qlog('✅ WOF V4.9.8 攻击尾帧护栏/漏判聚合版启动');","qlog('✅ WOF V4.9.9 稳定桥/覆盖收敛版启动');",'startup')
rep(
"""  qlog('⚡ 稳定器: WATCH不再绑定具体slot/Family；任意连续WATCH可确认，<=150ms紧急WATCH单帧确认；UP/DOWN/AB规则不变');""",
"""  qlog('⚡ 稳定器: WATCH连续性保持；UP/DOWN/AB未确认期间若raw危险<=350ms，先输出WATCH稳定桥，绝不提前动作/AB');
  qlog('🟦 稳定桥审计: bridgeCovered=raw危险已出现但动作分支尚未稳定时，由WATCH桥成功覆盖真实掉血；不进入FP校准');""",
'startup bridge info')

p.write_text(s,encoding='utf-8')
print('patched V4.9.9',len(s))
