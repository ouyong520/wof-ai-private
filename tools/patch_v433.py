from pathlib import Path

p = Path('wof_v4_install_once.js')
s = p.read_text(encoding='utf-8')

if "offline-dynamic-p1p2-v4.3.2" not in s:
    raise SystemExit('expected V4.3.2 input')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'{label} patch target missing')
    s = s.replace(old, new, 1)

# 1) Temporal confidence: Family sweep survival must affect runtime danger.
replace_once(
    "    auditHitEarlyMs:180,\n    padX:3,",
    "    auditHitEarlyMs:180,\n    survivalActionThreshold:0.35,\n    auditRevokeLeadMs:60,\n    padX:3,",
    'CFG',
)

replace_once(
"""          const sw=interp(f[7],age,'sw');if(!sw)continue;
          const confidence=hazard*fc.p*l.w;
          if(confidence<CFG.minConfidence)continue;
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,
            rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:fc.id,
            confidence,source:'startup',lookup:hit.kind});""",
"""          const sw=interp(f[7],age,'sw');if(!sw)continue;
          const survival=Math.max(0,Math.min(1,sw.survival??1));
          const confidence=hazard*fc.p*l.w*survival;
          if(confidence<CFG.minConfidence)continue;
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,
            rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:fc.id,
            confidence,survival,actionable:survival>=CFG.survivalActionThreshold,source:'startup',lookup:hit.kind});""",
    'startup survival',
)

replace_once(
"""      const sw=interp(f[7],a,'sw');if(!sw)continue;
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:s.locked,
        confidence:1,source:'active'});""",
"""      const sw=interp(f[7],a,'sw');if(!sw)continue;
      const survival=Math.max(0,Math.min(1,sw.survival??1));
      if(survival<CFG.minConfidence)continue;
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:s.locked,
        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold,source:'active'});""",
    'active survival',
)

# 2) Only high-survival known hazards may force movement/AB. Low-survival tails are WATCH-only.
replace_once(
"""  const knownDanger=danger.filter(d=>d.source!=='active-unknown');
  const fullCur=evalPath(p,'CONTINUE',danger,0);
  const cur=evalPath(p,'CONTINUE',knownDanger,0);""",
"""  const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false);
  const fullCur=evalPath(p,'CONTINUE',danger,0);
  const cur=evalPath(p,'CONTINUE',actionDanger,0);""",
    'decision danger split',
)
replace_once(
    "    if(!fullCur.safe&&fullCur.hit?.source==='active-unknown')",
    "    if(!fullCur.safe&&(fullCur.hit?.source==='active-unknown'||fullCur.hit?.actionable===false))",
    'advisory WATCH',
)
replace_once(
    "  const routeDanger=knownDanger.filter(d=>d.t<=routeUntil);",
    "  const routeDanger=actionDanger.filter(d=>d.t<=routeUntil);",
    'route danger',
)
replace_once(
    "    const known=h=>!!h&&h.family!=null&&h.source!=='active-unknown';",
    "    const known=h=>!!h&&h.family!=null&&h.source!=='active-unknown'&&h.actionable!==false;",
    'AB actionable gate',
)

# 3) Audit counters and diagnostics.
s = s.replace(
    "stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,falsePositive:0,safeMiss:0}",
    "stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0}",
)
replace_once(
    "{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,falsePositive:0,materialized:0}",
    "{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,materialized:0}",
    'family counters',
)
replace_once(
    "function geoText(e){return 'inside x'+fmt(e.mx)+' y'+fmt(e.my)+' z'+fmt(e.mz)+' r '+fmt(e.rx)+'/'+fmt(e.ry)+'/'+fmt(e.rz)+' conf '+fmt(e.confidence);}",
    "function geoText(e){return 'inside x'+fmt(e.mx)+' y'+fmt(e.my)+' z'+fmt(e.mz)+' r '+fmt(e.rx)+'/'+fmt(e.ry)+'/'+fmt(e.rz)+' conf '+fmt(e.confidence)+' surv '+fmt(e.survival);}",
    'geo survival',
)

