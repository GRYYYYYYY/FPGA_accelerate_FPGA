#include <cstdio>
#include <cstdint>
#include <cstring>
extern "C" void access_step(const uint32_t[20],uint32_t[6]);
int main(){
 FILE*f=std::fopen("vectors.txt","r"),*obs=std::fopen("observed.txt","w");if(!f||!obs)return 2;
 uint32_t in[20],expected[6],out[6];unsigned index,caseid,count=0,errors=0;
 while(std::fscanf(f,"%u %u",&index,&caseid)==2){
  if(index!=count)return 3;
  for(int j=0;j<20;j++)if(std::fscanf(f,"%x",in+j)!=1)return 4;
  for(int j=0;j<6;j++)if(std::fscanf(f,"%x",expected+j)!=1)return 5;
  access_step(in,out);std::fprintf(obs,"%u %u",index,caseid);for(auto v:out)std::fprintf(obs," %08x",v);std::fprintf(obs,"\n");
  if(std::memcmp(out,expected,24)){std::fprintf(stderr,"ACCESS_RTL_MISMATCH index=%u case=%u\n",index,caseid);errors++;}count++;
 }
 std::fclose(f);std::fclose(obs);if(!count||errors)return 6;
 std::printf("ACCESS_HLS_PASS steps=%u errors=%u\n",count,errors);return 0;
}
