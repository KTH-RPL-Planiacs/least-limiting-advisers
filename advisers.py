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

    # # reduce advice
    # for obs, sog in adv_obj.adviser.items():
    #     # TODO REFACTORING!
    #     # reduce the set of guards (sog)
    #     new_sog = sog
    #     changed = True
    #     while changed:
    #         changed = False
    #         reduced_sog = set()
    #         for guard in new_sog:
    #             for i, o in enumerate(guard):
    #                 # construct hypothetical obs
    #                 test_guard = list(guard)
    #                 if o == '1':
    #                     test_guard[i] = '0'
    #                 elif o == '0':
    #                     test_guard[i] = '1'
    #                 test_guard = ''.join(test_guard)
    #                 # check if this guard with a single flipped bit is also in the existing sog
    #                 already_in_sog = False
    #                 for g in new_sog:
    #                     # compare test_guard with g
    #                     match = True
    #                     for j in range(len(test_guard)):
    #                         if test_guard[j] == 'X':
    #                             continue
    #                         if test_guard[j] != g[j]:
    #                             match = False
    #                     if match:
    #                         already_in_sog = True
    #
    #                 if not already_in_sog:
    #                     # create reduced guard
    #                     reduced_guard = list(guard)
    #                     reduced_guard[i] = 'X'
    #                     reduced_guard = ''.join(reduced_guard)
    #
    #                     # add reduced guard if not already represented
    #                     exists = False
    #                     for g in reduced_sog:
    #                         # compare test_guard with g
    #                         match = True
    #                         for j in range(len(test_guard)):
    #                             if test_guard[j] == 'X':
    #                                 continue
    #                             if test_guard[j] != g[j]:
    #                                 match = False
    #                         if match:
    #                             exists = True
    #
    #                     if not exists:
    #                         reduced_sog.add(reduced_guard)
    #                         changed = True
    #                 else:
    #                     # add old guard if not already represented
    #                     exists = False
    #                     for g in reduced_sog:
    #                         # compare test_guard with g
    #                         match = True
    #                         for j in range(len(test_guard)):
    #                             if test_guard[j] == 'X':
    #                                 continue
    #                             if test_guard[j] != g[j]:
    #                                 match = False
    #                         if match:
    #                             exists = True
    #
    #                     if not exists:
    #                         reduced_sog.add(guard)
    #         new_sog = reduced_sog
    #         print(new_sog)

    return adv_obj
