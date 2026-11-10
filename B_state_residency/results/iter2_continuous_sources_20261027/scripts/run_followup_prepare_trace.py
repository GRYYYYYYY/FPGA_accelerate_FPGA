"""Isolated original-router capture of the selected connection's native ripup."""
from pathlib import Path
import runpy,sys
import run_followup_query as base
original_loader=base.importlib.util.spec_from_file_location
HOOK='''        if (std::getenv("B_QUERY_SEQUENCE") && st.sequence == std::atoi(std::getenv("B_QUERY_SEQUENCE"))) {
            FILE* f=nqs::open("prepare_ripup.txt");
            std::fprintf(f,"QUERY %d %d %d %d %d %d\\n",st.sequence,st.connIdx,c.netIdx,c.sourceRnode,c.sinkRnode,(int)c.hasAltSinks());
            std::fprintf(f,"PATH"); for(int id:c.rnodes)std::fprintf(f," %d",id); std::fprintf(f,"\\n");
            for(int id:c.rnodes)std::fprintf(f,"BEFORE %d %d %d %d %d\\n",id,ownerNet[id],ownerCnt[id],occCnt[id],countConnectionsOfUser(id,c.netIdx));
            ripUp(c);
            for(int id:c.rnodes)std::fprintf(f,"AFTER %d %d %d %d %d\\n",id,ownerNet[id],ownerCnt[id],occCnt[id],countConnectionsOfUser(id,c.netIdx));
            std::fclose(f);
        } else ripUp(c);'''
def loader(name,path):
 spec=original_loader(name,path)
 if name=='derive_census':
  old=spec.loader.exec_module
  def exec_module(mod):
   old(mod);derive=mod.derive
   def wrapped(code):
    code,changes=derive(code)
    before='        ripUp(c);\n        setAllTargets(c, st);'
    if before not in code: before='        ripUp(c);\n        setAllTargets(c,st);'
    assert code.count(before)==1
    after=HOOK+'\n'+before.split('\n',1)[1]
    return code.replace(before,after,1),changes+[(before,after)]
   mod.derive=wrapped
  spec.loader.exec_module=exec_module
 return spec
base.importlib.util.spec_from_file_location=loader
if __name__=='__main__':base.main()
