#!/usr/bin/env python
import unittest

import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from util import new_client, bluzelle

key1 = '%d' % (time.time())
key2 = '%d' % (time.time())
value1 = 'foo'
value2 = 'bar'
value3 = 'baz'

class TestMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = new_client()

    def test_crud(self):
        # create
        self.client.create(key1, value1)

        # read
        value = self.client.read(key1)
        self.assertEqual(value, value1, 'value mismatch %s != %s' % (value1, value2))

        # update
        self.client.update(key1, value2)
        value = self.client.read(key1)
        self.assertEqual(value, value2, 'value mismatch %s != %s' % (value2, value))
        self.assertNotEqual(value, value1, 'value mismatch %s == %s' % (value2, value))

        # delete
        self.client.delete(key1)
        with self.assertRaisesRegex(bluzelle.APIError, "key not found"):
            self.client.read(key1)

if __name__ == '__main__':
    unittest.main()
