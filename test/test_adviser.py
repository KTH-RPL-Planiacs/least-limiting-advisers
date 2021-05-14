import unittest
from advisers import reduce_set_of_guards, flip_guard_bit, replace_guard_bit


class TestAdviser(unittest.TestCase):

    def setUp(self):
        pass

    def test_replace_guard_bit(self):
        # replace a literal
        self.assertEqual(replace_guard_bit('000', 1, 'X'), '0X0')

    def test_flip_guard_bit(self):
        # check if a bit gets flipped
        self.assertEqual(flip_guard_bit('000', 1), '010')
        # check if a 1 flip gets ignored if parameter is set
        self.assertEqual(flip_guard_bit('010', 1, skip_ones=True), '010')

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
        # completely reducible
        res = reduce_set_of_guards({'00', '10', '01', '11'})
        self.assertEqual(res, {'XX'})
        # completely reducible with partial reductions should work as well
        res = reduce_set_of_guards({'X1', '1X', '00'})
        self.assertEqual(res, {'XX'})
        # same as above
        res = reduce_set_of_guards({'1XX', 'X1X', 'XX1', '000'})
        self.assertEqual(res, {'XXX'})
