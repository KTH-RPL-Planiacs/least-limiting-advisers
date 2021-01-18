def write_safass_prop():
    file_name = 'data/safass.prop'
    prism_file = open(file_name, 'w')
    prism_file.write('filter(printall, << p1,p2 >> Pmax =? [F "accept"])')
    prism_file.close()
    return file_name


def write_prism_model(synth):
    file_name = 'data/%s.prism' % synth.graph['name']
    prism_file = open(file_name, 'w')
    # Header
    prism_file.write('//synthesis game in PRISM-games language, generated from networkx digraph model \n')
    prism_file.write('\n')
    prism_file.write('smg \n')
    prism_file.write('\n')
    # player blocks
    prism_file.write('player p1 \n')
    prism_file.write('  [p1] \n')
    prism_file.write('endplayer \n')
    prism_file.write('\n')
    prism_file.write('player p2 \n')
    prism_file.write('  [p2] \n')
    prism_file.write('endplayer \n')
    prism_file.write('\n')
    # module
    prism_file.write('module %s \n' % synth.graph['name'])
    # number of states excludes probabilistic extra states
    num_states = sum(n[1]['player'] != 0 for n in synth.nodes(data=True)) - 1
    prism_file.write('  x : [0..%i] init 0;\n' % num_states)
    prism_file.write('\n')

    state_id = 1
    state_ids = {}

    synth_init = synth.graph['init']
    state_ids[synth_init] = 0

    for synth_from, synth_to, edge_data in synth.edges(data=True):
        # player 3 states and probabilistic transitions are encoded in player 2 transitions
        if synth.nodes[synth_from]['player'] == 0:
            continue
        # id of the originating state
        if synth_from not in state_ids.keys():
            state_ids[synth_from] = state_id
            state_id += 1
        from_id = state_ids[synth_from]

        if synth.nodes[synth_from]['player'] == 1:
            # id of the successor state
            if synth_to not in state_ids.keys():
                state_ids[synth_to] = state_id
                state_id += 1
            to_id = state_ids[synth_to]
            # player 1 transition written to PRISM
            prism_file.write('  [p1] x=%i -> (x\'=%i); \n' % (from_id, to_id))

        elif synth.nodes[synth_from]['player'] == 2:
            # every player 2 choice is it's own transition
            transition_str = '  [p2] x=%i -> ' % from_id
            # accumulate all possible outcomes of that choice
            for synth_succ in synth.successors(synth_to):
                # add player 1 states
                if synth_succ not in state_ids.keys():
                    state_ids[synth_succ] = state_id
                    state_id += 1
                succ_id = state_ids[synth_succ]
                prob = synth.edges[synth_to, synth_succ]['prob']
                transition_str += '%f : (x\'=%i) + ' % (prob, succ_id)
            transition_str = transition_str[:-3] + ';\n'
            prism_file.write(transition_str)

    prism_file.write('\n')
    prism_file.write('endmodule \n')
    prism_file.write('\n')

    if len(synth.graph['acc']) > 0:

        reach_cond = '('
        for acc_state in synth.graph['acc']:
            acc_id = state_ids[acc_state]
            reach_cond += 'x=%i | ' % acc_id
        reach_cond = reach_cond[:-3] + ')'
        prism_file.write('label "accept" = %s ;\n' % reach_cond)

    prism_file.close()

    return file_name, state_ids
