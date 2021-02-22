import unittest
import networkx as nx
from ltlf2dfa_nx import LTLf2nxParser


class TestLTL2dfaNx(unittest.TestCase):

    def setUp(self):
        self.ltlf_parser = LTLf2nxParser()

    def test_dot_no_formula(self):
        self.ltlf_parser.formula = None
        result = self.ltlf_parser.to_dot()
        assert(result is None)

    def test_dot(self):
        test_formula = 'G a'
        self.ltlf_parser.parse_formula(test_formula)
        dot_string = self.ltlf_parser.to_dot()
        # format does not need to be checked, it's not implemented by me (check ltl2dfa)
        assert type(dot_string) == str

    def test_mona_no_formula(self):
        self.ltlf_parser.formula = None
        result = self.ltlf_parser.to_mona_output()
        assert (result is None)

    def test_mona(self):
        test_formula = 'G a'
        self.ltlf_parser.parse_formula(test_formula)
        result = self.ltlf_parser.to_mona_output()
        # format does not need to be checked, it's not implemented by me (check ltl2dfa)
        assert type(result) == str

    def test_nx_no_formula(self):
        self.ltlf_parser.formula = None
        result = self.ltlf_parser.to_nxgraph()
        assert (result is None)

    def test_nx(self):
        test_formula = 'G a'
        self.ltlf_parser.parse_formula(test_formula)
        result = self.ltlf_parser.to_nxgraph()
        assert str(type(result)) == '<class \'networkx.classes.digraph.DiGraph\'>'
        assert len(result.nodes) == 3
        assert len(result.edges) == 5

        assert 'name' in result.graph.keys()
        assert 'acc' in result.graph.keys()
        assert 'ap' in result.graph.keys()

        for edge in result.edges:
            assert 'label' in result.edges[edge].keys()
            assert 'guard' in result.edges[edge].keys()
