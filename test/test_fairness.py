import unittest
import networkx as nx

from py4j.protocol import Py4JNetworkError
from prismhandler.prism_handler import PrismHandler
from fairness_assumptions import minimal_fairness_edges


class TestFairness(unittest.TestCase):

    def setUp(self):
        self.test_game = nx.DiGraph()
        self.test_game.graph['init'] = '1'
        self.test_game.graph['acc'] = ['5']
        self.test_game.graph['ap'] = ['START', 'GOAL']
        self.test_game.graph['ap'] = ['NAUGHTY', 'NICE']
        self.test_game.add_node('1', player=1, ap='10')
        self.test_game.add_node('5', player=1, ap='01')
        self.test_game.add_node('2', player=2)
        self.test_game.add_node('3', player=0)
        self.test_game.add_node('4', player=0)
        self.test_game.add_edge('1', '2', act='ask')
        self.test_game.add_edge('5', '2', act='restart')
        self.test_game.add_edge('2', '3', guards=['10'])
        self.test_game.add_edge('2', '4', guards=['01'])
        self.test_game.add_edge('3', '1', prob=1.0)
        self.test_game.add_edge('4', '5', prob=1.0)

        try:
            self.prism_handler = PrismHandler()
            print('Successfully connected to PRISM java gateway!')
        except Py4JNetworkError as err:
            print('Py4JNetworkError:', err)
            print('It is most likely that you forgot to start the PRISM java gateway. '
                  'Compile and launch prismhandler/PrismEntryPoint.java!')

    def test_minimal_fairness_edges(self):
        fairness_edges = minimal_fairness_edges(self.test_game, 'test', self.prism_handler, test=True)
        self.assertEqual(len(fairness_edges), 1)
