#!/usr/bin/env python
import unittest
import time
from .util import new_client, bluzelle, mnemonic

class TestOptions(unittest.TestCase):
    def test_requires_address(self):
        with self.assertRaisesRegex(bluzelle.OptionsError, "address is required"):
            bluzelle.new_client({})

    def test_requires_mnemonic(self):
        with self.assertRaisesRegex(bluzelle.OptionsError, "mnemonic is required"):
            bluzelle.new_client({
                "address": "1"
            })

    def test_validates_gas_info(self):
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info should be a dict of {gas_price, max_fee, max_gas}"):
            bluzelle.new_client({
                "address": "1",
                "mnemonic": "1",
                "gas_info": ""
            })
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info should be a dict of {gas_price, max_fee, max_gas}"):
            bluzelle.new_client({
                "address": "1",
                "mnemonic": "1",
                "gas_info": 1
            })
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info should be a dict of {gas_price, max_fee, max_gas}"):
            bluzelle.new_client({
                "address": "1",
                "mnemonic": "1",
                "gas_info": []
            })
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info\[gas_price\] should be an int"):
            bluzelle.new_client({
                "address": "1",
                "mnemonic": "1",
                "gas_info": {
                    "gas_price": ""
                }
            })
    def test_validates_mnemonic_and_address(self):
        with self.assertRaisesRegex(bluzelle.OptionsError, "bad credentials\(verify your address and mnemonic\)"):
            bluzelle.new_client({
                "address": "1",
                "mnemonic": mnemonic
            })