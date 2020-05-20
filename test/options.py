#!/usr/bin/env python
import unittest
import time
from .util import new_client, bluzelle, ADDRESS, Client

class TestOptions(unittest.TestCase):
    def test_requires_mnemonic(self):
        with self.assertRaisesRegex(bluzelle.OptionsError, "mnemonic is required"):
            bluzelle.new_client({
            })
        with self.assertRaisesRegex(bluzelle.OptionsError, "mnemonic must be a string"):
            bluzelle.new_client({
                'mnemonic': 1
            })

    def test_validates_gas_info(self):
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info should be a dict of {gas_price, max_fee, max_gas}"):
            Client.validate_gas_info("")
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info should be a dict of {gas_price, max_fee, max_gas}"):
            Client.validate_gas_info(1)
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info should be a dict of {gas_price, max_fee, max_gas}"):
            Client.validate_gas_info([])
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info\[max_fee\] should be an int"):
            Client.validate_gas_info({
                "max_fee": ""
            })
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info\[max_gas\] should be an int"):
            Client.validate_gas_info({
                "max_gas": ""
            })
        with self.assertRaisesRegex(bluzelle.OptionsError, "gas_info\[gas_price\] should be an int"):
            Client.validate_gas_info({
                "gas_price": ""
            })

    def test_correctly_derives_address(self):
        c = new_client()
        self.assertEqual(c.address, ADDRESS)

class TestLease(unittest.TestCase):
  def test_converts_blocks_to_seconds(self):
    self.assertEqual(Client.lease_blocks_to_seconds(1), 5)
    self.assertEqual(Client.lease_blocks_to_seconds(2), 10)
    self.assertEqual(Client.lease_blocks_to_seconds(3), 15)

  def test_converts_lease_info_to_blocks(self):
    self.assertEqual(Client.lease_info_to_blocks({
    }), 0)
    self.assertEqual(Client.lease_info_to_blocks({
      "seconds": 5
    }), 1)
    self.assertEqual(Client.lease_info_to_blocks({
      "seconds": 5,
      "minutes": 1,
    }), 13)
    self.assertEqual(Client.lease_info_to_blocks({
      "seconds": 5,
      "minutes": 1,
      "hours": 1,
    }), 733)
    self.assertEqual(Client.lease_info_to_blocks({
      "seconds": 5,
      "minutes": 1,
      "hours": 1,
      "days": 1,
    }), 18013)
