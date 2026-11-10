#pragma once
namespace natcodec {
inline void pad(FILE*f,unsigned long long bytes){while(bytes%64){std::fputc(0,f);bytes++;}}
template<class R,class S> void export_inputs(R&r,S&st){
 if(r.lazy||r.pruneDeadEnd||r.lmkReady)throw std::runtime_error("unsupported input codec profile");
 FILE*cost=nqs::open("cost.bin");
 for(auto&v:r.dyn)nqs::word(cost,nqs::bits(v.hist));
 pad(cost,r.ns.size()*4ull);
 for(float v:r.presentCongestionCosts)nqs::word(cost,nqs::bits(v));
 for(auto&n:r.nets){nqs::word(cost,nqs::bits(n.xCenter));nqs::word(cost,nqs::bits(n.yCenter));nqs::word(cost,n.connectionsSize);nqs::word(cost,n.doubleHpwl);}pad(cost,((r.ns.size()*4ull+63)/64)*64+1024+r.nets.size()*16ull);std::fclose(cost);
 FILE*q=nqs::open("connections.bin");
 for(size_t i=0;i<r.connections.size();i++){
  auto&c=r.connections[i];unsigned w[16]={0x43505331u,unsigned(i),unsigned(c.netIdx),unsigned(c.sinkRnode),unsigned(c.sourceRnode),nqs::bits(st.shareWeight),nqs::bits(st.rnodeWLWeight),nqs::bits(st.estWlWeight),nqs::bits(r.lmkInvScale),0,unsigned(r.superLongLineLength),unsigned((c.crossSLRnorth?8:0)|(c.crossSLRsouth?16:0)),nqs::bits(r.cfg.wirelengthWeight),nqs::bits(r.directedness),nqs::bits(r.cfg.shareExponent),0};for(auto x:w)nqs::word(q,x);
 }std::fclose(q);
 FILE*f=nqs::open("rows.bin");for(auto v:r.intYToSLRIndex)nqs::word(f,v);pad(f,r.intYToSLRIndex.size()*4ull);std::fclose(f);
 f=nqs::open("columns.bin");for(size_t i=0;i<r.nextLagunaColumn.size();i++){nqs::word(f,r.nextLagunaColumn[i]);nqs::word(f,r.prevLagunaColumn[i]);}if(r.nextLagunaColumn.empty())for(int i=0;i<16;i++)nqs::word(f,0);else pad(f,r.nextLagunaColumn.size()*8ull);std::fclose(f);
 f=nqs::open("input_layout.json");unsigned long long po=((r.ns.size()*4ull+63)/64)*64;
 std::fprintf(f,"{\"nodes\":%zu,\"edges\":%zu,\"nets\":%zu,\"connections\":%zu,\"query\":%d,\"price_offset\":%llu,\"net_offset\":%llu,\"owner_pool_capacity\":0,\"rows\":%zu,\"columns\":%zu,\"has_laguna\":%d}\n",r.ns.size(),r.childIds.size(),r.nets.size(),r.connections.size(),st.connIdx,po,po+1024,r.intYToSLRIndex.size(),r.nextLagunaColumn.size(),r.hasLaguna);std::fclose(f);
}
}
