class AdviserObject:

    def __init__(self, pre_ap, adv_ap, pre_init, adv_type):
        self.pre_ap = pre_ap
        self.adv_ap = adv_ap
        self.adv_type = adv_type
        self.adviser = {}
        self.pre_init = pre_init

    def print_advice(self):
        if self.adv_type == 'safety':
            if len(self.adviser) == 0:
                print('No safety advice!')
            for obs, sog in self.adviser.items():
                print('If', obs, self.pre_ap, 'never do', list(sog), self.adv_ap)
        elif self.adv_type == 'fairness':
            if len(self.adviser) == 0:
                print('No fairness advice!')
            for obs, sog in self.adviser.items():
                print('If', obs, self.pre_ap, 'sometimes do', list(sog), self.adv_ap)
        else:
            print('This Adviser is not correctly initialized! '
                  'self.adv_type should be \"safety\" or \"fairness\", but is:', self.adv_type)


def minimal_safety_edges(synth, state_ids, coop_reach):
    # create list of all doomed states that can never reach the accepting states
    doomed_states = []
    for state, state_id in state_ids.items():
        if not coop_reach[state_id]:
            doomed_states.append(state)

    print('doom', len(doomed_states))

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

    print('edges', safety_edges)
    return safety_edges


def simplest_safety_adviser(synth, safety_edges):
    saf_adv = AdviserObject(pre_ap=synth.graph['ap'],
                            adv_ap=synth.graph['env_ap'],
                            pre_init=synth.nodes[synth.graph['init']]['ap'],
                            adv_type='safety')

    for edge in safety_edges:
        es_from = edge[0]
        es_to = edge[1]
        assert len(list(synth.predecessors(es_from))) == 1, 'Your synthesized game has errors in the construction'
        es_from_pred = list(synth.predecessors(es_from))[0]
        obs = synth.nodes[es_from_pred]['ap']
        sog = synth.edges[es_from, es_to]['guards']

        # minimize obs -> for each ap, check if a state with that ap flipped, but others same exists.
        reduced_obs = obs
        for i, o in enumerate(obs):
            # construct hypothetical obs
            test_obs = list(obs)
            if o == '1':
                test_obs[i] = '0'
            elif o == '0':
                test_obs[i] = '1'
            test_obs = ''.join(test_obs)
            # check if that observation exists
            can_be_reduced = True
            for node, data in synth.nodes(data=True):
                if 'ap' not in data.keys():
                    continue                # this is not a player 1 state
                existing_obs = data['ap']

                # compare the two
                match = True
                for j in range(len(test_obs)):
                    if test_obs[j] == 'X':
                        continue
                    if test_obs[j] != existing_obs[j]:
                        match = False

                if match:       # this hypothetical other obs exists, so we cannot reduce it.
                    can_be_reduced = False

            if can_be_reduced: # we can reduce!
                reduced_obs = list(reduced_obs)
                reduced_obs[i] = 'X'
                reduced_obs = ''.join(reduced_obs)

        # add the reduced obs,sog to the adviser
        if reduced_obs not in saf_adv.adviser.keys():
            saf_adv.adviser[reduced_obs] = set(sog)
        else:
            saf_adv.adviser[reduced_obs].union(sog)

    return saf_adv

