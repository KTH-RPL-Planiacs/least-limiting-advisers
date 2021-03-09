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


def flip_guard_bit(guard, bit, skip_ones=False):
    # construct hypothetical test_guard
    test_guard = list(guard)
    if guard[bit] == '1' and not skip_ones:
        test_guard[bit] = '0'
    elif guard[bit] == '0':
        test_guard[bit] = '1'
    else:
        test_guard[bit] = 'X'
    test_guard = ''.join(test_guard)
    return test_guard


def replace_guard_bit(guard, bit, lit):
    new_guard = list(guard)
    new_guard[bit] = lit
    new_guard = ''.join(new_guard)
    return new_guard


def match_guards(guard, other_guard):
    match = True                # assume it is a match
    for j in range(len(guard)):
        if guard[j] == 'X' or other_guard[j] == 'X':
            continue            # X always matches
        if guard[j] != other_guard[j]:
            match = False       # counter-proof, cannot be a match
    return match


def reduce_set_of_guards(sog):
    # blow up the set of guards with all possible generalizations
    new_sog = sog
    changed = True
    while changed:
        blown_up_sog = set(new_sog)
        for guard in new_sog:  # for each guard
            for i, o in enumerate(guard):  # for each bit in the guard
                # construct hypothetical test_guard
                test_guard = flip_guard_bit(guard, i)

                # check if the test_guard and the guard are different (they are not if 'X' got "flipped")
                if test_guard == guard:
                    continue

                # check if this guard with a single flipped bit is also in the existing sog
                also_in_sog = False
                for g in new_sog:  # for each g in sog, compare test_guard with g
                    if match_guards(test_guard, g):  # if it was a match, set already_in_sog to True
                        also_in_sog = True
                        break

                # if the hypothetical guard is not also in the new sog, we cannot reduce
                if not also_in_sog:
                    continue

                # create a reduced guard
                reduced_guard = replace_guard_bit(guard, i, 'X')
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

        # reduce obs -> for each ap, check if a state with that ap flipped, but others same exists.
        reduced_obs = obs
        for i, o in enumerate(obs):
            # construct hypothetical obs
            # TODO: currently this only reduces 0 entries (models are one-hot-encoding)
            test_obs = flip_guard_bit(reduced_obs, i, skip_ones=True)

            # check if that observation exists
            can_be_reduced = True
            for node, data in synth.nodes(data=True):
                if 'ap' not in data.keys():
                    continue                # this is not a player 1 state
                existing_obs = data['ap']

                if match_guards(test_obs, existing_obs):    # this hypothetical other obs exists, so we cannot reduce
                    can_be_reduced = False

            if can_be_reduced:  # we can reduce!
                reduced_obs = replace_guard_bit(reduced_obs, i, 'X')

        # add the reduced obs,sog to the adviser
        if reduced_obs not in adv_obj.adviser.keys():
            adv_obj.adviser[reduced_obs] = set(sog)
        else:
            adv_obj.adviser[reduced_obs].union(sog)

    # reduce advice
    for obs, sog in adv_obj.adviser.items():
        adv_obj.adviser[obs] = reduce_set_of_guards(sog)

    return adv_obj
