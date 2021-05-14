from enum import Enum


class AdviserType(Enum):
    SAFETY = 0
    FAIRNESS = 1


class AdviserObject:

    def __init__(self, pre_ap, adv_ap, pre_init, adv_type):
        self.pre_ap = pre_ap
        self.adv_ap = adv_ap
        self.adv_type = adv_type
        self.adviser = {}
        self.pre_init = pre_init

    def print_advice(self):
        if self.adv_type == AdviserType.SAFETY:
            if len(self.adviser) == 0:
                print('No safety advice!')
            for obs, sog in self.adviser.items():
                print('If', obs, self.pre_ap, ', next never do', list(sog), self.adv_ap)
        elif self.adv_type == AdviserType.FAIRNESS:
            if len(self.adviser) == 0:
                print('No fairness advice!')
            for obs, sog in self.adviser.items():
                print('If', obs, self.pre_ap, ', next sometimes do', list(sog), self.adv_ap)
        else:
            print('This Adviser is not correctly initialized! '
                  'self.adv_type should be \"SAFETY\" or \"FAIRNESS\", but is:', self.adv_type)

    def safety_adviser_to_spec(self, adv_ap_filter):
        if self.adv_type != AdviserType.SAFETY:
            print('<AgentSynthGame.adviser_to_spec> Only safety is implemented!')
            return

        safety_formulas = []

        for pre, advs in self.adviser.items():
            pre_f = ''
            for index, value in enumerate(pre):
                if value == '1':
                    pre_f += self.pre_ap[index].lower() + ' & '
                elif value == '0':
                    pre_f += '!' + self.pre_ap[index].lower() + ' & '
                else:
                    assert value == 'X', value

            adv_f = ''
            overall_not_empty = False
            for adv in advs:
                not_empty = False
                for index, value in enumerate(adv):

                    if self.adv_ap[index] not in adv_ap_filter:
                        continue
                    if value == '1':
                        adv_f += self.adv_ap[index].lower() + ' & '
                        not_empty = True
                        overall_not_empty = True
                    elif value == '0':
                        adv_f += '!' + self.adv_ap[index].lower() + ' & '
                        not_empty = True
                        overall_not_empty = True
                    else:
                        assert value == 'X', value
                if not_empty:
                    adv_f = adv_f[0:-3] + ' | '

            if all(c == 'X' for c in pre):
                spec = 'G(!(' + adv_f[0:-3] + '))'
            else:
                spec = 'G(' + pre_f[0:-3] + ' -> X !(' + adv_f[0:-3] + '))'
            if overall_not_empty:
                safety_formulas.append(spec)

        return safety_formulas


def flip_guard_bit(guard, bit, skip_ones=False):
    # construct hypothetical test_guard
    test_guard = list(guard)
    if guard[bit] == '1':
        if skip_ones:
            test_guard[bit] = '1'
        else:
            test_guard[bit] = '0'
    elif guard[bit] == '0':
        test_guard[bit] = '1'
    elif guard[bit] == 'X':
        test_guard[bit] = 'X'
    test_guard = ''.join(test_guard)
    return test_guard


def replace_guard_bit(guard, bit, lit):
    new_guard = list(guard)
    new_guard[bit] = lit
    new_guard = ''.join(new_guard)
    return new_guard


def resolve_all_x(guard):
    return_set = set()
    for i, o in enumerate(guard):
        if o == 'X':
            return_set = return_set.union(resolve_all_x(replace_guard_bit(guard, i, '0')))
            return_set = return_set.union(resolve_all_x(replace_guard_bit(guard, i, '1')))

    if len(return_set) == 0:
        return_set.add(guard)
    return return_set


def reduce_set_of_guards(sog):
    # first, resolve all generalizations
    new_sog = set()
    for g in sog:
        new_sog = new_sog.union(resolve_all_x(g))
    changed = True
    # blow up the set of guards with all possible generalizations
    while changed:
        blown_up_sog = set(new_sog)
        for guard in new_sog:  # for each guard
            for i, o in enumerate(guard):  # for each bit in the guard
                # construct hypothetical test_guard
                test_guard = flip_guard_bit(guard, i)

                # check if the test_guard and the guard are different (they are not if 'X' got "flipped")
                if test_guard == guard:
                    continue

                # if the hypothetical guard is not also in the new sog, we cannot reduce
                test_guard_in_new_sog = False
                for g in new_sog:
                    if compare_obs(test_guard, g):
                        test_guard_in_new_sog = True
                if not test_guard_in_new_sog:
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


def compare_obs(test_obs, existing_obs):

    if len(test_obs) != len(existing_obs):
        return False

    for i in range(len(test_obs)):
        if test_obs[i] == 'X' and existing_obs[i] == 'X':
            continue
        if test_obs[i] != existing_obs[i]:
            return False

    return True


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
            # TODO: currently this only reduces 0 entries
            test_obs = flip_guard_bit(reduced_obs, i, skip_ones=True)

            if test_obs == reduced_obs:
                continue

            # check if that observation exists
            can_be_reduced = True
            for node, data in synth.nodes(data=True):
                if 'ap' not in data.keys():
                    continue                # this is not a player 1 state
                existing_obs = data['ap']
                if compare_obs(test_obs, existing_obs):    # this hypothetical other obs exists, so we cannot reduce
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

    # try to merge adviser items - currently only in the case where all items have same adv and pre combine to TRUE
    reduced_pre = reduce_set_of_guards(set(adv_obj.adviser.keys()))
    if len(reduced_pre) == 1 and all(c == 'X' for c in next(iter(reduced_pre))):
        list_to_check = list(adv_obj.adviser.values())
        same = True
        for adv in list_to_check:
            if adv != list_to_check[0]:
                same = False
                break
        if same:
            adv_obj.adviser = {next(iter(reduced_pre)): list_to_check[0]}

    return adv_obj
