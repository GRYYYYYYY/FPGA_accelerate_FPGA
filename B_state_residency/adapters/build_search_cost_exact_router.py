"""Replace scalar arithmetic only; keep complete route, geometry and TLD order intact."""
def generate(source,header):
 assert source.count('search_cost::')==6
 source=source.replace('search_cost::','search_cost_exact::')
 assert header.count('#include <fstream>')==1
 return source,header.replace('#include <fstream>','#include <fstream>\n#include "search_cost_exact.hpp"')
