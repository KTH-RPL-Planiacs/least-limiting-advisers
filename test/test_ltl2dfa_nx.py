import unittest
import networkx.classes.digraph
from ltlf2dfa_nx import LTLf2nxParser


class TestLTL2dfaNx(unittest.TestCase):

    def setUp(self):
        self.ltlf_parser = LTLf2nxParser()

    def test_dot_no_formula(self):
        """
        If no formula is set, the result should be None
        """
        self.ltlf_parser.formula = None
        result = self.ltlf_parser.to_dot()
        self.assertIsNone(result)

    def test_dot(self):
        """
        Check if the pass-through to the ltl2dfa library works and a dot_string is returned.
        Formatting is tested in the ltl2dfa library.
        """
        test_formula = 'G a'
        self.ltlf_parser.parse_formula(test_formula)
        dot_string = self.ltlf_parser.to_dot()
        # format does not need to be checked, it's not implemented by me (check ltl2dfa)
        self.assertEqual(type(dot_string), str)

    def test_mona_no_formula(self):
        """
        If no formula is set, the result should be None
        """
        self.ltlf_parser.formula = None
        result = self.ltlf_parser.to_mona_output()
        self.assertIsNone(result)

    def test_mona(self):
        """
        Check if the pass-through to the ltl2dfa library and subsequent MONA calls works and a dot_string is returned.
        Formatting is tested in the ltl2dfa library.
        """
        test_formula = 'G a'
        self.ltlf_parser.parse_formula(test_formula)
        result = self.ltlf_parser.to_mona_output()
        # format does not need to be checked, it's not implemented by me (check ltl2dfa)
        self.assertEqual(type(result), str)

    def test_nx_no_formula(self):
        """
        If no formula is set, the result should be None
        """
        self.ltlf_parser.formula = None
        result = self.ltlf_parser.to_nxgraph()
        self.assertIsNone(result)

    def test_nx(self):
        """
        Check if the transformation to a networkx graph object from an LTLf formula works
        """
        test_formula = 'G a'
        self.ltlf_parser.parse_formula(test_formula)
        result = self.ltlf_parser.to_nxgraph()
        self.assertIsInstance(result, networkx.classes.digraph.DiGraph)
        # check if the graph has the correct size
        self.assertEqual(len(result.nodes), 3)
        self.assertEqual(len(result.edges), 5)

        # graph metadata check
        self.assertIn('name', result.graph.keys())
        self.assertIn('acc', result.graph.keys())
        self.assertIn('ap', result.graph.keys())

        # check if the edges all have the necessary metadata
        for edge in result.edges:
            self.assertIn('label', result.edges[edge].keys())
            self.assertIn('guard', result.edges[edge].keys())
