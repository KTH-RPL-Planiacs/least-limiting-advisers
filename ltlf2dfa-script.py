from ltlf2dfa.parser.ltlf import LTLfParser
from ltlf2dfa.base import MonaProgram
from ltlf2dfa.ltlf2dfa import invoke_mona, createMonafile

import networkx as nx
import pygraphviz

import re


def get_value(text, regex, value_type=float):
    """Dump a value from a file based on a regex passed in."""
    pattern = re.compile(regex, re.MULTILINE)
    results = pattern.search(text)
    if results:
        return value_type(results.group(1))
    else:
        print("Could not find the value {}, in the text provided".format(regex))
        return value_type(0.0)

def formula_to_dot(formula_str):
    parser = LTLfParser()
    formula = parser(formula_str)       
    return formula.to_dfa()

def formula_to_mona_output(formula_str):
    parser = LTLfParser()
    formula = parser(formula_str)       
    mona_p_string = MonaProgram(formula).mona_program()
    createMonafile(mona_p_string)
    mona = invoke_mona()
    return mona

def formula_to_nxgraph(f):

    dot = formula_to_dot(f)
    mona = formula_to_mona_output(f)

    # create graph from dot output
    g = nx.drawing.nx_agraph.from_agraph(pygraphviz.AGraph(dot))
    # enforce directed graph (instead of MultiDiGraph)
    g = nx.DiGraph(g)

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

    g.graph['init'] = init
    g.remove_node('init')

    # adds alternate edge labels that are easier to parse, but harder to read

    if mona == "Formula is unsatisfiable":
        # nothing to do
        return g

    variables = get_value(mona, r'.*DFA for formula with free variables:[\s]*(.*?)\n.*', str)
    g.graph['vars'] = variables.split()

    for line in mona.splitlines():
        if line.startswith("State "):

            orig_state = get_value(line, r".*State[\s]*(\d+):\s.*", str)
            dest_state = get_value(line, r".*state[\s]*(\d+)[\s]*.*", str)
            guard = get_value(line, r".*:[\s](.*?)[\s]->.*", str)

            if orig_state == '0':
                # already deleted dummy state
                continue
            
            g.add_edge(orig_state, dest_state, guard= guard )

    return g


if __name__ == '__main__':
    f = "G(a -> X b)"
    g = formula_to_nxgraph(f)

    print(g)
    print('variables:', g.graph['vars'])
    print('initial states:', g.graph['init'])
    print('accepting states:', g.graph['acc'])
    print('nodes:', g.nodes())
    print('edges:', g.edges(data=True))

