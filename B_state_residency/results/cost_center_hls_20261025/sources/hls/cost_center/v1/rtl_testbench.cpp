#include <cstdio>
#include <cstdint>
extern "C" void cost_center_step(const std::uint32_t[4],std::uint32_t[2]);
int main(){
 FILE*in=std::fopen("vectors.txt","r");FILE*out=std::fopen("observed.txt","w");if(!in||!out)return 2;
 unsigned count=0,errors=0;std::uint32_t input[4],expected[2],actual[2];
 while(true){
  int n=std::fscanf(in,"%x %x %x %x %x %x",&input[0],&input[1],&input[2],&input[3],&expected[0],&expected[1]);
  if(n==EOF)break;if(n!=6)return 3;
  cost_center_step(input,actual);std::fprintf(out,"%08x %08x\n",actual[0],actual[1]);
  if(actual[0]!=expected[0]||actual[1]!=expected[1]){if(errors<8)std::printf("CENTER_FAIL case=%u got=%08x/%08x expected=%08x/%08x\n",count,actual[0],actual[1],expected[0],expected[1]);++errors;}
  ++count;
 }
 std::fclose(in);std::fclose(out);if(count!=110397||errors)return 4;
 std::printf("COST_CENTER_FROZEN_PASS cases=%u words=%u\n",count,count*2);return 0;
}
