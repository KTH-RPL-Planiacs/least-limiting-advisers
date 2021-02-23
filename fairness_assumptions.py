from safety_assumptions import AdviserObject
from prismhandler.prism_io import write_prism_model


def filter_player2(edge):
    if 'guards' in edge[2]:
        return True
    else:
        return False


def construct_fair_game(synth, fairness_edges):
    return synth


def minimal_fairness_edges(synth, name, prism_handler, test=False):
    # check if fairness is necessary
    win_prop = '<< p1 >> P>=1 [F \"accept\"]'
    # PRISM translations
    prism_model, state_ids = write_prism_model(synth, name + '_safe')
    prism_handler.load_model_file(prism_model, test=test)
    result = prism_handler.check_bool_property(win_prop)

    if result[0]:
        return []

    # fairness is necessary
    # start by assuming all player-2 edges are necessary
    fairness_edges = list(filter(filter_player2, synth.edges(data=True)))

    winnable = False
    round = 0
    while not winnable:
        assume_fair_synth = construct_fair_game(synth, fairness_edges)

        # PRISM translations
        prism_model, state_ids = write_prism_model(assume_fair_synth, name + '_fairness_r%i' % (round+1))
        prism_handler.load_model_file(prism_model, test=test)
        result = prism_handler.check_bool_property(win_prop)

        winnable = result[state_ids[synth.graph['init']]]

        if not winnable:
            round += 1
            break               # TODO

    return fairness_edges
