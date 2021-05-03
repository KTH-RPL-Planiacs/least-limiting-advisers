import networkx as nx


def corridor_no_turn_mdp(r_id, init_state):
    m = nx.DiGraph()

    # graph information
    m.graph['name'] = 'robot' + r_id
    m.graph['init'] = init_state
    # all uppercase required, order sensitive
    m.graph['ap'] = ['ET' + r_id, 'CT' + r_id, 'CRIT' + r_id, 'CB' + r_id, 'EB' + r_id]

    # player 1 states
    m.add_node('end_top', player=1, ap=['10000'])
    m.add_node('corridor_top', player=1, ap=['01000'])
    m.add_node('corridor_top_no_turn', player=1, ap=['00000'])
    m.add_node('crit', player=1, ap=['00100'])
    m.add_node('corridor_bot', player=1, ap=['00010'])
    m.add_node('corridor_bot_no_turn', player=1, ap=['00000'])
    m.add_node('end_bot', player=1, ap=['00001'])

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


def intersection_no_turn_symmetric_labels_mdp(r_id, init_state):
    m = nx.DiGraph()

    # graph information
    m.graph['name'] = 'robot' + r_id
    m.graph['init'] = init_state
    # all uppercase required, order sensitive
    m.graph['ap'] = ['ET' + r_id, 'EB' + r_id, 'EL' + r_id, 'ER' + r_id, 'C' + r_id, 'CRIT' + r_id]

    # player 1 states
    m.add_node('end_top', player=1, ap=['100000'])
    m.add_node('end_bot', player=1, ap=['010000'])
    m.add_node('end_left', player=1, ap=['001000'])
    m.add_node('end_right', player=1, ap=['000100'])

    m.add_node('corridor_top', player=1, ap=['000010'])
    m.add_node('corridor_bot', player=1, ap=['000010'])
    m.add_node('corridor_left', player=1, ap=['000010'])
    m.add_node('corridor_right', player=1, ap=['000010'])

    m.add_node('crit', player=1, ap=['000001'])

    m.add_node('corridor_top_no_turn', player=1, ap=['000000'])
    m.add_node('corridor_bot_no_turn', player=1, ap=['000000'])
    m.add_node('corridor_left_no_turn', player=1, ap=['000000'])
    m.add_node('corridor_right_no_turn', player=1, ap=['000000'])

    # probabilistic states
    m.add_node('crit_u', player=0)
    m.add_node('crit_d', player=0)
    m.add_node('crit_l', player=0)
    m.add_node('crit_r', player=0)

    # top
    m.add_node('end_top_s', player=0)
    m.add_node('end_top_d', player=0)

    m.add_node('corridor_top_s', player=0)
    m.add_node('corridor_top_u', player=0)
    m.add_node('corridor_top_d', player=0)

    m.add_node('corridor_top_no_turn_u', player=0)
    m.add_node('corridor_top_no_turn_s', player=0)

    # bot
    m.add_node('corridor_bot_s', player=0)
    m.add_node('corridor_bot_u', player=0)
    m.add_node('corridor_bot_d', player=0)

    m.add_node('corridor_bot_no_turn_s', player=0)
    m.add_node('corridor_bot_no_turn_d', player=0)

    m.add_node('end_bot_s', player=0)
    m.add_node('end_bot_u', player=0)

    # left
    m.add_node('corridor_left_s', player=0)
    m.add_node('corridor_left_l', player=0)
    m.add_node('corridor_left_r', player=0)

    m.add_node('corridor_left_no_turn_s', player=0)
    m.add_node('corridor_left_no_turn_l', player=0)

    m.add_node('end_left_s', player=0)
    m.add_node('end_left_r', player=0)

    # right
    m.add_node('corridor_right_s', player=0)
    m.add_node('corridor_right_l', player=0)
    m.add_node('corridor_right_r', player=0)

    m.add_node('corridor_right_no_turn_s', player=0)
    m.add_node('corridor_right_no_turn_r', player=0)

    m.add_node('end_right_s', player=0)
    m.add_node('end_right_l', player=0)

    # player 1 edges
    m.add_edge('crit', 'crit_u', act='up')
    m.add_edge('crit', 'crit_d', act='down')
    m.add_edge('crit', 'crit_l', act='left')
    m.add_edge('crit', 'crit_r', act='right')

    # top
    m.add_edge('end_top', 'end_top_s', act='stay')
    m.add_edge('end_top', 'end_top_d', act='down')

    m.add_edge('corridor_top', 'corridor_top_s', act='stay')
    m.add_edge('corridor_top', 'corridor_top_u', act='up')
    m.add_edge('corridor_top', 'corridor_top_d', act='down')

    m.add_edge('corridor_top_no_turn', 'corridor_top_no_turn_s', act='stay')
    m.add_edge('corridor_top_no_turn', 'corridor_top_no_turn_u', act='up')

    # bot
    m.add_edge('corridor_bot', 'corridor_bot_s', act='stay')
    m.add_edge('corridor_bot', 'corridor_bot_u', act='up')
    m.add_edge('corridor_bot', 'corridor_bot_d', act='down')

    m.add_edge('corridor_bot_no_turn', 'corridor_bot_no_turn_s', act='stay')
    m.add_edge('corridor_bot_no_turn', 'corridor_bot_no_turn_d', act='down')

    m.add_edge('end_bot', 'end_bot_s', act='stay')
    m.add_edge('end_bot', 'end_bot_u', act='up')

    # left
    m.add_edge('corridor_left', 'corridor_left_s', act='stay')
    m.add_edge('corridor_left', 'corridor_left_l', act='left')
    m.add_edge('corridor_left', 'corridor_left_r', act='right')

    m.add_edge('corridor_left_no_turn', 'corridor_left_no_turn_s', act='stay')
    m.add_edge('corridor_left_no_turn', 'corridor_left_no_turn_l', act='left')

    m.add_edge('end_left', 'end_left_s', act='stay')
    m.add_edge('end_left', 'end_left_r', act='right')

    # right
    m.add_edge('corridor_right', 'corridor_right_s', act='stay')
    m.add_edge('corridor_right', 'corridor_right_l', act='left')
    m.add_edge('corridor_right', 'corridor_right_r', act='right')

    m.add_edge('corridor_right_no_turn', 'corridor_right_no_turn_s', act='stay')
    m.add_edge('corridor_right_no_turn', 'corridor_right_no_turn_r', act='right')

    m.add_edge('end_right', 'end_right_s', act='stay')
    m.add_edge('end_right', 'end_right_l', act='left')

    # probabilistic edges
    m.add_edge('crit_u', 'corridor_top_no_turn', prob=1.0)
    m.add_edge('crit_d', 'corridor_bot_no_turn', prob=1.0)
    m.add_edge('crit_l', 'corridor_left_no_turn', prob=1.0)
    m.add_edge('crit_r', 'corridor_right_no_turn', prob=1.0)

    # top
    m.add_edge('end_top_s', 'end_top', prob=1.0)
    m.add_edge('end_top_d', 'corridor_top', prob=1.0)

    m.add_edge('corridor_top_s', 'corridor_top', prob=1.0)
    m.add_edge('corridor_top_u', 'end_top', prob=1.0)
    m.add_edge('corridor_top_d', 'crit', prob=1.0)

    m.add_edge('corridor_top_no_turn_s', 'corridor_top_no_turn', prob=1.0)
    m.add_edge('corridor_top_no_turn_u', 'end_top', prob=1.0)

    # bot
    m.add_edge('corridor_bot_s', 'corridor_bot', prob=1.0)
    m.add_edge('corridor_bot_u', 'crit', prob=1.0)
    m.add_edge('corridor_bot_d', 'end_bot', prob=1.0)

    m.add_edge('end_bot_s', 'end_bot', prob=1.0)
    m.add_edge('end_bot_u', 'corridor_bot', prob=1.0)

    m.add_edge('corridor_bot_no_turn_s', 'corridor_bot_no_turn', prob=1.0)
    m.add_edge('corridor_bot_no_turn_d', 'end_bot', prob=1.0)

    # left
    m.add_edge('corridor_left_s', 'corridor_left', prob=1.0)
    m.add_edge('corridor_left_r', 'crit', prob=1.0)
    m.add_edge('corridor_left_l', 'end_left', prob=1.0)

    m.add_edge('end_left_s', 'end_left', prob=1.0)
    m.add_edge('end_left_r', 'corridor_left', prob=1.0)

    m.add_edge('corridor_left_no_turn_s', 'corridor_left_no_turn', prob=1.0)
    m.add_edge('corridor_left_no_turn_l', 'end_left', prob=1.0)

    # right
    m.add_edge('corridor_right_s', 'corridor_right', prob=1.0)
    m.add_edge('corridor_right_l', 'crit', prob=1.0)
    m.add_edge('corridor_right_r', 'end_right', prob=1.0)

    m.add_edge('end_right_s', 'end_right', prob=1.0)
    m.add_edge('end_right_l', 'corridor_right', prob=1.0)

    m.add_edge('corridor_right_no_turn_s', 'corridor_right_no_turn', prob=1.0)
    m.add_edge('corridor_right_no_turn_r', 'end_right', prob=1.0)

    return m