# Track whether the predicted Family is still alive near the predicted collision time.
start = s.index("function trackEnemy(e,now){")
end = s.index("\n\nfunction auditResolve", start)
track = """function trackEnemy(e,now){
  if(!e||e.slot==null||e.slot<0||e.slot>=NSLOTS)return;
  const o=readActor(POOL+e.slot*STRIDE,e.slot);
  if(!o||o.type!==e.enemyType){
    if(now<=e.due+60)e.enemyLost=true;
    return;
  }
  e.enemyLastAttack=o.attack;
  const lk=SLOT[e.slot]?.locked||null;
  if(lk===e.family){
    e.familySeen=true;e.familyLastSeenAt=now;
  }else{
    if(lk&&lk!==e.family)e.otherFamily=lk;
    if(e.familySeen&&now<e.due-CFG.auditRevokeLeadMs)e.attackEndedEarly=true;
  }
}"""
s = s[:start] + track + s[end:]

replace_once(
    "  }else if(kind==='fp'){",
"""  }else if(kind==='revoked'){
    A.stats.revoked++;F.revoked++;
    console.log('🔵',name,'预测已撤销/不计误报',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,
      '目标攻击在预计碰撞前结束',extra);
  }else if(kind==='fp'){""",
    'revoked resolver',
)

replace_once(
    "      if(e.source==='active'||e.familySeen)auditResolve(name,'hit',e,'HP '+A.prevHp+'→'+hp);\n      else auditResolve(name,'ambiguous',e,'HP '+A.prevHp+'→'+hp);",
    "      if(e.attackEndedEarly)auditResolve(name,'ambiguous',e,'预测已撤销后发生 HP '+A.prevHp+'→'+hp);\n      else if(e.source==='active'||e.familySeen)auditResolve(name,'hit',e,'HP '+A.prevHp+'→'+hp);\n      else auditResolve(name,'ambiguous',e,'HP '+A.prevHp+'→'+hp);",
    'revoked damage handling',
)
replace_once(
    "      auditResolve(name,enemyInvalid?'enemy':q.changed?'changed':'fp',q,info);",
    "      auditResolve(name,q.attackEndedEarly?'revoked':enemyInvalid?'enemy':q.changed?'changed':'fp',q,info);",
    'deadline resolution',
)
replace_once(
    "    if(h.family==null||h.source==='active-unknown')return;",
    "    if(h.family==null||h.source==='active-unknown'||h.actionable===false)return;",
    'audit actionable gate',
)
replace_once(
    "      rx,ry,rz,confidence:+h.confidence||0,",
    "      rx,ry,rz,confidence:+h.confidence||0,survival:h.survival==null?1:+h.survival,",
    'audit survival field',
)
replace_once(
    "      familySeen:h.source==='active',materializedCounted:false,enemyLost:false,otherFamily:null,enemyLastAttack:null};",
    "      familySeen:h.source==='active',familyLastSeenAt:h.source==='active'?now:null,attackEndedEarly:false,materializedCounted:false,enemyLost:false,otherFamily:null,enemyLastAttack:null};",
    'audit continuity fields',
)

# Version / startup diagnostics.
replace_once("offline-dynamic-p1p2-v4.3.2", "offline-dynamic-p1p2-v4.3.3", 'version')
replace_once("✅ WOF V4.3.2 目标敌人连续性自验证版启动", "✅ WOF V4.3.3 时间有效性自验证版启动", 'startup label')
replace_once(
    "🧪 验证: 🎯命中 / 🟡路径改变 / 🟤敌人攻击取消或分支改变 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判",
    "🧪 验证: 🎯命中 / 🟡路径改变 / 🟤分支改变 / 🔵预测撤销 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判",
    'audit legend',
)

p.write_text(s, encoding='utf-8')
print('patched V4.3.3', len(s))
