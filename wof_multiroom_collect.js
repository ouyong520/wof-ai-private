(async()=>{
  'use strict';
  const CFG={
    dbName:'wof-multiroom-audit-v1',
    store:'sessions',
    durationMs:10*60*1000,
    checkpointMs:10*1000,
    runtimeUrl:'https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_v4_install_once.js'
  };

  function id(){
    try{return crypto.randomUUID().slice(0,8);}catch(_){return Math.random().toString(36).slice(2,10);}
  }
  function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
  function clone(x){return x==null?x:JSON.parse(JSON.stringify(x));}
  function openDb(){
    return new Promise((resolve,reject)=>{
      const q=indexedDB.open(CFG.dbName,1);
      q.onupgradeneeded=()=>{
        const db=q.result;
        if(!db.objectStoreNames.contains(CFG.store)){
          const s=db.createObjectStore(CFG.store,{keyPath:'id'});
          s.createIndex('startedAt','startedAt',{unique:false});
          s.createIndex('status','status',{unique:false});
        }
      };
      q.onsuccess=()=>resolve(q.result);
      q.onerror=()=>reject(q.error);
    });
  }
  async function put(db,row){
    return new Promise((resolve,reject)=>{
      const tx=db.transaction(CFG.store,'readwrite');
      tx.objectStore(CFG.store).put(row);
      tx.oncomplete=()=>resolve(true);
      tx.onerror=()=>reject(tx.error);
      tx.onabort=()=>reject(tx.error||new Error('IndexedDB transaction aborted'));
    });
  }
  function snap(){
    const s=self.WOFV4?.summary?.();
    return s?clone(s):null;
  }
  function misses(){
    const a=self.WOFV4?.misses?.();
    return Array.isArray(a)?clone(a.slice(-120)):[];
  }

  if(!self.WOFV4||!String(self.WOFV4.version||'').includes('v4.11.1')){
    const code=await fetch(CFG.runtimeUrl+'?'+Date.now()).then(r=>{if(!r.ok)throw new Error('runtime fetch '+r.status);return r.text();});
    (0,eval)(code);
    for(let i=0;i<50&&!self.WOFV4;i++)await sleep(100);
  }
  if(!self.WOFV4)throw new Error('WOFV4 runtime not available');
  self.WOFV4.spectateAll?.();
  self.WOFV4.quiet?.(true);

  if(self.__WOF_MULTIROOM_COLLECTOR?.running){
    console.log('🟦 多房间采集已在运行',self.__WOF_MULTIROOM_COLLECTOR.status());
    return self.__WOF_MULTIROOM_COLLECTOR.status();
  }

  const db=await openDb();
  const startedAt=Date.now(),sid='room-'+id();
  const row={
    schema:'wof-multiroom-audit-v1',
    id:sid,
    status:'running',
    startedAt,
    plannedEndAt:startedAt+CFG.durationMs,
    latestAt:startedAt,
    lastHeartbeatAt:startedAt,
    completedAt:null,
    runtimeVersion:self.WOFV4.version,
    workerLocation:String(self.location?.href||''),
    durationTargetMs:CFG.durationMs,
    checkpointMs:CFG.checkpointMs,
    start:snap(),
    checkpoints:[],
    final:null,
    misses:[],
    error:null
  };
  await put(db,row);

  let running=true,timer=null,finishing=false;
  async function checkpoint(final=false){
    if(finishing&&!final)return;
    const now=Date.now(),s=snap();
    row.latestAt=now;row.lastHeartbeatAt=now;
    if(s){
      if(final)row.final=s;
      else{
        row.checkpoints.push({at:now,summary:s});
        if(row.checkpoints.length>72)row.checkpoints.shift();
      }
    }
    if(final)row.misses=misses();
    await put(db,row);
  }
  async function finish(reason='complete'){
    if(finishing)return;
    finishing=true;running=false;
    if(timer){clearInterval(timer);timer=null;}
    try{
      row.status=reason==='complete'?'complete':'stopped';
      row.completedAt=Date.now();
      await checkpoint(true);
      row.latestAt=row.completedAt;row.lastHeartbeatAt=row.completedAt;
      await put(db,row);
      console.log('✅ 多房间采集结束',sid,row.status,'现在可运行下载脚本');
    }catch(e){
      row.status='error';row.error=String(e?.stack||e);row.completedAt=Date.now();
      try{await put(db,row);}catch(_){}
      console.error('❌ 多房间采集结束失败',e);
    }finally{
      try{db.close();}catch(_){}
      finishing=false;
    }
  }

  timer=setInterval(()=>{
    checkpoint(false).catch(e=>console.error('采集checkpoint失败',e));
    if(Date.now()>=row.plannedEndAt)finish('complete');
  },CFG.checkpointMs);

  self.__WOF_MULTIROOM_COLLECTOR={
    get running(){return running;},
    id:sid,
    status(){return {id:sid,running,status:row.status,startedAt:row.startedAt,plannedEndAt:row.plannedEndAt,latestAt:row.latestAt,checkpoints:row.checkpoints.length,version:row.runtimeVersion};},
    checkpoint(){return checkpoint(false);},
    finish(){return finish('stopped');}
  };

  console.log('🟢 多房间采集启动',sid,'| 10分钟 | 每10秒落盘 | V4.11.1审计去污染');
  console.log('🟢 房间中途关闭也没关系：已落盘的片段仍会保留，导出时自动标记 interrupted');
  return self.__WOF_MULTIROOM_COLLECTOR.status();
})().catch(e=>console.error('❌ 多房间采集启动失败',e));
