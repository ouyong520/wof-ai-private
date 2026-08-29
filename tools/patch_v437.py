from pathlib import Path
p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')

s=s.replace("const TRACK={P1:false,P2:false,P3:false};\n  let AUTO_LOCAL=true,LOCAL_NAME=null,LOCAL_SEAT=null,LOCAL_MODE='none';",
            "const TRACK={P1:true,P2:true,P3:true};\n  let PLAYER_MODE='spectator',LOCAL_NAME=null,LOCAL_SEAT=null,LOCAL_MODE='none';",1)

s=s.replace("if(!AUTO_LOCAL)return LOCAL_NAME;","if(PLAYER_MODE!=='local')return LOCAL_NAME;",1)

old="const now=performance.now();syncLocalPlayer();updatePlayers(now);const d=buildDanger(now);last={at:now,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),localSeat:LOCAL_SEAT,localMode:LOCAL_MODE,players:{},enemyCount:d.enemies.size,dangerPoints:d.danger.length,exact:d.exact,coarse:d.coarse};"
new="const now=performance.now();if(PLAYER_MODE==='local')syncLocalPlayer();updatePlayers(now);const d=buildDanger(now);last={at:now,playerMode:PLAYER_MODE,livePlayers:PLAYERS.filter(p=>!!readPlayer(p.base,p.name)).map(p=>p.name),players:{},enemyCount:d.enemies.size,dangerPoints:d.danger.length,exact:d.exact,coarse:d.coarse};"
if old not in s: raise SystemExit('tick header not found')
s=s.replace(old,new,1)

s=s.replace("    AUTO_LOCAL=false;\n    TRACK[name]=!!on;resetPlayerRuntime(name);",
            "    PLAYER_MODE='manual';\n    TRACK[name]=!!on;resetPlayerRuntime(name);",1)

old="function useLocalPlayer(){AUTO_LOCAL=true;syncLocalPlayer(true);return {localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),localSeat:LOCAL_SEAT,localMode:LOCAL_MODE,tracked:{...TRACK}};}"
new="""function useLocalPlayer(){PLAYER_MODE='local';syncLocalPlayer(true);return {mode:PLAYER_MODE,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),localSeat:LOCAL_SEAT,localMode:LOCAL_MODE,tracked:{...TRACK}};}
  function spectateAll(){
    PLAYER_MODE='spectator';LOCAL_NAME=null;LOCAL_SEAT=null;LOCAL_MODE='spectator';
    for(const p of PLAYERS){if(!TRACK[p.name]){TRACK[p.name]=true;resetPlayerRuntime(p.name);}}
    console.log('👁️ 观战模式：同时预测/审计 RAM 中存在的 P1/P2/P3');
    return {mode:PLAYER_MODE,tracked:{...TRACK}};
  }"""
if old not in s: raise SystemExit('useLocalPlayer function not found')
s=s.replace(old,new,1)

s=s.replace("version:'offline-dynamic-local-p123-v4.3.6'","version:'offline-dynamic-spectator-p123-v4.3.7'",1)

old="status(){return{version:this.version,db:this.dbInfo,last:this.last,autoLocal:AUTO_LOCAL,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),localSeat:LOCAL_SEAT,localMode:LOCAL_MODE,livePlayers:livePlayerNames(),tracked:{...TRACK},players:PS,audit:auditSnapshot(),auditFamilies:auditFamilies()};}"
new="status(){return{version:this.version,db:this.dbInfo,last:this.last,playerMode:PLAYER_MODE,livePlayers:livePlayerNames(),tracked:{...TRACK},players:PS,audit:auditSnapshot(),auditFamilies:auditFamilies()};}"
if old not in s: raise SystemExit('status function not found')
s=s.replace(old,new,1)

old="localPlayer(){const r=resolveLocalActor();return {name:LOCAL_NAME,no:localPlayerNo(),seat:LOCAL_SEAT,mode:LOCAL_MODE,live:r.live,auto:AUTO_LOCAL,tracked:{...TRACK}};}"
new="localPlayer(){const r=resolveLocalActor();return {name:LOCAL_NAME,no:localPlayerNo(),seat:LOCAL_SEAT,mode:PLAYER_MODE,live:r.live,tracked:{...TRACK}};}"
if old not in s: raise SystemExit('localPlayer function not found')
s=s.replace(old,new,1)

s=s.replace("    setPlayerEnabled,\n    useLocalPlayer,","    setPlayerEnabled,\n    useLocalPlayer,\n    spectateAll,",1)

s=s.replace("  syncLocalPlayer(true);\n  timer=setInterval(tick,CFG.tickMs);tick();",
            "  spectateAll();\n  timer=setInterval(tick,CFG.tickMs);tick();",1)

s=s.replace("console.log('✅ WOF V4.3.6 本机角色容错映射观战版启动');","console.log('✅ WOF V4.3.7 全玩家观战预测版启动');",1)
s=s.replace("console.log('✅ 本机seat优先；若seat对应RAM对象不存在且仅1个玩家对象存活，则自动映射唯一存活角色 × 20怪 × Future Danger Map');",
            "console.log('✅ 纯观战：不判断本机seat，同时预测 RAM 中存在的 P1/P2/P3 × 20怪 × Future Danger Map');",1)

p.write_text(s,encoding='utf-8')
