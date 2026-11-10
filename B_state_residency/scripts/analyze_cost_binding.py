"""Extract cost integration ordering and persistence requirements from frozen CPU source."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
 source=ROOT/'results/graph_image_20261024/reference/trace.cpp';s=source.read_text()
 def body(start,end):return s[s.index(start):s.index(end,s.index(start))]
 cost=body('    void evaluateCostAndPush(State& st,','    void exploreAndExpand(State& st,')
 ordered=['int countSourceUses = searchCountUser(childRnode, c.netIdx);','TLD(childRnode).prev = rnode;','float newPartial = TLD(rnode).upstream;','newPartial += getNodeCostSearch','int childY = searchEndY(childRnode);','push(st, childRnode, newPartial, newTotal, lookahead);']
 assert [cost.index(x)for x in ordered]==sorted(cost.index(x)for x in ordered)
 push=body('    void push(State& st,','    void evaluateCostAndPush(State& st,')
 pushes=['TLD(child).lb = newTotal;','TLD(child).upstream = newPartial;','TLD(child).visited = st.sequence;','if (lookahead)','st.queue->offer(newTotal, child);']
 assert [push.index(x)for x in pushes]==sorted(push.index(x)for x in pushes)
 assert 'dyn[id].hist * presentCongestionCost'in s and 'hist is PERSISTENT'in s
 fragments=ordered+pushes+['st.queue->clear();','int p = TLD(id).prev;','dyn[id].hist += overuse * historicalCongestionFactor;']
 locations={x:[s[:i].count('\n')+1 for i in range(len(s))if s.startswith(x,i)]for x in fragments}
 result={'status':'passed','scope':'Source order and dependency analysis only; not an integrated cost RTL test','source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'locations':locations,'order':['access decision','EARLY: query frontier CLEAR5 succeeds','same-net count/occupancy snapshot under operation lock','prev write succeeds','read parent upstream and post-prev geometry; read persistent history and frozen price/net inputs','exact cost arithmetic','lb then upstream then visited writes succeed','lookahead: recursive expansion; otherwise Frontier OFFER succeeds'],'missing_authorities':['design-level history storage/update independent of query label epoch','price table/version and design update fence','net center/fanout/HPWL and connection/share/weight parameter snapshots','integer geometry and cost packet construction after prev write','joined label writes, frontier and recursive stack']}
 out=Path(sys.argv[1]);assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='locations'},indent=2))
if __name__=='__main__':main()
