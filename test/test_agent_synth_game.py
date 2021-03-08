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
        pass

    def test_create_guard(self):
        pass

    def test_sog_fits_to_guard(self):
        pass
