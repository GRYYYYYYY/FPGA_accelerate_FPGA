"""Replace only integer arithmetic; leave all label/coordinate/SLR lookups ordered."""
def generate(source,header):
 def replace(old,new):
  nonlocal source
  assert source.count(old)==1,(old,source.count(old))
  assert new.count('\n')<=old.count('\n')
  source=source.replace(old,new+'\n'*(old.count('\n')-new.count('\n')))
 old='''                if (deltaSLR == 1) {
                    int overshootByY = deltaY - superLongLineLength;
                    if (overshootByY < 0) deltaY = superLongLineLength - overshootByY;
                }'''
 replace(old,'                deltaY = search_geometry::require(search_geometry::adjust_y(deltaY, deltaSLR, superLongLineLength));')
 a=source.index('                if (nextLag == prevLag) {',source.index('    void evaluateCostAndPush('))
 b=source.index('\n            }\n        }\n        int distanceToSink',a)
 replace(source[a:b],'''                deltaX = search_geometry::require(search_geometry::laguna_x(childX, sinkX, nextLag, prevLag, c.xMinBB, c.xMaxBB));''')
 replace('        int distanceToSink = deltaX + deltaY;','        int distanceToSink = search_geometry::require(search_geometry::sum(deltaX, deltaY));')
 assert header.count('#include <fstream>')==1
 header=header.replace('#include <fstream>','#include <fstream>\n#include "search_geometry_checked.hpp"')
 return source,header
