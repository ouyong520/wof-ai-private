from pathlib import Path

p = Path('wof_v4_install_once.js')
s = p.read_text(encoding='utf-8')

if "offline-dynamic-p1p2-v4.3.2" not in s:
    raise SystemExit('expected V4.3.2 input')

# 1) Temporal confidence: Family sweep survival must affect runtime danger.
s = s.replace(
    "    auditHitEarlyMs:180,\n    padX:3,",
    "    auditHitEarlyMs:180,\n    survivalActionThreshold:0.35,\n    auditRevokeLeadMs:60,\n    padX:3,",
    1,
)

old = """          const sw=interp(f[7],age,'sw');if(!sw)continue;
          const confidence=hazard*fc.p*l.w;
          if(confidence<CFG.minConfidence)continue;
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,
            rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:fc.id,
            confidence,source:'startup',lookup:hit.kind});"""
new = """          const sw=interp(f[7],age,'sw');if(!sw)continue;
          const survival=Math.max(0,Math.min(1,sw.survival??1));
          const confidence=hazard*fc.p*l.w*survival;
          if(confidence<CFG.minConfidence)continue;
          out.danger.push({t,x:org.x+sg*sw.x,y:org.y+sw.y,z:org.z+sw.z,
            rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:fc.id,
            confidence,survival,actionable:survival>=CFG.survivalActionThreshold,source:'startup',lookup:hit.kind});"""
if old not in s:
    raise SystemExit('startup survival patch target missing')
s = s.replace(old, new, 1)

old = """      const sw=interp(f[7],a,'sw');if(!sw)continue;
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:s.locked,
        confidence:1,source:'active'});"""
new = """      const sw=interp(f[7],a,'sw');if(!sw)continue;
      const survival=Math.max(0,Math.min(1,sw.survival??1));
      if(survival<CFG.minConfidence)continue;
      out.danger.push({t,x:s.origin.x+sg*sw.x,y:s.origin.y+sw.y,z:s.origin.z+sw.z,
        rx:rad.rx,ry:rad.ry,rz:rad.rz,slot:o.slot,type:o.type,family:s.locked,
        confidence:survival,survival,actionable:survival>=CFG.survivalActionThreshold,source:'active'});"""
if old not in s:
    raise SystemExit('active survival patch target missing')
s = s.replace(old, new, 1)

# 2) Only high-survival known hazards may force movement/AB. Low-survival tails are WATCH-only.
s = s.replace(
    "    const knownDanger=danger.filter(d=>d.source!=='active-unknown');\n    const fullCur=evalPath(p,'CONTINUE',danger,0);\n    const cur=evalPath(p,'CONTINUE',knownDanger,0);",
    "    const actionDanger=danger.filter(d=>d.source!=='active-unknown'&&d.actionable!==false);\n    const fullCur=evalPath(p,'CONTINUE',danger,0);\n    const cur=evalPath(p,'CONTINUE',actionDanger,0);",
    1,
)
s = s.replace(
    "      if(!fullCur.safe&&fullCur.hit?.source==='active-unknown')",
    "      if(!fullCur.safe&&(fullCur.hit?.source==='active-unknown'||fullCur.hit?.actionable===false))",
    1,
)
s = s.replace(
    "    const routeDanger=knownDanger.filter(d=>d.t<=routeUntil);",
    "    const routeDanger=actionDanger.filter(d=>d.t<=routeUntil);",
    1,
)
s = s.replace(
    "      const known=h=>!!h&&h.family!=null&&h.source!=='active-unknown';",
    "      const known=h=>!!h&&h.family!=null&&h.source!=='active-unknown'&&h.actionable!==false;",
    1,
)

# 3) Audit: an attack that ends before the predicted collision is a revoked prediction, not a false positive.
s = s.replace(
    "stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,falsePositive:0,safeMiss:0}",
    "stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0}",
)
s = s.replace(
    "{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,falsePositive:0,materialized:0}",
    "{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,materialized:0}",
    1,
)
s = s.replace(
    "function geoText(e){return 'inside x'+fmt(e.mx)+' y'+fmt(e.my)+' z'+fmt(e.mz)+' r '+fmt(e.rx)+'/'+fmt(e.ry)+'/'+fmt(e.rz)+' conf '+fmt(e.confidence);}",
    "function geoText(e){return 'inside x'+fmt(e.mx)+' y'+fmt(e.my)+' z'+fmt(e.mz)+' r '+fmt(e.rx)+'/'+fmt(e.ry)+'/'+fmt(e.rz)+' conf '+fmt(e.confidence)+' surv '+fmt(e.survival);}",
    1,
)

