import sys


def write_prism_model(synth, name=''):
    try:
        file_name = 'data/%s.prism' % name
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
        prism_file.write('module %s \n' % name)
        # number of states excludes probabilistic extra states
        num_states = sum(n[1]['player'] != 0 for n in synth.nodes(data=True)) - 1
        prism_file.write('  x : [0..%i] init 0;\n' % num_states)
        prism_file.write('\n')

        state_id = 1
        state_ids = {}

        synth_init = synth.graph['init']
        state_ids[synth_init] = 0

        for synth_from, synth_to in synth.edges():
            # player 3 states and probabilistic transitions are encoded in player 1 and 2 transitions
            if synth.nodes[synth_from]['player'] == 0:
                continue

            assert synth.nodes[synth_from]['player'] in [1, 2]
            # id of the originating state
            if synth_from not in state_ids.keys():
                state_ids[synth_from] = state_id
                state_id += 1
            from_id = state_ids[synth_from]

            # the successor is a non-probabilistic state, so create the transition
            if synth.nodes[synth_to]['player'] != 0:
                # id of the successor state
                if synth_to not in state_ids.keys():
                    state_ids[synth_to] = state_id
                    state_id += 1
                to_id = state_ids[synth_to]
                # player 1 transition written to PRISM
                prism_file.write('  [p%i] x=%i -> (x\'=%i); \n' % (synth.nodes[synth_from]['player'], from_id, to_id))

            # the successor is a probabilistic state, so accumulate all possible outcomes of that choice
            else:
                transition_str = '  [p%i] x=%i -> ' % (synth.nodes[synth_from]['player'], from_id)
                for synth_succ in synth.successors(synth_to):
                    assert synth.nodes[synth_succ]['player'] in [1, 2]
                    # the successor should be a player state, so get the id
                    if synth_succ not in state_ids.keys():
                        state_ids[synth_succ] = state_id
                        state_id += 1
                    succ_id = state_ids[synth_succ]
                    prob = synth.edges[synth_to, synth_succ]['prob']
                    transition_str += '%f : (x\'=%i) + ' % (prob, succ_id)   # accumulate possible outcomes
                transition_str = transition_str[:-3] + ';\n'
                prism_file.write(transition_str)

        prism_file.write('\n')
        prism_file.write('endmodule \n')
        prism_file.write('\n')

        assert len(synth.graph['acc']) > 0, '<write_prism_model> There are no accepting states!'

        reach_cond = '('
        for acc_state in synth.graph['acc']:
            acc_id = state_ids[acc_state]
            reach_cond += 'x=%i | ' % acc_id
        reach_cond = reach_cond[:-3] + ')'
        prism_file.write('label "accept" = %s ;\n' % reach_cond)

        prism_file.close()

        return file_name, state_ids

    except Exception as err:
        print('<write_prism_model>: an error occurred, no model file was written!')
        print(err)
        sys.exit(0)
