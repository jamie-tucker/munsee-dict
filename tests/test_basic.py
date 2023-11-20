import unittest

from munseedict import core

class BasicTestSuite(unittest.TestCase):
  """Basic test cases."""

  def test_one(self):
    assert core.test(1) == 1

class TestTwo(unittest.TestCase):
  """Test two."""

  def test_two(self):
    assert core.test(2) == 2

  def test_three(self):
    assert core.test(3) == 3