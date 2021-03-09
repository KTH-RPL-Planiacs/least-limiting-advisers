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
                print('If', obs, self.pre_ap, ', next never do', list(sog), self.adv_ap)
        elif self.adv_type == 'fairness':
            if len(self.adviser) == 0:
                print('No fairness advice!')
            for obs, sog in self.adviser.items():
                print('If', obs, self.pre_ap, ', next sometimes do', list(sog), self.adv_ap)
        else:
            print('This Adviser is not correctly initialized! '
                  'self.adv_type should be \"safety\" or \"fairness\", but is:', self.adv_type)


def reduce_set_of_guards(sog):
    # TODO REFACTORING!
    # blow up the set of guards with all possible generalizations
    new_sog = sog
    changed = True
    while changed:
        blown_up_sog = set(new_sog)
        for guard in new_sog:  # for each guard
            for i, o in enumerate(guard):  # for each bit in the guard
                # construct hypothetical test_guard
                test_guard = list(guard)
                if o == '1':
                    test_guard[i] = '0'
                elif o == '0':
                    test_guard[i] = '1'
                else:
                    test_guard[i] = 'X'
                test_guard = ''.join(test_guard)

                # check if the test_guard and the guard are different (they are not if 'X' got "flipped")
                if test_guard == guard:
                    continue

                # check if this guard with a single flipped bit is also in the existing sog
                also_in_sog = False
                for g in new_sog:  # for each g in sog, compare test_guard with g
                    match = True  # assume it is a match
                    for j in range(len(test_guard)):
                        if test_guard[j] == 'X' or g[j] == 'X':
                            continue  # skip X
                        if test_guard[j] != g[j]:
                            match = False  # counter example, can't be a match
                    if match:  # if it was a match, set already_in_sog to True
                        also_in_sog = True

                # if the hypothetical guard is not also in the new sog, we cannot reduce
                if not also_in_sog:
                    continue

                # create a reduced guard
                reduced_guard = list(guard)
                reduced_guard[i] = 'X'
                reduced_guard = ''.join(reduced_guard)
                # add it to the reduced sog
                blown_up_sog.add(reduced_guard)

        if new_sog == blown_up_sog:
            changed = False

        new_sog = blown_up_sog

    # sog is all blown up with all possible generalizations
    unnecessary_guards = set()
    for guard in new_sog:
        for other_guard in new_sog:
            # skip yourself
            if guard == other_guard:
                continue

            # check if the guard subsumes the other_guard
            subsumes = True
            for j in range(len(guard)):
                if guard[j] == 'X':
                    continue
                if other_guard[j] == 'X':
                    subsumes = False
                if not guard[j] == other_guard[j]:
                    subsumes = False
            if subsumes:
                unnecessary_guards.add(other_guard)

    return new_sog.difference(unnecessary_guards)


def simplest_adviser(synth, edges, adv_type):
    adv_obj = AdviserObject(pre_ap=synth.graph['ap'],
                            adv_ap=synth.graph['env_ap'],
                            pre_init=synth.nodes[synth.graph['init']]['ap'],
                            adv_type=adv_type)

    for edge in edges:
        es_from = edge[0]
        es_to = edge[1]
        assert len(list(synth.predecessors(es_from))) == 1, 'Your synthesized game has errors in the construction'
        es_from_pred = list(synth.predecessors(es_from))[0]
        obs = synth.nodes[es_from_pred]['ap']
        sog = synth.edges[es_from, es_to]['guards']

        # TODO REFACTORING!
        # reduce obs -> for each ap, check if a state with that ap flipped, but others same exists.
        reduced_obs = obs
        for i, o in enumerate(obs):
            # construct hypothetical obs
            test_obs = list(reduced_obs)
            if o == '1':
                continue    # TODO: currently this only reduces 0 entries (models are one-hot-encoding)
                # test_obs[i] = '0'
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

            if can_be_reduced:  # we can reduce!
                reduced_obs = list(reduced_obs)
                reduced_obs[i] = 'X'
                reduced_obs = ''.join(reduced_obs)

        # add the reduced obs,sog to the adviser
        if reduced_obs not in adv_obj.adviser.keys():
            adv_obj.adviser[reduced_obs] = set(sog)
        else:
            adv_obj.adviser[reduced_obs].union(sog)

    # reduce advice
    for obs, sog in adv_obj.adviser.items():
        adv_obj.adviser[obs] = reduce_set_of_guards(sog)

    return adv_obj
