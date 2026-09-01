from __future__ import annotations
import types, unittest
from dataclasses import dataclass
import discovery_v2_sync as d
WORLD='5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62'
def I(ok=True,sha=WORLD): return {'ok':ok,'identity':{'ok':ok,'sha256':sha},'reason':'ok' if ok else 'bad'}
class S:
 def __init__(self,c,t,s): self.client=c;self.target_id=t;self.session_id=s
 def request(self,m,params=None,timeout=None): self.client.methods.append((self.target_id,m));return {}
 def evaluate(self,e,await_promise=False,timeout=8):
  self.client.evals.append((self.target_id,e));x=self.client.state.get(self.target_id,{})
  if e=='L': return x.get('light',{'moduleOk':True,'heapOk':True,'ramWithinHeap':True})
  if e=='I': return x.get('identity',I())
  if e=='F': return x.get('full',{'ok':True,'identity':{'sha256':WORLD}})
 def close(self): pass
class C:
 def __init__(self,state=None,events=None): self.state=state or {};self.events=events or [];self.sent=False;self.methods=[];self.evals=[]
 def attach(self,t): return S(self,t,'sid-'+t)
 def event_cursor(self): return 0
 def wait_for_events(self,cursor,*,timeout,predicate=None):
  if self.sent:return cursor,[]
  self.sent=True;return 1,[x for x in self.events if predicate is None or predicate(x)]
@dataclass
class E: host:str;port:int
class M:
 def __init__(self,c,e=None):
  self.client=c;self.endpoint=e;self._wof052l_recorder_module=types.SimpleNamespace(WORLD_SHA256=WORLD,LIGHT_PROBE='L',CdpSession=S);self._wof052l_identity_probe_js='I';self._wof052l_identity_cache={};self.probe_js='F'
def P(i='p'): return {'targetId':i,'type':'page','url':'https://x/'+i}
def W(i='w',**k): x={'targetId':i,'type':'worker','url':'/gstyphoon.js'};x.update(k);return x
def A(parent,t,s=None): return {'method':'Target.attachedToTarget','sessionId':parent,'params':{'sessionId':s or 'sid-'+t['targetId'],'targetInfo':t}}
class T(unittest.TestCase):
 def test_matrix(self):
  cases=[]
  cases.append(('direct',M(C({'w':{'identity':I()}})),[P(),W(parentId='p')],lambda r,d:r and r[0].path=='direct-worker'))
  cases.append(('page-related',M(C({'w':{'identity':I()}},[A('sid-p',W())])),[P()],lambda r,d:r and r[0].path=='page-autoattach'))
  f={'targetId':'f','type':'iframe','url':'https://x/f'}
  cases.append(('iframe',M(C({'w':{'identity':I()}},[A('sid-p',f,'sid-f'),A('sid-f',W())])),[P()],lambda r,d:r and d['relatedPages'][0]['relatedTopology'][-1]['depth']==2))
  cases.append(('url-shape',M(C({'w':{'identity':I()}})),[P(),{'targetId':'w','type':'shared_worker','url':'https://cdn/worker-main.mjs?v=1','parentId':'p'}],lambda r,d:len(r)==1))
  cases.append(('wrong-id',M(C({'w':{'identity':I(False,'0'*64)}})),[P(),W(parentId='p')],lambda r,d:not r and any(x.get('status')=='wrong-identity' for x in d['directWorkers'])))
  cases.append(('wasm-wait',M(C({'w':{'light':{'moduleOk':False,'heapOk':False,'ramWithinHeap':False}}})),[P(),W(parentId='p')],lambda r,d:not r and any(x.get('status')=='wasm-not-ready' for x in d['directWorkers'])))
  amb=M(C({'w1':{'identity':I()},'w2':{'identity':I()}},[A('sid-p',W('w1')),A('sid-p',W('w2'))]))
  cases.append(('ambiguity',amb,[P()],lambda r,d:not r and d['relatedPages'][0]['ambiguous']))
  for name,m,targets,check in cases:
   with self.subTest(name=name):
    rows,diag=d.discover_candidates(m,targets);self.assertTrue(check(rows,diag));[x.close() for x in rows]
 def test_reload_replacement_and_10_endpoint_isolation(self):
  for wid in ('w1','w2'):
   m=M(C({wid:{'identity':I()}}));rows,_=d.discover_candidates(m,[P(),W(wid,parentId='p')]);self.assertEqual(rows[0].target['targetId'],wid);self.assertIn((wid,'I'),m.client.evals);rows[0].close()
  for i in range(10):
   p,w=f'p{i}',f'w{i}';m=M(C({w:{'identity':I()}}),E('127.0.0.1',9300+i));rows,diag=d.discover_candidates(m,[P(p),W(w,parentId=p)]);self.assertEqual(rows[0].target['targetId'],w);self.assertEqual(diag['endpoint']['port'],9300+i);rows[0].close()
 def test_read_only_install(self):
  class B:
   def __init__(self,*a,**k): self._ws=None;self._closed=types.SimpleNamespace(is_set=lambda:True)
   def close(self): pass
  class R:
   def __init__(self,*a,**k): pass
  class Q:
   def to_json(self,*,final,reason): return {}
  x=types.SimpleNamespace(READ_ONLY_METHODS={'Target.getTargets','Runtime.evaluate'},CdpClient=B,RecorderManager=R,RoomCapture=Q);d.install(x);self.assertIn('Target.setAutoAttach',x.READ_ONLY_METHODS);self.assertNotIn('Input.dispatchKeyEvent',x.READ_ONLY_METHODS);self.assertNotIn('Runtime.callFunctionOn',x.READ_ONLY_METHODS)
if __name__=='__main__':unittest.main()
