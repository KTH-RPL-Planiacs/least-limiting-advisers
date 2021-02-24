import unittest
import os
import networkx as nx
from prismhandler.prism_io import write_prism_model


class PrismIOTest(unittest.TestCase):

    def setUp(self):
        self.test_game = nx.DiGraph()
        self.test_game.graph['init'] = '1'
        self.test_game.graph['acc'] = ['1']
        self.test_game.add_node('1', player=1)
        self.test_game.add_node('1.5', player=0)
        self.test_game.add_node('2', player=2)
        self.test_game.add_node('3', player=0)
        self.test_game.add_edge('1', '1.5')
        self.test_game.add_edge('2', '3')
        self.test_game.add_edge('3', '1', prob=1.0)
        self.test_game.add_edge('1.5', '2', prob=1.0)

    def test_write_prism_model(self):
        write_prism_model(self.test_game, 'test')
        self.assertTrue(os.path.exists('data/test.prism'))
