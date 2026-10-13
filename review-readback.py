import json,hashlib
from pathlib import Path
p=Path(__file__).parent
def pages(s):
 a=[];d=json.JSONDecoder()
 while s.strip():
  s=s.lstrip();v,n=d.raw_decode(s);a.extend(v);s=s[n:]
 return a
changes=[]
for name in ['reviews','review-comments','issue-comments']:
 before={x['id']:x for x in pages((p/(name+'-before.json')).read_text())}
 for x in pages((p/(name+'-final.json')).read_text()):
  if x['user']['login']=='SunnyQjm':continue
  y=before.get(x['id'])
  fields=['body','state','commit_id','updated_at','submitted_at']
  if y is None or any(x.get(k)!=y.get(k) for k in fields):changes.append({'surface':name,'item':x})
triage=json.loads((p/'review-triage.json').read_text())['accepted']
unresolved=[]
for change in changes:
 item=change['item'];fingerprint=hashlib.sha256(json.dumps({k:item.get(k) for k in fields},sort_keys=True).encode()).hexdigest()
 if not any(t['surface']==change['surface'] and t['id']==item['id'] and t['login']==item['user']['login'] and t['fingerprint']==fingerprint for t in triage):unresolved.append(change)
r={'external_changes':changes,'unresolved_external_changes':unresolved,'full_pagination':True,'review_triage_file':'review-triage.json'}
(p/'review-readback.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
assert not unresolved,'new untriaged external review requires examination before cleanup'
