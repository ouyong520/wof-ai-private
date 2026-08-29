from pathlib import Path
p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')

s=s.replace("let AUTO_LOCAL=true,LOCAL_NAME=null;","let AUTO_LOCAL=true,LOCAL_NAME=null,LOCAL_SEAT=null,LOCAL_MODE='none';",1)

old="""  function syncLocalPlayer(force=false){
    if(!AUTO_LOCAL)return LOCAL_NAME;
    const n=localPlayerNo(),name=n?'P'+n:null;
    if(!force&&name===LOCAL_NAME)return LOCAL_NAME;
    const prev=LOCAL_NAME;LOCAL_NAME=name;
    for(const p of PLAYERS){
      const on=p.name===name;
      if(TRACK[p.name]!==on){TRACK[p.name]=on;resetPlayerRuntime(p.name);}
    }
    if(name&&name!==prev)console.log('🎮 本机玩家识别:',name,'(_0x2f9e12='+n+') — 只预测/审计本机玩家');
    if(!name&&prev)console.log('⚪ 暂未识别本机玩家，暂停玩家预测/审计');
    return LOCAL_NAME;
  }
"""
new="""  function livePlayerNames(){
    const out=[];
    for(const p of PLAYERS)if(readPlayer(p.base,p.name))out.push(p.name);
    return out;
  }
  function resolveLocalActor(){
    const seat=localPlayerNo(),seatName=seat?'P'+seat:null,live=livePlayerNames();
    if(seatName&&live.includes(seatName))return{name:seatName,seat,mode:'seat',live};
    if(live.length===1)return{name:live[0],seat,mode:'sole-live-fallback',live};
    return{name:null,seat,mode:seatName?'seat-object-missing':'seat-unknown',live};
  }
  function syncLocalPlayer(force=false){
    if(!AUTO_LOCAL)return LOCAL_NAME;
    const r=resolveLocalActor(),name=r.name;
    if(!force&&name===LOCAL_NAME&&r.seat===LOCAL_SEAT&&r.mode===LOCAL_MODE)return LOCAL_NAME;
    const prev=LOCAL_NAME,prevMode=LOCAL_MODE;
    LOCAL_NAME=name;LOCAL_SEAT=r.seat;LOCAL_MODE=r.mode;
    for(const p of PLAYERS){
      const on=p.name===name;
      if(TRACK[p.name]!==on){TRACK[p.name]=on;resetPlayerRuntime(p.name);}
    }
    if(name&&(name!==prev||r.mode!==prevMode))console.log('🎮 本机玩家映射:',name,'seat',r.seat??'?','mode',r.mode,'live',r.live.join(','));
    if(!name&&(prev||force))console.log('⚪ 暂未映射本机角色','seat',r.seat??'?','live',r.live.join(',')||'none','— 暂停玩家预测/审计');
    return LOCAL_NAME;
  }
"""
if old not in s: raise SystemExit('syncLocalPlayer block not found')
s=s.replace(old,new,1)

s=s.replace("last={at:now,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),players:{}","last={at:now,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),localSeat:LOCAL_SEAT,localMode:LOCAL_MODE,players:{}",1)

s=s.replace("function useLocalPlayer(){AUTO_LOCAL=true;syncLocalPlayer(true);return {localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),tracked:{...TRACK}};}","function useLocalPlayer(){AUTO_LOCAL=true;syncLocalPlayer(true);return {localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),localSeat:LOCAL_SEAT,localMode:LOCAL_MODE,tracked:{...TRACK}};}",1)

s=s.replace("version:'offline-dynamic-local-p123-v4.3.5'","version:'offline-dynamic-local-p123-v4.3.6'",1)
s=s.replace("status(){return{version:this.version,db:this.dbInfo,last:this.last,autoLocal:AUTO_LOCAL,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),tracked:{...TRACK},players:PS,audit:auditSnapshot(),auditFamilies:auditFamilies()};}","status(){return{version:this.version,db:this.dbInfo,last:this.last,autoLocal:AUTO_LOCAL,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),localSeat:LOCAL_SEAT,localMode:LOCAL_MODE,livePlayers:livePlayerNames(),tracked:{...TRACK},players:PS,audit:auditSnapshot(),auditFamilies:auditFamilies()};}",1)
s=s.replace("localPlayer(){return {name:LOCAL_NAME,no:localPlayerNo(),auto:AUTO_LOCAL,tracked:{...TRACK}};}","localPlayer(){const r=resolveLocalActor();return {name:LOCAL_NAME,no:localPlayerNo(),seat:LOCAL_SEAT,mode:LOCAL_MODE,live:r.live,auto:AUTO_LOCAL,tracked:{...TRACK}};}",1)
s=s.replace("console.log('✅ WOF V4.3.5 本机玩家自动识别观战版启动');","console.log('✅ WOF V4.3.6 本机角色容错映射观战版启动');",1)
s=s.replace("console.log('✅ 自动读取 Worker _0x2f9e12 → P1/P2/P3，只预测本机玩家 × 20怪 × Future Danger Map');","console.log('✅ 本机seat优先；若seat对应RAM对象不存在且仅1个玩家对象存活，则自动映射唯一存活角色 × 20怪 × Future Danger Map');",1)

p.write_text(s,encoding='utf-8')
