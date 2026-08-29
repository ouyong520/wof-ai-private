from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.8" not in s:
    raise SystemExit('expected V4.8 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' target missing')
    s=s.replace(old,new,1)

# 1) Variant is now the fast/precise demotion layer. Family/source are safety backstops again,
# so one bad branch no longer suppresses an otherwise useful Family and creates coverage holes.
rep(
"""    sourceDemoteConfirmed:2,sourceDemoteFp:2,sourceDemoteFpPlayers:1,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:5,sourceRecoverHit:2,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:3,familyDemoteFp:3,familyDemoteFpPlayers:1,familyDemotePrecision:.30,
    familyRecoverConfirmed:7,familyRecoverHit:3,familyRecoverPrecision:.50,
    variantDemoteConfirmed:3,variantDemoteFp:3,variantDemotePrecision:.20,
    variantRecoverConfirmed:6,variantRecoverHit:3,variantRecoverPrecision:.50,""",
"""    sourceDemoteConfirmed:6,sourceDemoteFp:5,sourceDemoteFpPlayers:2,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:10,sourceRecoverHit:4,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:10,familyDemoteFp:7,familyDemoteFpPlayers:2,familyDemotePrecision:.30,
    familyRecoverConfirmed:16,familyRecoverHit:6,familyRecoverPrecision:.50,
    variantDemoteConfirmed:2,variantDemoteFp:2,variantDemotePrecision:.20,
    variantRecoverConfirmed:5,variantRecoverHit:2,variantRecoverPrecision:.50,""",
'calibration hierarchy')

# Re-evaluate inherited watchOnly flags under the new hierarchy instead of carrying V4.7/V4.8's
# aggressive whole-source/Family demotions forward forever.
rep(
"importCalibration(__WOF_PREV_CAL||self.__WOF_CAL_CACHE);",
"""importCalibration(__WOF_PREV_CAL||self.__WOF_CAL_CACHE);
  function recalibrateImported(){
    for(const [map,scope] of [[CAL_VARIANT,'variant'],[CAL_SOURCE,'source'],[CAL_FAMILY,'family']]){
      for(const b of Object.values(map)){b.watchOnly=false;calRefresh(b,scope);}
    }
  }
  recalibrateImported();""",
're-evaluate inherited calibration')

# 2) Do not reset the 3-tick stability filter when active Variant changes from `early` to the
# measured 80ms motion bucket. Variant still controls calibration/actionability, just not debounce identity.
rep(
"let k=action+'|'+(h.slot??-1)+'|'+(h.family??'')+'|'+(h.variant??'');",
"let k=action+'|'+(h.slot??-1)+'|'+(h.family??'');",
'stable key ignores variant transition')

# 3) Split true SAFE misses from cases where raw prediction existed but did not survive debounce.
rep(
"if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.recent={};}",
"if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;A.lastRawWarnAt=-1e9;A.recent={};}",
'reset raw warning timestamp')

old_aud="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,safeMiss:0},byFamily:{}}
};"""
new_aud="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,lastRawWarnAt:-1e9,recent:{},stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0},byFamily:{}}
};"""
rep(old_aud,new_aud,'AUD raw coverage stats')

rep(
"function auditStep(name,ps,st,now){\n  const A=AUD[name],action=st?actionOf(st):null;",
"function auditStep(name,ps,st,raw,now){\n  const A=AUD[name],action=st?actionOf(st):null,rawAction=raw?actionOf(raw):null;\n  if(rawAction&&rawAction!=='SAFE')A.lastRawWarnAt=now;",
'audit raw prediction input')

rep(
"""    }else if(now-A.lastWarnAt>350){
      A.stats.safeMiss++;
      qlog('❌',name,'SAFE漏判候选','HP '+A.prevHp+'→'+hp,'近350ms无稳定危险提示');
    }""",
"""    }else if(now-A.lastWarnAt>350){
      if(now-A.lastRawWarnAt<=350){
        A.stats.unstableCovered++;
        qlog('🟧',name,'原始危险已覆盖/稳定器未确认','HP '+A.prevHp+'→'+hp,'近350ms有raw危险');
      }else{
        A.stats.safeMiss++;
        qlog('❌',name,'真实SAFE漏判候选','HP '+A.prevHp+'→'+hp,'近350ms raw/stable 都无危险');
      }
    }""",
'classify true miss vs debounce coverage')

rep(
"auditStep(p.name,ps,st,now);",
"auditStep(p.name,ps,st,raw,now);",
'tick passes raw prediction')

rep(
"const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,safeMiss:0};",
"const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,unstableCovered:0,safeMiss:0};",
'summary raw coverage count')

rep("version:'offline-dynamic-spectator-calibrated-v4.8'","version:'offline-dynamic-spectator-calibrated-v4.8.1'",'version')
rep("qlog('✅ WOF V4.8 上下文Variant校准观战版启动');","qlog('✅ WOF V4.8.1 Variant稳定性/真实漏判审计版启动');",'startup')
rep(
"qlog('🧬 Variant: startup按anim/state分支；active按起手上下文+80ms运动分支独立降级，不再一刀切整个Family');",
"qlog('🧬 Variant: 坏分支2次高可信误报即可WATCH；Family/source恢复为慢速安全兜底');\n  qlog('🟧 审计: unstableCovered=raw危险已覆盖但稳定器未确认；safeMiss=raw/stable都完全没看到危险');",
'v481 startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.8.1',len(s))
