#!/usr/bin/env python
import unittest
import time

# todo
if __name__ == '__main__':
    from util import new_client, bluzelle
else:
    from .util import new_client, bluzelle

now = time.time()
key1 = '%d' % (now)
key2 = '%d' % (now + 1000)
value1 = 'foo'
value2 = 'bar'
value3 = 'baz'

class TestMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = new_client()

    def test_create(self):
        self.client.create(key1, value1)

    def test_read(self):
        self.client.create(key1, value1)
        value = self.client.read(key1)
        self.assertEqual(value, value1, 'read failed: %s != %s' % (value1, value2))

    def test_update(self):
        self.client.create(key1, value1)
        self.client.update(key1, value2)
        value = self.client.read(key1)
        self.assertEqual(value, value2, 'update failed: %s != %s' % (value2, value))
        self.assertNotEqual(value, value1, 'update failed: %s == %s' % (value2, value))

    def test_delete(self):
        self.client.create(key1, value1)
        self.client.delete(key1)
        with self.assertRaisesRegex(bluzelle.APIError, "key not found"):
            self.client.read(key1)

    def test_rename(self):
        self.client.create(key1, value1)
        self.client.rename(key1, key2)
        value = self.client.read(key2)
        self.assertEqual(value, value1, 'rename failed: %s != %s' % (value1, value))
        with self.assertRaisesRegex(bluzelle.APIError, "key not found"):
            self.client.read(key1)

    def test_has(self):
        self.client.create(key1, value1)
        b = self.client.has(key1)
        self.assertTrue(b, 'has failed: %s' % (b))
