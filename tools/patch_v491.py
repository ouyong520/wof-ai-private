from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-spectator-calibrated-v4.9'" not in s:
    raise SystemExit('expected V4.9 input')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'missing target: {label}')
    s=s.replace(old,new,1)

rep(
"""    auditRepeatBlockMs:700,
    fallbackZThreshold:80,""",
"""    auditRepeatBlockMs:700,
    missHistoryMs:600,
    missCandidateLimit:5,
    fallbackZThreshold:80,""",
'cfg miss history')

rep(
"if(b.geoFp<3||Object.keys(b.fpFamilies||{}).length<2)return;",
"if(b.geoFp<4||Object.keys(b.fpFamilies||{}).length<3)return;",
'geo class evidence')

rep(
"""  const UNIQUE_ACTIVE=new Map();
  const MULTI_ACTIVE=new Set();""",
"""  const UNIQUE_ACTIVE=new Map();
  const MULTI_ACTIVE=new Set();
  const ENEMY_HISTORY=[];
  const MISS_CASES=[];""",
'history globals')

rep(
"""  function activeOrigin(o,f,lead){""",
"""  function captureEnemyFrame(now){
    const actors=[];
    for(let i=0;i<NSLOTS;i++){
      const o=readActor(POOL+i*STRIDE,i);if(!o)continue;
      const sl=SLOT[i]||{};
      actors.push({slot:i,type:o.type,x:+o.x.toFixed(1),y:+o.y.toFixed(1),z:+o.z.toFixed(1),face:o.face,
        attack:o.attack,anim:o.anim,s0:o.s0,s1:o.s1,s2:o.s2,s3:o.s3,frame:o.frame,locked:sl.locked||null});
    }
    ENEMY_HISTORY.push({t:now,actors});
    while(ENEMY_HISTORY.length&&now-ENEMY_HISTORY[0].t>CFG.missHistoryMs)ENEMY_HISTORY.shift();
  }

  function missEnemyCandidates(ps,now){
    const best=new Map();
    for(const fr of ENEMY_HISTORY){
      const age=Math.max(0,now-fr.t);
      for(const o of fr.actors){
        const dx=Math.abs(ps.x-o.x),dy=Math.abs(ps.y-o.y),dz=Math.abs(ps.z-o.z);
        const active=o.attack!==0;
        const score=dx+dy*4+dz*2+age*.04-(active?70:0)-(o.locked?20:0);
        const prev=best.get(o.slot);
        if(!prev||score<prev.score){
          let startupTop=[];
          if(!active){
            const h=lookup(o);
            if(h)startupTop=chooseFamilies(h.row).slice(0,2).map(x=>x.id);
          }
          best.set(o.slot,{score:+score.toFixed(1),ageMs:Math.round(age),slot:o.slot,type:o.type,attack:o.attack,
            locked:o.locked||null,anim:o.anim,state:[o.s0,o.s1,o.s2,o.s3],frame:o.frame,
            dx:+dx.toFixed(1),dy:+dy.toFixed(1),dz:+dz.toFixed(1),startupTop});
        }
      }
    }
    return [...best.values()].sort((a,b)=>a.score-b.score).slice(0,CFG.missCandidateLimit);
  }

  function captureMissCase(kind,name,ps,raw,now,hp0,hp1){
    const n=raw?.stay?.nearest||null;
    const c={id:MISS_CASES.length+1,kind,player:name,hp:hp0+'→'+hp1,
      at:+now.toFixed(1),pos:[+ps.x.toFixed(1),+ps.y.toFixed(1),+ps.z.toFixed(1)],
      nearest:n?{family:n.family||null,source:n.source||null,variant:n.variant||null,slot:n.slot??null,type:n.type??null,
        t:n.t,confidence:+(+n.confidence||0).toFixed(3),survival:+(+n.survival||0).toFixed(3),
        clearance:raw?.stay?.minClearance==null?null:+raw.stay.minClearance.toFixed(3)}:null,
      candidates:missEnemyCandidates(ps,now)};
    MISS_CASES.push(c);if(MISS_CASES.length>16)MISS_CASES.shift();
    return c;
  }

  function activeOrigin(o,f,lead){""",
'miss forensic helpers')

rep(
"""  function evalPath(p,mode,danger,delay=0){
    let earliest=null,hit=null,min=Infinity;
    for(const d of danger){
      if(d.t<CFG.reactFloorMs||d.confidence<CFG.minConfidence)continue;
      const pp=playerAt(p,mode,d.t,delay),c=clearNorm(pp,d);if(c<min)min=c;
      if(collides(pp,d)&&(earliest===null||d.t<earliest)){earliest=d.t;hit=d;}
    }
    return{mode,safe:earliest===null,collisionMs:earliest,minClearance:isFinite(min)?min:null,hit};
  }""",
"""  function evalPath(p,mode,danger,delay=0){
    let earliest=null,hit=null,min=Infinity,nearest=null;
    for(const d of danger){
      if(d.t<CFG.reactFloorMs||d.confidence<CFG.minConfidence)continue;
      const pp=playerAt(p,mode,d.t,delay),c=clearNorm(pp,d);
      if(c<min){min=c;nearest=d;}
      if(collides(pp,d)&&(earliest===null||d.t<earliest)){earliest=d.t;hit=d;}
    }
    return{mode,safe:earliest===null,collisionMs:earliest,minClearance:isFinite(min)?min:null,hit,nearest};
  }""",
'evalPath nearest')

