from threading import Thread

from config import gcdocs
from gcdocs import GCdocs
from tasks import *

# personnel records
root_id = 30713183
page_size = 100

root = gcdocs.get_node(node_id=root_id)
total_subnodes = gcdocs.get_result_value(response=root, key='size')
total_pages = (total_subnodes + page_size - 1) // page_size

for page in range(50, total_pages + 1):
    print(f'page {page}/{total_pages}')
    nodes = gcdocs.get_subnodes(
        parent_node_id=root_id,
        filter_node_types=GCdocs.ITEM_TYPE_BUSINESS_WORKSPACE,
        limit=page_size,
        page=page
    )
    node_ids = gcdocs.get_result_values(response=nodes, key='id')
    threads: list[Thread] = []

    for node_id in node_ids:
        threads.append(Thread(
            target=gcdocs.assign_permission,
            args=(node_id, GCdocs.PERMISSION_TYPES, 'custom', 31897943, 2)
        ))

    for t in threads:
        t.start()

    for t in threads:
        t.join()
