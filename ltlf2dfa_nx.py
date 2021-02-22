from ltlf2dfa.parser.ltlf import LTLfParser
from ltlf2dfa.base import MonaProgram
from ltlf2dfa.ltlf2dfa import invoke_mona, createMonafile

import networkx as nx
import pygraphviz

import re


# Dump a value from a file based on a regex passed in.
def get_value(text, regex, value_type=float):
    pattern = re.compile(regex, re.MULTILINE)
    results = pattern.search(text)
    if results:
        return value_type(results.group(1))
    else:
        print("Could not find the value {}, in the text provided".format(regex))
        return value_type(0.0)


class LTLf2nxParser:

    def __init__(self):
        self.parser = LTLfParser()
        self.formula = None

    def parse_formula(self, formula_str):
        self.formula = self.parser(formula_str)

    def to_dot(self):
        if self.formula is None:
            print('<LTLf2ndParser.to_dot()> No formula parsed. Please parse a formula first using parse_formula(str)!')
            return None

        return self.formula.to_dfa()

    def to_mona_output(self):
        if self.formula is None:
            print('<LTLf2ndParser.to_dot()> No formula parsed. Please parse a formula first using parse_formula(str)!')
            return None

        mona_p_string = MonaProgram(self.formula).mona_program()
        createMonafile(mona_p_string)
        mona = invoke_mona()
        return mona

    def to_nxgraph(self, name= 'MONA_DFA'):
        if self.formula is None:
            print('<LTLf2ndParser.to_dot()> No formula parsed. Please parse a formula first using parse_formula(str)!')
            return None

        dot = self.to_dot()
        mona = self.to_mona_output()

        # create graph from dot output
        g = nx.drawing.nx_agraph.from_agraph(pygraphviz.AGraph(dot))
        # enforce directed graph (instead of MultiDiGraph)
        g = nx.DiGraph(g)
        g.graph.clear()
        g.graph['name'] = name

        # re-label all shape doublecircle nodes as accepting nodes
        acc = []
        for node in g.nodes():
            if 'shape' in g.nodes[node] and g.nodes[node]['shape'] == 'doublecircle':
                acc.append(node)
                del g.nodes[node]['shape']

        g.graph['acc'] = acc

        # label actual init nodes and remove dummy init node !ASSUMES SINGULAR INIT NODE!
        init = []
        for succ in g.successors('init'):
            init.append(succ)

        g.graph['init'] = init[0]
        g.remove_node('init')

        # adds alternate edge labels that are easier to parse, but harder to read

        if mona == "Formula is unsatisfiable":
            # nothing to do
            return g

        variables = get_value(mona, r'.*DFA for formula with free variables:[\s]*(.*?)\n.*', str)
        g.graph['ap'] = variables.split()

        for line in mona.splitlines():
            if line.startswith("State "):

                orig_state = get_value(line, r".*State[\s]*(\d+):\s.*", str)
                dest_state = get_value(line, r".*state[\s]*(\d+)[\s]*.*", str)
                guard = get_value(line, r".*:[\s](.*?)[\s]->.*", str)

                if orig_state == '0':
                    # already deleted dummy state
                    continue

                if 'guard' in g.edges[orig_state, dest_state]:
                    new_guard = g.edges[orig_state, dest_state]['guard']
                    new_guard.append(guard)
                    g.add_edge(orig_state, dest_state, guard=new_guard)
                else:
                    g.add_edge(orig_state, dest_state, guard=[guard])

        return g
