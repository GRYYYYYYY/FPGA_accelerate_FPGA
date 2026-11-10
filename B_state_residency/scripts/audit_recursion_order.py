from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for group,base in [('sources',out/'sources'),('artifacts',out)]:
  for name,h in m[group].items():assert sha(base/name)==h,name
 assert all(c['exit_code']==0 for c in m['commands']) and len(m['commands'])==4
 src=out/'sources';ref=(src/'reference/trace.cpp').read_text();a=(src/'immediate.cpp').read_text();b=(src/'deferred.cpp').read_text()
 assert b==a.replace('            exploreAndExpand(st, child);','            order_deferred.push_back(child);',1)
 norm=a[a.index(ref.splitlines()[0]):]
 norm=norm.replace('    std::vector<int> order_deferred;\n','',1).replace('\n        record_push(child,newPartial,newTotal,lookahead,st.sequence);','',1).replace('\n        record_expand(rnode);','',1).replace('if (TLD(childRNode).visited == seq) { record_skip(rnode,childRNode); continue; }','if (TLD(childRNode).visited == seq) continue;',1)
 assert norm==ref,'observer normalization must recover entire original source'
 case=(src/'case.cpp').read_text();assert 'r.cfg={};r.cfg.shareExponent=2.0f;r.cfg.wirelengthWeight=0.8f;' in case
 assert '*r.childrenCache[0]={1,2};*r.childrenCache[1]={2};'in case
 logs=[(out/(k+'_execute.log')).read_text().splitlines() for k in ['immediate','deferred']]
 events=[[x for x in l if x[0]in 'EPS']for l in logs]
 assert [x.split()[:2]for x in events[0]]==[['E','0'],['P','1'],['E','1'],['P','2'],['S','0']]
 assert [x.split()[:2]for x in events[1]]==[['E','0'],['P','1'],['P','2'],['E','1'],['S','1'],['E','2']]
 labels=[{int(x.split()[1]):x.split()[2:]for x in l if x.startswith('L ')}for l in logs]
 assert len(labels[0])==len(labels[1])==5
 for n in [0,1,3,4]:assert labels[0][n]==labels[1][n]
 assert labels[0][2]==['4089999a','402ccccd','1','77','0']
 assert labels[1][2]==['40400000','3fb33334','0','77','0']
 assert [x for x in logs[0]if x.startswith('Q ')]==['Q 2 4089999a']
 assert not any(x.startswith('Q ')for x in logs[1])
 record={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'events':events,'node2_labels': [l[2]for l in labels],'scope':m['scope']}
 (out/'source_bound_audit.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if __name__=='__main__':main()
