#!/usr/bin/env python
import unittest
import time
from .util import new_client, bluzelle, key_values_to_dict

class TestMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = new_client()

    def setUp(self):
        now = time.time()
        self.key1 = '%d' % (now)
        self.key2 = '%d' % (now + 1000)
        self.key3 = '%d' % (now + 2000)
        self.value1 = 'foo'
        self.value2 = 'bar'
        self.value3 = 'baz'
        self.lease1 = {"seconds": 10}
        self.lease2 = {"seconds": 20}
        self.gas_info = {
            'max_fee': 4000001,
        }

    #

    def test_account(self):
        account = self.client.account()
        self.assertTrue('address' in account)

    def test_version(self):
        version = self.client.version()
        self.assertTrue(bool(version))

    #

    def test_create(self):
        self.client.create(self.key1, self.value1, self.gas_info)

    def test_create_with_lease(self):
        self.client.create(self.key1, self.value1, self.gas_info, {
            "seconds": 60
        })

    def test_create_validate_gas_info(self):
        with self.assertRaisesRegex(bluzelle.APIError, "insufficient fee: insufficient fees; got: 1ubnt required: 2000000ubnt"):
            self.client.create(self.key2, self.value1, {
              "max_fee": 1
            })

    def test_create_with_key_containing_symbols(self):
        k = self.key1 + " !\"#$%&\'()*+,-.0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        self.client.create(k, self.value1, self.gas_info)
        keys = self.client.keys()
        self.assertTrue(k in keys)
        self.client.read(k)

    def test_creates_fails_if_key_contains_slash(self):
        with self.assertRaisesRegex(bluzelle.OptionsError, "Key cannot contain a slash"):
            self.client.create("123/", self.value1, self.gas_info)

    def test_update(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        self.client.update(self.key1, self.value2, self.gas_info)
        value = self.client.read(self.key1)
        self.assertEqual(value, self.value2)
        self.assertNotEqual(value, self.value1)

    def test_delete(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        self.client.delete(self.key1, self.gas_info)
        with self.assertRaisesRegex(bluzelle.APIError, "key not found"):
            self.client.read(self.key1)

    def test_rename(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        self.client.rename(self.key1, self.key2, self.gas_info)
        value = self.client.read(self.key2)
        self.assertEqual(value, self.value1)
        with self.assertRaisesRegex(bluzelle.APIError, "key not found"):
            self.client.read(self.key1)

    def test_delete_all(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        self.client.create(self.key2, self.value1, self.gas_info)
        self.client.read(self.key1)
        self.client.read(self.key1)
        self.client.delete_all(self.gas_info)
        num = self.client.count()
        self.assertEqual(num, 0)

    def test_multi_update(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        self.client.create(self.key2, self.value1, self.gas_info)
        #
        data = [
            {"key": self.key1, "value": self.key1},
            {"key": self.key2, "value": self.key2},
        ]
        self.client.multi_update(data, self.gas_info)
        #
        self.assertEqual(self.client.read(self.key1), self.key1)
        self.assertEqual(self.client.read(self.key2), self.key2)

    def test_renew_lease(self):
        self.client.create(self.key1, self.value1, self.gas_info, self.lease1)
        self.client.renew_lease(self.key1, self.gas_info, self.lease2)
        lease = self.client.get_lease(self.key1)
        self.assertTrue(lease > self.lease1["seconds"])

    def test_renew_all_leases(self):
        self.client.create(self.key1, self.value1, self.gas_info, self.lease1)
        self.client.renew_all_leases(self.gas_info, self.lease2)
        lease = self.client.get_lease(self.key1)
        self.assertTrue(lease > self.lease1["seconds"])

    #

    def test_read(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        value = self.client.read(self.key1)
        self.assertEqual(value, self.value1)

    def test_has(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        b = self.client.has(self.key1)
        self.assertTrue(b)

    def test_count(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        num = self.client.count()
        self.assertTrue(num > 0)

    def test_keys(self):
        keys = self.client.keys()
        self.assertTrue(not(self.key1 in keys))
        self.client.create(self.key1, self.value1, self.gas_info)
        keys = self.client.keys()
        self.assertTrue(self.key1 in keys)

    def test_key_values(self):
        key_values = key_values_to_dict(self.client.key_values())
        self.assertTrue(not(self.key1 in key_values))
        self.client.create(self.key1, self.value1, self.gas_info)
        key_values = key_values_to_dict(self.client.key_values())
        self.assertEqual(key_values[self.key1], self.value1)

    def test_get_lease(self):
        self.client.create(self.key1, self.value1, self.gas_info, self.lease1)
        lease = self.client.get_lease(self.key1)
        self.assertTrue(lease <= self.lease1["seconds"])

    def test_get_n_shortest_leases(self):
        self.client.create(self.key1, self.value1, self.gas_info, self.lease1)
        self.client.create(self.key2, self.value1, self.gas_info, self.lease1)
        self.client.create(self.key3, self.value1, self.gas_info, self.lease1)
        keyleases = self.client.get_n_shortest_leases(2)
        self.assertTrue(len(keyleases) == 2)

    #

    def test_tx_read(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        value = self.client.tx_read(self.key1, self.gas_info)
        self.assertEqual(value, self.value1)

    def test_tx_has(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        b = self.client.tx_has(self.key1, self.gas_info)
        self.assertTrue(b)

    def test_tx_count(self):
        self.client.create(self.key1, self.value1, self.gas_info)
        num = self.client.tx_count(self.gas_info)
        self.assertTrue(num > 0)

    def test_tx_keys(self):
        keys = self.client.tx_keys(self.gas_info)
        self.assertTrue(not(self.key1 in keys))
        self.client.create(self.key1, self.value1, self.gas_info)
        keys = self.client.tx_keys(self.gas_info)
        self.assertTrue(self.key1 in keys)

    def test_tx_key_values(self):
        key_values = key_values_to_dict(self.client.tx_key_values(self.gas_info))
        self.assertTrue(not(self.key1 in key_values))
        self.client.create(self.key1, self.value1, self.gas_info)
        key_values = key_values_to_dict(self.client.tx_key_values(self.gas_info))
        self.assertEqual(key_values[self.key1], self.value1)

    def test_tx_get_lease(self):
        self.client.create(self.key1, self.value1, self.gas_info, self.lease1)
        lease = self.client.tx_get_lease(self.key1, self.gas_info)
        self.assertTrue(lease <= self.lease1["seconds"])

    def test_tx_get_n_shortest_leases(self):
        self.client.create(self.key1, self.value1, self.gas_info, self.lease1)
        self.client.create(self.key2, self.value1, self.gas_info, self.lease1)
        self.client.create(self.key3, self.value1, self.gas_info, self.lease1)
        keyleases = self.client.tx_get_n_shortest_leases(2, self.gas_info)
        self.assertTrue(len(keyleases) == 2)
