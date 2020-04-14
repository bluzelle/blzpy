import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest

if __name__ == '__main__':
    from test import TestMethods
    unittest.main()
