#pragma once
#include <cstdint>
namespace search_access {
enum Request : uint32_t { DONE=0,VISITED=1,TARGET=2,BBOX_END_Y=3,WILL_OVERUSE=4,SINK_TARGET=5,COUNT_USER=6,CHILD_SLR=7,SINK_SLR=8,PARENT_PREV=9,PREV_TILE=10,GRAPH_END_Y=11 };
enum Phase : uint32_t { END=0,V=1,T=2,BY=3,TO=4,ST=5,SC=6,LO=7,LS=8,LC=9,WO=10,NC=11,NS=12,PC1=13,PC2=14,PT=15,GC=16,GS=17,GY=18 };
enum Flags : uint32_t { PRUNE=1,DEAD=2,BB=4,NORTH=8,SOUTH=16,P_LAG=32,C_LAG=64,PINBOUNCE=128,HOT=256 };
enum Bits : uint32_t { AHEAD=1,IS_TARGET=2,EARLY=4,PRUNED=8 };
struct Config {uint32_t sequence,flags,child_type,parent_type,sink_type;int32_t child_x,child_tile,sink_tile,sink_x,sink_y,xmin,xmax,ymin,ymax;};
struct State {uint32_t phase,bits;int32_t aux;uint32_t action;};
inline bool local(uint32_t t){return (t>=6&&t<=9)||(t>=13&&t<=16);}
inline bool lead_local(uint32_t t){return t>=6&&t<=9;}
inline bool west(uint32_t t){return t==7||t==9||t==15;}
inline bool east(uint32_t t){return t==6||t==8||t==14;}
inline bool exclusive(uint32_t t){return t>=1&&t<=4;}
inline bool cross(const Config&c){return c.flags&(NORTH|SOUTH);}
inline bool direction(const Config&c){return ((c.child_type==6||c.child_type==7||c.child_type==10)&&(c.flags&NORTH))||((c.child_type==8||c.child_type==9||c.child_type==11)&&(c.flags&SOUTH));}
inline void finish(State&s,bool allow){s.phase=END;s.action=allow?((s.bits&AHEAD)?2:1):0;}
inline void same_side(const Config&c,State&s){
 bool same=c.child_tile==c.sink_tile;
 switch(c.sink_type){
 case 14:case 2:if(west(c.child_type)||c.child_type==16){finish(s,false);return;}break;
 case 15:case 3:if(east(c.child_type)||c.child_type==16){finish(s,false);return;}break;
 case 1:if(!same||c.child_type!=13){finish(s,false);return;}break;
 case 4:finish(s,false);return;
 default:break;
 }
 if(same){finish(s,true);return;}
 if(c.child_x!=c.sink_x){finish(s,false);return;}
 s.phase=GY;
}
inline void nonlocal_finish(const Config&c,State&s){if(c.flags&(P_LAG|C_LAG))s.bits|=AHEAD;finish(s,true);}
inline void graph(const Config&c,State&s){
 if(local(c.child_type)){
  if(cross(c)&&lead_local(c.child_type))s.phase=GC;
  else same_side(c,s);
 }else if(c.child_type==12){
  if(local(c.parent_type)){
   if(c.flags&C_LAG){if(cross(c))s.phase=NC;else finish(s,false);}
   else nonlocal_finish(c,s);
  }else if(c.parent_type==5)s.phase=PC1;
  else nonlocal_finish(c,s);
 }else nonlocal_finish(c,s);
}
inline void after_box(const Config&c,State&s){
 if(lead_local(c.child_type)){s.phase=LO;return;}
 if(local(c.child_type)){graph(c,s);return;}
 if(c.child_type==10||c.child_type==11){if(cross(c))s.phase=LS;else graph(c,s);return;}
 if(c.child_type==12){graph(c,s);return;}
 if(exclusive(c.child_type)){s.phase=ST;return;}
 finish(s,true);
}
inline uint32_t request(const State&s){
 switch(s.phase){case V:return VISITED;case T:return TARGET;case BY:return BBOX_END_Y;
 case TO:case LO:case WO:return WILL_OVERUSE;case ST:return SINK_TARGET;case SC:return COUNT_USER;
 case LC:case NC:case GC:return CHILD_SLR;case LS:case NS:case GS:return SINK_SLR;
 case PC1:case PC2:return PARENT_PREV;case PT:return PREV_TILE;case GY:return GRAPH_END_Y;default:return DONE;}
}
inline State start(){return {V,0,0,0};}
inline bool valid(const Config&c,const State&s){return c.flags<512&&c.child_type<256&&c.parent_type<256&&c.sink_type<256&&s.phase<=GY&&s.bits<16&&s.action<=2;}
inline bool accept(const Config&c,State&s,uint32_t value){
 if(!valid(c,s)||s.phase==END)return false;
 int32_t v=static_cast<int32_t>(value);
 switch(s.phase){
 case V:
  if(value==c.sequence)finish(s,false);
  else if((c.flags&(PRUNE|DEAD))==(PRUNE|DEAD)){s.bits|=PRUNED;finish(s,false);}
  else s.phase=T;break;
 case T:
  if(value){s.bits|=IS_TARGET;if(exclusive(c.child_type)){s.bits|=EARLY;finish(s,true);}else s.phase=TO;}
  else if(c.flags&BB)s.phase=BY;else after_box(c,s);break;
 case BY:
  if(c.child_x>c.xmin&&c.child_x<c.xmax&&v>c.ymin&&v<c.ymax)after_box(c,s);else finish(s,false);break;
 case TO:if(!value)s.bits|=EARLY;finish(s,true);break;
 case ST:if(value)finish(s,true);else s.phase=SC;break;
 case SC:finish(s,value!=0&&(c.flags&PINBOUNCE));break;
 case LO:if(!value)s.bits|=AHEAD;graph(c,s);break;
 case LS:s.aux=v;s.phase=LC;break;
 case LC:if(s.aux!=v&&direction(c))s.phase=WO;else graph(c,s);break;
 case WO:if(!value)s.bits|=AHEAD;graph(c,s);break;
 case NC:s.aux=v;s.phase=NS;break;
 case NS:if(s.aux==v)finish(s,false);else nonlocal_finish(c,s);break;
 case PC1:if(v==-1)nonlocal_finish(c,s);else s.phase=PC2;break;
 case PC2:s.aux=v;s.phase=PT;break;
 case PT:if(v==c.child_tile)finish(s,false);else nonlocal_finish(c,s);break;
 case GC:s.aux=v;s.phase=GS;break;
 case GS:if(s.aux!=v)finish(s,direction(c));else same_side(c,s);break;
 case GY:{int64_t delta=int64_t(v)-c.sink_y;finish(s,delta>=-1&&delta<=1);break;}
 default:return false;
 }
 return true;
}
}
