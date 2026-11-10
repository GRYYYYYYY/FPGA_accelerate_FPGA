// Complete native adjacency comparison, including empty-known and unknown rows.
#include "packed_graph.hpp"
int main(int argc,char** argv){try{
 require(argc==3,"usage: template_scope_check original.agr candidate.agr");
 Graph original(argv[1],0),candidate(argv[2],0);
 require(original.mode==1&&candidate.mode==1,"compact required");
 require(original.node_count()==candidate.node_count()&&original.source_count()==candidate.source_count(),"domain differs");
 uint64_t known=0,unknown=0,empty=0,edges=0;std::vector<Edge> a,b;
 for(uint32_t node=0;node<original.node_count();++node){
  const bool ka=original.neighbors(node,a),kb=candidate.neighbors(node,b);
  require(ka==kb,"known/unknown status differs");
  if(!ka){++unknown;continue;}
  ++known;if(a.empty())++empty;
  require(a.size()==b.size(),"edge count differs");
  for(size_t i=0;i<a.size();++i)require(!(a[i]<b[i])&&!(b[i]<a[i]),"edge identity/direction/attributes/order differs");
  edges+=a.size();
 }
 require(known==original.source_count(),"known source domain differs");
 std::cout<<"{\"status\":\"all_native_rows_equivalent\",\"nodes\":"<<original.node_count()
          <<",\"known_rows\":"<<known<<",\"unknown_rows\":"<<unknown<<",\"empty_known_rows\":"<<empty
          <<",\"directed_edges\":"<<edges<<"}\n";
 return 0;
}catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<'\n';return 2;}}
