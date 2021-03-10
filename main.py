import time
import sys

from py4j.protocol import Py4JNetworkError

# OTHER CODE #
from ltlf2dfa_nx import LTLf2nxParser
from agent_synth_game import AgentSynthGame
from prismhandler.prism_handler import PrismHandler
from prismhandler.prism_io import write_prism_model
from safety_assumptions import minimal_safety_edges
from fairness_assumptions import minimal_fairness_edges
from advisers import simplest_adviser
from models import *


class AdviserFramework:

    def __init__(self, agents):
        # PRISM API gateway
        try:
            self.prism_handler = PrismHandler()
            print('Successfully connected to PRISM java gateway!')
        except Py4JNetworkError as err:
            print('Py4JNetworkError:', err)
            print('It is most likely that you forgot to start the PRISM java gateway. '
                  'Compile and launch prismhandler/PrismEntryPoint.java!')
            sys.exit()

        self.ltlf_parser = LTLf2nxParser()
        self.agents = agents
        self.create_synth_games()

    def create_synth_games(self):
        start_time = time.time()
        for agent in self.agents:
            agent.create_dfa(self.ltlf_parser)          # update spec according to other safety advisers and create DFA
            agent.create_synthesis_game()               # create synthesis game
            # TODO                                      # update edges that can be assumed fair
            agent.prune_game(additional_pruning=True)   # modify game according to own safety and fairness advisers

        print('Created synthesis games for all agents.')
        print('Took', time.time() - start_time, 'seconds. \n')

    def check_winnable(self, verbose=True):
        results = []
        # check if agents can win with the current game
        for agent in self.agents:
            prism_model, state_ids = write_prism_model(agent.synth, agent.name + '_win')
            self.prism_handler.load_model_file(prism_model)
            result = self.prism_handler.check_bool_property('<< p1 >> P>=1 [F \"accept\"]')
            results.append(result[0])
            if verbose:
                print('Agent %s has a winning strategy:' % agent.name, result[0])

        return results

    def compute_and_exchange_fairness(self):
        fairness_start_time = time.time()
        fairness_changed = True
        rounds = 0

        # compute safety first
        self.compute_and_exchange_safety()

        while fairness_changed:
            start_time = time.time()
            print('')
            print('########################')
            print('Starting fairness computations round %i...' % (rounds + 1))
            print('########################')
            print('')

            for agent in self.agents:
                fairness_edges = minimal_fairness_edges(agent.synth, agent.name, self.prism_handler)
                sfa = simplest_adviser(agent.synth, fairness_edges, 'fairness')

                if len(sfa.adviser) > 0:
                    print('Fairness Advisers for Agent %s:' % agent.name)
                    agent.own_advisers.append(sfa)
                    agent.fairness_edges.extend(fairness_edges)

                    for other_agent in self.agents:
                        if agent.name == other_agent.name:
                            continue

                        other_agent.other_advisers.append(sfa)

            print('Computed locally minimal set of fairness assumptions.')
            print('Took', time.time() - start_time, 'seconds.\n')

            # TODO: unfinished
            fairness_changed = False

        print('Fairness converged after %i rounds.' % rounds)
        print('Took', time.time() - fairness_start_time, 'seconds. \n')
        print('')

        for agent in self.agents:
            print('Final Fairness Advisers for Agent %s:' % agent.name)
            for adviser in agent.own_advisers:
                if not adviser.adv_type == 'fairness':
                    continue
                adviser.print_advice()
            print('')

    def compute_and_exchange_safety(self):
        safety_start_time = time.time()
        safety_changed = True
        rounds = 0
        while safety_changed:
            print('')
            print('########################')
            print('Starting safety computations round %i...' % (rounds + 1))
            print('########################')
            print('')

            self.create_synth_games()

            # SAFETY ASSUMPTIONS
            # call PRISM-games to compute cooperative safe set
            # then, compute simplest safety advisers
            # and save advisers if they are nonempty
            start_time = time.time()
            safety_changed = False

            for agent in self.agents:
                safety_edges = minimal_safety_edges(agent.synth, agent.name + '_safety', self.prism_handler)
                ssa = simplest_adviser(agent.synth, safety_edges, 'safety')

                if len(ssa.adviser) > 0:
                    safety_changed = True
                    agent.own_advisers.append(ssa)

                    for other_agent in self.agents:
                        if agent.name == other_agent.name:
                            continue

                        other_agent.other_advisers.append(ssa)

            rounds += 1
            print('Called PRISM-games to compute cooperative reachability objective.')
            print('Computed minimal set of safety assumptions.')
            print('Added safety adviser to spec.')
            print('Took', time.time() - start_time, 'seconds. \n')

        print('Safety converged after %i rounds.' % rounds)
        print('Took', time.time() - safety_start_time, 'seconds. \n')
        print('')

        for agent in self.agents:
            print('Final Safety Advisers for Agent %s:' % agent.name)
            for adviser in agent.own_advisers:
                if not adviser.adv_type == 'safety':
                    continue

                adviser.print_advice()
            print('')


if __name__ == '__main__':

    agents_list = [AgentSynthGame(mdp=corridor_mdp('A', init_state='end_top'), formula='F(eba) & G!(crita && critb)'),
                   AgentSynthGame(mdp=corridor_mdp('B', init_state='end_bot'), formula='F(etb) & G!(crita && critb)')]

    framework = AdviserFramework(agents_list)
    winnable = framework.check_winnable()

    if all(winnable):
        print('No adviser computation necessary, winning strategies already exists!')
    else:
        print('Winning strategy does not exist for some agents, will compute minimal assumptions.')
        framework.compute_and_exchange_fairness()
