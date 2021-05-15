import networkx as nx


def corridor_mdp(r_id, init_state):
    m = nx.DiGraph()

    # graph information
    m.graph['name'] = 'robot' + r_id
    m.graph['init'] = init_state
    # all uppercase required, order sensitive
    m.graph['ap'] = ['ET' + r_id, 'CT' + r_id, 'CRIT' + r_id, 'CB' + r_id, 'EB' + r_id]

    # player 1 states
    m.add_node('end_top', player=1, ap=['10000'])
    m.add_node('corridor_top', player=1, ap=['01000'])
    m.add_node('crit', player=1, ap=['00100'])
    m.add_node('corridor_bot', player=1, ap=['00010'])
    m.add_node('end_bot', player=1, ap=['00001'])

    # probabilistic states
    m.add_node('end_top_s', player=0)
    m.add_node('end_top_d', player=0)

    m.add_node('corridor_top_s', player=0)
    m.add_node('corridor_top_u', player=0)
    m.add_node('corridor_top_d', player=0)

    m.add_node('crit_u', player=0)
    m.add_node('crit_d', player=0)

    m.add_node('corridor_bot_s', player=0)
    m.add_node('corridor_bot_u', player=0)
    m.add_node('corridor_bot_d', player=0)

    m.add_node('end_bot_s', player=0)
    m.add_node('end_bot_u', player=0)

    # player 1 edges
    m.add_edge('end_top', 'end_top_s', act='stay')
    m.add_edge('end_top', 'end_top_d', act='down')

    m.add_edge('corridor_top', 'corridor_top_s', act='stay')
    m.add_edge('corridor_top', 'corridor_top_u', act='up')
    m.add_edge('corridor_top', 'corridor_top_d', act='down')

    m.add_edge('crit', 'crit_u', act='up')
    m.add_edge('crit', 'crit_d', act='down')

    m.add_edge('corridor_bot', 'corridor_bot_s', act='stay')
    m.add_edge('corridor_bot', 'corridor_bot_u', act='up')
    m.add_edge('corridor_bot', 'corridor_bot_d', act='down')

    m.add_edge('end_bot', 'end_bot_s', act='stay')
    m.add_edge('end_bot', 'end_bot_u', act='up')

    # probabilistic edges
    m.add_edge('end_top_s', 'end_top', prob=1.0)
    m.add_edge('end_top_d', 'corridor_top', prob=1.0)

    m.add_edge('corridor_top_s', 'corridor_top', prob=1.0)
    m.add_edge('corridor_top_u', 'end_top', prob=1.0)
    m.add_edge('corridor_top_d', 'crit', prob=1.0)

    m.add_edge('crit_u', 'corridor_top', prob=1.0)
    m.add_edge('crit_d', 'corridor_bot', prob=1.0)

    m.add_edge('corridor_bot_s', 'corridor_bot', prob=1.0)
    m.add_edge('corridor_bot_u', 'crit', prob=1.0)
    m.add_edge('corridor_bot_d', 'end_bot', prob=1.0)

    m.add_edge('end_bot_s', 'end_bot', prob=1.0)
    m.add_edge('end_bot_u', 'corridor_bot', prob=1.0)
    return m


