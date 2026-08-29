from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9.2" not in s:
    raise SystemExit('expected V4.9.2 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,1)

rep(
"""    missHistoryMs:600,
    missCandidateLimit:5,
    fallbackZThreshold:80,""",
"""    missHistoryMs:600,
    missCandidateLimit:5,
    shadowHorizonMs:350,
    shadowRadiusScale:1.18,
    fallbackZThreshold:80,""",
'cfg shadow')

# Reset new warning timestamps when a spectator actor disappears/reappears.
rep(
"""    const A=AUD?.[name];if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.lastRawWarnAt=-1e9;A.recent={};}""",
"""    const A=AUD?.[name];if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.lastRawWarnAt=-1e9;A.lastShadowWarnAt=-1e9;A.lastShadowRawAt=-1e9;A.recent={};}""",
'reset shadow timestamps')

# Add a WATCH-only halo outside the full model geometry. It cannot issue UP/DOWN/AB.
rep(
"""  const fullCur=evalPath(p,'CONTINUE',danger,0);
  const cur=evalPath(p,'CONTINUE',actionDanger,0);

  if(cur.safe){
    if(!fullCur.safe){
      const gh=fullCur.hit||{};
      const geometryWatch=!!gh.geometryFallback;
      return{danger:true,watchOnly:true,geometryWatchOnly:geometryWatch,edgeWatchOnly:!geometryWatch,
        best:'WATCH',hitMs:fullCur.collisionMs,hit:gh,stay:fullCur};
    }
    return{danger:false,best:'CONTINUE',stay:cur};
  }""",
"""  const fullCur=evalPath(p,'CONTINUE',danger,0);
  const shadowDanger=danger.filter(d=>d.t<=CFG.shadowHorizonMs).map(d=>({...d,
    rx:Math.max(1,(+d.rx||1)*CFG.shadowRadiusScale),
    ry:Math.max(1,(+d.ry||1)*CFG.shadowRadiusScale),
    rz:Math.max(1,(+d.rz||1)*CFG.shadowRadiusScale),shadowOnly:true}));
  const shadowCur=evalPath(p,'CONTINUE',shadowDanger,0);
  const cur=evalPath(p,'CONTINUE',actionDanger,0);

  if(cur.safe){
    if(!fullCur.safe){
      const gh=fullCur.hit||{};
      const geometryWatch=!!gh.geometryFallback;
      return{danger:true,watchOnly:true,geometryWatchOnly:geometryWatch,edgeWatchOnly:!geometryWatch,
        best:'WATCH',hitMs:fullCur.collisionMs,hit:gh,stay:fullCur};
    }
    if(!shadowCur.safe){
      const gh=shadowCur.hit||{};
      return{danger:true,watchOnly:true,shadowWatchOnly:true,best:'WATCH',hitMs:shadowCur.collisionMs,hit:gh,stay:shadowCur};
    }
    return{danger:false,best:'CONTINUE',stay:cur};
  }""",
'decision shadow halo')

# Shadow WATCH is informational only, so one frame is enough; actionable advice stays unchanged.
rep(
"""  const need=action==='SAFE'?2:action==='WATCH'?2:action==='AB'?3:((+r.hitMs||9999)<=300?2:3);
  if(s.n>=need)s.v=r;""",
"""  const need=r.shadowWatchOnly?1:action==='SAFE'?2:action==='WATCH'?2:action==='AB'?3:((+r.hitMs||9999)<=300?2:3);
  if(s.n>=need)s.v=r;""",
'shadow stability')

rep(
"""  else if(action==='WATCH'&&r.edgeWatchOnly)qlog('🟪',name,'WATCH-边缘','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'edge',Math.round(CFG.actionPenetrationMin*100)+'%','source',h.source||'?');
  else if(action==='WATCH')qlog('🟠',name,'WATCH','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?','source',h.source||'?');""",
"""  else if(action==='WATCH'&&r.edgeWatchOnly)qlog('🟪',name,'WATCH-边缘','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'edge',Math.round(CFG.actionPenetrationMin*100)+'%','source',h.source||'?');
  else if(action==='WATCH'&&r.shadowWatchOnly)qlog('🟨',name,'WATCH-安全影子','约'+r.hitMs+'ms','slot',h.slot,'family',h.family||'?',
    'halo',Math.round((CFG.shadowRadiusScale-1)*100)+'%','source',h.source||'?');
  else if(action==='WATCH')qlog('🟠',name,'WATCH','约'+r.hitMs+'ms','slot',h.slot,'type',h.type,'family',h.family||'?','source',h.source||'?');""",
'print shadow watch')

# Track stable WATCH coverage separately from actionable hit validation.
old_aud="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0},byFamily:{}}
};"""
new_aud="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,lastShadowWarnAt:-1e9,lastShadowRawAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0},byFamily:{}}
};"""
rep(old_aud,new_aud,'audit stats shadow coverage')

# Record raw/stable shadow warning timestamps and classify damage after stable WATCH as covered.
rep(
"""  const A=AUD[name],action=st?actionOf(st):null,rawAction=raw?actionOf(raw):null;
  if(rawAction&&rawAction!=='SAFE')A.lastRawWarnAt=now;
  const hp=ps.hp;""",
"""  const A=AUD[name],action=st?actionOf(st):null,rawAction=raw?actionOf(raw):null;
  if(rawAction&&rawAction!=='SAFE')A.lastRawWarnAt=now;
  if(raw?.shadowWatchOnly)A.lastShadowRawAt=now;
  const hp=ps.hp;""",
'audit raw shadow timestamp')

