import unittest
import networkx.classes.digraph
from ltlf2dfa_nx import LTLf2nxParser


class TestLTL2dfaNx(unittest.TestCase):

    def setUp(self):
        self.ltlf_parser = LTLf2nxParser()

    def test_dot_no_formula(self):
        self.ltlf_parser.formula = None
        result = self.ltlf_parser.to_dot()
        self.assertIsNone(result)

    def test_dot(self):
        test_formula = 'G a'
        self.ltlf_parser.parse_formula(test_formula)
        dot_string = self.ltlf_parser.to_dot()
        # format does not need to be checked, it's not implemented by me (check ltl2dfa)
        self.assertEqual(type(dot_string), str)

    def test_mona_no_formula(self):
        self.ltlf_parser.formula = None
        result = self.ltlf_parser.to_mona_output()
        self.assertIsNone(result)

    def test_mona(self):
        test_formula = 'G a'
        self.ltlf_parser.parse_formula(test_formula)
        result = self.ltlf_parser.to_mona_output()
        # format does not need to be checked, it's not implemented by me (check ltl2dfa)
        self.assertEqual(type(result), str)

    def test_nx_no_formula(self):
        self.ltlf_parser.formula = None
        result = self.ltlf_parser.to_nxgraph()
        self.assertIsNone(result)

    def test_nx(self):
        test_formula = 'G a'
        self.ltlf_parser.parse_formula(test_formula)
        result = self.ltlf_parser.to_nxgraph()
        self.assertIsInstance(result, networkx.classes.digraph.DiGraph)
        self.assertEqual(len(result.nodes), 3)
        self.assertEqual(len(result.edges), 5)

        self.assertIn('name', result.graph.keys())
        self.assertIn('acc', result.graph.keys())
        self.assertIn('ap', result.graph.keys())

        for edge in result.edges:
            self.assertIn('label', result.edges[edge].keys())
            self.assertIn('guard', result.edges[edge].keys())
