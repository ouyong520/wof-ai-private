from pathlib import Path

p=Path('wof_v4_install_once.js')
s=p.read_text(encoding='utf-8')

assert "offline-dynamic-p1p2-v4.3.4" in s, 'expected V4.3.4 base'

old="""  const PLAYERS=[
    {name:'P1',base:0xFFBE1C},
    {name:'P2',base:0xFFBEFC}
  ];
"""
new="""  const PLAYERS=[
    {name:'P1',base:0xFFBE1C},
    {name:'P2',base:0xFFBEFC},
    {name:'P3',base:0xFFBFDC}
  ];
"""
assert old in s
s=s.replace(old,new,1)

old="""  const PH={P1:[],P2:[]};
  const PS={};
  const TRACK={P1:true,P2:true};

  function updatePlayers(now){
"""
new="""  const PH={P1:[],P2:[],P3:[]};
  const PS={};
  const TRACK={P1:false,P2:false,P3:false};
  let AUTO_LOCAL=true,LOCAL_NAME=null;

  function localPlayerNo(){
    try{const n=Number(_0x2f9e12);return n>=1&&n<=3?n:null;}catch(e){return null;}
  }
  function resetPlayerRuntime(name){
    PH[name]=[];delete PS[name];
    const A=AUD?.[name];if(A){A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;}
    const S=ST?.[name];if(S){S.k='';S.n=0;S.v=null;}
    if(name in PRINT)PRINT[name]='';
  }
  function syncLocalPlayer(force=false){
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

  function updatePlayers(now){
"""
assert old in s
s=s.replace(old,new,1)

old="""  const ST={P1:{k:'',n:0,v:null},P2:{k:'',n:0,v:null}},PRINT={P1:'',P2:''};
"""
new="""  const ST={P1:{k:'',n:0,v:null},P2:{k:'',n:0,v:null},P3:{k:'',n:0,v:null}},PRINT={P1:'',P2:'',P3:''};
"""
assert old in s
s=s.replace(old,new,1)

