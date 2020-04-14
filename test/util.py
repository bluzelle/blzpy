#!/usr/bin/env python

import os
import lib as bluzelle
import distutils.util
from dotenv import load_dotenv

load_dotenv()

address = os.getenv('ADDRESS', '')
mnemonic = os.getenv('MNEMONIC', '')

def new_client():
    debug = False
    try:
        debug = distutils.util.strtobool(os.getenv('DEBUG', 'false'))
    except Exception:
        pass

    return bluzelle.new_client({
        'address':  address,
        'mnemonic': mnemonic,
        'uuid':     os.getenv('UUID', ''),
        'endpoint': os.getenv('ENDPOINT', ''),
        'chain_id':  os.getenv('CHAIN_ID', ''),
        'gas_info': {
            'max_fee': 4000001,
        },
        'debug': debug,
    })

def key_values_to_dict(key_values):
    ret = {}
    for key_value in key_values:
        ret[key_value['key']] = key_value['value']
    return ret
