def derive(s):
 s=s.replace('#include ROUTER_SOURCE','#include "router.cpp"').replace('int main(){','int main(int argc,char**argv){if(argc!=2)throw std::runtime_error("mode");recensus::init();',1).replace('r.ns[0].isLaguna=true;','r.ns[0].isLaguna=std::atoi(argv[1])!=0;r.ns[0].childCount=2;r.ns[1].childCount=1;').replace('raw_bits(', 'recensus::bits(')
 s=s.replace(' r.exploreAndExpand(st,0);', ''' {
 recensus::Attempt guard(1,0,0,0,0,4,1,0,1.0f,false,&c.routed,&c.rnodes);
 guard.sequence=77;guard.share=recensus::bits(st.shareWeight);guard.wire=recensus::bits(st.rnodeWLWeight);guard.estimate=recensus::bits(st.estWlWeight);
 r.exploreAndExpand(st,0);
 }
 recensus::finish();''',1)
 return s.replace(' for(size_t i=0;i<r.order_deferred.size();++i)r.exploreAndExpand(st,r.order_deferred[i]);\n','',1)
