#pragma once
#include <cstdint>
namespace softfp {
using U=std::uint32_t;using W=std::uint64_t;
inline bool nan(U a){return (a&0x7fffffffU)>0x7f800000U;}
inline bool inf(U a){return (a&0x7fffffffU)==0x7f800000U;}
inline bool zero(U a){return (a&0x7fffffffU)==0;}
inline U quiet(U a){return a|0x00400000U;}
inline W jam(W x,unsigned n){if(!n)return x;if(n>=64)return x!=0;return (x>>n)|((x&((W(1)<<n)-1))!=0);}
// sig has 24 significand bits plus guard/round/sticky, hidden bit at 26.
inline U pack(U sign,int exp,W sig){
 if(!sig)return sign;
 if(exp<1){sig=jam(sig,unsigned(1-exp));exp=1;}
 W main=sig>>3;unsigned rem=sig&7;
 if(rem>4||(rem==4&&(main&1)))++main;
 if(main>=0x1000000ULL){main>>=1;++exp;}
 if(exp>=255)return sign|0x7f800000U;
 return sign|(main>=0x800000ULL?(U(exp)<<23):0)|U(main&0x7fffffU);
}
inline U add(U a,U b){
 if(nan(a))return quiet(a);if(nan(b))return quiet(b);
 if(inf(a)||inf(b)){if(inf(a)&&inf(b)&&((a^b)>>31))return 0xffc00000U;return inf(a)?a:b;}
 U sa=a&0x80000000U,sb=b&0x80000000U;
 int ea=(a>>23)&255,eb=(b>>23)&255;
 W ma=(a&0x7fffffU)|(ea?0x800000U:0),mb=(b&0x7fffffU)|(eb?0x800000U:0);
 if(!ea)ea=1;if(!eb)eb=1;
 if(ea<eb||(ea==eb&&ma<mb)){int te=ea;ea=eb;eb=te;W tm=ma;ma=mb;mb=tm;U ts=sa;sa=sb;sb=ts;}
 W x=ma<<3,y=jam(mb<<3,unsigned(ea-eb)),s;
 if(sa==sb){s=x+y;if(s&(W(1)<<27)){s=jam(s,1);++ea;}}
 else {s=x-y;if(!s)return 0;for(int i=0;i<26;i++){if(s<(W(1)<<26)&&ea>1){s<<=1;--ea;}}}
 return pack(sa,ea,s);
}
inline U mul(U a,U b){
 if(nan(a))return quiet(a);if(nan(b))return quiet(b);
 U sign=(a^b)&0x80000000U;
 if(inf(a)||inf(b)){if(zero(a)||zero(b))return 0xffc00000U;return sign|0x7f800000U;}
 if(zero(a)||zero(b))return sign;
 int ea=(a>>23)&255,eb=(b>>23)&255;
 W ma=(a&0x7fffffU)|(ea?0x800000U:0),mb=(b&0x7fffffU)|(eb?0x800000U:0);
 if(!ea)ea=1;if(!eb)eb=1;
 // Normalize BEFORE discarding product bits, preserving subnormal precision.
 for(int i=0;i<23;i++){if(ma<0x800000ULL){ma<<=1;--ea;}if(mb<0x800000ULL){mb<<=1;--eb;}}
 W prod=ma*mb;int e=ea+eb-127;
 W s;if(prod&(W(1)<<47)){s=jam(prod,21);++e;}else s=jam(prod,20);
 return pack(sign,e,s);
}
inline U div(U a,U b){
 if(nan(a))return quiet(a);if(nan(b))return quiet(b);
 U sign=(a^b)&0x80000000U;
 if((inf(a)&&inf(b))||(zero(a)&&zero(b)))return 0xffc00000U;
 if(inf(a)||zero(b))return sign|0x7f800000U;
 if(zero(a)||inf(b))return sign;
 int ea=(a>>23)&255,eb=(b>>23)&255;
 W ma=(a&0x7fffffU)|(ea?0x800000U:0),mb=(b&0x7fffffU)|(eb?0x800000U:0);
 if(!ea)ea=1;if(!eb)eb=1;
 for(int i=0;i<23;i++){if(ma<0x800000ULL){ma<<=1;--ea;}if(mb<0x800000ULL){mb<<=1;--eb;}}
 int e=ea-eb+127;unsigned shift=26;if(ma<mb){shift=27;--e;}
 W numerator=ma<<shift;W q=numerator/mb;W rem=numerator%mb;
 return pack(sign,e,q|(rem!=0));
}
inline U from_int(std::int32_t a){
 if(!a)return 0;U sign=a<0?0x80000000U:0;W m=a<0?W(-std::int64_t(a)):W(a);int msb=0;
 for(int i=1;i<32;i++)if(m>>i)msb=i;
 W s=msb>26?jam(m,unsigned(msb-26)):m<<unsigned(26-msb);
 return pack(sign,127+msb,s);
}
inline bool less(U a,U b){
 if(nan(a)||nan(b)||((a|b)&0x7fffffffU)==0)return false;
 if((a^b)&0x80000000U)return (a>>31)!=0;
 return (a>>31)?a>b:a<b;
}
inline U min(U a,U b){return less(b,a)?b:a;}
}