old="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}}
};
"""
new="""const AUD={
  P1:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}},
  P2:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}},
  P3:{pending:null,prevHp:null,lastWarnAt:-1e9,stats:{tested:0,hit:0,changed:0,enemyChanged:0,ambiguousDamage:0,revoked:0,falsePositive:0,safeMiss:0},byFamily:{}}
};
"""
assert old in s
s=s.replace(old,new,1)

s=s.replace("for(const n of ['P1','P2'])out[n]=", "for(const n of ['P1','P2','P3'])out[n]=", 2)

old="""  function tick(){
  const now=performance.now();updatePlayers(now);const d=buildDanger(now);last={at:now,players:{},enemyCount:d.enemies.size,dangerPoints:d.danger.length,exact:d.exact,coarse:d.coarse};
"""
new="""  function tick(){
  const now=performance.now();syncLocalPlayer();updatePlayers(now);const d=buildDanger(now);last={at:now,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),players:{},enemyCount:d.enemies.size,dangerPoints:d.danger.length,exact:d.exact,coarse:d.coarse};
"""
assert old in s
s=s.replace(old,new,1)

old="""  function setPlayerEnabled(name,on){
    if(!(name in TRACK))throw new Error('player must be P1 or P2');
    TRACK[name]=!!on;PH[name]=[];delete PS[name];
    const A=AUD[name];A.pending=null;A.prevHp=null;A.lastWarnAt=-1e9;
    ST[name].k='';ST[name].n=0;ST[name].v=null;PRINT[name]='';
    console.log(TRACK[name]?'🔵':'⚫',name,TRACK[name]?'已加入预测/审计':'已移出预测/审计（人物可继续留在游戏中）');
    return {...TRACK};
  }

  self.WOFV4={
    version:'offline-dynamic-p1p2-v4.3.4',config:CFG,last:null,
    dbInfo:{exact:Object.keys(DB.e).length,coarse:Object.keys(DB.c).length,activeStart:Object.keys(DB.a).length,families:Object.keys(DB.f).length},
    status(){return{version:this.version,db:this.dbInfo,last:this.last,tracked:{...TRACK},players:PS,audit:auditSnapshot(),auditFamilies:auditFamilies()};},
    tracked(){return {...TRACK};},
    setPlayerEnabled,
    onlyP1(){setPlayerEnabled('P1',true);setPlayerEnabled('P2',false);return {...TRACK};},
    bothPlayers(){setPlayerEnabled('P1',true);setPlayerEnabled('P2',true);return {...TRACK};},
    audit(){return auditSnapshot();},
    auditFamilies(){return auditFamilies();},
    stop(){if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF V4关闭');}
  };
  timer=setInterval(tick,CFG.tickMs);tick();
  console.log('✅ WOF V4.3.4 玩家追踪过滤观战版启动');
  console.log('🧪 验证: 🎯命中 / 🟡路径改变 / 🟤分支改变 / 🔵预测撤销 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判');
  console.log('✅ DB',self.WOFV4.dbInfo.families,'Family / exact',self.WOFV4.dbInfo.exact,'/ coarse',self.WOFV4.dbInfo.coarse);
  console.log('✅ P1+P2动态轨迹 × 20怪 × 3D/斜向轨迹 × 每Family危险范围');
  console.log('⚠️ 只预测，不控制任何玩家；P2真人离开时可 WOFV4.setPlayerEnabled(\\'P2\\',false)');
"""
new="""  function setPlayerEnabled(name,on){
    if(!(name in TRACK))throw new Error('player must be P1/P2/P3');
    AUTO_LOCAL=false;
    TRACK[name]=!!on;resetPlayerRuntime(name);
    console.log(TRACK[name]?'🔵':'⚫',name,TRACK[name]?'已手动加入预测/审计':'已手动移出预测/审计');
    return {...TRACK};
  }
  function useLocalPlayer(){AUTO_LOCAL=true;syncLocalPlayer(true);return {localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),tracked:{...TRACK}};}

  self.WOFV4={
    version:'offline-dynamic-local-p123-v4.3.5',config:CFG,last:null,
    dbInfo:{exact:Object.keys(DB.e).length,coarse:Object.keys(DB.c).length,activeStart:Object.keys(DB.a).length,families:Object.keys(DB.f).length},
    status(){return{version:this.version,db:this.dbInfo,last:this.last,autoLocal:AUTO_LOCAL,localPlayer:LOCAL_NAME,localPlayerNo:localPlayerNo(),tracked:{...TRACK},players:PS,audit:auditSnapshot(),auditFamilies:auditFamilies()};},
    localPlayer(){return {name:LOCAL_NAME,no:localPlayerNo(),auto:AUTO_LOCAL,tracked:{...TRACK}};},
    tracked(){return {...TRACK};},
    setPlayerEnabled,
    useLocalPlayer,
    audit(){return auditSnapshot();},
    auditFamilies(){return auditFamilies();},
    stop(){if(timer){clearInterval(timer);timer=null;}console.log('⛔ WOF V4关闭');}
  };
  syncLocalPlayer(true);
  timer=setInterval(tick,CFG.tickMs);tick();
  console.log('✅ WOF V4.3.5 本机玩家自动识别观战版启动');
  console.log('🧪 验证: 🎯命中 / 🟡路径改变 / 🟤分支改变 / 🔵预测撤销 / ⚪歧义掉血 / 🔴高可信误报 / ❌SAFE漏判');
  console.log('✅ DB',self.WOFV4.dbInfo.families,'Family / exact',self.WOFV4.dbInfo.exact,'/ coarse',self.WOFV4.dbInfo.coarse);
  console.log('✅ 自动读取 Worker _0x2f9e12 → P1/P2/P3，只预测本机玩家 × 20怪 × Future Danger Map');
  console.log('⚠️ 只预测，不控制任何玩家');
"""
assert old in s, 'API/startup block not found'
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('patched to V4.3.5',len(s))
