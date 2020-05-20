#!/usr/bin/env python

import os
import lib as bluzelle
from lib.bluzelle import Client
import distutils.util
from dotenv import load_dotenv

load_dotenv()

ADDRESS = os.getenv('ADDRESS', '')

def new_client():
    d = os.getenv('DEBUG', 'false')
    debug = d == 'm' # 🤔
    try:
        debug = distutils.util.strtobool(d)
    except Exception:
        pass

    return bluzelle.new_client({
        'mnemonic': os.getenv('MNEMONIC', None),
        'uuid':     os.getenv('UUID', None),
        'endpoint': os.getenv('ENDPOINT', None),
        'chain_id':  os.getenv('CHAIN_ID', None),
        'debug': debug,
    })

def key_values_to_dict(key_values):
    ret = {}
    for key_value in key_values:
        ret[key_value['key']] = key_value['value']
    return ret
