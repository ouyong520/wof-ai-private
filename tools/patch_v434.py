from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-p1p2-v4.3.3" not in s:
    raise SystemExit('expected V4.3.3 runtime')

# Lifecycle/audit timing.
s=s.replace("    auditRevokeLeadMs:60,\n", "    auditRevokeLeadMs:60,\n    playerWarmupMs:600,\n    safeMissConfirmMs:500,\n", 1)

# Track online/offline state and keep HP=0 players out of the planner.
s=s.replace("  const PH={P1:[],P2:[]};\n  const PS={};\n", "  const PH={P1:[],P2:[]};\n  const PS={};\n  const LIFE={P1:{online:false,warmUntil:0},P2:{online:false,warmUntil:0}};\n", 1)
old="""      const cur=readPlayer(p.base,p.name);
      if(!cur){PH[p.name]=[];delete PS[p.name];continue;}
      const h=PH[p.name]; h.push({t:now,x:cur.x,y:cur.y,z:cur.z});
"""
new="""      const cur=readPlayer(p.base,p.name),lf=LIFE[p.name];
      if(!cur||cur.hp<=0){
        if(lf.online)console.log('⚫',p.name,'玩家离线/HP0，暂停预测与审计');
        lf.online=false;lf.warmUntil=0;PH[p.name]=[];delete PS[p.name];continue;
      }
      if(!lf.online){lf.online=true;lf.warmUntil=now+CFG.playerWarmupMs;console.log('🔵',p.name,'玩家上线，审计预热'+CFG.playerWarmupMs+'ms');}
      const h=PH[p.name]; h.push({t:now,x:cur.x,y:cur.y,z:cur.z});
"""
if old not in s: raise SystemExit('updatePlayers head target missing')
s=s.replace(old,new,1)
s=s.replace("      PS[p.name]={name:p.name,x:cur.x,y:cur.y,z:cur.z,vx,vy,vz,hp:cur.hp};", "      PS[p.name]={name:p.name,x:cur.x,y:cur.y,z:cur.z,vx,vy,vz,hp:cur.hp,warmup:now<lf.warmUntil};", 1)

# Add deferred SAFE-miss lifecycle state.
s=s.replace("P1:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,falsePositive:0,safeMiss:0,revoked:0},byFamily:{}}", "P1:{pending:null,prevHp:null,lastWarnAt:-1e9,safeMissPending:null,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,falsePositive:0,safeMiss:0,revoked:0,lifecycleIgnored:0},byFamily:{}}", 1)
s=s.replace("P2:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,falsePositive:0,safeMiss:0,revoked:0},byFamily:{}}", "P2:{pending:null,prevHp:null,lastWarnAt:-1e9,safeMissPending:null,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,falsePositive:0,safeMiss:0,revoked:0,lifecycleIgnored:0},byFamily:{}}", 1)

# Warmup guard: do not audit join/respawn RAM transitions.
needle="""  const hp=ps.hp;
  const e=A.pending;
  if(e)trackEnemy(e,now);

  const dropped=A.prevHp!=null&&hp<A.prevHp;
"""
repl="""  const hp=ps.hp;
  if(ps.warmup){A.pending=null;A.safeMissPending=null;A.prevHp=hp;return;}
  const e=A.pending;
  if(e)trackEnemy(e,now);

  const dropped=A.prevHp!=null&&hp<A.prevHp;
"""
if needle not in s: raise SystemExit('audit warmup target missing')
s=s.replace(needle,repl,1)

# Defer SAFE miss so leave/death countdowns can be discarded when HP reaches zero.
old="""    }else if(now-A.lastWarnAt>350){
      A.stats.safeMiss++;
      console.log('❌',name,'SAFE漏判候选','HP '+A.prevHp+'→'+hp,'近350ms无稳定危险提示');
    }
  }
  A.prevHp=hp;

  const q=A.pending;
"""
new="""    }else if(now-A.lastWarnAt>350){
      if(!A.safeMissPending)A.safeMissPending={from:A.prevHp,to:hp,at:now,lastAt:now};
      else{A.safeMissPending.to=hp;A.safeMissPending.lastAt=now;}
    }
  }
  A.prevHp=hp;

  if(A.safeMissPending&&now-A.safeMissPending.lastAt>=CFG.safeMissConfirmMs){
    const m=A.safeMissPending;
    A.stats.safeMiss++;
    console.log('❌',name,'SAFE漏判候选','HP '+m.from+'→'+m.to,'持续在线'+CFG.safeMissConfirmMs+'ms且近350ms无稳定危险提示');
    A.safeMissPending=null;
  }

  const q=A.pending;
"""
if old not in s: raise SystemExit('safeMiss defer target missing')
s=s.replace(old,new,1)

# Reset audit/stability immediately while player is offline; discard deferred SAFE miss.
old="""  for(const p of PLAYERS){
    const ps=PS[p.name];if(!ps)continue;
    const raw=decision(ps,d.danger),st=stable(p.name,raw);
"""
new="""  for(const p of PLAYERS){
    const ps=PS[p.name];
    if(!ps){
      const A=AUD[p.name];
      if(A.safeMissPending){A.stats.lifecycleIgnored++;A.safeMissPending=null;}
      A.pending=null;A.prevHp=null;ST[p.name].k='';ST[p.name].n=0;ST[p.name].v=null;PRINT[p.name]='';
      continue;
    }
    const raw=decision(ps,d.danger),st=stable(p.name,raw);
"""
if old not in s: raise SystemExit('tick offline reset target missing')
s=s.replace(old,new,1)

s=s.replace("version:'offline-dynamic-p1p2-v4.3.3'", "version:'offline-dynamic-p1p2-v4.3.4'", 1)
s=s.replace("✅ WOF V4.3.3 时间有效性自验证版启动", "✅ WOF V4.3.4 玩家生命周期自验证版启动", 1)
s=s.replace("🧪 验证: 🎯命中 / 🟡路径改变 / 🟤分支改变 / 🔵预测撤销 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判", "🧪 验证: 🎯命中 / 🟡路径改变 / 🟤分支改变 / 🔵预测撤销 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判；⚫离线不审计", 1)

p.write_text(s,encoding='utf-8')
print('patched V4.3.4')
