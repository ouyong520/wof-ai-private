(async()=>{
  'use strict';
  const DB='wof-multiroom-audit-v1',STORE='sessions',MAX_AGE_MS=12*60*60*1000;
  function openDb(){
    return new Promise((resolve,reject)=>{
      const q=indexedDB.open(DB,1);
      q.onupgradeneeded=()=>{
        const db=q.result;
        if(!db.objectStoreNames.contains(STORE)){
          const s=db.createObjectStore(STORE,{keyPath:'id'});
          s.createIndex('startedAt','startedAt',{unique:false});
          s.createIndex('status','status',{unique:false});
        }
      };
      q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error);
    });
  }
  function getAll(db){
    return new Promise((resolve,reject)=>{
      const q=db.transaction(STORE,'readonly').objectStore(STORE).getAll();
      q.onsuccess=()=>resolve(q.result||[]);q.onerror=()=>reject(q.error);
    });
  }
  function subObj(a,b){
    const out={};
    for(const k of Object.keys(a||{})){
      if(typeof a[k]==='number'&&typeof (b||{})[k]==='number')out[k]=a[k]-b[k];
    }
    return out;
  }
  function decisionDelta(end,start){
    const e=end?.evaluation?.decisionLoad?.total||end?.decisionLoad?.total||{};
    const s=start?.evaluation?.decisionLoad?.total||start?.decisionLoad?.total||{};
    const d=subObj(e,s);
    const ticks=(d.NONE||0)+(d.SAFE||0)+(d.WATCH||0)+(d.UP||0)+(d.DOWN||0)+(d.AB||0);
    const warning=(d.WATCH||0)+(d.UP||0)+(d.DOWN||0)+(d.AB||0);
    const action=(d.UP||0)+(d.DOWN||0)+(d.AB||0);
    return {...d,ticks,warningTicks:warning,actionTicks:action,
      warningRate:ticks?+(warning/ticks).toFixed(4):null,
      actionRate:ticks?+(action/ticks).toFixed(4):null,
      watchRate:ticks?+((d.WATCH||0)/ticks).toFixed(4):null};
  }
  function summarize(r){
    const end=r.final||r.checkpoints?.[r.checkpoints.length-1]?.summary||null;
    const start=r.start||null;
    const total=subObj(end?.total||{},start?.total||{});
    const completed=(total.hit||0)+(total.changed||0)+(total.enemyChanged||0)+(total.revoked||0)+(total.falsePositive||0)+(total.weakFalsePositive||0);
    const materialized=(total.hit||0)+(total.changed||0)+(total.falsePositive||0)+(total.weakFalsePositive||0);
    const damage=(total.hit||0)+(total.ambiguousDamage||0)+(total.watchCovered||0)+(total.unstableCovered||0)+(total.safeMiss||0);
    return {
      id:r.id,status:r.status,version:r.runtimeVersion,
      startedAt:r.startedAt,endedAt:r.completedAt||r.latestAt,
      durationSec:Math.max(0,Math.round(((r.completedAt||r.latestAt||r.startedAt)-r.startedAt)/1000)),
      checkpoints:r.checkpoints?.length||0,total,
      evaluation:{
        completed,materialized,
        materializationRate:completed?+(materialized/completed).toFixed(4):null,
        naturalPathChangeRate:materialized?+((total.changed||0)/materialized).toFixed(4):null,
        unchangedValidated:(total.hit||0)+(total.falsePositive||0),
        unchangedPrecision:((total.hit||0)+(total.falsePositive||0))?+((total.hit||0)/((total.hit||0)+(total.falsePositive||0))).toFixed(4):null,
        damageEvents:damage,
        rawDamageCoverage:damage?+(((total.hit||0)+(total.ambiguousDamage||0)+(total.watchCovered||0)+(total.unstableCovered||0))/damage).toFixed(4):null,
        stableDamageCoverage:damage?+(((total.hit||0)+(total.ambiguousDamage||0)+(total.watchCovered||0))/damage).toFixed(4):null,
        decisionLoad:decisionDelta(end,start)
      }
    };
  }

  const db=await openDb();
  const cutoff=Date.now()-MAX_AGE_MS;
  const sessions=(await getAll(db)).filter(r=>(r.startedAt||0)>=cutoff).sort((a,b)=>(a.startedAt||0)-(b.startedAt||0));
  db.close();
  if(!sessions.length){console.warn('没有找到最近12小时的多房间采集数据');return null;}
  const summaries=sessions.map(summarize);
  const bundle={
    schema:'wof-multiroom-export-v1',
    exportedAt:Date.now(),
    sessionCount:sessions.length,
    completeCount:sessions.filter(x=>x.status==='complete').length,
    summaries,
    sessions
  };
  const text=JSON.stringify(bundle,null,2);
  const name='wof_multiroom_'+new Date().toISOString().replace(/[:.]/g,'-')+'.json';
  const blob=new Blob([text],{type:'application/json'}),url=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=url;a.download=name;a.style.display='none';document.body.appendChild(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),30000);
  console.table(summaries.map(x=>({room:x.id,status:x.status,min:(x.durationSec/60).toFixed(1),tested:x.total.tested||0,damage:x.evaluation.damageEvents,safeMiss:x.total.safeMiss||0,materialize:x.evaluation.materializationRate,warningRate:x.evaluation.decisionLoad.warningRate})));
  console.log('✅ 已下载',name,'房间数',sessions.length,'完成',bundle.completeCount);
  return bundle;
})().catch(e=>console.error('❌ 多房间导出失败',e));
