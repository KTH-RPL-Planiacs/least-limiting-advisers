import networkx as nx
import queue
from itertools import chain, combinations
from copy import deepcopy
from fairness_assumptions import construct_fair_game
from advisers import AdviserType


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


def sog_fits_to_guard(guard, sog, guard_ap, sog_ap):
    guards = deepcopy(sog)

    # check if this guard fits to one of the guards
    for i, g_value in enumerate(guard):
        if g_value == 'X':
            continue
        if guard_ap[i] in sog_ap:
            j = sog_ap.index(guard_ap[i])
            wrong_guards = []
            for guard in guards:
                if guard[j] != 'X' and guard[j] != g_value:
                    # if a synth guard is not matching to the current config, mark for removal
                    wrong_guards.append(guard)
            # remove marked guards
            for wg in wrong_guards:
                guards.remove(wg)

    return guards


class AgentSynthGame:

    def __init__(self, mdp, formula, name='agent'):
        self.mdp = mdp
        self.spec = formula
        self.dfa = None
        self.synth = nx.DiGraph()
        self.name = mdp.graph['name'] + '_' + name
        self.own_advisers = []
        self.other_advisers = []

    def get_spec_formula(self):
        """
        creates the spec formula from own spec + other safety advisers
        :return: the full LTLf specification formula
        """
        f = self.spec

        safety_formulas = []
        for adviser in self.other_advisers:
            if not adviser.adv_type == AdviserType.SAFETY:
                continue

            safety_formulas.extend(adviser.safety_adviser_to_spec())

        f += ' & '

        for s in safety_formulas:
            f += '(' + s + ') & '

        f = f[:-3]

        return f

    def create_dfa(self, parser):
        full_spec = self.get_spec_formula()
        parser.parse_formula(full_spec)
        self.dfa = parser.to_nxgraph()

    def create_synthesis_game(self):
        assert self.dfa, '<AgentSynthGame.create_synthesis_game> set self.dfa before calling this function!'

        self.synth = nx.DiGraph()
        self.synth.graph['acc'] = []  # list of accepting states

        # initial state
        dfa_init = self.dfa.graph['init']
        mdp_init = self.mdp.graph['init']
        synth_init = (mdp_init, dfa_init)

        if dfa_init in self.dfa.graph['acc']:
            self.synth.graph['acc'].append(synth_init)

        self.synth.add_node(synth_init, player=1, ap=self.mdp.nodes[mdp_init]['ap'][0])
        self.synth.graph['init'] = synth_init

        # dfa and mdp atomic propositions
        dfa_ap = self.dfa.graph['ap']
        mdp_ap = self.mdp.graph['ap']
        self.synth.graph['ap'] = mdp_ap  # order sensitive because of the edge guards
        env_ap = list(set(dfa_ap).difference(set(mdp_ap)))  # order sensitive
        self.synth.graph['env_ap'] = env_ap
        joined_ap = mdp_ap + env_ap

        # queue of open states
        que = queue.Queue()
        que.put(synth_init)  # initialize the queue

        # work the queue
        while not que.empty():
            synth_from = que.get()
            mdp_from = synth_from[0]
            dfa_from = synth_from[1]

            assert self.synth.nodes[synth_from]['player'] in [1, 2, 0], "Each state need to belong to player 1,2 or 0!"

            # player 1 states, mdp gets to move
            if self.synth.nodes[synth_from]['player'] == 1:
                # for all possible mdp moves
                for mdp_succ in self.mdp.successors(mdp_from):
                    assert self.mdp.nodes[mdp_succ]['player'] == 0  # this should be a probabilistic state in the mdp
                    # add the new state to the synthesis product and connect it
                    synth_succ = (mdp_succ, dfa_from)
                    if not self.synth.has_node(synth_succ):
                        self.synth.add_node(synth_succ, player=2)
                        que.put(synth_succ)  # put new states in queue
                    self.synth.add_edge(synth_from, synth_succ, act=self.mdp.edges[mdp_from, mdp_succ]['act'])

            # player 2 states, opponent fills out "missing" propositions
            elif self.synth.nodes[synth_from]['player'] == 2:
                results = {}  # possible outcomes are stored

                for opt in powerset(env_ap):
                    # generate guard for chosen option
                    opt_guard = create_guard(opt, env_ap)
                    results[opt_guard] = []

                    for mdp_succ in self.mdp.successors(mdp_from):
                        # generate configuration guard for chosen option and potential next mdp state
                        mdp_obs = self.mdp.nodes[mdp_succ]['ap'][0]
                        config = mdp_obs + opt_guard

                        for dfa_succ in self.dfa.successors(dfa_from):
                            # check if config matches at least one dfa guard
                            matched_guards = sog_fits_to_guard(config, self.dfa.edges[dfa_from, dfa_succ]['guard'],
                                                               joined_ap, dfa_ap)
                            if len(matched_guards) > 0:  # this config matches to this dfa successor
                                results[opt_guard].append((mdp_succ, dfa_succ))

                # flip and group the results to see which options lead to the same results
                grouped_results = group_and_flip(results)

                for res, opts in grouped_results.items():
                    # TODO: simplify guards for each grouped option

                    # create a probabilistic state, add it and connect it
                    synth_succ = (mdp_from, dfa_from, frozenset(opts))
                    if not self.synth.has_node(synth_succ):
                        self.synth.add_node(synth_succ, player=0, res=res)
                        que.put(synth_succ)  # put new states in queue
                    self.synth.add_edge(synth_from, synth_succ, guards=opts)

            # player 3 states, probabilistic function moves and dfa moves accordingly
            elif self.synth.nodes[synth_from]['player'] == 0:
                for synth_succ in self.synth.nodes[synth_from]['res']:
                    mdp_succ = synth_succ[0]
                    dfa_succ = synth_succ[1]

                    if not self.synth.has_node(synth_succ):
                        self.synth.add_node(synth_succ, player=1, ap=self.mdp.nodes[mdp_succ]['ap'][0])
                        if dfa_succ in self.dfa.graph['acc']:
                            self.synth.graph['acc'].append(synth_succ)
                        que.put(synth_succ)  # put new states in queue
                    self.synth.add_edge(synth_from, synth_succ, prob=self.mdp.edges[mdp_from, mdp_succ]['prob'])
                # res is only temporarily needed for creation of player 3 state successors, not in the final product
                del self.synth.nodes[synth_from]['res']

    # delete minimal set of unsafe edges
    def delete_unsafe_edges(self, safety_edges):
        for edge in safety_edges:
            self.synth.remove_edge(edge[0], edge[1])

    # returns edges affected by OWN simplest fairness adviser
    def assumed_fair_edges_sfa(self, sfa):
        assert sfa.adv_type == AdviserType.FAIRNESS
        assert sfa.pre_ap == self.synth.graph['ap']
        assert set(sfa.adv_ap).issubset(set(self.synth.graph['env_ap']))

        fairness_edges = []

        for pre, adv in sfa.adviser.items():
            for node, data in self.synth.nodes(data=True):
                # check if it's a player 2 state
                if data['player'] != 2:
                    continue

                # check if the preceding player 1 state fulfills the precondition
                assert len(list(self.synth.predecessors(node))) == 1, \
                    '<AgentSynthGame.assumed_fair_edges_sfa>: Your synthesized game has errors in the construction'
                node_pred = list(self.synth.predecessors(node))[0]

                if not sog_fits_to_guard(self.synth.nodes[node_pred]['ap'], [pre], self.synth.graph['ap'], sfa.pre_ap):
                    continue

                # this is a state that matches the preconditions
                for succ in self.synth.successors(node):

                    guards = deepcopy(self.synth.edges[node, succ]['guards'])
                    for g in adv:
                        matched_guards = sog_fits_to_guard(g, guards, sfa.adv_ap, self.synth.graph['env_ap'])
                        if matched_guards:
                            fairness_edges.append((node, succ, self.synth.edges[node, succ]))
                            break

        return fairness_edges

    # delete edges specified by OWN simplest safety adviser, which is an overapproximation of the actual needed edges
    def delete_unsafe_edges_ssa(self, ssa):
        assert ssa.adv_type == AdviserType.SAFETY
        assert ssa.pre_ap == self.synth.graph['ap']
        assert set(ssa.adv_ap).issubset(set(self.synth.graph['env_ap']))

        for pre, adv in ssa.adviser.items():
            for node, data in self.synth.nodes(data=True):
                # check if it's a player 2 state
                if data['player'] != 2:
                    continue
                # check if the preceding player 1 state fulfills the precondition
                assert len(list(self.synth.predecessors(node))) == 1, \
                    '<AgentSynthGame.delete_unsafe_edges_ssa>: Your synthesized game has errors in the construction'
                node_pred = list(self.synth.predecessors(node))[0]

                if not sog_fits_to_guard(self.synth.nodes[node_pred]['ap'], [pre], self.synth.graph['ap'], ssa.pre_ap):
                    continue

                # this is a state that matches the preconditions, so player2 choices will be pruned
                to_remove = []
                for succ in self.synth.successors(node):
                    guards = deepcopy(self.synth.edges[node, succ]['guards'])
                    for g in adv:
                        matched_guards = sog_fits_to_guard(g, guards, ssa.adv_ap, self.synth.graph['env_ap'])
                        for mg in matched_guards:
                            guards.remove(mg)
                    if len(guards) == 0:
                        # mark edge for removal
                        to_remove.append((node, succ))
                    else:
                        # save remaining choices that player 2 is still assumed to be able to do
                        self.synth.edges[node, succ]['guards'] = list(guards)

                # remove marked edges
                for rem_f, rem_t in to_remove:
                    self.synth.remove_edge(rem_f, rem_t)

    def modify_game_own_advisers(self, additional_pruning=False):
        fairness_edges = []

        # prune by own safety advisers and collect assumed fair edges
        for adviser in self.own_advisers:
            if adviser.adv_type == AdviserType.SAFETY:
                self.delete_unsafe_edges_ssa(adviser)
            if adviser.adv_type == AdviserType.FAIRNESS:
                fairness_edges.extend(self.assumed_fair_edges_sfa(adviser))

        # modify by own fairness edges
        self.synth = construct_fair_game(self.synth, fairness_edges)

        if additional_pruning:
            # prune unreachable nodes
            reach = nx.single_source_shortest_path_length(self.synth, self.synth.graph['init'])

            unreachable_nodes = []
            for node in self.synth.nodes:
                if node not in reach.keys():
                    unreachable_nodes.append(node)

            for urn in unreachable_nodes:
                self.synth.remove_node(urn)

    # modify the game according to "simplest fairness incorporation"
    # just fulfill the advice every time with probability > 0
    def modify_game_other_fairness(self):
        nodes_to_add = {}

        for sfa in self.other_advisers:
            if not sfa.adv_type == AdviserType.FAIRNESS:
                continue

            for obs, adv in sfa.adviser.items():
                # in each player 1 state, if player 1 cannot fulfill the advice, then this induces new safety advice.
                for node, data in self.synth.nodes(data=True):
                    # check if it's a player 1 state
                    if data['player'] != 1:
                        continue

                    available_actions = []
                    promise_actions = []

                    # check if they have actions that would fulfill the advice
                    mdp_state = node[0]

                    for mdp_succ in self.mdp.successors(mdp_state):
                        available_actions.append(self.mdp.edges[mdp_state, mdp_succ]['act'])

                        valid_choice = False
                        for outcome in self.mdp.successors(mdp_succ):
                            outcome_obs = self.mdp.nodes[outcome]['ap'][0]
                            fitting_sog = sog_fits_to_guard(outcome_obs, adv, self.mdp.graph['ap'], sfa.adv_ap)
                            if fitting_sog:
                                valid_choice = True
                                break

                        if valid_choice:
                            promise_actions.append(self.mdp.edges[mdp_state, mdp_succ]['act'])

                    if not promise_actions:
                        print('IN THIS STATE', node, 'I CANNOT FULFILL:')
                        print(obs, adv)
                        print('')
                        return False

                    if node not in nodes_to_add.keys():
                        nodes_to_add[node] = {}

                    # if all available actions fulfill the promise, we do not need to keep track of this fairness
                    if not promise_actions == available_actions:
                        nodes_to_add[node][(obs, tuple(sfa.pre_ap))] = promise_actions

        # we now have gathered all information about new promises and can construct the new promise_fulfilling states
        for node, promises in nodes_to_add.items():
            # save old predecessors of node for later
            node_preds = list(self.synth.predecessors(node))
            # create new probabilistic node to choose between promise nodes
            prob_node = (node, 'promise')
            self.synth.add_node(prob_node, player=0, promise_node=True)
            p = 1 / (len(promises) + 1)

            for pre, promise in promises.items():
                # for each different fairness advice, create a promise node and connect
                promise_node = (node, 'promise'+pre[0]+str(pre[1]))
                self.synth.add_node(promise_node, player=1)
                self.synth.add_edge(prob_node, promise_node, prob=p, pre=pre)

                for succ in self.synth.successors(node):
                    # connect from promise node to player-2 node,
                    #  but only enable choice if it fulfills the promise
                    if self.synth.edges[node, succ]['act'] in promise:
                        self.synth.add_edge(promise_node, succ)

            # don't forget the unrestrained option to the original node
            self.synth.add_edge(prob_node, node, prob=p)

            # sever old connections and reconnect
            for pred in node_preds:
                self.synth.add_edge(pred, prob_node, prob=self.synth.edges[pred, node]['prob'])
                self.synth.remove_edge(pred, node)
        return True
