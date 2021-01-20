import time
import sys
import networkx as nx
from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError

# OTHER CODE #
from ltlf2dfa_nx import formula_to_nxgraph
from dfa_mdp_prod import dfa_mdp_synth
from prism_interface import write_prism_model
from minimal_assumptions import minimal_safety_assumptions, simplest_safety_adviser


def dummy_mdp():
    # player 1 states
    m = nx.DiGraph()
    m.graph['name'] = 'switch'
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
    abs_start_time = time.time()
    # setup PRISM gateway to java API handler
    try:
        gateway = JavaGateway()
        prism_handler = gateway.entry_point.getPrismHandler()
        print('Connected to Java PRISM gateway!')
    except Py4JNetworkError as err:
        print('Py4JNetworkError:', err)
        print('It is most likely that you forgot to start the PRISM java gateway. '
              'Compile and launch prismhandler/PrismEntryPoint.java!')
        sys.exit()

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

    # PRISM translations
    start_time = time.time()
    prism_model, state_ids = write_prism_model(synth_prod)
    safass_prop = '<< p1,p2 >> Pmax =? [F \"accept\"]'
    win_prop = '<< p1 >> Pmax =? [F \"accept\"]'

    print('Wrote synthesis game to PRISM model file.')
    print('Took', time.time() - start_time, 'seconds. \n')

    # call PRISM-games to see if there exists a strategy
    start_time = time.time()
    prism_handler.loadModelFile('../'+prism_model)   # java handler is in a subfolder
    result = prism_handler.checkProperty(win_prop)
    print('Called PRISM-games to compute strategy.')
    print('Took', time.time() - start_time, 'seconds. \n')

    if result[0] >= 1:  # initial state always has id 0
        print('No adviser computation necessary, winning strategy already exists!')
        sys.exit()

    # call PRISM-games to compute cooperative safe set
    start_time = time.time()
    result = prism_handler.checkProperty(safass_prop)

    # TODO: ugly stuff! makes a copy to separate from java gateway
    res_copy = []
    for res in result:
        res_copy.append(res)
    print(res_copy)

    print('Called PRISM-games to compute cooperative reachability objective.')
    print('Took', time.time() - start_time, 'seconds. \n')

    # compute simplest safety advisers
    start_time = time.time()
    safass_edges = minimal_safety_assumptions(synth_prod, state_ids, res_copy)
    saf_adv = simplest_safety_adviser(synth_prod, safass_edges)
    print('Computed minimal set of safety assumptions.')
    print('Took', time.time() - start_time, 'seconds. \n')
    if not saf_adv:
        print('No safety assumptions necessary!')
    for adv in saf_adv:
        print('If you see', adv[0], synth_prod.graph['ap'], 'never do', list(adv[1]), synth_prod.graph['env_ap'])

    print('')
    print('Took', time.time() - abs_start_time, 'seconds in total. \n')