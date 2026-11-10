"""Extend the already exact natural replay with read-only cost/image export."""
def derive(router,driver):
 observer=r'''        if(nqs::active){
            static FILE* cf=nqs::open("cost_vectors.txt");
            int occ=useHotExpand?hot[childRnode].occCnt:getOccupancy(childRnode);
            int pi=countSourceUses?(occ>0?occ-1:0):occ;
            uint32_t words[23]={nqs::bits(st.shareWeight),uint32_t(countSourceUses),nqs::bits(ns[childRnode].baseCost),nqs::bits(dyn[childRnode].hist),nqs::bits(presentCongestionCosts[pi]),uint32_t(nets[c.netIdx].connectionsSize),nqs::bits(std::abs(childX-nets[c.netIdx].xCenter)+std::abs(childY-nets[c.netIdx].yCenter)),uint32_t(nets[c.netIdx].doubleHpwl),nqs::bits(TLD(rnode).upstream),nqs::bits(st.rnodeWLWeight),uint32_t(ns[childRnode].length),nqs::bits(st.estWlWeight),uint32_t(distanceToSink),uint32_t(lmkReady),nqs::bits(lmkInvScale)};
            uint32_t result[5]={nqs::bits(sharingFactor),nqs::bits(getNodeCostSearch(childRnode,c,countSourceUses,sharingFactor)),nqs::bits(newPartial),nqs::bits(hBase),nqs::bits(newTotal)};
            std::fprintf(cf,"%d %d",rnode,childRnode);for(auto w:words)std::fprintf(cf," %08x",w);for(auto w:result)std::fprintf(cf," %08x",w);std::fprintf(cf,"\n");std::fflush(cf);
        }
'''
 needle='        push(st, childRnode, newPartial, newTotal, lookahead);';assert router.count(needle)==1
 router=router.replace(needle,observer+needle)
 assert driver.count(' nqs::begin(r,st);')==1
 driver=driver.replace(' nqs::begin(r,st);',' natcodec::export_inputs(r,st);\n nqs::begin(r,st);')
 driver=driver.replace('#undef main','#undef main\n#include "export_inputs.hpp"',1)
 return router,driver,observer
