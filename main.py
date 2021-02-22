import time
import sys

from py4j.java_gateway import JavaGateway
from py4j.protocol import Py4JNetworkError

# OTHER CODE #
from ltlf2dfa_nx import LTLf2nxParser
from agent_synth_game import AgentSynthGame
from prismhandler.prism_handler import PrismHandler
from prismhandler.prism_io import write_prism_model
from assumptions import *
from models import *


if __name__ == '__main__':
    abs_start_time = time.time()
    # setup PRISM gateway to java API handler
    try:
        prism_handler = PrismHandler()
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
        print('########################')
        print('Starting safety computations round %i...' % (i+1))
        print('########################')
        start_time = time.time()

        agent1.create_dfa(ltlf_parser)
        agent2.create_dfa(ltlf_parser)

        agent1.create_synthesis_game()
        agent2.create_synthesis_game()

        print('Created synthesis games.')
        print('Agent1:', len(agent1.synth.nodes), 'states,', len(agent1.synth.edges), 'edges')
        print('Agent1:', len(agent1.synth.nodes), 'states,', len(agent1.synth.edges), 'edges')

        agent1.prune_game()
        agent2.prune_game()

        print('Pruned synthesis games.')
        print('Agent1:', len(agent1.synth.nodes), 'states,', len(agent1.synth.edges), 'edges')
        print('Agent1:', len(agent1.synth.nodes), 'states,', len(agent1.synth.edges), 'edges')
        print('Took', time.time() - start_time, 'seconds. \n')

        # PRISM translations
        prism_model1, state_ids1 = write_prism_model(agent1.synth, agent1.name + '_safety_r%i' % i)
        prism_model2, state_ids2 = write_prism_model(agent2.synth, agent2.name + '_safety_r%i' % i)
        print('Wrote synthesis game to PRISM model file.')

        # call PRISM-games to see if there exists a strategy
        start_time = time.time()

        prism_handler.load_model_file('../' + prism_model1)   # java handler is in a subfolder
        result1 = prism_handler.check_bool_property(win_prop)

        prism_handler.load_model_file('../' + prism_model2)  # java handler is in a subfolder
        result2 = prism_handler.check_bool_property(win_prop)
        print('Called PRISM-games to compute strategy.')

        if result1[0] and result2[0]:  # initial state always has id 0
            print('No adviser computation necessary, winning strategy already exists!')
            print('Took', time.time() - start_time, 'seconds.\n')
            break
        else:
            print('Agent1:', result1[0], ', Agent2:', result2[0])
            print('Winning strategy does not exist, will compute minimal safety assumptions.')
            print('Took', time.time() - start_time, 'seconds.\n')

        # SAFETY ASSUMPTIONS
        # call PRISM-games to compute cooperative safe set
        start_time = time.time()
        prism_handler.load_model_file('../' + prism_model1)
        result1 = prism_handler.check_bool_property(safass_prop)

        prism_handler.load_model_file('../' + prism_model1)
        result2 = prism_handler.check_bool_property(safass_prop)

        print('Called PRISM-games to compute cooperative reachability objective.')
        print('Took', time.time() - start_time, 'seconds. \n')

        # compute simplest safety advisers
        safety_edges1 = minimal_safety_edges(agent1.synth, state_ids1, result1)
        ssa1 = simplest_safety_adviser(agent1.synth, safety_edges1)
        print('Agent 1:')
        ssa1.print_advice()
        print('')

        safety_edges2 = minimal_safety_edges(agent2.synth, state_ids2, result2)
        ssa2 = simplest_safety_adviser(agent2.synth, safety_edges2)
        print('Agent 2:')
        ssa2.print_advice()
        print('')

        print('Computed minimal set of safety assumptions.')

        # save advisers
        agent1.own_advisers.append(ssa1)
        agent2.own_advisers.append(ssa2)

        agent1.other_advisers.append(ssa2)
        agent2.other_advisers.append(ssa1)

        # incorporate simplest safety adviser to specification
        agent1.adviser_to_spec(ssa2)
        agent2.adviser_to_spec(ssa1)

        print('Added safety adviser to spec.')

    print('Took', time.time() - abs_start_time, 'seconds in total. \n')