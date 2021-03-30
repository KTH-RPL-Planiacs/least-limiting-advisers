import networkx as nx


def corridor_no_turn_mdp(r_id, init_state='00'):
    m = nx.DiGraph()

    # graph information
    m.graph['name'] = 'robot'+r_id
    m.graph['init'] = init_state
    # all uppercase required, order sensitive
    m.graph['ap'] = ['ET'+r_id, 'CT'+r_id, 'CRIT'+r_id, 'CB'+r_id, 'EB'+r_id]

    # player 1 states
    m.add_node('end_top',       player=1, ap=['10000'])
    m.add_node('corridor_top',  player=1, ap=['01000'])
    m.add_node('corridor_top_no_turn',  player=1, ap=['00000'])
    m.add_node('crit',          player=1, ap=['00100'])
    m.add_node('corridor_bot',  player=1, ap=['00010'])
    m.add_node('corridor_bot_no_turn', player=1, ap=['00000'])
    m.add_node('end_bot',       player=1, ap=['00001'])

    # probabilistic states
    m.add_node('end_top_s', player=0)
    m.add_node('end_top_d', player=0)

    m.add_node('corridor_top_s', player=0)
    m.add_node('corridor_top_u', player=0)
    m.add_node('corridor_top_d', player=0)

    m.add_node('corridor_top_no_turn_u', player=0)
    m.add_node('corridor_top_no_turn_s', player=0)

    m.add_node('crit_u', player=0)
    m.add_node('crit_d', player=0)

    m.add_node('corridor_bot_s', player=0)
    m.add_node('corridor_bot_u', player=0)
    m.add_node('corridor_bot_d', player=0)

    m.add_node('corridor_bot_no_turn_s', player=0)
    m.add_node('corridor_bot_no_turn_d', player=0)

    m.add_node('end_bot_s', player=0)
    m.add_node('end_bot_u', player=0)

    # player 1 edges
    m.add_edge('end_top', 'end_top_s', act='stay')
    m.add_edge('end_top', 'end_top_d', act='down')

    m.add_edge('corridor_top', 'corridor_top_s', act='stay')
    m.add_edge('corridor_top', 'corridor_top_u', act='up')
    m.add_edge('corridor_top', 'corridor_top_d', act='down')

    m.add_edge('corridor_top_no_turn', 'corridor_top_no_turn_s', act='stay')
    m.add_edge('corridor_top_no_turn', 'corridor_top_no_turn_u', act='up')

    m.add_edge('crit', 'crit_u', act='up')
    m.add_edge('crit', 'crit_d', act='down')

    m.add_edge('corridor_bot', 'corridor_bot_s', act='stay')
    m.add_edge('corridor_bot', 'corridor_bot_u', act='up')
    m.add_edge('corridor_bot', 'corridor_bot_d', act='down')

    m.add_edge('corridor_bot_no_turn', 'corridor_bot_no_turn_s', act='stay')
    m.add_edge('corridor_bot_no_turn', 'corridor_bot_no_turn_d', act='down')

    m.add_edge('end_bot', 'end_bot_s', act='stay')
    m.add_edge('end_bot', 'end_bot_u', act='up')

    # probabilistic edges
    m.add_edge('end_top_s', 'end_top', prob=1.0)
    m.add_edge('end_top_d', 'corridor_top', prob=1.0)

    m.add_edge('corridor_top_s', 'corridor_top', prob=1.0)
    m.add_edge('corridor_top_u', 'end_top', prob=1.0)
    m.add_edge('corridor_top_d', 'crit', prob=1.0)

    m.add_edge('crit_u', 'corridor_top_no_turn', prob=1.0)
    m.add_edge('crit_d', 'corridor_bot_no_turn', prob=1.0)

    m.add_edge('corridor_bot_s', 'corridor_bot', prob=1.0)
    m.add_edge('corridor_bot_u', 'crit', prob=1.0)
    m.add_edge('corridor_bot_d', 'end_bot', prob=1.0)

    m.add_edge('end_bot_s', 'end_bot', prob=1.0)
    m.add_edge('end_bot_u', 'corridor_bot', prob=1.0)

    m.add_edge('corridor_top_no_turn_s', 'corridor_top_no_turn', prob=1.0)
    m.add_edge('corridor_top_no_turn_u', 'end_top', prob=1.0)

    m.add_edge('corridor_bot_no_turn_s', 'corridor_bot_no_turn', prob=1.0)
    m.add_edge('corridor_bot_no_turn_d', 'end_bot', prob=1.0)

    return m