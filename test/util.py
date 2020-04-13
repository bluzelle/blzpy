#!/usr/bin/env python

import os
import lib as bluzelle
import distutils.util
from dotenv import load_dotenv

load_dotenv()

def new_client():
    return bluzelle.new_client({
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
