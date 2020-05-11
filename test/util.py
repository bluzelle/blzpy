#!/usr/bin/env python

import os
import lib as bluzelle
from lib.bluzelle import Client
import distutils.util
from dotenv import load_dotenv

load_dotenv()

address = os.getenv('ADDRESS', '')
mnemonic = os.getenv('MNEMONIC', '')

def new_client():
    d = os.getenv('DEBUG', 'false')
    debug = d == 'm' # 🤔
    try:
        debug = distutils.util.strtobool(d)
    except Exception:
        pass

    return bluzelle.new_client({
        'address':  address,
        'mnemonic': mnemonic,
        'uuid':     os.getenv('UUID', ''),
        'endpoint': os.getenv('ENDPOINT', ''),
        'chain_id':  os.getenv('CHAIN_ID', ''),
        'debug': debug,
    })

def key_values_to_dict(key_values):
    ret = {}
    for key_value in key_values:
        ret[key_value['key']] = key_value['value']
    return ret
