import unittest

from agent_synth_game import *


class TestAgentSynthGame(unittest.TestCase):

    def setUp(self):
        pass

    def test_group_and_flip(self):
        test_dict = {'a': [1, 2], 'b': [2, 1], 'c': [1, 3, 5]}
        flipped_dict = group_and_flip(test_dict)
        self.assertEqual(list(flipped_dict.keys()), [frozenset([1, 2]), frozenset([1, 3, 5])])
        self.assertEqual(flipped_dict[frozenset([1, 2])], ['a', 'b'])
        self.assertEqual(flipped_dict[frozenset([1, 3, 5])], ['c'])

    def test_powerset(self):
        test_input = [1, 2, 3]
        result_list = list(powerset(test_input))
        self.assertEqual(len(result_list), 8)
        for thing in result_list:
            self.assertIsInstance(thing, tuple)
        self.assertIn((), result_list)
        self.assertIn((1,), result_list)
        self.assertIn((2,), result_list)
        self.assertIn((3,), result_list)
        self.assertIn((1, 2), result_list)
        self.assertIn((1, 3), result_list)
        self.assertIn((2, 3), result_list)
        self.assertIn((1, 2, 3), result_list)

    def test_create_guard(self):
        test_ap = ['A', 'B', 'C']
        self.assertEqual(create_guard((), test_ap), '000')
        self.assertEqual(create_guard(('A', 'C'), test_ap), '101')
        self.assertEqual(create_guard(('A', 'B', 'C'), test_ap), '111')

    def test_sog_fits_to_guard(self):
        guard_ap = ['A', 'B', 'C']
        sog_ap = ['A', 'B', 'C']

        res = sog_fits_to_guard(guard='000', sog=['000'], guard_ap=guard_ap, sog_ap=sog_ap)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], '000')

        res = sog_fits_to_guard(guard='000', sog=['0X0'], guard_ap=guard_ap, sog_ap=sog_ap)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], '0X0')

        res = sog_fits_to_guard(guard='000', sog=['0X1, 11X, XX1'], guard_ap=guard_ap, sog_ap=sog_ap)
        self.assertEqual(len(res), 0)

        res = sog_fits_to_guard(guard='000', sog=['0X0', '000', '1XX'], guard_ap=guard_ap, sog_ap=sog_ap)
        self.assertEqual(len(res), 2)
        self.assertEqual(res, ['0X0', '000'])
