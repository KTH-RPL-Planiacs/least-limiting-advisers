import networkx as nx


def brokenswitch_mdp():
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


def robot1_2x3_mdp():
    m = nx.DiGraph()

    # graph information
    m.graph['name'] = 'robot1'
    m.graph['init'] = '00'
    m.graph['ap'] = ["CRITA", "FLOORA", "GOALA"]  # all uppercase required, order sensitive

    # player 1 states
    m.add_node('00', player=1, ap=['000'])
    m.add_node('01', player=1, ap=['010'])
    m.add_node('02', player=1, ap=['000'])
    m.add_node('10', player=1, ap=['000'])
    m.add_node('11', player=1, ap=['010'])
    m.add_node('12', player=1, ap=['001'])
    m.add_node('crit', player=1, ap=['100'])

    # probabilistic states
    m.add_node('00s', player=0)
    m.add_node('00r', player=0)
    m.add_node('01s', player=0)
    m.add_node('01l', player=0)
    m.add_node('01d', player=0)
    m.add_node('01r', player=0)
    m.add_node('02s', player=0)
    m.add_node('02l', player=0)
    m.add_node('10s', player=0)
    m.add_node('10r', player=0)
    m.add_node('11s', player=0)
    m.add_node('11l', player=0)
    m.add_node('11u', player=0)
    m.add_node('11r', player=0)
    m.add_node('12s', player=0)
    m.add_node('12l', player=0)
    m.add_node('critd', player=0)
    m.add_node('critu', player=0)

    # player 1 edges
    m.add_edge('00', '00s', act='stay')
    m.add_edge('00', '00r', act='right')

    m.add_edge('01', '01s', act='stay')
    m.add_edge('01', '01l', act='left')
    m.add_edge('01', '01r', act='right')
    m.add_edge('01', '01d', act='down')

    m.add_edge('02', '02s', act='stay')
    m.add_edge('02', '02l', act='left')

    m.add_edge('10', '10s', act='stay')
    m.add_edge('10', '10r', act='right')

    m.add_edge('11', '11s', act='stay')
    m.add_edge('11', '11l', act='left')
    m.add_edge('11', '11r', act='right')
    m.add_edge('11', '11u', act='up')

    m.add_edge('12', '12s', act='stay')
    m.add_edge('12', '12l', act='left')

    m.add_edge('crit', 'critu', act='up')
    m.add_edge('crit', 'critd', act='down')

    # probabilistic edges
    m.add_edge('00s', '00', prob=1.0)
    m.add_edge('00r', '01', prob=1.0)

    m.add_edge('01s', '01', prob=1.0)
    m.add_edge('01l', '00', prob=1.0)
    m.add_edge('01r', '02', prob=1.0)
    m.add_edge('01d', 'crit', prob=1.0)

    m.add_edge('02s', '02', prob=1.0)
    m.add_edge('02l', '01', prob=1.0)

    m.add_edge('10s', '10', prob=1.0)
    m.add_edge('10r', '11', prob=1.0)

    m.add_edge('11s', '11', prob=1.0)
    m.add_edge('11l', '10', prob=1.0)
    m.add_edge('11r', '12', prob=1.0)
    m.add_edge('11u', 'crit', prob=1.0)

    m.add_edge('12s', '12', prob=1.0)
    m.add_edge('12l', '11', prob=1.0)

    m.add_edge('critu', '01', prob=1.0)
    m.add_edge('critd', '11', prob=1.0)

    return m


def robot2_2x3_mdp():
    m = nx.DiGraph()

    # graph information
    m.graph['init'] = '12'
    m.graph['ap'] = ["CRITB", "FLOORB", "GOALB"]  # all uppercase required, order sensitive
    m.graph['name'] = 'robot2'

    # player 1 states
    m.add_node('00', player=1, ap=['001'])
    m.add_node('01', player=1, ap=['010'])
    m.add_node('02', player=1, ap=['000'])
    m.add_node('10', player=1, ap=['000'])
    m.add_node('11', player=1, ap=['010'])
    m.add_node('12', player=1, ap=['000'])
    m.add_node('crit', player=1, ap=['100'])

    # probabilistic states
    m.add_node('00s', player=0)
    m.add_node('00r', player=0)
    m.add_node('01s', player=0)
    m.add_node('01l', player=0)
    m.add_node('01d', player=0)
    m.add_node('01r', player=0)
    m.add_node('02s', player=0)
    m.add_node('02l', player=0)
    m.add_node('10s', player=0)
    m.add_node('10r', player=0)
    m.add_node('11s', player=0)
    m.add_node('11l', player=0)
    m.add_node('11u', player=0)
    m.add_node('11r', player=0)
    m.add_node('12s', player=0)
    m.add_node('12l', player=0)
    m.add_node('critd', player=0)
    m.add_node('critu', player=0)

    # player 1 edges
    m.add_edge('00', '00s', act='stay')
    m.add_edge('00', '00r', act='right')

    m.add_edge('01', '01s', act='stay')
    m.add_edge('01', '01l', act='left')
    m.add_edge('01', '01r', act='right')
    m.add_edge('01', '01d', act='down')

    m.add_edge('02', '02s', act='stay')
    m.add_edge('02', '02l', act='left')

    m.add_edge('10', '10s', act='stay')
    m.add_edge('10', '10r', act='right')

    m.add_edge('11', '11s', act='stay')
    m.add_edge('11', '11l', act='left')
    m.add_edge('11', '11r', act='right')
    m.add_edge('11', '11u', act='up')

    m.add_edge('12', '12s', act='stay')
    m.add_edge('12', '12l', act='left')

    m.add_edge('crit', 'critu', act='up')
    m.add_edge('crit', 'critd', act='down')

    # probabilistic edges
    m.add_edge('00s', '00', prob=1.0)
    m.add_edge('00r', '01', prob=1.0)

    m.add_edge('01s', '01', prob=1.0)
    m.add_edge('01l', '00', prob=1.0)
    m.add_edge('01r', '02', prob=1.0)
    m.add_edge('01d', 'crit', prob=1.0)

    m.add_edge('02s', '02', prob=1.0)
    m.add_edge('02l', '01', prob=1.0)

    m.add_edge('10s', '10', prob=1.0)
    m.add_edge('10r', '11', prob=1.0)

    m.add_edge('11s', '11', prob=1.0)
    m.add_edge('11l', '10', prob=1.0)
    m.add_edge('11r', '12', prob=1.0)
    m.add_edge('11u', 'crit', prob=1.0)

    m.add_edge('12s', '12', prob=1.0)
    m.add_edge('12l', '11', prob=1.0)

    m.add_edge('critu', '01', prob=1.0)
    m.add_edge('critd', '11', prob=1.0)

    return m
