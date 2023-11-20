import unittest

from munseedict import core

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_one(self):
        assert core.test() == 1