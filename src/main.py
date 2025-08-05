import logging
import os
from threading import Thread

from dotenv import load_dotenv
import urllib3
from pyxecm import OTCS

from tasks import *

logging.basicConfig(filename='app.log', filemode='w+', level=logging.DEBUG)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if load_dotenv():
    hostname = os.getenv('OTCS_HOSTNAME')
    username = os.getenv('OTCS_USERNAME')
    password = os.getenv('OTCS_PASSWORD')
else:
    print('.env file not found')
    quit()

otcs = OTCS(
    protocol='https',
    hostname=hostname,
    port=443,
    public_url=hostname,
    username=username,
    password=password
)

otcs.authenticate()
quit()

root_id = 33266495
root = otcs.get_node(node_id=root_id)
total_subnodes = otcs.get_result_value(response=root, key='size')
page_size = 100
total_pages = (total_subnodes + page_size - 1) // page_size

for page in range(1, total_pages + 1):
    print('page', page)
    nodes = otcs.get_subnodes(parent_node_id=root_id, page=page)
    threads: list[Thread] = []

    for i in range(len(nodes['results'])):
        subtype = otcs.get_result_value(response=nodes, key='type', index=i)

        if subtype != OTCS.ITEM_TYPE_BUSINESS_WORKSPACE:
            continue

        node_id = otcs.get_result_value(response=nodes, key='id', index=i)
        t = Thread(target=task2, args=(otcs, node_id))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()