# creates a nxn grid where you can move up, down, left, right or stay in each step. does not have any AP yet
def square_grid_mdp(size, r_id, init_state):
    m = nx.DiGraph()

    # graph information
    m.graph['name'] = 'robot' + r_id
    m.graph['init'] = init_state

    # create nodes p1 and p0 and edges p1-p0
    for x in range(size):
        for y in range(size):
            node_name = '%i,%i' % (x, y)
            m.add_node(node_name, player=1)

            if x > 0:
                up_name = '%i,%i_u' % (x, y)
                m.add_node(up_name, player=0)
                m.add_edge(node_name, up_name, act='up')
            if x < size - 1:
                down_name = '%i,%i_d' % (x, y)
                m.add_node(down_name, player=0)
                m.add_edge(node_name, down_name, act='down')
            if y > 0:
                left_name = '%i,%i_l' % (x, y)
                m.add_node(left_name, player=0)
                m.add_edge(node_name, left_name, act='left')
            if y < size - 1:
                right_name = '%i,%i_r' % (x, y)
                m.add_node(right_name, player=0)
                m.add_edge(node_name, right_name, act='right')

    # create edges from probabilistic states
    for x in range(size):
        for y in range(size):
            node_name = '%i,%i' % (x, y)
            if x > 0:
                down_name = '%i,%i_d' % (x-1, y)
                m.add_edge(down_name, node_name, prob=1.0)
            if x < size - 1:
                up_name = '%i,%i_u' % (x+1, y)
                m.add_edge(up_name, node_name, prob=1.0)
            if y > 0:
                right_name = '%i,%i_r' % (x, y-1)
                m.add_edge(right_name, node_name, prob=1.0)
            if y < size - 1:
                left_name = '%i,%i_l' % (x, y+1)
                m.add_edge(left_name, node_name, prob=1.0)

    return m


def office_mdp(r_id, init_state):
    size = 10
    m = square_grid_mdp(size, r_id, init_state)
    m.graph['ap'] = ['HALLWAY' + r_id]

    # create hallway walls


    attrs = {}
    for node in m.nodes():
        if m.nodes[node]['player'] != 1:
            continue
        attrs[node] = ['0']
    nx.set_node_attributes(m, attrs, 'ap')

    return m


if __name__ == '__main__':
    mdp = office_mdp('A', '0,0')
    # mdp = corridor_no_turn_mdp('0', 'et0')
    print(mdp.nodes(data=True))
