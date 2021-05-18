from agent_synth_game import AgentSynthGame
from adviser_framework import AdviserFramework
from models.corridor import corridor_directions_mdp
from models.misc import *
from models.office_generator import *


def running_example():
    agents = [AgentSynthGame(mdp=corridor_directions_mdp(r_id='A', init_state='end_l_fr'),
                             formula='F(era) & G!(crita & critb)'),
              AgentSynthGame(mdp=corridor_directions_mdp(r_id='B', init_state='end_r_fl'),
                             formula='F(elb) & G!(critb & crita)')]
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/running_example.p', verbose=True)


def scalable_running_example(n_agents):
    assert n_agents > 1
    agents = []
    for n in range(n_agents):
        ltlf = 'F er%i & ' % n
        ltlf += 'G!('
        for m in range(n_agents):
            if m == n:
                continue
            ltlf += '(crit%i & crit%i) | ' % (n, m)
        ltlf = ltlf[:-3] + ' )'
        print(ltlf)
        agents.append(AgentSynthGame(mdp=corridor_directions_mdp(r_id='%i' % n, init_state='end_l_fr'), formula=ltlf))
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/scalable_running_example_%i.p' % n_agents, verbose=True)


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


def office_safe_spillage_10x5(n_bin_agents, n_bins, n_clean_agents):
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


def office_fair_spillage_10x5(n_bin_agents, n_bins, n_clean_agents):
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
        ltlf = '(F (off%i%i &' % (n - n_bin_agents, n)
        for i in range(n_bin_agents):
            ltlf += '!off%i%i & ' % (n - n_bin_agents, i)
        ltlf = ltlf[:-3] + '))'
        agents.append(AgentSynthGame(mdp=office_spillage_5x10_mdp(r_id='%i' % n, n_bins=n_bins, is_bin=False, n_cleaners=n_clean_agents), formula=ltlf))
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/office_spillage_10x5_%i_%i_%i.p' % (n_bin_agents, n_bins, n_clean_agents), verbose=False)


def office_crit_10x5(n_agents, n_doors):
    agents = []
    for n in range(n_agents):
        ltlf = 'F bin%i & ' % n
        for d in range(n_doors):
            ltlf += 'G!('
            for m in range(n_agents):
                if m == n:
                    continue
                ltlf += '(door%i%i & door%i%i) & ' % (d, n, d, m)
            ltlf = ltlf[:-3] + ') & '
        ltlf = ltlf[:-3]
        agents.append(AgentSynthGame(mdp=office_critical_doors_5x10_mdp(r_id='%i' % n, n_doors=n_doors), formula=ltlf))
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/office_10x5_%i_%i.p' % (n_agents, n_doors), verbose=True)


def office_crit_5x5(n_agents, n_doors):
    agents = []
    for n in range(n_agents):
        ltlf = 'F bin%i & ' % n
        for d in range(n_doors):
            ltlf += 'G!('
            for m in range(n_agents):
                if m == n:
                    continue
                ltlf += '(door%i%i & door%i%i) & ' % (d, n, d, m)
            ltlf = ltlf[:-3] + ') & '
        ltlf = ltlf[:-3]
        agents.append(AgentSynthGame(mdp=office_critical_doors_5x5_mdp(r_id='%i' % n, n_doors=n_doors), formula=ltlf))
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/office_10x5_%i_%i.p' % (n_agents, n_doors), verbose=True)


def switch_test():
    agents = [
        AgentSynthGame(mdp=switch_mdp('0', 'off'), formula='G !on0'),
        AgentSynthGame(mdp=switch_mdp('1', 'off'), formula='G !on0')
    ]
    framework = AdviserFramework(agents)
    return framework.complete_strategy_synthesis('results/switch_test.p', verbose=True)


if __name__ == '__main__':
    running_example()
