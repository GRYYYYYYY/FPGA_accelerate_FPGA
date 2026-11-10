#define main b_original_main
#include "trace.cpp"
#undef main
#include <fstream>
#include <stdexcept>
static void ck(bool ok){if(!ok)throw std::runtime_error("coordinate source mismatch");}
static int32_t i32(std::ifstream&f){unsigned char b[4];f.read((char*)b,4);ck(bool(f));return int32_t(uint32_t(b[0])|(uint32_t(b[1])<<8)|(uint32_t(b[2])<<16)|(uint32_t(b[3])<<24));}
int main(int argc,char**argv){
 ck(argc==3);Router r;r.load(argv[1]);std::string dir=argv[2];
 std::ifstream rows(dir+"/real/rows.bin",std::ios::binary),cols(dir+"/real/columns.bin",std::ios::binary);
 for(size_t y=0;y<r.intYToSLRIndex.size();y++){ck(i32(rows)==r.intYToSLRIndex[y]);ck(i32(rows)==(r.hasLaguna?r.intYToNorthboundLaguna[y]:0));}
 for(size_t x=0;x<r.nextLagunaColumn.size();x++){ck(i32(cols)==r.nextLagunaColumn[x]);ck(i32(cols)==r.prevLagunaColumn[x]);}
 ck(rows.peek()==std::char_traits<char>::eof());ck(cols.peek()==std::char_traits<char>::eof());
 std::printf("TABLE_ORIGINAL_PASS rows=%zu columns=%zu laguna=%d\n",r.intYToSLRIndex.size(),r.nextLagunaColumn.size(),int(r.hasLaguna));
 // Exercise original coordinate code against BOTH original label stores.
 r.ns[0].endY=70;r.ns[1].beginY=10;r.ns[1].endY=70;r.ns[5].beginY=20;r.ns[5].endY=70;
 r.type[1]=RouteNodeType::SUPER_LONG_LINE;r.type[5]=RouteNodeType::SUPER_LONG_LINE;
 r.initHotFromStatic(0);r.initHotFromStatic(1);r.initHotFromStatic(5);
 Router::tl_dyn=r.dyn.data();Router::tl_sparse=nullptr;r.dyn[1].prev=-1;r.dyn[5].prev=0;
 for(int hot=0;hot<2;hot++){
  r.useHotExpand=hot;ck(r.searchEndY(1)==70);
  Router::SparseLabels sparse;sparse.initPaged(r.ns.size(),3);Router::tl_sparse=&sparse;
  ck(sparse.at(1).prev==0);ck(r.searchEndY(1)==10);
  sparse.at(1).prev=-1;ck(r.searchEndY(1)==70);
  sparse.at(1).prev=5;sparse.at(5).prev=0;ck(r.searchEndY(5)==20);ck(r.searchEndY(1)==10);
  sparse.reset();ck(sparse.at(1).prev==0);ck(r.searchEndY(1)==10);Router::tl_sparse=nullptr;
  std::printf("PREV_DEFAULT_NEGATIVE hot=%d dense_y=70 paged_absent_y=10 explicit_minus_one_y=70 static_predecessor_y=10 reset_y=10\n",hot);
 }
 std::puts("COORDINATE_INPUTS_PASS");return 0;
}
