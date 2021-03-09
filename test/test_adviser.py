import unittest
from advisers import reduce_set_of_guards


class TestAdviser(unittest.TestCase):

    def setUp(self):
        pass

    def test_reduce_set_of_guards(self):
        # one guard should stay the same
        res = reduce_set_of_guards({'000'})
        self.assertEqual(res, {'000'})
        # two independent guards should stay the same
        res = reduce_set_of_guards({'100', '001'})
        self.assertEqual(res, {'100', '001'})
        # two reducible guards should get reduced
        res = reduce_set_of_guards({'000', '100'})
        self.assertEqual(res, {'X00'})
        # four reducible guards should get reduced
        res = reduce_set_of_guards({'000', '100', '010', '110'})
        self.assertEqual(res, {'XX0'})
        # partially reducible should get partially reduced
        res = reduce_set_of_guards({'110', '010', '100'})
        self.assertEqual(res, {'X10', '1X0'})
