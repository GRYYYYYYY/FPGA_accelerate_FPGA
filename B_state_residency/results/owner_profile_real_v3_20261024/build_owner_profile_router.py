"""Instrument original owner mutations without shifting TLD source-line identities."""
def generate(source, header):
    original_lines = source.count('\n')
    for method, op in [('incUserSlot', 1), ('decUserSlot', 2)]:
        signature = f'    inline void {method}(int id, int nw) {{'
        assert source.count(signature) == 1
        start = source.index(signature)
        end = source.index('\n    }', start)
        body = source[start:end]
        assert body.count('syncHotOcc(id);') == 1
        body = body.replace(signature, signature + f' const auto b_owner_before=bowner::before(*this,id,nw,{op});')
        body = body.replace('syncHotOcc(id);', f'syncHotOcc(id); bowner::after(*this,id,nw,{op},b_owner_before);')
        source = source[:start] + body + source[end:]
    anchor = '    auto b_route_start = clk::now();\n    router.routeIndirectConnectionsIteratively();'
    assert source.count(anchor) == 1
    source = source.replace(anchor, '    auto b_route_start = clk::now();\n    bowner::start(router); router.routeIndirectConnectionsIteratively(); bowner::finish(router);')
    assert source.count('\n') == original_lines
    assert header.count('#include <fstream>') == 1
    header = header.replace('#include <fstream>', '#include <fstream>\n#include "owner_profile.hpp"')
    return source, header
