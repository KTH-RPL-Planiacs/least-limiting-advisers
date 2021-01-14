import networkx as nx
import queue
import time
from itertools import chain, combinations
from copy import deepcopy

from ltlf2dfa_nx import formula_to_nxgraph


# group_and_flip({'a':[1,2], 'b':[2,1], 'c':[1,3,5]}) --> {{frozenset({1, 2}): ['a', 'b'], frozenset({1, 3, 5}): ['c']}}
def group_and_flip(d):
    grouped_dict = {}
    for k, v in d.items():
        hashable_v = frozenset(v)
        if hashable_v not in grouped_dict:
            grouped_dict[hashable_v] = [k]
        else:
            grouped_dict[hashable_v].append(k)
    return grouped_dict


# list(powerset([1,2,3])) --> [(), (1,), (2,), (3,), (1,2), (1,3), (2,3), (1,2,3)]
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def create_guard(opt, ap):
    guard = ''
    for e in ap:
        if e in opt:
            guard += '1'
        else:
            guard += '0'
    return guard


def dfa_mdp_synth(dfa, mdp):
    synth = nx.DiGraph()
    synth.graph['name'] = mdp.graph['name'] + 'x' + dfa.graph['name']
    synth.graph['acc'] = []  # list of accepting states

    # initial state
    dfa_init = dfa.graph['init']
    mdp_init = mdp.graph['init']
    synth_init = (mdp_init, dfa_init)

    if dfa_init in dfa.graph['acc']:
        synth.graph['acc'].append(synth_init)

    synth.add_node(synth_init, player=1, ap=mdp.nodes[mdp_init]['ap'])
    synth.graph['init'] = synth_init

    # dfa and mdp atomic propositions
    dfa_ap = dfa.graph['ap']
    mdp_ap = mdp.graph['ap']
    synth.graph['ap'] = mdp_ap  # order sensitive because of the edge guards
    env_ap = list(set(dfa_ap).difference(set(mdp_ap)))  # order sensitive
    joined_ap = mdp_ap + env_ap

    # todo queue
    que = queue.Queue()
    que.put(synth_init)  # initialize the queue

    # work the queue
    while not que.empty():
        synth_from = que.get()
        mdp_from = synth_from[0]
        dfa_from = synth_from[1]

        assert synth.nodes[synth_from]['player'] in [1, 2, 0], "Each state need to belong to player 1,2 or 0!"

        # player 1 states, mdp gets to move
        if synth.nodes[synth_from]['player'] == 1:
            # for all possible mdp moves
            for mdp_succ in mdp.successors(mdp_from):
                assert mdp.nodes[mdp_succ]['player'] == 0  # this should be a probabilistic state in the mdp
                # add the new state to the synthesis product and connect it
                synth_succ = (mdp_succ, dfa_from)
                if not synth.has_node(synth_succ):
                    synth.add_node(synth_succ, player=2)
                    que.put(synth_succ)  # put new states in queue
                synth.add_edge(synth_from, synth_succ, act=mdp.edges[mdp_from, mdp_succ]['act'])

        # player 2 states, opponent fills out "missing" propositions
        elif synth.nodes[synth_from]['player'] == 2:
            results = {}  # possible outcomes are stored

            for opt in powerset(env_ap):
                # generate guard for chosen option
                opt_guard = create_guard(opt, env_ap)
                results[opt_guard] = []

                for mdp_succ in mdp.successors(mdp_from):
                    # generate configuration guard for chosen option and potential next mdp state
                    mdp_obs = mdp.nodes[mdp_succ]['ap'][0]
                    config = mdp_obs + opt_guard

                    for dfa_succ in dfa.successors(dfa_from):
                        # we are gonna delete parts, deepcopy for safety
                        dfa_guards = deepcopy(dfa.edges[dfa_from, dfa_succ]['guard'])

                        # check if config matches at least one dfa guard
                        for i in range(0, len(config)):
                            if joined_ap[i] in dfa_ap:
                                j = dfa_ap.index(joined_ap[i])

                                for guard in dfa_guards:
                                    if guard[j] != 'X' and guard[j] != config[i]:
                                        # if a dfa guard is not matching to the current config, remove it
                                        dfa_guards.remove(guard)

                        if len(dfa_guards) > 0:  # this config does match to this dfa successor
                            results[opt_guard].append((mdp_succ, dfa_succ))

            # flip and group the results to see which options lead to the same results
            grouped_results = group_and_flip(results)

            for res, opts in grouped_results.items():
                # TODO: simplify guards for each grouped option

                # create a probabilistic state, add it and connect it
                synth_succ = (mdp_from, dfa_from, frozenset(opts))
                if not synth.has_node(synth_succ):
                    synth.add_node(synth_succ, player=0, res=res)
                    que.put(synth_succ)  # put new states in queue
                synth.add_edge(synth_from, synth_succ, guards=opts)

        # player 3 states, probabilistic function moves and dfa moves accordingly
        elif synth.nodes[synth_from]['player'] == 0:
            for synth_succ in synth.nodes[synth_from]['res']:
                mdp_succ = synth_succ[0]
                dfa_succ = synth_succ[1]

                if not synth.has_node(synth_succ):
                    synth.add_node(synth_succ, player=1, ap=mdp.nodes[mdp_succ]['ap'])
                    que.put(synth_succ)  # put new states in queue
                synth.add_edge(synth_from, synth_succ, prob=mdp.edges[mdp_from, mdp_succ]['prob'])

    return synth


if __name__ == '__main__':
    # dummy mdp
    # player 1 states
    nx_mdp = nx.DiGraph()
    nx_mdp.graph['name'] = 'DUMMY_MDP'
    nx_mdp.add_node("off", player=1, ap=["10"])
    nx_mdp.add_node("on", player=1, ap=["01"])
    # probabilistic states
    nx_mdp.add_node("off_wait", player=0)
    nx_mdp.add_node("off_switch", player=0)
    nx_mdp.add_node("on_wait", player=0)
    nx_mdp.add_node("on_switch", player=0)
    # player 1 edges
    nx_mdp.add_edge("off", "off_wait", act="wait")
    nx_mdp.add_edge("off", "off_switch", act="switch")
    nx_mdp.add_edge("on", "on_wait", act="wait")
    nx_mdp.add_edge("on", "on_switch", act="switch")
    # probabilistic edges
    nx_mdp.add_edge("off_wait", "off", prob=1)
    nx_mdp.add_edge("off_switch", "on", prob=0.9)
    nx_mdp.add_edge("off_switch", "off", prob=0.1)
    nx_mdp.add_edge("on_wait", "on", prob=1)
    nx_mdp.add_edge("on_switch", "off", prob=0.9)
    nx_mdp.add_edge("on_switch", "on", prob=0.1)
    # graph information
    nx_mdp.graph['init'] = "off"
    nx_mdp.graph['ap'] = ["OFF", "ON"]  # all uppercase required, order sensitive

    # DFA from LTL formula
    nx_dfa = formula_to_nxgraph("G(req -> F on)")

    start_time = time.time()
    # synthesis game according to paper
    synth_prod = dfa_mdp_synth(nx_dfa, nx_mdp)
    print('Created synthesis game:', synth_prod.graph['name'])
    print(len(synth_prod.nodes), 'states,', len(synth_prod.edges), 'edges')
    print('Took', time.time() - start_time, 'seconds.')
