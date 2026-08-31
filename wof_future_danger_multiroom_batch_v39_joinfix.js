(async()=>{
'use strict';
const DB='wof-future-danger-multiroom-v1',STORE='control',KEY='active';
const EXTEND_MS=125000,GRACE_MS=150000,MAX_ROOMS=5;
function openDb(){return new Promise((res,rej)=>{const q=indexedDB.open(DB,1);q.onupgradeneeded=()=>{const db=q.result;if(!db.objectStoreNames.contains('control'))db.createObjectStore('control',{keyPath:'key'});if(!db.objectStoreNames.contains('rooms')){const s=db.createObjectStore('rooms',{keyPath:'key'});s.createIndex('batchId','batchId',{unique:false});}};q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error);});}
async function extendActive(){const db=await openDb();try{await new Promise((res,rej)=>{const tx=db.transaction(STORE,'readwrite'),s=tx.objectStore(STORE),q=s.get(KEY);q.onsuccess=()=>{const c=q.result,now=Date.now();if(c&&!c.finalizedAt&&!c.combined&&(c.roomKeys?.length||0)<MAX_ROOMS&&now<(c.createdAt||0)+10*60*1000){c.joinUntil=Math.max(Number(c.joinUntil||0),now+EXTEND_MS);c.finalizeDeadline=Math.max(Number(c.finalizeDeadline||0),c.joinUntil+GRACE_MS);s.put(c);console.log('🟢 [WOF-039] batch join window extended',c.batchId,'rooms',c.roomKeys?.length||0);} };q.onerror=()=>rej(q.error);tx.oncomplete=()=>res();tx.onerror=()=>rej(tx.error);});}finally{try{db.close()}catch(_){}}}
await extendActive();
const url='https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_batch_v39.js?x='+Date.now();
const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw new Error('WOF-039 fetch '+r.status);return(0,eval)(await r.text());
})().catch(e=>{console.error('[WOF-039 JOINFIX] ERROR',e);throw e;});