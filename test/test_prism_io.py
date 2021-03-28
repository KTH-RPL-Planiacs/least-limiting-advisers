import unittest
import os
import networkx as nx
from prismhandler.prism_io import write_prism_model


class PrismIOTest(unittest.TestCase):

    def setUp(self):
        """
        create a mock stochastic game
        """
        self.test_game = nx.DiGraph()
        self.test_game.graph['init'] = '1'
        self.test_game.graph['acc'] = ['1']
        self.test_game.add_node('A', player=1)
        self.test_game.add_node('B', player=2)
        self.test_game.add_node('C', player=2)
        self.test_game.add_node('C_p', player=0)
        self.test_game.add_node('C_pp', player=0)
        self.test_game.add_edge('A', 'B')
        self.test_game.add_edge('A', 'C')
        self.test_game.add_edge('B', 'A')
        self.test_game.add_edge('C', 'C_p')
        self.test_game.add_edge('C_p', 'A', prob=0.5)
        self.test_game.add_edge('C_p', 'C_pp', prob=0.5)
        self.test_game.add_edge('C_pp', 'B', prob=1)

    def test_write_prism_model(self):
        """
        check if the function created a file with the correct name in the correct place
        """
        write_prism_model(self.test_game, 'test')
        self.assertTrue(os.path.exists('data/test.prism'))
