import logging
import os
import sys

import urllib3
from dotenv import load_dotenv

from gcdocs import GCdocs

logging.basicConfig(filename='gcdocs.log', filemode='w+', level=logging.DEBUG)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if not load_dotenv():
    sys.exit('.env file not found')

GCDOCS_HOSTNAME = os.getenv('GCDOCS_HOSTNAME')
GCDOCS_USERNAME = os.getenv('GCDOCS_USERNAME')
GCDOCS_PASSWORD = os.getenv('GCDOCS_PASSWORD')

gcdocs = GCdocs(
    protocol='https',
    hostname=GCDOCS_HOSTNAME,
    port=443,
    public_url=GCDOCS_HOSTNAME,
    username=GCDOCS_USERNAME,
    password=GCDOCS_PASSWORD
)

gcdocs.authenticate()
