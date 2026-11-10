// Exhaustive CPU adjacency traversal, optionally emitting every numeric record.
#include "packed_graph.hpp"
#include <new>
int main(int argc,char** argv){try{
 require(argc==2||argc==3,"usage: scale_domain_scan image.agr [dump.bin]");
 Graph graph(argv[1],0); std::ofstream dump;
 if(argc==3){dump.open(argv[2],std::ios::binary);require(bool(dump),"dump open");}
 uint64_t known=0,unknown=0,empty=0,edges=0,hash=14695981039346656037ull;
 auto mix=[&](uint32_t value){for(unsigned i=0;i<4;++i){hash^=(value>>(8*i))&255;hash*=1099511628211ull;}};
 std::vector<Edge> row;
 for(uint32_t node=0;node<graph.node_count();++node){
  bool ok=graph.neighbors(node,row);mix(node);mix(ok?1:0);
  if(!ok){++unknown;continue;}++known;if(row.empty())++empty;
  for(const auto& edge:row){
   uint32_t record[8]={node,edge.dst,edge.tile,edge.pip,edge.up,edge.down,edge.attr,edge.dir};
   for(auto value:record)mix(value);
   if(argc==3)dump.write(reinterpret_cast<const char*>(record),sizeof(record));
  }
  edges+=row.size();
 }
 if(argc==3){dump.flush();require(bool(dump),"dump write");}
 std::cout<<"{\"status\":\"complete_native_adjacency_scan\",\"nodes\":"<<graph.node_count()
 <<",\"known_rows\":"<<known<<",\"unknown_rows\":"<<unknown<<",\"empty_known_rows\":"<<empty
 <<",\"directed_edges\":"<<edges<<",\"record_fingerprint\":"<<hash<<"}\n";
 return 0;
}catch(const std::bad_alloc&){std::cerr<<"ALLOCATION_FAILED\n";return 3;}
 catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<'\n';return 2;}}
