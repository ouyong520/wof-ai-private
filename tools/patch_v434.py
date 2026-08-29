from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')
if "offline-dynamic-p1p2-v4.3.3" not in s:
    raise SystemExit('expected V4.3.3 runtime')

s=s.replace(
"  const PH={P1:[],P2:[]};\n  const PS={};\n",
"  const PH={P1:[],P2:[]};\n  const PS={};\n  const TRACK={P1:true,P2:true};\n",
1)

old="""    for(const p of PLAYERS){
      const cur=readPlayer(p.base,p.name);
      if(!cur){PH[p.name]=[];delete PS[p.name];continue;}
"""
new="""    for(const p of PLAYERS){
      if(!TRACK[p.name]){PH[p.name]=[];delete PS[p.name];continue;}
      const cur=readPlayer(p.base,p.name);
      if(!cur){PH[p.name]=[];delete PS[p.name];continue;}
"""
if old not in s: raise SystemExit('updatePlayers target missing')
s=s.replace(old,new,1)

# Add helper just before WOFV4 object.
needle="""  self.WOFV4={
    version:'offline-dynamic-p1p2-v4.3.3',config:CFG,last:null,
"""
repl="""  function setPlayerEnabled(name,on){
    if(!(name in TRACK))throw new Error('player must be P1 or P2');
    TRACK[name]=!!on;PH[name]=[];delete PS[name];
    const A=AUD[name];A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;
    ST[name].k='';ST[name].n=0;ST[name].v=null;PRINT[name]='';
    console.log(TRACK[name]?'🔵':'⚫',name,TRACK[name]?'已加入预测/审计':'已移出预测/审计（人物可继续留在游戏中）');
    return {...TRACK};
  }

  self.WOFV4={
    version:'offline-dynamic-p1p2-v4.3.4',config:CFG,last:null,
"""
if needle not in s: raise SystemExit('WOFV4 target missing')
s=s.replace(needle,repl,1)

s=s.replace(
"    status(){return{version:this.version,db:this.dbInfo,last:this.last,players:PS,audit:auditSnapshot(),auditFamilies:auditFamilies()};},\n    audit(){return auditSnapshot();},\n",
"    status(){return{version:this.version,db:this.dbInfo,last:this.last,tracked:{...TRACK},players:PS,audit:auditSnapshot(),auditFamilies:auditFamilies()};},\n    tracked(){return {...TRACK};},\n    setPlayerEnabled,\n    onlyP1(){setPlayerEnabled('P1',true);setPlayerEnabled('P2',false);return {...TRACK};},\n    bothPlayers(){setPlayerEnabled('P1',true);setPlayerEnabled('P2',true);return {...TRACK};},\n    audit(){return auditSnapshot();},\n",
1)

s=s.replace("✅ WOF V4.3.3 时间有效性自验证版启动","✅ WOF V4.3.4 玩家追踪过滤观战版启动",1)
s=s.replace("console.log('⚠️ 只预测，不控制任何玩家');","console.log('⚠️ 只预测，不控制任何玩家；P2真人离开时可 WOFV4.setPlayerEnabled(\\'P2\\',false)');",1)

p.write_text(s,encoding='utf-8')
print('patched V4.3.4 tracked-player filter')
