import time
import sys

from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError

# OTHER CODE #
from ltlf2dfa_nx import LTLf2nxParser
from agent_synth_game import AgentSynthGame
from prism_interface import write_prism_model
from assumptions import *
from models import *


# TODO: ugly stuff! makes a copy to separate from java gateway
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

    # create agents
    agent1 = AgentSynthGame(mdp=robot1_2x3_mdp(), formula='F(goala) & G!(crita && critb)')
    agent2 = AgentSynthGame(mdp=robot2_2x3_mdp(), formula='F(goalb) & G!(crita && critb)')

    # PRISM goal properties
    safass_prop = '<< p1,p2 >> P>=1 [F \"accept\"]'
    win_prop = '<< p1 >> P>=1 [F \"accept\"]'

    for i in range(2):
        start_time = time.time()

        agent1.create_dfa(ltlf_parser)
        agent2.create_dfa(ltlf_parser)

        if i == 1:
            f = agent1.get_spec_formula()
            ltlf_parser.parse_formula(f)
            print(ltlf_parser.to_dot())

        agent1.create_synthesis_game()
        agent2.create_synthesis_game()

        if i == 1:
            print(agent1.synth.graph)

        print('Created synthesis games.')
        print('Agent1:', len(agent1.synth.nodes), 'states,', len(agent1.synth.edges), 'edges')
        print('Agent1:', len(agent1.synth.nodes), 'states,', len(agent1.synth.edges), 'edges')
        print('Took', time.time() - start_time, 'seconds. \n')

        # PRISM translations
        prism_model1, state_ids1 = write_prism_model(agent1.synth, agent1.name)
        prism_model2, state_ids2 = write_prism_model(agent2.synth, agent2.name)
        print('Wrote synthesis game to PRISM model file.')

        # call PRISM-games to see if there exists a strategy
        start_time = time.time()

        prism_handler.loadModelFile('../'+prism_model1)   # java handler is in a subfolder
        result1 = prism_handler.checkBoolProperty(win_prop)
        result1 = pythonify(result1)

        prism_handler.loadModelFile('../' + prism_model2)  # java handler is in a subfolder
        result2 = prism_handler.checkBoolProperty(win_prop)
        result2 = pythonify(result2)
        print('Called PRISM-games to compute strategy.')

        if result1[0] and result2[0]:  # initial state always has id 0
            print('No adviser computation necessary, winning strategy already exists!')
            print('Took', time.time() - start_time, 'seconds.\n')
            sys.exit()
        else:
            print('Agent1:', result1[0], ', Agent2:', result2[0])
            print('Winning strategy does not exist, will compute minimal safety assumptions.')
            print('Took', time.time() - start_time, 'seconds.\n')

        # SAFETY ASSUMPTIONS
        # call PRISM-games to compute cooperative safe set
        start_time = time.time()
        prism_handler.loadModelFile('../' + prism_model1)
        result1 = prism_handler.checkBoolProperty(safass_prop)
        result1 = pythonify(result1)

        prism_handler.loadModelFile('../' + prism_model1)
        result2 = prism_handler.checkBoolProperty(safass_prop)
        result2 = pythonify(result2)

        print('Called PRISM-games to compute cooperative reachability objective.')
        print('Took', time.time() - start_time, 'seconds. \n')

        # compute simplest safety advisers
        safety_edges1 = minimal_safety_edges(agent1.synth, state_ids1, result1)
        ssa1 = simplest_safety_adviser(agent1.synth, safety_edges1)
        agent1.delete_unsafe_edges_ssa(ssa1)     # alternative: agent_game.delete_unsafe_edges(safety_edges)
        print('Agent 1:')
        ssa1.print_advice()
        print('')

        safety_edges2 = minimal_safety_edges(agent2.synth, state_ids2, result2)
        ssa2 = simplest_safety_adviser(agent2.synth, safety_edges2)
        agent2.delete_unsafe_edges_ssa(ssa2)  # alternative: agent_game.delete_unsafe_edges(safety_edges)
        print('Agent 2:')
        ssa2.print_advice()
        print('')

        print('Computed and removed minimal set of safety assumptions.')

        # check if there is a winning strategy now
        # start_time = time.time()
        # safe_prism_model1, save_state_ids1 = write_prism_model(agent1.synth, agent1.name + '_safe')
        # prism_handler.loadModelFile('../' + safe_prism_model1)  # java handler is in a subfolder
        # result1 = prism_handler.checkBoolProperty(win_prop)
        # result1 = pythonify(result1)
        #
        # safe_prism_model2, save_state_ids2 = write_prism_model(agent2.synth, agent2.name + '_safe')
        # prism_handler.loadModelFile('../' + safe_prism_model1)  # java handler is in a subfolder
        # result2 = prism_handler.checkBoolProperty(win_prop)
        # result2 = pythonify(result2)
        #
        # print('Called PRISM-games to compute strategy on game with safety assumptions.')
        # print('Agent1:', result1[0], ', Agent2:', result2[0])
        # print('Took', time.time() - start_time, 'seconds. \n')

        # incorporate simplest safety adviser
        agent1.adviser_to_spec(ssa2)
        agent2.adviser_to_spec(ssa1)

        print('Added safety adviser to spec.')


    """
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
    """

    print('Took', time.time() - abs_start_time, 'seconds in total. \n')