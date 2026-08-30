(async()=>{
'use strict';
const SRC='https://raw.githubusercontent.com/ouyong520/wof-ai-private/72c7170b0b87b2bfb1fbc3863dbd33a37b86dc16/wof_state_dispatch_lock.js';
const r=await fetch(SRC+'?room='+Date.now(),{cache:'no-store'});
if(!r.ok)throw new Error('recovery fetch failed '+r.status);
const s=await r.text();
if(!s.includes('New-room recovery')&&!s.includes('v2-self-recover'))throw new Error('unexpected stale recovery script');
console.log('✅ room-recovery bootstrap loaded · immutable commit 72c7170');
return (0,eval)(s);
})();
