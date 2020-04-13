#!/usr/bin/env python
import unittest

import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from util import new_client

class TestMethods(unittest.TestCase):
    def test_create(self):
        client = new_client()
        key = '%d' % (time.time())
        value = 'foo'
        client.create(key, value)
        value2 = client.read(key)
        assert value == value2, 'key value mismatch %s != %s' % (value, value2)


if __name__ == '__main__':
    unittest.main()
