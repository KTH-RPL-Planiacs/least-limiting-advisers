class AdviserObject:
    adv_type = ''
    pre_ap = []
    adv_ap = []
    adviser = set()

    def __init__(self, pre_ap, adv_ap, adv_type):
        self.pre_ap = pre_ap
        self.adv_ap = adv_ap
        self.adv_type = adv_type


def minimal_safety_edges(synth, state_ids, coop_reach):
    safety_edges = []

    # create list of all doomed states that can never reach the accepting states
    doomed_states = []
    for state, state_id in state_ids.items():
        if coop_reach[state_id] < 1:
            doomed_states.append(state)

    # search for all player 2 edges that could lead to a doomed state from a safe state
    for node, data in synth.nodes(data=True):
        if data['player'] != 2:
            continue
        if node in doomed_states:
            continue
        for succ in synth.successors(node):
            unsafe = any(elem in doomed_states for elem in synth.successors(succ))
            if unsafe:
                safety_edges.append((node, succ))

    return safety_edges


def simplest_safety_adviser(synth, safety_edges):
    saf_adv = AdviserObject(pre_ap=synth.graph['ap'],
                            adv_ap=synth.graph['env_ap'],
                            adv_type='safety')

    for edge in safety_edges:
        es_from = edge[0]
        es_to = edge[1]
        assert len(list(synth.predecessors(es_from))) == 1, 'Your synthesized game has errors in the construction'
        es_from_pred = list(synth.predecessors(es_from))[0]
        saf_adv.adviser.add((synth.nodes[es_from_pred]['ap'], frozenset(synth.edges[es_from, es_to]['guards'])))

    return saf_adv


# delete minimal set of unsafe edges
def delete_unsafe_edges(synth, safety_edges):
    for edge in safety_edges:
        synth.remove_edge(edge[0], edge[1])


def print_ssa(synth, ssa):
    for obs, sog in ssa.adviser:
        print('If', obs, ssa.pre_ap, 'never do', list(sog), ssa.adv_ap)


# delete edges specified by OWN simplest safety adviser, which is an overapproximation of the actual needed edges
def delete_unsafe_edges_ssa(synth, ssa):
    assert ssa.adv_type == 'safety' and ssa.pre_ap == synth.graph['ap'] and ssa.adv_ap == synth.graph['env_ap'], \
        '<delete_unsafe_edges_ssa>: This method should only be called for OWN safety advisers'
    for pre, adv in ssa.adviser:
        for node, data in synth.nodes(data=True):
            # check if it's a player 2 state
            if data['player'] != 2:
                continue
            # check if the preceding player 1 state fulfills the precondition
            assert len(list(synth.predecessors(node))) == 1, \
                '<delete_unsafe_edges_ssa>: Your synthesized game has errors in the construction'
            node_pred = list(synth.predecessors(node))[0]
            if synth.nodes[node_pred]['ap'] != pre:
                continue
            # this is a state that matches the preconditions, so player2 choices will be pruned
            to_remove = []
            for succ in synth.successors(node):
                guards = set(synth.edges[node, succ]['guards'])
                for g in adv:
                    if g in guards:
                        guards.remove(g)
                if len(guards) == 0:
                    # mark edge for removal
                    to_remove.append((node, succ))
                else:
                    # save remaining choices that player 2 is still assumed to be able to do
                    synth.edges[node, succ]['guards'] = list(guards)

            # remove marked edges
            for rem_f, rem_t in to_remove:
                synth.remove_edge(rem_f, rem_t)