rep(
"""  const need=action==='SAFE'?2:3;
  if(s.n>=need)s.v=r;""",
"""  const need=action==='SAFE'?2:action==='WATCH'?2:action==='AB'?3:((+r.hitMs||9999)<=300?2:3);
  if(s.n>=need)s.v=r;""",
'urgent stability')

rep(
"""      if(now-A.lastRawWarnAt<=350){
        A.stats.unstableCovered++;
        qlog('🟧',name,'原始危险已覆盖/稳定器未确认','HP '+A.prevHp+'→'+hp,'近350ms有raw危险');
      }else{
        A.stats.safeMiss++;
        qlog('❌',name,'真实SAFE漏判候选','HP '+A.prevHp+'→'+hp,'近350ms raw/stable 都无危险');
      }""",
"""      if(now-A.lastRawWarnAt<=350){
        A.stats.unstableCovered++;
        const mc=captureMissCase('unstableCovered',name,ps,raw,now,A.prevHp,hp);
        qlog('🟧',name,'原始危险已覆盖/稳定器未确认','HP '+A.prevHp+'→'+hp,'case#'+mc.id);
      }else{
        A.stats.safeMiss++;
        const mc=captureMissCase('safeMiss',name,ps,raw,now,A.prevHp,hp);
        qlog('❌',name,'真实SAFE漏判','HP '+A.prevHp+'→'+hp,'case#'+mc.id,
          '候选',mc.candidates.slice(0,3).map(x=>'s'+x.slot+'/T'+x.type+'/A'+x.attack+'/'+(x.locked||'?')).join(' '));
      }""",
'miss capture')

rep(
"""  const geoAdjusted=[...(c.variant||[]),...(c.source||[])].filter(r=>Array.isArray(r.geo)&&Math.min(...r.geo)<.995)
    .sort((x,y)=>Math.min(...x.geo)-Math.min(...y.geo)).slice(0,20);
  const geoClasses=(c.geom||[]).filter(r=>Array.isArray(r.geo)&&((r.geoFp||0)>0||Math.min(...r.geo)<.995))
    .sort((x,y)=>(y.geoFp||0)-(x.geoFp||0)).slice(0,20);
  return frozenCopy({at:Date.now(),total,players:a,topFalse,demoted,geoAdjusted,geoClasses});""",
"""  const geoAdjusted=[...(c.variant||[]),...(c.source||[])].filter(r=>Array.isArray(r.geo)&&Math.min(...r.geo)<.995)
    .sort((x,y)=>Math.min(...x.geo)-Math.min(...y.geo)).slice(0,20);
  const geoClasses=(c.geom||[]).filter(r=>Array.isArray(r.geo)&&((r.geoFp||0)>0||Math.min(...r.geo)<.995))
    .sort((x,y)=>(y.geoFp||0)-(x.geoFp||0)).slice(0,20);
  const validated=total.hit+total.falsePositive;
  const damageEvents=total.hit+total.ambiguousDamage+total.unstableCovered+total.safeMiss;
  const metrics={actionPrecision:validated?+(total.hit/validated).toFixed(3):null,
    rawDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage+total.unstableCovered)/damageEvents).toFixed(3):null,
    stableDamageCoverage:damageEvents?+((total.hit+total.ambiguousDamage)/damageEvents).toFixed(3):null,
    validated,damageEvents};
  return frozenCopy({at:Date.now(),total,metrics,players:a,topFalse,demoted,geoAdjusted,geoClasses,missCases:MISS_CASES.slice(-8)});""",
'summary metrics')

rep(
"""  const now=performance.now();if(PLAYER_MODE==='local')syncLocalPlayer();updatePlayers(now);const d=buildDanger(now);last={at:now,""",
"""  const now=performance.now();if(PLAYER_MODE==='local')syncLocalPlayer();updatePlayers(now);const d=buildDanger(now);captureEnemyFrame(now);last={at:now,""",
'tick history')

rep(
"""    summary(){return summarySnapshot();},
    report(){const t=reportText();self.console.log(t);return t;},""",
"""    summary(){return summarySnapshot();},
    misses(){return frozenCopy(MISS_CASES.slice());},
    report(){const t=reportText();self.console.log(t);return t;},""",
'expose misses')

rep("version:'offline-dynamic-spectator-calibrated-v4.9'","version:'offline-dynamic-spectator-calibrated-v4.9.1'",'version')
rep("qlog('✅ WOF V4.9 共享几何类学习观战版启动');","qlog('✅ WOF V4.9.1 漏判取证/紧急稳定观战版启动');",'startup')
rep(
"qlog('🧱 共享几何类: 同一fallback半径至少3次高可信误报且来自>=2个Family才开始收缩行动核心');",
"qlog('🔬 漏判取证: 真实SAFE漏判自动保存最近600ms敌人状态/ATTACK/Family候选；WOFV4.misses()可查看');\n  qlog('⚡ 稳定器: WATCH与<=300ms紧急UP/DOWN改为2帧确认；AB仍需3帧');\n  qlog('🧱 共享几何类: 至少4次高可信误报且来自>=3个Family才开始收缩行动核心');",
'startup info')

p.write_text(s,encoding='utf-8')
print('patched V4.9.1',len(s))
