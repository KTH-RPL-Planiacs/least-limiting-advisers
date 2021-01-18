def minimal_safety_assumptions(synth, state_ids, coop_reach):
    minsaf = []

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
                minsaf.append((node, succ))

    return minsaf


def simplest_safety_adviser(synth, minsaf):
    saf_adv = set()
    for edge in minsaf:
        es_from = edge[0]
        es_to = edge[1]
        assert len(list(synth.predecessors(es_from))) == 1, 'DAMN BOY'
        es_from_pred = list(synth.predecessors(es_from))[0]
        saf_adv.add((synth.nodes[es_from_pred]['ap'], frozenset(synth.edges[es_from, es_to]['guards'])))

    return saf_adv


def minimal_fairness_assumptions():
    return None
