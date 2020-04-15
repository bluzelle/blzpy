#!/usr/bin/env python
import unittest
import time
from .util import new_client, bluzelle, key_values_to_dict, mnemonic

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

class TestMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = new_client()

    def setUp(self):
        now = time.time()
        self.key1 = '%d' % (now)
        self.key2 = '%d' % (now + 1000)
        self.value1 = 'foo'
        self.value2 = 'bar'
        self.value3 = 'baz'
        self.lease1 = 10
        self.lease2 = 20

    def test_create(self):
        self.client.create(self.key1, self.value1)

    def test_read(self):
        self.client.create(self.key1, self.value1)
        value = self.client.read(self.key1)
        self.assertEqual(value, self.value1, 'read failed: %s != %s' % (value, self.value1))

    def test_update(self):
        self.client.create(self.key1, self.value1)
        self.client.update(self.key1, self.value2)
        value = self.client.read(self.key1)
        self.assertEqual(value, self.value2, 'update failed: %s != %s' % (self.value2, value))
        self.assertNotEqual(value, self.value1, 'update failed: %s == %s' % (self.value2, value))

    def test_delete(self):
        self.client.create(self.key1, self.value1)
        self.client.delete(self.key1)
        with self.assertRaisesRegex(bluzelle.APIError, "key not found"):
            self.client.read(self.key1)

    def test_rename(self):
        self.client.create(self.key1, self.value1)
        self.client.rename(self.key1, self.key2)
        value = self.client.read(self.key2)
        self.assertEqual(value, self.value1, 'rename failed: %s != %s' % (self.value1, value))
        with self.assertRaisesRegex(bluzelle.APIError, "key not found"):
            self.client.read(self.key1)

    def test_has(self):
        self.client.create(self.key1, self.value1)
        b = self.client.has(self.key1)
        self.assertTrue(b, 'has failed: %s' % (b))

    def test_count(self):
        num = self.client.count()
        self.client.create(self.key1, self.value1)
        num2 = self.client.count()
        self.assertEqual(num+1, num2, 'count failed: %s != %s' % (num+1, num2))

    def test_keys(self):
        keys = self.client.keys()
        self.assertTrue(not(self.key1 in keys), 'keys failed: %s found in keys %s' % (self.key1, keys))
        self.client.create(self.key1, self.value1)
        keys = self.client.keys()
        self.assertTrue(self.key1 in keys, 'keys failed: %s not found in keys %s' % (self.key1, keys))

    def test_key_values(self):
        key_values = key_values_to_dict(self.client.key_values())
        self.assertTrue(not(self.key1 in key_values), 'key_values failed: %s found in keys %s' % (self.key1, key_values))
        self.client.create(self.key1, self.value1)
        key_values = key_values_to_dict(self.client.key_values())
        self.assertEqual(key_values[self.key1], self.value1, 'key_values failed: %s not found in keys %s' % (self.key1, key_values))

    def test_delete_all(self):
        self.client.create(self.key1, self.value1)
        self.client.create(self.key2, self.value1)
        self.client.read(self.key1)
        self.client.read(self.key1)
        self.client.delete_all()
        num = self.client.count()
        self.assertEqual(num, 0, 'delete failed: %s != %s' % (num, 0))

    def test_multi_update(self):
        self.client.create(self.key1, self.value1)
        self.client.create(self.key2, self.value1)
        with self.assertRaisesRegex(Exception, "not yet implemented"):
            data = {}
            data[self.key1] = self.key1
            data[self.key2] = self.key2
            self.client.multi_update(data)

    def test_read_account(self):
        account = self.client.read_account()
        self.assertTrue(bool(account['address']), 'address not defined %s' % (account['address']))

    def test_version(self):
        version = self.client.version()
        self.assertTrue(bool(version), 'version not defined %s' % (version))

    def test_tx_read(self):
        self.client.create(self.key1, self.value1)
        value = self.client.tx_read(self.key1)
        self.assertEqual(value, self.value1, 'tx_read failed: %s != %s' % (self.value1, self.value2))

    def test_tx_has(self):
        self.client.create(self.key1, self.value1)
        b = self.client.tx_has(self.key1)
        self.assertTrue(b, 'tx_has failed: %s' % (b))

    def test_tx_count(self):
        num = self.client.tx_count()
        self.client.create(self.key1, self.value1)
        num2 = self.client.tx_count()
        self.assertEqual(num+1, num2, 'tx_count failed: %s != %s' % (num+1, num2))

    def test_tx_keys(self):
        keys = self.client.tx_keys()
        self.assertTrue(not(self.key1 in keys), 'keys failed: %s found in keys %s' % (self.key1, keys))
        self.client.create(self.key1, self.value1)
        keys = self.client.tx_keys()
        self.assertTrue(self.key1 in keys, 'keys failed: %s not found in keys %s' % (self.key1, keys))

    def test_tx_key_values(self):
        key_values = key_values_to_dict(self.client.tx_key_values())
        self.assertTrue(not(self.key1 in key_values), 'key_values failed: %s found in keys %s' % (self.key1, key_values))
        self.client.create(self.key1, self.value1)
        key_values = key_values_to_dict(self.client.tx_key_values())
        self.assertEqual(key_values[self.key1], self.value1, 'key_values failed: %s not found in keys %s' % (self.key1, key_values))

    def test_get_lease(self):
        self.client.create(self.key1, self.value1, self.lease1)
        lease = self.client.get_lease(self.key1)
        self.assertEqual(lease, self.lease1, 'get_lease failed: %s != %s' % (lease, self.lease1))
