class AdviserObject:

    def __init__(self, pre_ap, adv_ap, adv_type):
        self.pre_ap = pre_ap
        self.adv_ap = adv_ap
        self.adv_type = adv_type
        self.adviser = set()

    def print_advice(self):
        if self.adv_type == 'safety':
            if len(self.adviser) == 0:
                print('No safety advice!')
            for obs, sog in self.adviser:
                print('If', obs, self.pre_ap, 'never do', list(sog), self.adv_ap)
        elif self.adv_type == 'fairness':
            if len(self.adviser) == 0:
                print('No fairness advice!')
            for obs, sog in self.adviser:
                print('If', obs, self.pre_ap, 'sometimes do', list(sog), self.adv_ap)
        else:
            print('This Adviser is not correctly initialized! '
                  'self.adv_type should be \"safety\" or \"fairness\", but is:', self.adv_type)


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

