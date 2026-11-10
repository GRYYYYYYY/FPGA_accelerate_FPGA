// Native bounded-search benchmark; decoder is shared with routing backends.
#include "packed_graph.hpp"
struct Result{std::string status="no_path";int distance=-1;uint32_t expanded=0,examined=0,fetched=0;std::vector<std::pair<uint32_t,Edge>> path;double init=0,kernel=0,backtrace=0,total=0;uint64_t logical=0,hits=0,misses=0;};
static Result search(Graph& graph,const Query& q){
 auto begin=Clock::now();Result r;require(q.src<graph.node_count()&&q.dst<graph.node_count(),"query node outside graph");
 auto bytes=graph.logical_bytes,hits=graph.hits,misses=graph.misses;
 std::vector<int32_t> distance(graph.node_count(),-1);std::vector<uint32_t> parent(graph.node_count());std::vector<Edge> pe(graph.node_count());
 std::vector<uint32_t> queue;queue.reserve(graph.node_count());queue.push_back(q.src);distance[q.src]=0;std::vector<Edge> edges;r.init=ms(begin);
 auto kernel=Clock::now();
 for(size_t pos=0;pos<queue.size();pos++){
  auto node=queue[pos];if(node==q.dst){r.status="found";break;}
  if(r.expanded>=q.budget){r.status="budget_exhausted";break;}
  if(!graph.neighbors(node,edges)){r.status="incomplete_domain";break;}
  r.expanded++;r.fetched+=edges.size();
  for(auto e:edges){r.examined++;if(distance[e.dst]<0){distance[e.dst]=distance[node]+1;parent[e.dst]=node;pe[e.dst]=e;queue.push_back(e.dst);if(e.dst==q.dst){r.status="found";break;}}}
  if(r.status=="found")break;
 }
 r.kernel=ms(kernel);auto bt=Clock::now();
 if(r.status=="found"){r.distance=distance[q.dst];for(auto cur=q.dst;cur!=q.src;cur=parent[cur])r.path.emplace_back(parent[cur],pe[cur]);std::reverse(r.path.begin(),r.path.end());}
 r.backtrace=ms(bt);r.total=ms(begin);r.logical=graph.logical_bytes-bytes;r.hits=graph.hits-hits;r.misses=graph.misses-misses;return r;
}
static void print_result(const Result& r){
 std::cout<<"{\"status\":\""<<r.status<<"\",\"distance\":"<<r.distance<<",\"expanded\":"<<r.expanded<<",\"examined\":"<<r.examined<<",\"fetched\":"<<r.fetched<<",\"path\":[";
 bool first=true;for(auto p:r.path){if(!first)std::cout<<',';first=false;auto e=p.second;std::cout<<'['<<p.first<<','<<e.dst<<','<<e.tile<<','<<e.pip<<','<<e.up<<','<<e.down<<','<<e.attr<<','<<e.dir<<']';}std::cout<<"]}";
}
int main(int argc,char** argv){try{
 require(argc==7,"usage: packed_bench graph.agr queries.bin cache_entries repetitions dump.bin direct|expanded");
 size_t capacity=std::stoul(argv[3]);int repetitions=std::stoi(argv[4]);require(repetitions>0,"invalid repetitions");
 auto load_start=Clock::now();Graph graph(argv[1],capacity);double load_ms=ms(load_start);
 std::ifstream qf(argv[2],std::ios::binary);require(bool(qf),"open queries");qf.seekg(0,std::ios::end);size_t qbytes=qf.tellg();require(qbytes%sizeof(Query)==0&&qbytes>0,"bad queries shape");qf.seekg(0);
 std::vector<Query> queries(qbytes/sizeof(Query));qf.read(reinterpret_cast<char*>(queries.data()),qbytes);require(bool(qf),"read queries");
 graph.dump(argv[5]);require(std::string(argv[6])=="direct"||std::string(argv[6])=="expanded","bad execution mode");
 auto prep=Clock::now();if(std::string(argv[6])=="expanded")graph.materialize_all();double materialize_ms=ms(prep);
 std::vector<Result> first;for(auto q:queries){auto start=Clock::now();auto r=search(graph,q);r.total=ms(start);first.push_back(std::move(r));}
 std::vector<std::array<double,4>> resident;std::vector<std::array<uint64_t,3>> counters;
 for(int repeat=0;repeat<repetitions;repeat++){
  std::array<double,4> totals{};std::array<uint64_t,3> counts{};
  for(size_t i=0;i<queries.size();i++)if(queries[i].timed){auto start=Clock::now();auto r=search(graph,queries[i]);r.total=ms(start);require(r.status==first[i].status&&r.distance==first[i].distance&&r.expanded==first[i].expanded&&r.examined==first[i].examined,"repetition semantics differ");
   totals[0]+=r.init;totals[1]+=r.kernel;totals[2]+=r.backtrace;totals[3]+=r.total;counts[0]+=r.logical;counts[1]+=r.hits;counts[2]+=r.misses;}
  resident.push_back(totals);counters.push_back(counts);
 }
 std::ifstream status_file("/proc/self/status");std::string line;uint64_t vm_hwm=0;
 while(std::getline(status_file,line))if(line.rfind("VmHWM:",0)==0){std::istringstream value(line.substr(6));value>>vm_hwm;vm_hwm*=1024;}
 require(vm_hwm>0,"VmHWM unavailable");
 std::cout<<std::setprecision(12)<<"{\"file_bytes\":"<<graph.file_bytes()<<",\"process_vm_hwm_bytes\":"<<vm_hwm<<",\"load_and_directory_ms\":"<<load_ms<<",\"materialize_ms\":"<<materialize_ms<<",\"expanded_allocation_bytes\":"<<graph.expanded_allocation_bytes()<<",\"cache_entries\":"<<capacity<<",\"peak_cache_edge_payload_bytes\":"<<graph.peak_cache_edge_bytes<<",\"state_payload_bytes_per_query\":"<<graph.node_count()*(sizeof(int32_t)+sizeof(uint32_t)+sizeof(Edge)+sizeof(uint32_t))<<",\"first_results\":[";
 for(size_t i=0;i<first.size();i++){if(i)std::cout<<',';print_result(first[i]);}std::cout<<"],\"first_timed_phase_ms\":[";
 std::array<double,4> totals{};for(size_t i=0;i<first.size();i++)if(queries[i].timed){totals[0]+=first[i].init;totals[1]+=first[i].kernel;totals[2]+=first[i].backtrace;totals[3]+=first[i].total;}
 for(int j=0;j<4;j++){if(j)std::cout<<',';std::cout<<totals[j];}std::cout<<"],\"resident_phase_ms\":[";
 for(size_t i=0;i<resident.size();i++){if(i)std::cout<<',';std::cout<<'[';for(int j=0;j<4;j++){if(j)std::cout<<',';std::cout<<resident[i][j];}std::cout<<']';}
 std::cout<<"],\"resident_counters\":[";for(size_t i=0;i<counters.size();i++){if(i)std::cout<<',';std::cout<<'['<<counters[i][0]<<','<<counters[i][1]<<','<<counters[i][2]<<']';}
 std::cout<<"]}\n";return 0;
 }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<'\n';return 2;}}