start = s.index("  function trackEnemy(e,now){")
end = s.index("\n\n  function auditResolve", start)
track = """  function trackEnemy(e,now){
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

needle = """    }else if(kind==='ambiguous'){
      A.stats.ambiguousDamage++;F.ambiguousDamage++;
      console.log('⚪',name,'发生掉血但目标Family未确认/不计命中',e.action,e.family||'?',e.hitMs+'ms',extra);
    }else if(kind==='fp'){"""
replacement = """    }else if(kind==='ambiguous'){
      A.stats.ambiguousDamage++;F.ambiguousDamage++;
      console.log('⚪',name,'发生掉血但目标Family未确认/不计命中',e.action,e.family||'?',e.hitMs+'ms',extra);
    }else if(kind==='revoked'){
      A.stats.revoked++;F.revoked++;
      console.log('🔵',name,'预测已撤销/不计误报',e.action,e.family||'?',e.source||'?',e.hitMs+'ms','slot',e.slot,
        '目标攻击在预计碰撞前结束',extra);
    }else if(kind==='fp'){"""
if needle not in s:
    raise SystemExit('auditResolve patch target missing')
s = s.replace(needle, replacement, 1)

s = s.replace(
    "if(e.source==='active'||e.familySeen)auditResolve(name,'hit',e,'HP '+A.prevHp+'→'+hp);\n        else auditResolve(name,'ambiguous',e,'HP '+A.prevHp+'→'+hp);",
    "if(e.attackEndedEarly)auditResolve(name,'ambiguous',e,'预测已撤销后发生 HP '+A.prevHp+'→'+hp);\n        else if(e.source==='active'||e.familySeen)auditResolve(name,'hit',e,'HP '+A.prevHp+'→'+hp);\n        else auditResolve(name,'ambiguous',e,'HP '+A.prevHp+'→'+hp);",
    1,
)

old = """      if(A.pending&&now>=q.deadline){
        const info='偏移 x'+fmt(q.dx)+' y'+fmt(q.dy)+' z'+fmt(q.dz);
        const enemyInvalid=q.enemyLost||(q.source==='startup'&&!q.familySeen);
        auditResolve(name,enemyInvalid?'enemy':q.changed?'changed':'fp',q,info);
      }"""
new = """      if(A.pending&&now>=q.deadline){
        const info='偏移 x'+fmt(q.dx)+' y'+fmt(q.dy)+' z'+fmt(q.dz);
        const enemyInvalid=q.enemyLost||(q.source==='startup'&&!q.familySeen);
        auditResolve(name,q.attackEndedEarly?'revoked':enemyInvalid?'enemy':q.changed?'changed':'fp',q,info);
      }"""
if old not in s:
    raise SystemExit('deadline audit patch target missing')
s = s.replace(old, new, 1)

s = s.replace(
    "if(h.family==null||h.source==='active-unknown')return;",
    "if(h.family==null||h.source==='active-unknown'||h.actionable===false)return;",
    1,
)
s = s.replace(
    "rx,ry,rz,confidence:+h.confidence||0,",
    "rx,ry,rz,confidence:+h.confidence||0,survival:h.survival==null?1:+h.survival,",
    1,
)
s = s.replace(
    "familySeen:h.source==='active',materializedCounted:false,enemyLost:false,otherFamily:null,enemyLastAttack:null};",
    "familySeen:h.source==='active',familyLastSeenAt:h.source==='active'?now:null,attackEndedEarly:false,materializedCounted:false,enemyLost:false,otherFamily:null,enemyLastAttack:null};",
    1,
)

# Version / diagnostics.
s = s.replace("offline-dynamic-p1p2-v4.3.2", "offline-dynamic-p1p2-v4.3.3", 1)
s = s.replace("✅ WOF V4.3.2 目标敌人连续性自验证版启动", "✅ WOF V4.3.3 时间有效性自验证版启动", 1)
s = s.replace(
    "🧪 验证: 🎯命中 / 🟡路径改变 / 🟤敌人攻击取消或分支改变 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判",
    "🧪 验证: 🎯命中 / 🟡路径改变 / 🟤分支改变 / 🔵预测撤销 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判",
    1,
)

p.write_text(s, encoding='utf-8')
print('patched V4.3.3', len(s))
