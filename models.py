import networkx as nx


def broken_switch_mdp():
    m = nx.DiGraph()

    # graph information
    m.graph['init'] = "off"
    m.graph['ap'] = ["ON", "BROKE"]  # all uppercase required, order sensitive
    m.graph['name'] = 'broken_switch'

    # player 1 states
    m.add_node("off", player=1, ap=["00"])
    m.add_node("on", player=1, ap=["10"])
    m.add_node("broke", player=1, ap=["01"])

    # probabilistic states
    m.add_node("broke_repair", player=0)
    m.add_node("off_wait", player=0)
    m.add_node("off_switch", player=0)
    m.add_node("on_wait", player=0)
    m.add_node("on_switch", player=0)

    # player 1 edges
    m.add_edge("broke", "broke_repair", act="repair")
    m.add_edge("off", "off_wait", act="wait")
    m.add_edge("off", "off_switch", act="switch")
    m.add_edge("on", "on_wait", act="wait")
    m.add_edge("on", "on_switch", act="switch")

    # probabilistic edges
    m.add_edge("broke_repair", "off", prob=0.5)
    m.add_edge("broke_repair", "broke", prob=0.5)

    m.add_edge("off_wait", "off", prob=1)

    m.add_edge("off_switch", "on", prob=0.8)
    m.add_edge("off_switch", "off", prob=0.1)
    m.add_edge("off_switch", "broke", prob=0.1)

    m.add_edge("on_wait", "on", prob=1)
    m.add_edge("on_switch", "off", prob=1)

    return m


def corridor_mdp(r_id, init_state='00'):
    m = nx.DiGraph()

    # graph information
    m.graph['name'] = 'robot'+r_id
    m.graph['init'] = init_state
    # all uppercase required, order sensitive
    m.graph['ap'] = ['ET'+r_id, 'CT'+r_id, 'CRIT'+r_id, 'CB'+r_id, 'EB'+r_id]

    # player 1 states
    m.add_node('end_top',       player=1, ap=['10000'])
    m.add_node('corridor_top',  player=1, ap=['01000'])
    m.add_node('crit',          player=1, ap=['00100'])
    m.add_node('corridor_bot',  player=1, ap=['00010'])
    m.add_node('end_bot',       player=1, ap=['00001'])

    # probabilistic states
    m.add_node('end_top_s', player=0)
    m.add_node('end_top_d', player=0)

    m.add_node('corridor_top_s', player=0)
    m.add_node('corridor_top_u', player=0)
    m.add_node('corridor_top_d', player=0)

    m.add_node('crit_s', player=0)
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

    m.add_edge('crit', 'crit_s', act='stay')
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

    m.add_edge('crit_s', 'crit', prob=1.0)
    m.add_edge('crit_u', 'corridor_top', prob=1.0)
    m.add_edge('crit_d', 'corridor_bot', prob=1.0)

    m.add_edge('corridor_bot_s', 'corridor_bot', prob=1.0)
    m.add_edge('corridor_bot_u', 'crit', prob=1.0)
    m.add_edge('corridor_bot_d', 'end_bot', prob=1.0)

    m.add_edge('end_bot_s', 'end_bot', prob=1.0)
    m.add_edge('end_bot_u', 'corridor_bot', prob=1.0)

    return m

