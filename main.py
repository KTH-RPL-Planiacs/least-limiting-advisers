from ltlf2dfa_nx import formula_to_nxgraph
from dfa_mdp_prod import dfa_mdp_synth
from synth2prism import write_prism_model, write_safass_prop

import time
import networkx as nx
import subprocess


def dummy_mdp():
    # player 1 states
    m = nx.DiGraph()
    m.graph['name'] = 'weird_switch'
    m.add_node("off", player=1, ap=["10"])
    m.add_node("on", player=1, ap=["01"])
    # probabilistic states
    m.add_node("off_wait", player=0)
    m.add_node("off_switch", player=0)
    m.add_node("on_wait", player=0)
    m.add_node("on_switch", player=0)
    # player 1 edges
    m.add_edge("off", "off_wait", act="wait")
    m.add_edge("off", "off_switch", act="switch")
    m.add_edge("on", "on_wait", act="wait")
    m.add_edge("on", "on_switch", act="switch")
    # probabilistic edges
    m.add_edge("off_wait", "off", prob=1)
    m.add_edge("off_switch", "on", prob=0.9)
    m.add_edge("off_switch", "off", prob=0.1)
    m.add_edge("on_wait", "on", prob=1)
    m.add_edge("on_switch", "off", prob=0.9)
    m.add_edge("on_switch", "on", prob=0.1)
    # graph information
    m.graph['init'] = "off"
    m.graph['ap'] = ["OFF", "ON"]  # all uppercase required, order sensitive

    return m


if __name__ == '__main__':
    # path to PRISM-games bin
    prism_games = '/home/gschup/prism-games-3.0-src/prism/bin/prism'
    # dummy mdp
    nx_mdp = dummy_mdp()

    # DFA from LTL formula
    # ltlf_formula = 'G(req -> F on)'
    ltlf_formula = 'G(! req)'
    nx_dfa = formula_to_nxgraph(ltlf_formula)

    # synthesis game according to paper
    start_time = time.time()
    synth_prod = dfa_mdp_synth(nx_dfa, nx_mdp)
    print('Created synthesis game:', synth_prod.graph['name'])
    print(len(synth_prod.nodes), 'states,', len(synth_prod.edges), 'edges')
    print('Took', time.time() - start_time, 'seconds. \n')

    # PRISM computations
    try:
        start_time = time.time()
        # translate model to PRISM
        prism_model, state_ids = write_prism_model(synth_prod)
        # compute safety assumption
        safass_prop = write_safass_prop()

        print('Translated synthesis game to PRISM.')
        print('Took', time.time() - start_time, 'seconds. \n')

        start_time = time.time()
        # call PRISM-games
        process = subprocess.run([prism_games, "%s" % prism_model, "%s" % safass_prop],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        # print(process.stdout)
        print('Used PRISM-games to compute minimal safety assumption edges')
        print('Took', time.time() - start_time, 'seconds.')

    except Exception as err:
        print(err)
