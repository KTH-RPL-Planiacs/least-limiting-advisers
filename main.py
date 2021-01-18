from ltlf2dfa_nx import formula_to_nxgraph
from dfa_mdp_prod import dfa_mdp_synth
from prism_interface import write_prism_model, write_safass_prop, read_results
from minimal_assumptions import minimal_safety_assumptions, minimal_fairness_assumptions, simplest_safety_adviser

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
        prism_model, state_ids = write_prism_model(synth_prod)
        safass_prop = write_safass_prop()

        print('Translated synthesis game to PRISM.')
        print('Took', time.time() - start_time, 'seconds. \n')

        # call PRISM-games to compute cooperative safe set
        start_time = time.time()
        process = subprocess.run([prism_games, '%s' % prism_model, '%s' % safass_prop, '-exportvector', 'data/safass_results'],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        reach_probs = read_results('data/safass_results')
        print('Called PRISM-games to compute cooperative reachability objective.')
        print('Took', time.time() - start_time, 'seconds. \n')

        # compute simplest safety advisers
        start_time = time.time()
        safass_edges = minimal_safety_assumptions(synth_prod, state_ids, reach_probs)
        saf_adv = simplest_safety_adviser(synth_prod, safass_edges)
        print('Computed minimal set of safety assumptions.')
        print('Took', time.time() - start_time, 'seconds. \n')
        for adv in saf_adv:
            print('If you see', adv[0], synth_prod.graph['ap'], 'never do', adv[1], synth_prod.graph['env_ap'])

    except Exception as err:
        print(err)
