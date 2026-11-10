#include "cost_api.hpp"
#include <cstdio>
int main(){
 FILE* in=std::fopen("vectors.txt","r"),*out=std::fopen("observed.txt","w");if(!in||!out)return 2;
 unsigned group,x[23],expected[5],actual[5],cases=0,bad=0,normal_bad=0,words=0;
 while(std::fscanf(in,"%u",&group)==1){
  for(int i=0;i<23;i++)if(std::fscanf(in,"%x",&x[i])!=1)return 3;
  for(int i=0;i<5;i++)if(std::fscanf(in,"%x",&expected[i])!=1)return 4;
  cost_step(x,actual);bool mismatch=false;std::fprintf(out,"%u %u",cases,group);
  for(int i=0;i<5;i++){std::fprintf(out," %08x",actual[i]);if(actual[i]!=expected[i]){mismatch=true;words++;}}
  std::fprintf(out,"\n");if(mismatch){bad++;if(group==0)normal_bad++;if(bad<=16)std::printf("COST_DIFF case=%u group=%u actual=%08x/%08x/%08x/%08x/%08x expected=%08x/%08x/%08x/%08x/%08x\n",cases,group,actual[0],actual[1],actual[2],actual[3],actual[4],expected[0],expected[1],expected[2],expected[3],expected[4]);}
  cases++;
 }
 std::fclose(in);std::fclose(out);
 std::printf("COST_CHARACTERIZED cases=%u mismatched_cases=%u mismatched_words=%u normal_mismatches=%u\n",cases,bad,words,normal_bad);
 return cases==4776?0:5; // Characterization completion is NOT an exactness PASS.
}
