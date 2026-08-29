from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.6.1" not in s:
    raise SystemExit('expected V4.6.1 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' target missing')
    s=s.replace(old,new,1)

# Faster WATCH demotion. Demotion never deletes hazard points: it only removes UP/DOWN/AB actionability.
rep(
"""    sourceDemoteConfirmed:6,sourceDemoteFp:5,sourceDemoteFpPlayers:2,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:10,sourceRecoverHit:4,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:10,familyDemoteFp:7,familyDemoteFpPlayers:2,familyDemotePrecision:.30,
    familyRecoverConfirmed:16,familyRecoverHit:6,familyRecoverPrecision:.50,""",
"""    sourceDemoteConfirmed:4,sourceDemoteFp:3,sourceDemoteFpPlayers:2,sourceDemotePrecision:.25,
    sourceRecoverConfirmed:8,sourceRecoverHit:4,sourceRecoverPrecision:.50,
    familyDemoteConfirmed:6,familyDemoteFp:4,familyDemoteFpPlayers:2,familyDemotePrecision:.30,
    familyRecoverConfirmed:12,familyRecoverHit:6,familyRecoverPrecision:.50,""",
'calibration thresholds')

# Add a compact snapshot so the user does not need to scroll the huge full report.
rep(
"""function reportSnapshot(){
  return frozenCopy({at:Date.now(),audit:auditSnapshot(),auditFamilies:auditFamilies(),calibration:calibrationSnapshot()});
}
function reportText(){return JSON.stringify(reportSnapshot(),null,2);}""",
"""function reportSnapshot(){
  return frozenCopy({at:Date.now(),audit:auditSnapshot(),auditFamilies:auditFamilies(),calibration:calibrationSnapshot()});
}
function summarySnapshot(){
  const a=auditSnapshot(),af=auditFamilies(),c=calibrationSnapshot();
  const total={tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,weakFalsePositive:0,safeMiss:0};
  for(const n of ['P1','P2','P3'])for(const k of Object.keys(total))total[k]+=+a[n]?.[k]||0;
  const fam=[];
  for(const n of ['P1','P2','P3'])for(const r of af[n]||[])fam.push({player:n,...r});
  const topFalse=fam.filter(r=>(r.falsePositive||0)+(r.weakFalsePositive||0)>0)
    .sort((x,y)=>((y.falsePositive||0)-(x.falsePositive||0))||((y.weakFalsePositive||0)-(x.weakFalsePositive||0))||(y.tested-x.tested)).slice(0,12);
  const demoted=[...(c.source||[]),...(c.family||[])].filter(r=>r.watchOnly).slice(0,20);
  return frozenCopy({at:Date.now(),total,players:a,topFalse,demoted});
}
function reportText(){return JSON.stringify(reportSnapshot(),null,2);}
function summaryText(){return JSON.stringify(summarySnapshot(),null,2);}""",
'summary helpers')

rep(
"""    snapshot(){return reportSnapshot();},
    report(){const t=reportText();self.console.log(t);return t;},
    quiet(on=true){QUIET=!!on;self.console.log(QUIET?'🔇 WOF实时日志已静音，统计继续':'🔊 WOF实时日志已恢复');return QUIET;},""",
"""    snapshot(){return reportSnapshot();},
    summary(){return summarySnapshot();},
    report(){const t=reportText();self.console.log(t);return t;},
    reportShort(){const t=summaryText();self.console.log(t);return t;},
    quiet(on=true){QUIET=!!on;self.console.log(QUIET?'🔇 WOF实时日志已静音，统计继续':'🔊 WOF实时日志已恢复');return QUIET;},""",
'API compact summary')

rep("version:'offline-dynamic-spectator-calibrated-v4.6.1'","version:'offline-dynamic-spectator-calibrated-v4.6.2'",'version')
rep("qlog('✅ WOF V4.6.1 置信度分层观战版启动');","qlog('✅ WOF V4.6.2 快速在线降级观战版启动');",'startup')
rep(
"qlog('📸 需要固定数据时用 WOFV4.report()；可先 WOFV4.quiet(true) 静音但继续统计');",
"qlog('📸 快照: WOFV4.reportShort() 看精简统计；WOFV4.report() 看完整数据');",
'report hint')

p.write_text(s,encoding='utf-8')
print('patched V4.6.2',len(s))
