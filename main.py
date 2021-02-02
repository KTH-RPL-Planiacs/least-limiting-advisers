import time
import sys
import networkx as nx
from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError

# OTHER CODE #
from ltlf2dfa_nx import LTLf2nxParser
from agent_synth_game import AgentSynthGame
from prism_interface import write_prism_model
from assumptions import *


def dummy_mdp():
    # player 1 states
    m = nx.DiGraph()
    m.graph['name'] = 'broken_switch'
    m.add_node("off", player=1, ap=["00"])
    m.add_node("on", player=1, ap=["10"])
    m.add_node("broke", player=1, ap=["01"])

    # probabilistic states
    m.add_node("broke_repair", player=0)
    m.add_node("off_wait", player=0)
    m.add_node("off_switch", player=0)
    m.add_node("on_wait", player=0)
    m.add_node("on_switch", player=0)

    # player 1 edges
    m.add_edge("broke", "broke_repair", act="repair")
    m.add_edge("off", "off_wait", act="wait")
    m.add_edge("off", "off_switch", act="switch")
    m.add_edge("on", "on_wait", act="wait")
    m.add_edge("on", "on_switch", act="switch")

    # probabilistic edges
    m.add_edge("broke_repair", "off", prob=0.5)
    m.add_edge("broke_repair", "broke", prob=0.5)

    m.add_edge("off_wait", "off", prob=1)

    m.add_edge("off_switch", "on", prob=0.8)
    m.add_edge("off_switch", "off", prob=0.1)
    m.add_edge("off_switch", "broke", prob=0.1)

    m.add_edge("on_wait", "on", prob=1)
    m.add_edge("on_switch", "off", prob=1)

    # graph information
    m.graph['init'] = "off"
    m.graph['ap'] = ["ON", "BROKE"]  # all uppercase required, order sensitive

    return m


def pythonify(gateway_obj):
    res_copy = []
    for res in gateway_obj:
        res_copy.append(res)
    return res_copy


if __name__ == '__main__':
    abs_start_time = time.time()
    # setup PRISM gateway to java API handler
    try:
        gateway = JavaGateway()
        prism_handler = gateway.entry_point.getPrismHandler()
        print('Successfully connected to PRISM java gateway!')
    except Py4JNetworkError as err:
        print('Py4JNetworkError:', err)
        print('It is most likely that you forgot to start the PRISM java gateway. '
              'Compile and launch prismhandler/PrismEntryPoint.java!')
        sys.exit()

    # LTLf -> DFA parser init
    ltlf_parser = LTLf2nxParser()

    # synthesis game according to paper
    start_time = time.time()
    agent = AgentSynthGame(mdp=dummy_mdp(), formula='F(on) & G(broke -> ! X req)')
    agent.create_dfa(ltlf_parser)
    agent.create_synthesis_game()
    print('Created synthesis game:', agent.name)
    print(len(agent.synth.nodes), 'states,', len(agent.synth.edges), 'edges')
    print('Took', time.time() - start_time, 'seconds. \n')

    # PRISM translations
    start_time = time.time()
    prism_model, state_ids = write_prism_model(agent.synth, agent.name)
    safass_prop = '<< p1,p2 >> P>=1 [F \"accept\"]'
    win_prop = '<< p1 >> P>=1 [F \"accept\"]'

    print('Wrote synthesis game to PRISM model file.')
    print('Took', time.time() - start_time, 'seconds. \n')

    # call PRISM-games to see if there exists a strategy
    start_time = time.time()
    prism_handler.loadModelFile('../'+prism_model)   # java handler is in a subfolder
    result = prism_handler.checkBoolProperty(win_prop)
    result = pythonify(result)
    print('Called PRISM-games to compute strategy.')

    if result[0]:  # initial state always has id 0
        print('No adviser computation necessary, winning strategy already exists!')
        print('Took', time.time() - start_time, 'seconds.\n')
        sys.exit()
    else:
        print('Winning strategy does not exist, will compute minimal safety assumptions.')
        print('Took', time.time() - start_time, 'seconds.\n')

    # call PRISM-games to compute cooperative safe set
    start_time = time.time()
    result = prism_handler.checkBoolProperty(safass_prop)
    result = pythonify(result)      # TODO: ugly stuff! makes a copy to separate from java gateway

    print('Called PRISM-games to compute cooperative reachability objective.')
    print('Took', time.time() - start_time, 'seconds. \n')

    # compute simplest safety advisers
    start_time = time.time()
    safety_edges = minimal_safety_edges(agent.synth, state_ids, result)
    ssa = simplest_safety_adviser(agent.synth, safety_edges)
    # incorporate own safety adviser
    agent.delete_unsafe_edges_ssa(ssa)     # alternative: agent_game.delete_unsafe_edges(safety_edges)

    print('Computed and removed minimal set of safety assumptions.')
    ssa.print_advice()
    print('Took', time.time() - start_time, 'seconds. \n')

    # check if there is a winning strategy now
    start_time = time.time()
    safe_prism_model, state_ids = write_prism_model(agent.synth, agent.name + '_safe')
    prism_handler.loadModelFile('../' + safe_prism_model)  # java handler is in a subfolder
    result = prism_handler.checkBoolProperty(win_prop)
    result = pythonify(result)      # TODO: ugly stuff! makes a copy to separate from java gateway
    print('Called PRISM-games to compute strategy on game with safety assumptions.')
    if result[0]:
        print('Winning strategy exists.')
    else:
        print('Additional fairness needed.')
    print('Took', time.time() - start_time, 'seconds. \n')

    # incorporate simplest safety adviser test
    start_time = time.time()
    dummy_saf_adv = AdviserObject(pre_ap=['TEST'],
                                  adv_ap=['BROKE'],
                                  pre_init='0',
                                  adv_type='safety')
    dummy_saf_adv.adviser['1'] = ['1']

    agent.adviser_to_spec(dummy_saf_adv)
    agent.create_dfa(ltlf_parser)
    agent.create_synthesis_game()
    print('Incorporated dummy safety advice into synth game')
    print('Took', time.time() - start_time, 'seconds. \n')

    print('Took', time.time() - abs_start_time, 'seconds in total. \n')