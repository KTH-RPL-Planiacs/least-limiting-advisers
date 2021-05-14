from agent_synth_game import AgentSynthGame
from adviser_framework import AdviserFramework
from models.corridor import corridor_directions_mdp
from models.misc import *
from models.office_generator import *
import statistics


def running_example():
    agents = [AgentSynthGame(mdp=corridor_directions_mdp(r_id='A', init_state='end_l_fr'),
                             formula='F(era) & G!(crita & critb)'),
              AgentSynthGame(mdp=corridor_directions_mdp(r_id='B', init_state='end_r_fl'),
                             formula='F(elb) & G!(critb & crita)')]
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/running_example.p', verbose=True)


def office_10x5(n_agents, n_bins):
    agents = []
    for n in range(n_agents):
        ltlf = ''
        for i in range(n_bins):
            ltlf += '(F bin%i%i) & ' % (i, n)
        ltlf = ltlf[:-3]
        agents.append(AgentSynthGame(mdp=office_5x10_mdp(r_id='%i' % n, n_bins=n_bins), formula=ltlf))
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/office_10x5_%i_%i.p' % (n_agents, n_bins), verbose=True)


def office_spillage_10x5(n_bin_agents, n_bins, n_clean_agents):
    assert n_clean_agents <= 5, 'office layout only allows for max 5 cleaning agents.'
    agents = []

    # BIN AGENTS
    for n in range(n_bin_agents):
        ltlf = ''
        for i in range(n_bins):
            ltlf += '(F bin%i%i) & ' % (i, n)
        ltlf = ltlf[:-3]
        agents.append(AgentSynthGame(mdp=office_spillage_5x10_mdp(r_id='%i' % n, n_bins=n_bins, is_bin=True, n_cleaners=n_clean_agents), formula=ltlf))

    # SPILLAGE AGENTS
    for n in range(n_bin_agents, n_bin_agents+n_clean_agents):
        ltlf = '(F off%i%i) & ' % (n - n_bin_agents, n)
        for i in range(n_bin_agents):
            ltlf += '(G !off%i%i) & ' % (n - n_bin_agents, i)
        ltlf = ltlf[:-3]
        agents.append(AgentSynthGame(mdp=office_spillage_5x10_mdp(r_id='%i' % n, n_bins=n_bins, is_bin=False, n_cleaners=n_clean_agents), formula=ltlf))
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/office_spillage_10x5_%i_%i_%i.p' % (n_bin_agents, n_bins, n_clean_agents), verbose=True)


def switch_test():
    agents = [
        AgentSynthGame(mdp=switch_mdp('0', 'off'), formula='G !on0'),
        AgentSynthGame(mdp=switch_mdp('1', 'off'), formula='G !on0')
    ]
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/switch_test.p', verbose=True)


if __name__ == '__main__':
    results = []
    for n in range(1, 6):
        times = []
        while len(times) < 10:
            # times.append(office_10x5(n_agents=5, n_bins=3))
            try:
                times.append(office_spillage_10x5(n_bin_agents=n, n_clean_agents=5, n_bins=1))
            except:
                print('WHOOPSIE!')
        print('MEAN TIME:', statistics.mean(times))
        print('STD DEV:', statistics.stdev(times))
        results.append((statistics.mean(times), statistics.stdev(times)))
    print(results)

# def intersection():
#     agents = [AgentSynthGame(mdp=intersection_no_turn_symmetric_labels_mdp(r_id='A', init_state='end_top'),
#                              formula='F(eba) & G!(crita & critb | crita & critc | crita & critd)'),
#               AgentSynthGame(mdp=intersection_no_turn_symmetric_labels_mdp(r_id='B', init_state='end_bot'),
#                              formula='F(etb) & G!(critb & crita | critb & critc | critb & critd)'),
#               AgentSynthGame(mdp=intersection_no_turn_symmetric_labels_mdp(r_id='C', init_state='end_left'),
#                              formula='F(erc) & G!(critc & crita | critc & critb | critc & critd)'),
#               AgentSynthGame(mdp=intersection_no_turn_symmetric_labels_mdp(r_id='D', init_state='end_right'),
#                              formula='F(eld) & G!(critd & crita | critd & critb | critd & critc)')]
#     framework = AdviserFramework(agents)
#     framework.complete_strategy_synthesis('results/intersection.p', verbose=True)
#
#
# def old_office_example():
#     agents = [AgentSynthGame(mdp=office_clean_mdp(r_id='A', init_state='4,0'),
#                              formula='F(officetra & clean & !officetrc) & '
#                                      'F(officetla & clean & !officetlb)'),
#               AgentSynthGame(mdp=office_clean_mdp(r_id='D', init_state='5,0'),
#                              formula='F(officebrd & clean & !officebrc) & '
#                                      'F(officebld & clean & !officeblb)'),
#               AgentSynthGame(mdp=office_bins_mdp(r_id='B', init_state='5,9'),
#                              formula='F(officeblb & bin) & '
#                                      'F(officetlb & bin)'),
#               AgentSynthGame(mdp=office_bins_mdp(r_id='C', init_state='4,9'),
#                              formula='F(officebrc & bin) & '
#                                      'F(officetrc & bin)')]
#     framework = AdviserFramework(agents)
#     framework.complete_strategy_synthesis('results/old_office_example.p', verbose=True)