rep(
"""    }else if(now-A.lastWarnAt>350){
      if(now-A.lastRawWarnAt<=350){
        A.stats.unstableCovered++;
        const mc=captureMissCase('unstableCovered',name,ps,raw,now,A.prevHp,hp);
        qlog('🟧',name,'原始危险已覆盖/稳定器未确认','HP '+A.prevHp+'→'+hp,'case#'+mc.id);
      }else{
        A.stats.safeMiss++;
        const mc=captureMissCase('safeMiss',name,ps,raw,now,A.prevHp,hp);
        qlog('❌',name,'真实SAFE漏判','HP '+A.prevHp+'→'+hp,'case#'+mc.id,
          '候选',mc.candidates.slice(0,3).map(x=>'s'+x.slot+'/T'+x.type+'/A'+x.attack+'/'+(x.locked||'?')).join(' '));
      }
    }""",
"""    }else if(now-A.lastWarnAt<=350){
      A.stats.watchCovered++;
      const shadow=now-A.lastShadowWarnAt<=350;
      if(shadow)A.stats.shadowCovered++;
      qlog(shadow?'🟨':'🟩',name,shadow?'安全影子WATCH覆盖掉血':'稳定WATCH覆盖掉血','HP '+A.prevHp+'→'+hp);
    }else if(now-A.lastRawWarnAt<=350){
      A.stats.unstableCovered++;
      const mc=captureMissCase('unstableCovered',name,ps,raw,now,A.prevHp,hp);
      qlog('🟧',name,'原始危险已覆盖/稳定器未确认','HP '+A.prevHp+'→'+hp,'case#'+mc.id);
    }else{
      A.stats.safeMiss++;
      const mc=captureMissCase('safeMiss',name,ps,raw,now,A.prevHp,hp);
      qlog('❌',name,'真实SAFE漏判','HP '+A.prevHp+'→'+hp,'case#'+mc.id,
        '候选',mc.candidates.slice(0,3).map(x=>'s'+x.slot+'/T'+x.type+'/A'+x.attack+'/'+(x.locked||'?')).join(' '));
    }""",
'audit stable watch coverage')

rep(
"""  if(st&&action!=='SAFE')A.lastWarnAt=now;
  if(!A.pending&&st&&action!=='SAFE'&&st.hitMs!=null){""",
"""  if(st&&action!=='SAFE')A.lastWarnAt=now;
  if(st?.shadowWatchOnly)A.lastShadowWarnAt=now;
  if(!A.pending&&st&&action!=='SAFE'&&st.hitMs!=null){""",
'audit stable shadow timestamp')

# Shadow WATCH must never create an actionable audit pending/false-positive sample.
rep(
"""    if(st.geometryWatchOnly||st.edgeWatchOnly)return;""",
"""    if(st.geometryWatchOnly||st.edgeWatchOnly||st.shadowWatchOnly)return;""",
'skip shadow audit')

rep(
"""  const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0};""",
"""  const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,watchCovered:0,shadowCovered:0,unstableCovered:0,safeMiss:0};""",
'summary totals')

rep(
"""  const damageEvents=total.hit+total.ambiguousDamage+total.unstableCovered+total.safeMiss;
  const metrics={actionPrecision:validated?+(total.hit/validated).toFixed(3):null,
    rawDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage+total.unstableCovered)/damageEvents).toFixed(3):null,
    stableDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage)/damageEvents).toFixed(3):null,""",
"""  const damageEvents=total.hit+total.ambiguousDamage+total.watchCovered+total.unstableCovered+total.safeMiss;
  const metrics={actionPrecision:validated?+(total.hit/validated).toFixed(3):null,
    rawDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage+total.watchCovered+total.unstableCovered)/damageEvents).toFixed(3):null,
    stableDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage+total.watchCovered)/damageEvents).toFixed(3):null,
    shadowDamageCoverage:damageEvents?+(total.shadowCovered/damageEvents).toFixed(3):null,""",
'metrics shadow coverage')

rep("version:'offline-dynamic-spectator-calibrated-v4.9.2'","version:'offline-dynamic-spectator-calibrated-v4.9.3'",'version')
rep("qlog('✅ WOF V4.9.2 精度优先信任门控观战版启动');","qlog('✅ WOF V4.9.3 安全影子恢复观战版启动');",'startup')
rep(
"qlog('🎯 精度优先: Variant首次高可信误报即隔离为WATCH；低精度source/family会联动隔离，新分支使用更小行动核心');",
"qlog('🎯 精度优先: 保留V4.9.2信任门控；坏分支继续WATCH，不重新扩大UP/DOWN/AB行动核心');\n  qlog('🟨 安全影子: 完整危险壳外再加18%短时WATCH halo，仅预警不参与UP/DOWN/AB，也不计误报校准');",
'startup shadow info')
rep(
"qlog('🟧 审计: unstableCovered=raw危险已覆盖但稳定器未确认；safeMiss=raw/stable都完全没看到危险');",
"qlog('🟧 审计: watchCovered=稳定WATCH覆盖掉血；shadowCovered=其中由安全影子覆盖；unstableCovered=仅raw覆盖；safeMiss=完全未覆盖');",
'audit info')

p.write_text(s,encoding='utf-8')
print('patched V4.9.3',len(s))
