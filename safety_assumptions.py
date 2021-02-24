def minimal_safety_edges(synth, state_ids, coop_reach):
    # create list of all doomed states that can never reach the accepting states
    doomed_states = []
    for state, state_id in state_ids.items():
        if not coop_reach[state_id]:
            doomed_states.append(state)

    safety_edges = []
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