def corridor_directions_mdp(r_id, init_state):
    m = nx.DiGraph()

    # graph information
    m.graph['name'] = 'robot' + r_id
    m.graph['init'] = init_state
    # all uppercase required, order sensitive
    m.graph['ap'] = ['EL' + r_id, 'CL' + r_id, 'CRIT' + r_id, 'CR' + r_id, 'ER' + r_id, 'FR' + r_id]

    # player 1 states
    m.add_node('end_l_fr', player=1, ap=['100001'])
    m.add_node('end_l_fl', player=1, ap=['100000'])
    m.add_node('cor_l_fr', player=1, ap=['010001'])
    m.add_node('cor_l_fl', player=1, ap=['010000'])
    m.add_node('crit_fr', player=1, ap=['001001'])
    m.add_node('crit_fl', player=1, ap=['001000'])
    m.add_node('cor_r_fr', player=1, ap=['000101'])
    m.add_node('cor_r_fl', player=1, ap=['000100'])
    m.add_node('end_r_fr', player=1, ap=['000011'])
    m.add_node('end_r_fl', player=1, ap=['000010'])

    # probabilistic states
    m.add_node('end_l_fr_s', player=0)
    m.add_node('end_l_fr_t', player=0)
    m.add_node('end_l_fr_m', player=0)

    m.add_node('end_l_fl_s', player=0)
    m.add_node('end_l_fl_t', player=0)
    m.add_node('end_l_fl_m', player=0)

    m.add_node('cor_l_fr_s', player=0)
    m.add_node('cor_l_fr_t', player=0)
    m.add_node('cor_l_fr_m', player=0)

    m.add_node('cor_l_fl_s', player=0)
    m.add_node('cor_l_fl_t', player=0)
    m.add_node('cor_l_fl_m', player=0)

    m.add_node('crit_fr_s', player=0)
    m.add_node('crit_fr_t', player=0)
    m.add_node('crit_fr_m', player=0)

    m.add_node('crit_fl_s', player=0)
    m.add_node('crit_fl_t', player=0)
    m.add_node('crit_fl_m', player=0)

    m.add_node('cor_r_fr_s', player=0)
    m.add_node('cor_r_fr_t', player=0)
    m.add_node('cor_r_fr_m', player=0)

    m.add_node('cor_r_fl_s', player=0)
    m.add_node('cor_r_fl_t', player=0)
    m.add_node('cor_r_fl_m', player=0)

    m.add_node('end_r_fr_s', player=0)
    m.add_node('end_r_fr_t', player=0)
    m.add_node('end_r_fr_m', player=0)

    m.add_node('end_r_fl_s', player=0)
    m.add_node('end_r_fl_m', player=0)
    m.add_node('end_r_fl_t', player=0)

    # player 1 edges
    m.add_edge('end_l_fr', 'end_l_fr_s', act='stay')
    m.add_edge('end_l_fr', 'end_l_fr_t', act='turn')
    m.add_edge('end_l_fr', 'end_l_fr_m', act='move')

    m.add_edge('end_l_fl', 'end_l_fl_s', act='stay')
    m.add_edge('end_l_fl', 'end_l_fl_t', act='turn')
    m.add_edge('end_l_fl', 'end_l_fl_m', act='move')

    m.add_edge('cor_l_fr', 'cor_l_fr_s', act='stay')
    m.add_edge('cor_l_fr', 'cor_l_fr_t', act='turn')
    m.add_edge('cor_l_fr', 'cor_l_fr_m', act='move')

    m.add_edge('cor_l_fl', 'cor_l_fl_s', act='stay')
    m.add_edge('cor_l_fl', 'cor_l_fl_t', act='turn')
    m.add_edge('cor_l_fl', 'cor_l_fl_m', act='move')

    #m.add_edge('crit_fr', 'crit_fr_s', act='stay')
    #m.add_edge('crit_fr', 'crit_fr_t', act='turn')
    m.add_edge('crit_fr', 'crit_fr_m', act='move')

    #m.add_edge('crit_fl', 'crit_fl_s', act='stay')
    #m.add_edge('crit_fl', 'crit_fl_t', act='turn')
    m.add_edge('crit_fl', 'crit_fl_m', act='move')

    m.add_edge('cor_r_fr', 'cor_r_fr_s', act='stay')
    m.add_edge('cor_r_fr', 'cor_r_fr_t', act='turn')
    m.add_edge('cor_r_fr', 'cor_r_fr_m', act='move')

    m.add_edge('cor_r_fl', 'cor_r_fl_s', act='stay')
    m.add_edge('cor_r_fl', 'cor_r_fl_t', act='turn')
    m.add_edge('cor_r_fl', 'cor_r_fl_m', act='move')

    m.add_edge('end_r_fr', 'end_r_fr_s', act='stay')
    m.add_edge('end_r_fr', 'end_r_fr_t', act='turn')
    m.add_edge('end_r_fr', 'end_r_fr_m', act='move')

    m.add_edge('end_r_fl', 'end_r_fl_s', act='stay')
    m.add_edge('end_r_fl', 'end_r_fl_t', act='turn')
    m.add_edge('end_r_fl', 'end_r_fl_m', act='move')

    # probabilistic edges
    m.add_edge('end_l_fr_s', 'end_l_fr', prob=1.0)
    m.add_edge('end_l_fr_t', 'end_l_fl', prob=1.0)
    m.add_edge('end_l_fr_m', 'cor_l_fr', prob=1.0)

    m.add_edge('end_l_fl_s', 'end_l_fl', prob=1.0)
    m.add_edge('end_l_fl_t', 'end_l_fr', prob=1.0)
    m.add_edge('end_l_fl_m', 'end_l_fl', prob=1.0)

    m.add_edge('cor_l_fr_s', 'cor_l_fr', prob=1.0)
    m.add_edge('cor_l_fr_t', 'cor_l_fl', prob=1.0)
    m.add_edge('cor_l_fr_m', 'crit_fr', prob=1.0)

    m.add_edge('cor_l_fl_s', 'cor_l_fl', prob=1.0)
    m.add_edge('cor_l_fl_t', 'cor_l_fr', prob=1.0)
    m.add_edge('cor_l_fl_m', 'end_l_fl', prob=1.0)

    m.add_edge('crit_fr_s', 'crit_fr', prob=1.0)
    m.add_edge('crit_fr_t', 'crit_fl', prob=1.0)
    m.add_edge('crit_fr_m', 'cor_r_fr', prob=1.0)

    m.add_edge('crit_fl_s', 'crit_fl', prob=1.0)
    m.add_edge('crit_fl_t', 'crit_fr', prob=1.0)
    m.add_edge('crit_fl_m', 'cor_l_fl', prob=1.0)

    m.add_edge('cor_r_fr_s', 'cor_r_fr', prob=1.0)
    m.add_edge('cor_r_fr_t', 'cor_r_fl', prob=1.0)
    m.add_edge('cor_r_fr_m', 'end_r_fr', prob=1.0)

    m.add_edge('cor_r_fl_s', 'cor_r_fl', prob=1.0)
    m.add_edge('cor_r_fl_t', 'cor_r_fr', prob=1.0)
    m.add_edge('cor_r_fl_m', 'crit_fl', prob=1.0)

    m.add_edge('end_r_fr_s', 'end_r_fr', prob=1.0)
    m.add_edge('end_r_fr_t', 'end_r_fl', prob=1.0)
    m.add_edge('end_r_fr_m', 'end_r_fr', prob=1.0)

    m.add_edge('end_r_fl_s', 'end_r_fl', prob=1.0)
    m.add_edge('end_r_fl_t', 'end_r_fr', prob=1.0)
    m.add_edge('end_r_fl_m', 'cor_r_fl', prob=1.0)
    return m
