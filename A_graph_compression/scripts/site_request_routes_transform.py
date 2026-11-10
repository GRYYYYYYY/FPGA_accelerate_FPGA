"""Feed packed tree demands to the actual request encoder before site commit."""
from derive_search_flat_controller import replace_once as one


def routes(text):
    return one(text,'ledger.replace(q.net,demands);result.site_demands[q.net]=std::move(demands);',
               'ledger.replace_packed(q.net,tree.demands());result.site_demands[q.net]=std::move(demands);')
