import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import lib as bluzelle
import time
import distutils.util
from dotenv import load_dotenv

load_dotenv()

client = bluzelle.new_client({
    'address':  os.getenv('ADDRESS', ''),
    'mnemonic': os.getenv('MNEMONIC', ''),
    'uuid':     os.getenv('UUID', ''),
    'endpoint': os.getenv('ENDPOINT', ''),
    'chain_id':  os.getenv('CHAIN_ID', ''),
    'gas_info': {
        'max_fee': 4000001,
    },
    'debug': distutils.util.strtobool(os.getenv('DEBUG', 'false')),
})

key = '%i' % time.time()
value = 'bar'

print('creating %s=%s' % (key, value))
try:
    client.create(key, value)
    print('created key')
except bluzelle.APIError as err:
    print('error creating key %s' % (err))
else:
    print()
    print('reading value for key(%s)' % (key))
    try:
        value = client.read(key)
        print('read value %s' % (value))
    except bluzelle.APIError as err:
        print('error reading key %s' % (err))
    else:
        try:
            print()
            print('deleting key')
            client.delete(key)
        except bluzelle.APIError as err:
            print('deleted key')
